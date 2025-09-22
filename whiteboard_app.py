"""
whiteboard_app.py
===================

This script provides a simple gesture‑controlled whiteboard application
implemented in pure Python.  It uses the existing TensorFlow Lite
model contained in the repository (``models/gesture_model_3d_final.tflite``)
to recognise a set of hand micro‑gestures and map them to drawing
commands on a canvas.  The application relies on OpenCV for
video capture and drawing, MediaPipe for hand landmark detection,
and TensorFlow Lite for model inference.

The supported gestures mirror those defined in the original project:

``write_start``    – begin drawing on the canvas
``write_stop``     – stop drawing
``erase``          – toggle eraser mode
``zoom_in``        – zoom into the canvas (not implemented in this simplified version)
``zoom_out``       – zoom out of the canvas (not implemented)
``draw_shapes``    – switch into shape drawing mode (not implemented)
``undo``           – undo the last drawing action (not implemented)
``redo``           – redo the last undone action (not implemented)
``change_color``   – cycle through a predefined set of colours
``save``           – save the current canvas as a PNG file
``pan``            – pan the canvas (not implemented)
``clear_all``      – clear the entire canvas

Only a subset of these are fully implemented below.  The code is
structured so additional commands can be added easily by editing
the ``handle_gesture`` method.  This script can be run directly
from a Python environment with a webcam attached.  Make sure the
dependencies ``opencv-python``, ``mediapipe`` and ``tensorflow`` (for
the TensorFlow Lite interpreter) are installed.
"""

import os
import time
from collections import deque

import cv2  # type: ignore
import mediapipe as mp  # type: ignore
import numpy as np  # type: ignore
import tensorflow.lite as tflite  # type: ignore


class GestureWhiteboard:
    """Gesture‑controlled whiteboard application.

    This class encapsulates the state and behaviour for drawing on a
    canvas based on recognised hand gestures.  It manages the
    drawing mode, erasing, current colour and saving of the canvas.
    A minimal set of commands is implemented; further commands from
    the original project can be added following the same pattern.
    """

    # Mapping of model output indices to gesture names.  This
    # corresponds to the GESTURE_MAP in the original repo.
    GESTURE_MAP = {
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
        11: "clear_all",
    }

    # Predefined drawing colours (BGR format since OpenCV uses BGR)
    COLOURS = [
        (0, 0, 255),    # red
        (0, 255, 0),    # green
        (255, 0, 0),    # blue
        (0, 255, 255),  # yellow
        (255, 0, 255),  # magenta
        (255, 255, 0),  # cyan
        (0, 0, 0),      # black
    ]

    def __init__(self, model_path: str) -> None:
        # Load TFLite gesture model
        self.interpreter = tflite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        # MediaPipe hands initialisation
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils

        # Canvas parameters
        self.canvas_width = 1200
        self.canvas_height = 800
        self.canvas = np.ones((self.canvas_height, self.canvas_width, 3), dtype=np.uint8) * 255
        self.temp_canvas = self.canvas.copy()

        # Drawing state
        self.drawing = False
        self.erasing = False
        self.current_colour_idx = 0
        self.brush_thickness = 5
        self.eraser_thickness = 25
        self.prev_x = 0
        self.prev_y = 0

        # Sequence buffer for temporal model input
        self.sequence_length = 4
        self.frame_buffer: deque[np.ndarray] = deque(maxlen=self.sequence_length)

        # Gesture control state
        self.last_gesture: str | None = None
        self.gesture_cooldown = 1.0  # seconds
        self.last_gesture_time = 0.0

        # History for undo/redo functionality. We store
        # snapshots of the canvas after each completed stroke. The
        # history_index points at the current canvas in the history.
        self.history: list[np.ndarray] = []
        self.history_index: int = -1

    def preprocess_landmarks(self, landmarks: list[mp.framework.formats.landmark_pb2.NormalizedLandmark]) -> np.ndarray | None:
        """Flatten MediaPipe landmarks to the model input shape.

        The model expects shape (1, 1, 21, 3).  We capture one hand so the
        outer batch dimension will be added in ``run``, combining
        multiple frames to produce (1, sequence_length, 21, 3).
        """
        if len(landmarks) != 21:
            return None
        coords = np.array([[lm.x, lm.y, lm.z] for lm in landmarks])
        return coords.reshape(1, 1, 21, 3).astype(np.float32)

    def predict_gesture(self, input_data: np.ndarray) -> tuple[int | None, float]:
        """Run the TFLite model on the concatenated frames.

        Returns the predicted class index and confidence.  If the
        sequence length is incorrect, ``(None, 0.0)`` is returned.
        """
        if input_data.shape[1] != self.sequence_length:
            return (None, 0.0)
        # Set input tensor
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()
        output = self.interpreter.get_tensor(self.output_details[0]['index'])
        predicted_class = int(np.argmax(output[0]))
        confidence = float(output[0][predicted_class])
        return (predicted_class, confidence)

    def handle_gesture(self, gesture_name: str) -> None:
        """Map recognised gesture names to whiteboard actions."""
        if gesture_name == "write_start":
            self.drawing = True
        elif gesture_name == "write_stop":
            # End of a stroke. Take a snapshot of the canvas for undo/redo
            # only if we were previously drawing. This avoids pushing
            # duplicate canvases when "write_stop" is detected multiple
            # times without a corresponding draw.
            if self.drawing:
                # Discard any redo history when a new stroke is made
                self.history = self.history[: self.history_index + 1]
                self.history.append(self.canvas.copy())
                self.history_index = len(self.history) - 1
            self.drawing = False
        elif gesture_name == "erase":
            # Toggle eraser mode
            self.erasing = not self.erasing
        elif gesture_name == "change_color":
            # Cycle through colours
            self.current_colour_idx = (self.current_colour_idx + 1) % len(self.COLOURS)
        elif gesture_name == "save":
            # Save the current canvas as a PNG
            filename = f"whiteboard_{int(time.time())}.png"
            cv2.imwrite(filename, self.canvas)
            print(f"Saved canvas to {filename}")
        elif gesture_name == "clear_all":
            self.canvas[:] = 255
            print("Canvas cleared")
        elif gesture_name == "undo":
            # Undo: move back in history if possible
            if self.history_index > 0:
                self.history_index -= 1
                self.canvas = self.history[self.history_index].copy()
                print("Undo")
        elif gesture_name == "redo":
            # Redo: move forward in history if possible
            if self.history_index < len(self.history) - 1:
                self.history_index += 1
                self.canvas = self.history[self.history_index].copy()
                print("Redo")
        # Other gestures (zoom, undo, redo, shapes, pan) can be added here

    def run(self) -> None:
        """Main loop: capture camera, recognise gestures and draw."""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open camera.")
            return
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("Error: Could not read frame.")
                    break
                # Mirror the image for a more natural interaction
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Detect hands
                results = self.hands.process(rgb_frame)
                landmarks = None
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Draw hand landmarks for user feedback
                        self.mp_drawing.draw_landmarks(
                            frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                        )
                        # Collect landmarks for gesture prediction
                        landmarks = [hand_landmarks.landmark[i] for i in range(21)]
                        processed = self.preprocess_landmarks(landmarks)
                        if processed is not None:
                            self.frame_buffer.append(processed)
                        # When enough frames collected, run prediction
                        if len(self.frame_buffer) == self.sequence_length:
                            input_data = np.concatenate(list(self.frame_buffer), axis=1)
                            predicted_class, confidence = self.predict_gesture(input_data)
                            if predicted_class is not None and confidence > 0.7:
                                gesture_name = self.GESTURE_MAP.get(predicted_class, "unknown")
                                current_time = time.time()
                                # Apply a cooldown to avoid repeated commands
                                if (gesture_name != self.last_gesture) or (
                                    current_time - self.last_gesture_time > self.gesture_cooldown
                                ):
                                    self.last_gesture = gesture_name
                                    self.last_gesture_time = current_time
                                    self.handle_gesture(gesture_name)
                                    print(f"Gesture: {gesture_name} ({confidence:.2f})")
                # Determine drawing point from index finger tip
                if landmarks:
                    index_tip = landmarks[8]
                    x = int(index_tip.x * self.canvas_width)
                    y = int(index_tip.y * self.canvas_height)
                    if self.drawing:
                        # Choose brush or eraser colour
                        colour = (255, 255, 255) if self.erasing else self.COLOURS[self.current_colour_idx]
                        thickness = self.eraser_thickness if self.erasing else self.brush_thickness
                        cv2.line(self.canvas, (self.prev_x, self.prev_y), (x, y), colour, thickness)
                    self.prev_x, self.prev_y = x, y
                # Display the combined view: camera feed and canvas overlay
                display = frame.copy()
                # Resize canvas to match camera frame width
                canvas_display = cv2.resize(self.canvas, (frame.shape[1], frame.shape[0]))
                # Overlay the canvas with some transparency
                blended = cv2.addWeighted(display, 0.5, canvas_display, 0.5, 0)

                # Annotate the view with mode and colour information
                mode_text = "Erase" if self.erasing else ("Draw" if self.drawing else "Idle")
                colour = self.COLOURS[self.current_colour_idx] if not self.erasing else (0, 0, 0)
                colour_text = f"Colour: BGR({colour[0]}, {colour[1]}, {colour[2]})"
                gesture_text = f"Last gesture: {self.last_gesture or 'None'}"
                cv2.putText(
                    blended,
                    f"Mode: {mode_text}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 0),
                    2,
                    lineType=cv2.LINE_AA,
                )
                cv2.putText(
                    blended,
                    colour_text,
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 0),
                    2,
                    lineType=cv2.LINE_AA,
                )
                cv2.putText(
                    blended,
                    gesture_text,
                    (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 0),
                    2,
                    lineType=cv2.LINE_AA,
                )

                cv2.imshow("Gesture Whiteboard", blended)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()


def main() -> None:
    """Entry point: resolve model path and start the whiteboard."""
    # Determine path to the TFLite model relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_rel_path = os.path.join(script_dir, "models", "gesture_model_3d_final.tflite")
    if not os.path.exists(model_rel_path):
        # Fallback: check models folder at project root
        model_rel_path = os.path.join(script_dir, "..", "models", "gesture_model_3d_final.tflite")
    if not os.path.exists(model_rel_path):
        print(f"Model not found at {model_rel_path}. Please ensure the TFLite file exists.")
        return
    print(f"Using gesture model: {model_rel_path}")
    app = GestureWhiteboard(model_rel_path)
    app.run()


if __name__ == "__main__":
    main()