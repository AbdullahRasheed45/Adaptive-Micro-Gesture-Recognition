import requests
import json
import cv2
import mediapipe as mp
import numpy as np

class GestureWhiteboardIntegration:
    def __init__(self, whiteboard_url="http://localhost:3000"):
        self.whiteboard_url = whiteboard_url
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
    def send_gesture_data(self, gesture, coordinates, confidence):
        """Send gesture data to the Next.js whiteboard"""
        try:
            data = {
                "gesture": gesture,
                "coordinates": coordinates,
                "confidence": confidence,
                "timestamp": int(cv2.getTickCount())
            }
            
            response = requests.post(
                f"{self.whiteboard_url}/api/gesture",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print(f"Gesture sent successfully: {gesture}")
                return response.json()
            else:
                print(f"Error sending gesture: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error sending gesture data: {e}")
            return None
    
    def detect_gesture(self, landmarks):
        """Detect gesture from hand landmarks"""
        # Example gesture detection logic
        # You can implement your own gesture recognition here
        
        # Get fingertip positions
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        
        # Get finger MCP positions
        index_mcp = landmarks[5]
        middle_mcp = landmarks[9]
        ring_mcp = landmarks[13]
        pinky_mcp = landmarks[17]
        
        # Simple gesture detection
        fingers_up = []
        
        # Thumb
        if thumb_tip.x > landmarks[3].x:
            fingers_up.append(1)
        else:
            fingers_up.append(0)
            
        # Other fingers
        for tip, mcp in [(index_tip, index_mcp), (middle_tip, middle_mcp), 
                        (ring_tip, ring_mcp), (pinky_tip, pinky_mcp)]:
            if tip.y < mcp.y:
                fingers_up.append(1)
            else:
                fingers_up.append(0)
        
        # Gesture classification
        if fingers_up == [0, 1, 0, 0, 0]:  # Only index finger up
            return "draw"
        elif fingers_up == [0, 1, 1, 0, 0]:  # Index and middle up
            return "erase"
        elif sum(fingers_up) == 0:  # Fist
            return "clear"
        elif sum(fingers_up) == 5:  # Open hand
            return "undo"
        else:
            return "none"
    
    def run_gesture_recognition(self):
        """Main loop for gesture recognition"""
        cap = cv2.VideoCapture(0)
        
        print("Starting gesture recognition...")
        print("Gestures:")
        print("- Index finger: Draw")
        print("- Index + Middle: Erase")
        print("- Fist: Clear canvas")
        print("- Open hand: Undo")
        print("Press 'q' to quit")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process frame
            results = self.hands.process(rgb_frame)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw landmarks
                    self.mp_draw.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                    )
                    
                    # Detect gesture
                    gesture = self.detect_gesture(hand_landmarks.landmark)
                    
                    if gesture != "none":
                        # Get index finger tip position for coordinates
                        index_tip = hand_landmarks.landmark[8]
                        
                        # Convert to canvas coordinates (assuming 1200x800 canvas)
                        canvas_x = int(index_tip.x * 1200)
                        canvas_y = int(index_tip.y * 800)
                        
                        coordinates = {"x": canvas_x, "y": canvas_y}
                        
                        # Send gesture to whiteboard
                        self.send_gesture_data(gesture, coordinates, 0.9)
                        
                        # Display gesture on frame
                        cv2.putText(frame, f"Gesture: {gesture}", 
                                  (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                                  1, (0, 255, 0), 2)
            
            cv2.imshow('Gesture Recognition', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

# Example usage
if __name__ == "__main__":
    integration = GestureWhiteboardIntegration()
    integration.run_gesture_recognition()
