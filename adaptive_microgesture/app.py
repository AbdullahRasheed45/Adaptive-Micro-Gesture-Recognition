import numpy as np
import tensorflow.lite as tflite
import cv2
import mediapipe as mp
import os
import time
from collections import deque

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Initialize TFLite interpreter
interpreter = tflite.Interpreter(
    model_path=r"D:\Generative AI\Project\Adaptive-Micro-Gesture-Recognition\models\gesture_model_3d_final.tflite"
)
interpreter.allocate_tensors()

# Get input and output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Gesture class mapping
GESTURE_MAP = {
    0: "write_start", 1: "write_stop", 2: "erase", 3: "zoom_in", 
    4: "zoom_out", 5: "draw_shapes", 6: "undo", 7: "redo", 
    8: "change_color", 9: "save", 10: "pan", 11: "clear_all"
}

# Whiteboard application class
class WhiteboardApp:
    def __init__(self):
        # Drawing state
        self.drawing = False
        self.erasing = False
        self.drawing_color = (0, 0, 255)  # BGR - Start with red
        self.eraser_color = (255, 255, 255)  # White
        self.line_thickness = 5
        self.eraser_thickness = 25
        
        # Canvas setup
        self.canvas_width, self.canvas_height = 1200, 800
        self.canvas = np.ones((self.canvas_height, self.canvas_width, 3), dtype=np.uint8) * 255
        self.temp_canvas = self.canvas.copy()
        
        # History for undo/redo
        self.history = deque(maxlen=50)
        self.redo_stack = deque(maxlen=50)
        self.save_history()
        
        # Zoom and pan
        self.zoom_factor = 1.0
        self.offset_x, self.offset_y = 0, 0
        self.pan_mode = False
        self.prev_pan_x, self.prev_pan_y = 0, 0
        
        # Shape drawing
        self.shape_drawing = False
        self.shape_start_point = None
        self.current_shape = "rectangle"  # Default shape
        self.shapes = ["rectangle", "circle", "line", "arrow"]
        self.shape_index = 0
        
        # Gesture processing
        self.sequence_length = 4
        self.frame_buffer = deque(maxlen=self.sequence_length)
        self.last_gesture_time = time.time()
        self.gesture_cooldown = 1.0  # seconds
        self.last_gesture = None
        
        # Colors for UI
        self.ui_colors = {
            "background": (50, 50, 50),
            "header": (30, 30, 40),
            "button": (70, 70, 100),
            "active": (0, 150, 255),
            "text": (255, 255, 255)
        }
        
        # Status messages
        self.status_message = ""
        self.status_expire = 0
        
    def save_history(self):
        """Save current canvas state to history"""
        self.history.append(self.canvas.copy())
        self.redo_stack.clear()
    
    def undo(self):
        """Undo the last drawing action"""
        if len(self.history) > 1:
            self.redo_stack.append(self.history.pop())
            self.canvas = self.history[-1].copy()
            self.temp_canvas = self.canvas.copy()
            self.status("Undo performed")
    
    def redo(self):
        """Redo the last undone action"""
        if self.redo_stack:
            self.canvas = self.redo_stack.pop().copy()
            self.history.append(self.canvas.copy())
            self.temp_canvas = self.canvas.copy()
            self.status("Redo performed")
    
    def clear_canvas(self):
        """Clear the entire canvas"""
        self.canvas = np.ones((self.canvas_height, self.canvas_width, 3), dtype=np.uint8) * 255
        self.save_history()
        self.status("Canvas cleared")
    
    def change_color(self):
        """Cycle through different drawing colors"""
        colors = [
            (0, 0, 255),    # Red
            (0, 255, 0),    # Green
            (255, 0, 0),    # Blue
            (0, 255, 255),  # Yellow
            (255, 0, 255),  # Magenta
            (255, 255, 0)   # Cyan
        ]
        current_idx = colors.index(self.drawing_color) if self.drawing_color in colors else 0
        next_idx = (current_idx + 1) % len(colors)
        self.drawing_color = colors[next_idx]
        self.status(f"Color changed: {['Red', 'Green', 'Blue', 'Yellow', 'Magenta', 'Cyan'][next_idx]}")
    
    def change_shape(self):
        """Cycle through available shapes"""
        self.shape_index = (self.shape_index + 1) % len(self.shapes)
        self.current_shape = self.shapes[self.shape_index]
        self.status(f"Shape changed: {self.current_shape.capitalize()}")
    
    def zoom(self, direction):
        """Zoom in or out"""
        if direction == "in":
            self.zoom_factor = min(3.0, self.zoom_factor + 0.2)
        else:  # zoom out
            self.zoom_factor = max(1.0, self.zoom_factor - 0.2)
        self.status(f"Zoom: {int(self.zoom_factor * 100)}%")
    
    def toggle_erasing(self):
        """Toggle between drawing and erasing"""
        self.erasing = not self.erasing
        if self.erasing:
            self.status("Eraser activated")
        else:
            self.status("Drawing mode")
    
    def save_canvas(self):
        """Save the current canvas to a file"""
        filename = f"whiteboard_{time.strftime('%Y%m%d_%H%M%S')}.png"
        cv2.imwrite(filename, self.canvas)
        self.status(f"Saved as {filename}")
    
    def start_pan(self, x, y):
        """Start panning the canvas"""
        self.pan_mode = True
        self.prev_pan_x, self.prev_pan_y = x, y
        self.status("Pan mode activated")
    
    def pan(self, x, y):
        """Pan the canvas based on hand movement"""
        if self.pan_mode:
            dx = (x - self.prev_pan_x) * 2
            dy = (y - self.prev_pan_y) * 2
            self.offset_x += dx
            self.offset_y += dy
            
            # Clamp offset values
            self.offset_x = max(-self.canvas_width * (self.zoom_factor - 1), 
                               min(0, self.offset_x))
            self.offset_y = max(-self.canvas_height * (self.zoom_factor - 1), 
                               min(0, self.offset_y))
            
            self.prev_pan_x, self.prev_pan_y = x, y
    
    def end_pan(self):
        """End panning mode"""
        self.pan_mode = False
        self.status("Pan mode deactivated")
    
    def start_drawing(self, x, y):
        """Start drawing or erasing"""
        self.drawing = True
        self.prev_x, self.prev_y = x, y
        
        if self.shape_drawing:
            self.shape_start_point = (x, y)
    
    def draw(self, x, y):
        """Draw or erase on the canvas"""
        if self.drawing:
            # For shape drawing, we'll draw on the temp canvas
            target_canvas = self.temp_canvas if self.shape_drawing else self.canvas
            
            if self.erasing:
                cv2.line(target_canvas, (self.prev_x, self.prev_y), (x, y), 
                         self.eraser_color, self.eraser_thickness)
            else:
                cv2.line(target_canvas, (self.prev_x, self.prev_y), (x, y), 
                         self.drawing_color, self.line_thickness)
            
            self.prev_x, self.prev_y = x, y
    
    def end_drawing(self):
        """End drawing operation"""
        if self.drawing:
            self.drawing = False
            
            if self.shape_drawing:
                # Commit the shape to the main canvas
                self.canvas = self.temp_canvas.copy()
                self.save_history()
                self.shape_drawing = False
            elif not self.erasing:  # Only save history if we were drawing, not erasing
                self.save_history()
        
        self.temp_canvas = self.canvas.copy()
        self.shape_start_point = None
    
    def draw_shape(self, end_x, end_y):
        """Draw a shape on the temp canvas"""
        if self.shape_start_point:
            start_x, start_y = self.shape_start_point
            self.temp_canvas = self.canvas.copy()  # Reset temp canvas
            
            color = self.eraser_color if self.erasing else self.drawing_color
            thickness = self.eraser_thickness if self.erasing else self.line_thickness
            
            if self.current_shape == "rectangle":
                cv2.rectangle(self.temp_canvas, (start_x, start_y), 
                             (end_x, end_y), color, thickness)
            elif self.current_shape == "circle":
                center_x = (start_x + end_x) // 2
                center_y = (start_y + end_y) // 2
                radius = int(np.sqrt((end_x - start_x)**2 + (end_y - start_y)**2) // 2)
                cv2.circle(self.temp_canvas, (center_x, center_y), 
                          radius, color, thickness)
            elif self.current_shape == "line":
                cv2.line(self.temp_canvas, (start_x, start_y), 
                        (end_x, end_y), color, thickness)
            elif self.current_shape == "arrow":
                cv2.arrowedLine(self.temp_canvas, (start_x, start_y), 
                               (end_x, end_y), color, thickness, tipLength=0.3)
    
    def status(self, message):
        """Set a status message to display"""
        self.status_message = message
        self.status_expire = time.time() + 3.0  # Show for 3 seconds
    
    def process_landmarks(self, landmarks):
        """Process hand landmarks and add to frame buffer"""
        if len(landmarks) != 21:
            return None
            
        coords = np.array([[lm.x, lm.y, lm.z] for lm in landmarks]).flatten()
        return coords.reshape(1, 1, 21, 3).astype(np.float32)
    
    def predict_gesture(self, input_data):
        """Predict gesture from input data"""
        if input_data.shape[1] != self.sequence_length:
            return None, 0.0
            
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        output = interpreter.get_tensor(output_details[0]['index'])
        predicted_class = np.argmax(output[0])
        confidence = output[0][predicted_class]
        return predicted_class, confidence
    
    def handle_gesture(self, gesture_id):
        """Handle the detected gesture"""
        current_time = time.time()
        if current_time - self.last_gesture_time < self.gesture_cooldown:
            return
            
        gesture_name = GESTURE_MAP.get(gesture_id, "Unknown")
        
        # Only process new gestures
        if gesture_name != self.last_gesture:
            self.last_gesture = gesture_name
            self.last_gesture_time = current_time
            
            if gesture_name == "write_start":
                self.status("Drawing started")
            elif gesture_name == "write_stop":
                self.end_drawing()
                self.status("Drawing stopped")
            elif gesture_name == "erase":
                self.toggle_erasing()
            elif gesture_name == "zoom_in":
                self.zoom("in")
            elif gesture_name == "zoom_out":
                self.zoom("out")
            elif gesture_name == "draw_shapes":
                self.shape_drawing = True
                self.status(f"Shape mode: {self.current_shape}")
            elif gesture_name == "undo":
                self.undo()
            elif gesture_name == "redo":
                self.redo()
            elif gesture_name == "change_color":
                self.change_color()
            elif gesture_name == "save":
                self.save_canvas()
            elif gesture_name == "pan":
                self.status("Pan mode - move hand to pan")
            elif gesture_name == "clear_all":
                self.clear_canvas()
    
    def get_index_finger_position(self, landmarks):
        """Get the position of the index finger tip"""
        if landmarks and len(landmarks) >= 9:
            # Index finger tip is landmark 8
            index_finger = landmarks[8]
            return int(index_finger.x * self.canvas_width), int(index_finger.y * self.canvas_height)
        return None
    
    def create_ui(self, display_width=1200):
        """Create the application UI layout"""
        # Create a dark-themed UI background
        ui_height = 800
        ui_width = display_width
        ui = np.zeros((ui_height, ui_width, 3), dtype=np.uint8)
        
        # Header section
        cv2.rectangle(ui, (0, 0), (ui_width, 60), self.ui_colors["header"], -1)
        cv2.putText(ui, "Gesture-Controlled Whiteboard", (20, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, self.ui_colors["text"], 2)
        
        # Status bar
        cv2.rectangle(ui, (0, ui_height - 40), (ui_width, ui_height), (40, 40, 50), -1)
        
        # Display status message if active
        if time.time() < self.status_expire:
            cv2.putText(ui, self.status_message, (20, ui_height - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 255, 100), 2)
        
        # Display current mode
        mode_text = f"Mode: {'Erasing' if self.erasing else 'Drawing'} | "
        mode_text += f"Shape: {self.current_shape.capitalize() if self.shape_drawing else 'Freehand'} | "
        mode_text += f"Color: {'Eraser' if self.erasing else 'Pen'}"
        cv2.putText(ui, mode_text, (ui_width - 600, ui_height - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.ui_colors["text"], 1)
        
        # Create instruction panel
        instructions = [
            "GESTURE CONTROLS:",
            "Closed Fist: Start Drawing",
            "Open Palm: Stop Drawing",
            "Thumb Down: Erase",
            "Zoom In: Pinch In",
            "Zoom Out: Pinch Out",
            "Peace Sign: Draw Shapes",
            "Thumb Left: Undo",
            "Thumb Right: Redo",
            "Three Fingers: Change Color",
            "Stop Sign: Save Canvas",
            "One Finger: Pan Canvas",
            "Stop Inverted: Clear All"
        ]
        
        # Draw instruction panel
        cv2.rectangle(ui, (ui_width - 400, 80), (ui_width - 20, ui_height - 60), (40, 40, 50), -1)
        cv2.rectangle(ui, (ui_width - 400, 80), (ui_width - 20, ui_height - 60), (100, 100, 150), 2)
        cv2.putText(ui, "Gesture Controls", (ui_width - 380, 110), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 200, 255), 2)
        
        # Draw instructions
        for i, text in enumerate(instructions):
            cv2.putText(ui, text, (ui_width - 380, 150 + i*40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.ui_colors["text"], 1)
        
        return ui
    
    def run(self):
        """Run the whiteboard application"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open camera.")
            return
        
        # Create a window
        cv2.namedWindow("Gesture Whiteboard", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Gesture Whiteboard", 1200, 800)
        
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("Error: Couldn't read frame.")
                    break
                
                # Flip the frame horizontally for a mirror effect
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process the frame with MediaPipe Hands
                results = hands.process(rgb_frame)
                landmarks = None
                
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Draw hand landmarks on the frame
                        mp_drawing.draw_landmarks(
                            frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                            mp_drawing.DrawingSpec(color=(0, 150, 0), thickness=2)
                        )
                        
                        # Get landmarks for processing
                        landmarks = [hand_landmarks.landmark[i] for i in range(21)]
                        
                        # Process landmarks for gesture recognition
                        processed_landmarks = self.process_landmarks(landmarks)
                        if processed_landmarks is not None:
                            self.frame_buffer.append(processed_landmarks)
                            
                            if len(self.frame_buffer) == self.sequence_length:
                                input_data = np.concatenate(list(self.frame_buffer), axis=1)
                                gesture_id, confidence = self.predict_gesture(input_data)
                                
                                if confidence > 0.7:
                                    self.handle_gesture(gesture_id)
                
                # Get index finger position
                finger_pos = self.get_index_finger_position(landmarks) if landmarks else None
                
                # Handle pan mode
                if self.last_gesture == "pan" and finger_pos:
                    if self.pan_mode:
                        self.pan(finger_pos[0], finger_pos[1])
                    else:
                        self.start_pan(finger_pos[0], finger_pos[1])
                elif self.pan_mode:
                    self.end_pan()
                
                # Handle drawing
                if finger_pos:
                    x, y = finger_pos
                    
                    # Start drawing if gesture detected
                    if self.last_gesture == "write_start" and not self.drawing:
                        self.start_drawing(x, y)
                    
                    # Continue drawing
                    if self.drawing:
                        if self.shape_drawing and self.shape_start_point:
                            self.draw_shape(x, y)
                        else:
                            self.draw(x, y)
                
                # Create the UI
                ui = self.create_ui()
                
                # Prepare the canvas for display
                display_canvas = self.temp_canvas if self.shape_drawing else self.canvas
                
                # Resize the camera frame to fit in the UI
                camera_display = cv2.resize(frame, (400, 300))
                
                # Place the camera feed in the UI
                ui[80:380, 20:420] = camera_display
                
                # Place the whiteboard in the UI
                canvas_display = cv2.resize(display_canvas, (700, 500))
                ui[80:580, 440:1140] = canvas_display
                
                # Display the current gesture
                if self.last_gesture:
                    cv2.putText(ui, f"Current: {self.last_gesture.replace('_', ' ')}", 
                               (20, 700), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 255, 100), 2)
                
                # Display the UI
                cv2.imshow("Gesture Whiteboard", ui)
                
                # Handle key events
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('c'):
                    self.clear_canvas()
                elif key == ord('u'):
                    self.undo()
                elif key == ord('r'):
                    self.redo()
                elif key == ord('s'):
                    self.save_canvas()
                elif key == ord('e'):
                    self.toggle_erasing()
                elif key == ord('z'):
                    self.zoom("in")
                elif key == ord('x'):
                    self.zoom("out")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()

# Run the application
if __name__ == "__main__":
    app = WhiteboardApp()
    app.run()