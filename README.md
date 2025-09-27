Adaptive Micro‑Gesture Recognition for Accessibility

Adaptive‑Micro‑Gesture‑Recognition is a full‑stack research prototype that turns subtle hand movements into computer commands for people with motor impairments. It combines real‑time hand tracking, spatio‑temporal deep learning and an interactive whiteboard interface so that users can draw, click and navigate using only micro‑gestures. The system is built around a 3D Convolutional Neural Network (3D CNN) trained on the HaGRID dataset plus a synthetic micro‑gesture pipeline, then optimized with TensorFlow Lite for low‑latency on‑device inference.

This project was developed as part of a master’s thesis, and the accompanying research paper (included in this repository) describes the methodology, experiments and results in detail. The work achieved ≈94.6 % accuracy and ≈94.5 % F1‑score on ten micro‑gesture classes and runs at >20 frames per second on a smartphone.

Table of contents

Features

System overview

3D CNN architecture

Dataset and synthetic augmentation

Training details

Performance

Installation

Usage

Research paper

License

Features

Adaptive micro‑gesture recognition – identifies small hand/finger movements such as palm, fist, point, OK sign, thumbs up/down, victory/peace, swipe left/right and pinch; these gestures were selected from HaGRID for their accessibility and mapped to drawing actions.

Real‑time hand tracking – uses MediaPipe Hands
 to locate the hand region and generate bounding boxes/keypoints for each frame. This allows the system to crop and stabilise the input before classification.

Spatio‑temporal deep learning – a lightweight 3D CNN processes sequences of 8 frames to capture motion patterns and classify the gesture. A TensorFlow Lite version with 8‑bit quantization provides low‑latency inference on mobile devices.

Cross‑platform drawing interface – the server exposes a REST API to the Fabric.js front‑end (web) and a Python/OpenCV client (desktop), enabling drawing on a canvas with micro‑gestures. Supported actions include drawing, erasing, undo/redo, shape tools, zoom/pan and colour/size selection.

Adaptive calibration – optional user‑specific calibration adjusts gesture thresholds (e.g., pinch distance) so the system works for people with varying range of motion.

Extensible architecture – the core recognition model can be re‑trained on other gesture sets or adapted for facial micro‑expressions or head movements.

System overview

The system has three main components:

Hand detector/pre‑processing. Frames from a webcam (desktop) or browser (web client) are passed through MediaPipe to extract the hand bounding box and 21 keypoints. The bounding box is used to crop and resize an 8‑frame clip for input to the classifier. Gesture predictions are buffered to produce stable outputs and to avoid false triggers.

3D CNN gesture classifier. A CNN with 3D convolutions and pooling layers captures both spatial and temporal information directly from the video clip. It outputs the probability of each gesture class plus a “no‑gesture” class. A TensorFlow Lite version of the network enables real‑time inference on CPUs/GPUs with minimal latency.

Whiteboard application. Predictions from the classifier are sent to the front‑end, which interprets them as drawing commands. For example, fist corresponds to drawing, palm to stop, point to selecting tools, thumbs up to undo and thumbs down to redo. Swipe gestures pan the canvas; a pinch gesture changes brush size.

3D CNN architecture

The 3D CNN architecture was designed to efficiently capture motion across a short video clip while remaining compact enough for on‑device deployment. The layer sequence is summarised below:

Layer	Purpose
Conv3D (Temporal × Spatial)	First 3D convolution layer with a temporal receptive field of 3 frames to detect low‑level motion features (edges moving). Followed by batch normalisation and ReLU activation.
MaxPooling3D	Down‑samples the feature map in space and time to reduce computation and learn motion segments.
Conv3D × 2	Additional 3D convolution layers with smaller kernels increase the temporal receptive field (up to 5 frames) and capture finer motion patterns. Each convolution is followed by batch normalisation and ReLU.
Spatial MaxPooling / Flatten	Collapses the temporal dimension by treating the remaining frame features as separate channels and flattens them.
Dropout (50 %)	Applied during training to mitigate overfitting given the moderate dataset size.
Fully connected & softmax	The final layers transform flattened features into class probabilities.

The entire model is quantized to 8‑bit integers using TensorFlow Lite with negligible accuracy loss, resulting in a ~1.2 MB .tflite model file.

Dataset and synthetic augmentation

Real gestures (HaGRID). The HaGRID dataset provides millions of labelled images for 18 hand gestures. For micro‑gestures, seven classes were selected—palm, fist, point, OK, thumbs up, thumbs down and victory/peace. Approximate image counts after filtering were: 30k palm, 28k fist, 27k point, 25k OK, 26k thumbs up, 24k thumbs down and 22k victory. Videos were segmented into 8‑frame sequences and split by subject ID into 70 % training, 15 % validation and 15 % test.

Synthetic micro‑gesture pipeline. Real gesture sequences were augmented to simulate the reduced amplitude and subtle motions exhibited by motor‑impaired users. The pipeline applied random cropping, scaling and temporal subsampling to shrink the motion range; small horizontal/vertical translations created “mini‑swipes”, while pinch/unpinch sequences were synthesised by gradually changing finger distance. This synthetic augmentation doubled the training set size and improved generalisation.

Real micro‑gesture test set. To evaluate true micro‑gesture performance, a separate set of videos was recorded with subjects performing minimal‑amplitude versions of the gestures. This allowed the researchers to measure detection latency and real‑world accuracy.

Training details

The model was implemented in TensorFlow 2.9 (Keras) and trained on a Google Colab with an NVIDIA T4 GPU. Key hyper‑parameters are as follows:

Optimizer: Adam with default betas; learning rate selected via a small grid search.

Loss: Categorical cross‑entropy.

Batch size: 64 sequences.

Epochs: Trained for 30 epochs with early stopping (patience 5) based on validation loss. Training converged at ≈27 epochs with ~98 % training accuracy and ~95 % validation accuracy.

After training, the best checkpoint was converted to TensorFlow Lite. Quantization produced a model of ~1.2 MB, enabling inference times around 40 ms per 8‑frame sequence on a Pixel smartphone.

Performance

On the test set of 8,500 gesture sequences, the 3D CNN achieved 94.6 % accuracy, 94.9 % precision, 94.6 % recall and 94.5 % F1‑score. Per‑class performance highlights include:

Class	Precision (%)	Recall (%)	F1 (%)	Notes
Palm (open)	95.2	96.7	95.9	Neutral/stop gesture.
Fist (closed)	97.1	94.3	95.7	Used for drawing; occasional confusion with palm.
Point (index)	93.5	91.0	92.2	Selects tools.
OK sign	94.4	93.7	94.0	Positive confirmation.
Thumbs up	98.0	97.5	97.7	Undo action.
Thumbs down	98.3	96.1	97.2	Redo action.
Victory/Peace	92.0	90.2	91.1	Switches modes.

The model generalised well to external data: on a cross‑dataset test it achieved ≈92 % accuracy, confirming robustness to different cameras and environments. Quantized inference on a smartphone sustained >20 frames per second.

Installation

This repository contains both the back‑end server and the front‑end clients. The following installation instructions assume you have Python 3.8+ and Node.js installed.

Back‑end (Python/Flask)

Create a virtual environment and install dependencies:

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


Download the pre‑trained model.tflite file and place it in the backend/model/ directory. (The research paper explains how to train and convert the model.)

Start the Flask server:

python backend/app.py


The API will be available at http://localhost:5000. Endpoints include /predict for classifying sequences and /calibrate for optional user calibration.

Front‑end (Web)

Navigate to frontend/web and install dependencies:

cd frontend/web
npm install


Start the development server:

npm start


This will launch the whiteboard application in your browser. It will connect to the Flask API by default; ensure the back‑end is running. For production builds, run npm run build.

Desktop client

For a desktop application that uses OpenCV and MediaPipe Hands to capture webcam frames:

cd frontend/desktop
python client.py


This client streams frames to the back‑end, receives gesture predictions and updates the drawing canvas accordingly. The desktop version may provide better performance and camera access on systems without WebRTC.

Usage

Once both the server and front‑end are running, follow these steps:

Select a drawing tool. Use the point gesture to open the tool menu and choose between free draw, straight line, rectangle, circle, text or eraser.

Draw or erase. Perform a fist gesture to draw and a fist with two fingers extended (OK) to erase. The system will track your finger movements across frames and update the canvas in real time.

Undo/redo. Use thumbs up to undo the last action and thumbs down to redo.

Zoom/pan. Perform a small horizontal swipe gesture to pan the canvas left or right; perform a pinch gesture to zoom in/out (this requires calibration). The system is designed to detect these micro‑swipes with minimal movement.

Calibration (optional). If your range of motion is limited, send a calibration request via the API or use the UI to capture a few examples of each gesture. The classifier will adjust thresholds to your personal motion range.

For troubleshooting or to change gesture mappings, consult config.yaml in the backend folder. You can also re‑train the model on additional gestures by following the training instructions in the paper.

Research paper

The repository includes the MSc thesis “Adaptive Micro‑Gesture Recognition for Accessibility”. The paper provides the full research context, methodology, dataset details, results, discussion and future directions. Key contributions include:

A novel synthetic micro‑gesture augmentation pipeline and calibration strategy.

A compact 3D CNN architecture optimised with TensorFlow Lite for real‑time inference.

Experimental results demonstrating high accuracy (94.6 %) and F1‑score (94.5) on micro‑gestures.

Discussion on cross‑dataset generalisation, limitations, future work and ethical considerations.

You are encouraged to read the paper to understand the research decisions and replicate or extend the work.

License

This project is released under the MIT License. See the LICENSE file for details.
