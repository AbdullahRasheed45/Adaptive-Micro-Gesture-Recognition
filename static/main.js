const canvas = new fabric.Canvas('whiteboard', {
    isDrawingMode: false,
    width: window.innerWidth,
    height: window.innerHeight * 0.85
});
const video = document.getElementById('webcam');
const gestureOverlay = document.getElementById('gesture-overlay');
const colorBtn = document.getElementById('color-btn');
const currentColorSpan = document.getElementById('current-color');
const saveBtn = document.getElementById('save-btn');
const undoBtn = document.getElementById('undo-btn');
const redoBtn = document.getElementById('redo-btn');
const clearBtn = document.getElementById('clear-btn');
const webcamContainer = document.getElementById('webcam-container');

let model, hands, lastGestureTime = 0, gestureBuffer = [], isWriting = false, isPanning = false, isShapeMode = false;
let currentColorIndex = 0;
const colors = ['black', 'red', 'blue', 'green'];
const gestureNames = ['write_start', 'write_stop', 'change_color', 'zoom_in', 'erase', 'zoom_out', 'undo', 'redo', 'draw_shapes', 'save', 'pan', 'clear_all'];
const history = [];
let redoStack = [];

// Initialize webcam
async function setupWebcam() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        console.log('Webcam initialized');
    } catch (err) {
        console.error('Error accessing webcam:', err);
        gestureOverlay.textContent = `Error: Webcam - ${err.message}`;
    }
}

// Initialize MediaPipe Hands
async function initializeHands() {
    if (typeof Hands === 'undefined') {
        console.error('MediaPipe Hands is not defined. Check script loading.');
        gestureOverlay.textContent = 'Error: MediaPipe Hands not loaded';
        return null;
    }
    const handsDetector = new Hands({
        locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.2/${file}`
    });
    handsDetector.setOptions({
        maxNumHands: 1,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5
    });
    try {
        await handsDetector.initialize();
        handsDetector.onResults(onHandResults);
        console.log('MediaPipe Hands initialized');
        return handsDetector;
    } catch (err) {
        console.error('MediaPipe Hands initialization failed:', err);
        gestureOverlay.textContent = `Error: MediaPipe - ${err.message}`;
        return null;
    }
}

// Initialize TFLite model
async function loadModel() {
    try {
        console.log('Checking TFJS TFLite:', !!tf.tflite); // Debug log
        if (!tf || !tf.tflite) {
            console.error('TFJS TFLite not available');
            gestureOverlay.textContent = 'Error: TFJS TFLite not loaded';
            return;
        }
        model = await tf.tflite.loadTFLiteModel('/static/gesture_model_3d_final.tflite');
        console.log('TFLite model loaded successfully');
    } catch (err) {
        console.error('Error loading TFLite model:', err);
        gestureOverlay.textContent = `Error: Model load - ${err.message}`;
    }
}

// Process hand landmarks
function onHandResults(results) {
    if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
        const landmarks = results.multiHandLandmarks[0];
        const frame = landmarks.map(lm => [lm.x, lm.y, lm.z]);
        gestureBuffer.push(frame);
        if (gestureBuffer.length > 4) gestureBuffer.shift();
        if (gestureBuffer.length === 4) processGesture();
    } else {
        gestureOverlay.textContent = 'Gesture: None (0%)';
    }
}

// Process gesture with majority vote (simplified)
async function processGesture() {
    if (!model || !hands) return;
    const input = tf.tensor(gestureBuffer.flat(2), [1, 4, 21, 3], 'float32');
    const output = await model.predict(input);
    const predictions = output.dataSync();
    const gestureIdx = predictions.indexOf(Math.max(...predictions));
    const confidence = predictions[gestureIdx];

    if (confidence < 0.7) {
        gestureOverlay.textContent = `Gesture: None (${(confidence * 100).toFixed(0)}%)`;
        return;
    }

    const now = Date.now();
    if (now - lastGestureTime < 500) return; // Debounce
    lastGestureTime = now;

    gestureOverlay.textContent = `Gesture: ${gestureNames[gestureIdx]} (${(confidence * 100).toFixed(0)}%)`;
    handleGesture(gestureIdx, confidence);
    input.dispose(); // Clean up tensor
}

// Handle gestures
function handleGesture(gestureIdx, confidence) {
    switch (gestureIdx) {
        case 0: // write_start
            isWriting = true;
            isPanning = false;
            canvas.isDrawingMode = true;
            canvas.freeDrawingBrush.color = colors[currentColorIndex];
            break;
        case 1: // write_stop
            isWriting = false;
            canvas.isDrawingMode = false;
            break;
        case 2: // change_color
            currentColorIndex = (currentColorIndex + 1) % colors.length;
            currentColorSpan.textContent = colors[currentColorIndex].charAt(0).toUpperCase() + colors[currentColorIndex].slice(1);
            canvas.freeDrawingBrush.color = colors[currentColorIndex];
            break;
        case 3: // zoom_in
            canvas.setZoom(canvas.getZoom() * 1.1);
            break;
        case 4: // erase
            canvas.isDrawingMode = true;
            canvas.freeDrawingBrush.color = 'white';
            canvas.freeDrawingBrush.width = 20;
            break;
        case 5: // zoom_out
            canvas.setZoom(canvas.getZoom() / 1.1);
            break;
        case 6: // undo
            if (history.length > 0) {
                redoStack.push(canvas.toJSON());
                canvas.loadFromJSON(history.pop(), canvas.renderAll.bind(canvas));
            }
            break;
        case 7: // redo
            if (redoStack.length > 0) {
                history.push(canvas.toJSON());
                canvas.loadFromJSON(redoStack.pop(), canvas.renderAll.bind(canvas));
            }
            break;
        case 8: // draw_shapes
            isShapeMode = true;
            canvas.isDrawingMode = false;
            break;
        case 9: // save
            saveCanvas();
            break;
        case 10: // pan
            isPanning = true;
            isWriting = false;
            canvas.isDrawingMode = false;
            canvas.selection = true;
            break;
        case 11: // clear_all
            canvas.clear();
            history.length = 0;
            redoStack.length = 0;
            break;
    }
}

// Save canvas as PNG
async function saveCanvas() {
    const dataUrl = canvas.toDataURL('image/png');
    try {
        const response = await fetch('/api/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: dataUrl })
        });
        const result = await response.json();
        if (response.ok) {
            alert(`Drawing saved as ${result.filename}`);
        } else {
            alert(`Error: ${result.error}`);
        }
    } catch (err) {
        alert(`Error saving drawing: ${err}`);
    }
}

// Canvas event listeners
canvas.on('path:created', () => {
    history.push(canvas.toJSON());
    redoStack.length = 0;
});

// Toolbar button listeners
saveBtn.addEventListener('click', saveCanvas);
undoBtn.addEventListener('click', () => handleGesture(6, 1.0));
redoBtn.addEventListener('click', () => handleGesture(7, 1.0));
clearBtn.addEventListener('click', () => handleGesture(11, 1.0));
colorBtn.addEventListener('click', () => handleGesture(2, 1.0));

// Draggable webcam container
let isDragging = false, startX, startY;
webcamContainer.addEventListener('mousedown', (e) => {
    isDragging = true;
    startX = e.clientX - parseInt(webcamContainer.style.left || 0);
    startY = e.clientY - parseInt(webcamContainer.style.top || 0);
});
document.addEventListener('mousemove', (e) => {
    if (isDragging) {
        webcamContainer.style.left = `${e.clientX - startX}px`;
        webcamContainer.style.top = `${e.clientY - startY}px`;
    }
});
document.addEventListener('mouseup', () => { isDragging = false; });

// Animation loop
function animate() {
    if (video.readyState >= 2 && hands) {
        hands.send({ image: video });
    }
    requestAnimationFrame(animate);
    console.log('Animation frame running');
}

// Initialize
async function init() {
    await setupWebcam();
    await loadModel();
    hands = await initializeHands();
    if (!hands) {
        console.error('Failed to initialize hands detector. Gesture detection disabled.');
        return;
    }
    animate();
}

init();