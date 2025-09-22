# Adaptive-Micro-Gesture-Recognition
The project will follow a modular structure, separating concerns like data preprocessing, model definition, training, inference, and whiteboard integration, while being adaptable for the LeapGestRecog Dataset and the Lightweight Micro-Gesture Transformer (LMGT).
## Gesture Whiteboard Application

In addition to the original web‑based interface, this repository now includes a standalone Python application (`whiteboard_app.py`) that lets you control a drawing canvas using the provided micro‑gesture model.  The app uses OpenCV to display your webcam feed, MediaPipe to extract hand landmarks and a TensorFlow Lite interpreter to classify gestures. Recognised gestures are mapped to drawing commands such as starting/stopping a stroke, toggling the eraser, cycling through colours, saving the canvas and clearing all.  The script is extensible so you can add support for zoom, panning, undo/redo and shape drawing.

### Running the whiteboard app

1. Make sure Python 3.8 or later is installed on your system.
2. Install the required Python packages:

```
pip install opencv-python mediapipe tensorflow==2.*  # or tensorflow-cpu if GPU support is not needed
```

3. Execute the script from the project root:

```
python whiteboard_app.py
```

   A window labelled **“Gesture Whiteboard”** will open. It overlays the live camera feed with a blank canvas.  Use the micro‑gestures to draw, erase, change colours, save your artwork or clear the canvas.  Press `q` to exit.
4. The model file (`gesture_model_3d_final.tflite`) should be located in the `models` directory.  The script automatically searches for this file in `./models/` and in the parent directory if necessary.  If you have trained or converted your own model, place it in the same directory and update the path accordingly.

See the comments in `whiteboard_app.py` for more details and for instructions on how to extend the gesture mappings.
