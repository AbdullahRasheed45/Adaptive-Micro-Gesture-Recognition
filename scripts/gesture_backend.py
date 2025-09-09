import asyncio
import websockets
import json
import numpy as np
import tensorflow.lite as tflite
import cv2
import mediapipe as mp
import threading
import time
from collections import deque
import os

class GestureRecognitionBackend:
    def __init__(self):
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1, 
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Load TFLite model
        self.load_model()
        
        # Gesture mapping
        self.gesture_map = {
            0: "write_start",
            1: "write_stop", 
            2: "erase",
            3: "zoom_in",
            4: "zoom_out",
            5: "draw_shapes",
            6: "undo",
            7: "redo",
            8: "change_color",
            9: "save",
            10: "pan",
            11: "clear_all"
        }
        
        # Frame buffer for sequence processing
        self.frame_buffer = deque(maxlen=4)
        self.sequence_length = 4
        
        # WebSocket connections
        self.connected_clients = set()
        
        # Camera setup
        self.cap = None
        self.camera_thread = None
        self.running = False
        
        # Gesture state
        self.current_gesture = None
        self.gesture_confidence = 0.0
        self.last_gesture_time = 0
        self.gesture_cooldown = 0.5  # 500ms cooldown between gestures
        
    def load_model(self):
        """Load the TFLite model"""
        model_path = "models/gesture_model_3d_final.tflite"
        
        try:
            # Try loading with Flex delegate first
            flex_delegate_path = r"C:\Users\USER\anaconda3\Lib\site-packages\tensorflow\lite\delegates\flex\flex_delegate.dll"
            
            if os.path.exists(flex_delegate_path):
                delegate_options = {
                    "target": "CPU",
                    "library_path": flex_delegate_path
                }
                self.interpreter = tflite.Interpreter(
                    model_path=model_path,
                    experimental_delegates=[tflite.experimental.load_delegate('TFLite_FlexDelegate', delegate_options)]
                )
                print("Loaded model with Flex delegate")
            else:
                self.interpreter = tflite.Interpreter(model_path=model_path)
                print("Loaded model without Flex delegate")
                
        except Exception as e:
            print(f"Error loading model: {e}")
            # Fallback to basic interpreter
            self.interpreter = tflite.Interpreter(model_path=model_path)
            
        self.interpreter.allocate_tensors()
        
        # Get input and output details
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        print("Model loaded successfully")
        print("Input shape:", self.input_details[0]['shape'])
        print("Output shape:", self.output_details[0]['shape'])
    
    def preprocess_landmarks(self, landmarks):
        """Preprocess landmarks to match model input"""
        if len(landmarks) != 21:
            return None
            
        coords = np.array([[lm.x, lm.y, lm.z] for lm in landmarks])
        return coords.reshape(1, 1, 21, 3).astype(np.float32)
    
    def predict_gesture(self, input_data):
        """Perform gesture prediction"""
        if input_data.shape[1] != self.sequence_length:
            return None, 0.0
            
        try:
            self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
            self.interpreter.invoke()
            output = self.interpreter.get_tensor(self.output_details[0]['index'])
            
            predicted_class = np.argmax(output[0])
            confidence = output[0][predicted_class]
            
            return predicted_class, confidence
        except Exception as e:
            print(f"Prediction error: {e}")
            return None, 0.0
    
    def process_frame(self, frame):
        """Process video frame and detect gestures"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        gesture_data = None
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks on frame
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )
                
                # Extract landmarks
                landmarks = [hand_landmarks.landmark[i] for i in range(21)]
                processed_landmarks = self.preprocess_landmarks(landmarks)
                
                if processed_landmarks is not None:
                    self.frame_buffer.append(processed_landmarks)
                    
                    # Only predict when we have enough frames
                    if len(self.frame_buffer) == self.sequence_length:
                        input_data = np.concatenate(list(self.frame_buffer), axis=1)
                        predicted_class, confidence = self.predict_gesture(input_data)
                        
                        if predicted_class is not None and confidence > 0.7:
                            gesture_name = self.gesture_map.get(predicted_class, "Unknown")
                            
                            # Apply cooldown to prevent rapid firing
                            current_time = time.time()
                            if (current_time - self.last_gesture_time) > self.gesture_cooldown:
                                self.current_gesture = gesture_name
                                self.gesture_confidence = confidence
                                self.last_gesture_time = current_time
                                
                                # Get hand position for cursor
                                index_tip = hand_landmarks.landmark[8]  # Index finger tip
                                
                                gesture_data = {
                                    "gesture": gesture_name,
                                    "confidence": float(confidence),
                                    "coordinates": {
                                        "x": float(index_tip.x),
                                        "y": float(index_tip.y)
                                    },
                                    "timestamp": current_time
                                }
                
                # Display current gesture on frame
                if self.current_gesture:
                    cv2.putText(frame, f"Gesture: {self.current_gesture} ({self.gesture_confidence:.2f})",
                              (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        return frame, gesture_data
    
    def start_camera(self):
        """Start camera capture in separate thread"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open camera")
            return
            
        self.running = True
        self.camera_thread = threading.Thread(target=self.camera_loop)
        self.camera_thread.start()
        print("Camera started")
    
    def camera_loop(self):
        """Main camera processing loop"""
        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                continue
                
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Process frame and get gesture data
            processed_frame, gesture_data = self.process_frame(frame)
            
            # Send gesture data to connected clients
            if gesture_data and self.connected_clients:
                asyncio.run(self.broadcast_gesture(gesture_data))
            
            # Display frame
            cv2.imshow('Gesture Recognition', processed_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.stop_camera()
    
    def stop_camera(self):
        """Stop camera capture"""
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("Camera stopped")
    
    async def broadcast_gesture(self, gesture_data):
        """Broadcast gesture data to all connected clients"""
        if self.connected_clients:
            message = json.dumps(gesture_data)
            disconnected = set()
            
            for client in self.connected_clients:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)
            
            # Remove disconnected clients
            self.connected_clients -= disconnected
    
    async def handle_client(self, websocket, path):
        """Handle WebSocket client connections"""
        self.connected_clients.add(websocket)
        print(f"Client connected. Total clients: {len(self.connected_clients)}")
        
        try:
            # Send initial status
            await websocket.send(json.dumps({
                "type": "status",
                "message": "Connected to gesture recognition",
                "gestures": list(self.gesture_map.values())
            }))
            
            # Keep connection alive
            async for message in websocket:
                data = json.loads(message)
                
                if data.get("type") == "start_camera":
                    if not self.running:
                        self.start_camera()
                        await websocket.send(json.dumps({
                            "type": "camera_status", 
                            "status": "started"
                        }))
                
                elif data.get("type") == "stop_camera":
                    if self.running:
                        self.stop_camera()
                        await websocket.send(json.dumps({
                            "type": "camera_status", 
                            "status": "stopped"
                        }))
                        
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.connected_clients.discard(websocket)
            print(f"Client disconnected. Total clients: {len(self.connected_clients)}")
    
    async def start_server(self, host="localhost", port=8765):
        """Start WebSocket server"""
        print(f"Starting gesture recognition server on ws://{host}:{port}")
        await websockets.serve(self.handle_client, host, port)

# Main execution
async def main():
    backend = GestureRecognitionBackend()
    await backend.start_server()
    
    # Keep server running
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        print("Shutting down server...")
        backend.stop_camera()

if __name__ == "__main__":
    asyncio.run(main())
