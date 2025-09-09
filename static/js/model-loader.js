/**
 * TensorFlow.js Model Loader for Frontend Gesture Recognition
 * Loads and runs TFLite model directly in browser for low-latency inference
 */

class GestureModelLoader {
    constructor() {
        this.model = null;
        this.isLoaded = false;
        this.modelPath = '/static/models/gesture_model.tflite';
        
        // Gesture class mapping (must match training)
        this.gestureClasses = {
            0: 'write_start',     // index finger (one)
            1: 'write_stop',      // fist (rock)
            2: 'change_color',    // stop
            3: 'zoom_in',         // peace
            4: 'erase',           // palm
            5: 'zoom_out',        // peace_inverted
            6: 'undo',            // two_up
            7: 'redo',            // peace_inverted (with noise)
            8: 'draw_shapes',     // three
            9: 'save',            // call
            10: 'pan',            // one (index finger, reused)
            11: 'clear_all'       // stop_inverted
        };
    }
    
    async loadModel() {
        try {
            console.log('Loading TensorFlow.js model...');
            
            // Check if TensorFlow.js is available
            if (typeof tf === 'undefined') {
                throw new Error('TensorFlow.js not loaded');
            }
            
            // Set backend to WebGL for GPU acceleration
            await tf.setBackend('webgl');
            console.log('TensorFlow.js backend:', tf.getBackend());
            
            // Load the TFLite model
            this.model = await tf.loadLayersModel(this.modelPath);
            
            if (!this.model) {
                throw new Error('Failed to load model');
            }
            
            // Warm up the model with dummy data
            await this.warmUpModel();
            
            this.isLoaded = true;
            console.log('Model loaded successfully');
            console.log('Model input shape:', this.model.inputs[0].shape);
            console.log('Model output shape:', this.model.outputs[0].shape);
            
            return true;
            
        } catch (error) {
            console.error('Model loading failed:', error);
            this.isLoaded = false;
            return false;
        }
    }
    
    async warmUpModel() {
        if (!this.model) return;
        
        try {
            // Create dummy input with correct shape [1, 4, 21, 3]
            const dummyInput = tf.zeros([1, 4, 21, 3]);
            
            // Run inference to warm up the model
            const prediction = this.model.predict(dummyInput);
            prediction.dispose();
            dummyInput.dispose();
            
            console.log('Model warmed up successfully');
            
        } catch (error) {
            console.warn('Model warm-up failed:', error);
        }
    }
    
    async predict(landmarksBuffer) {
        if (!this.isLoaded || !this.model) {
            throw new Error('Model not loaded');
        }
        
        try {
            // Convert landmarks buffer to tensor
            // Expected input: [4, 21, 3] array of landmarks
            const inputTensor = tf.tensor4d([landmarksBuffer], [1, 4, 21, 3]);
            
            // Run inference
            const prediction = this.model.predict(inputTensor);
            
            // Get probabilities
            const probabilities = await prediction.data();
            
            // Find predicted class
            const predictedClass = prediction.argMax(-1).dataSync()[0];
            const confidence = probabilities[predictedClass];
            
            // Clean up tensors
            inputTensor.dispose();
            prediction.dispose();
            
            return {
                gesture: this.gestureClasses[predictedClass] || 'unknown',
                class_id: predictedClass,
                confidence: confidence,
                probabilities: Array.from(probabilities)
            };
            
        } catch (error) {
            console.error('Prediction error:', error);
            throw error;
        }
    }
    
    // Alternative method for loading TFLite model (if available)
    async loadTFLiteModel() {
        try {
            console.log('Attempting to load TFLite model...');
            
            // Check if tflite is available
            if (typeof tflite === 'undefined') {
                console.warn('TFLite not available, falling back to TensorFlow.js');
                return await this.loadModel();
            }
            
            // Load TFLite model
            const response = await fetch(this.modelPath);
            const modelBuffer = await response.arrayBuffer();
            
            this.model = await tflite.loadTFLiteModel(modelBuffer);
            this.isLoaded = true;
            
            console.log('TFLite model loaded successfully');
            return true;
            
        } catch (error) {
            console.error('TFLite loading failed:', error);
            console.log('Falling back to TensorFlow.js...');
            return await this.loadModel();
        }
    }
    
    // Batch prediction for multiple frames
    async predictBatch(landmarksBufferArray) {
        if (!this.isLoaded || !this.model) {
            throw new Error('Model not loaded');
        }
        
        try {
            const batchSize = landmarksBufferArray.length;
            const inputTensor = tf.tensor4d(landmarksBufferArray, [batchSize, 4, 21, 3]);
            
            const predictions = this.model.predict(inputTensor);
            const probabilities = await predictions.data();
            const predictedClasses = predictions.argMax(-1).dataSync();
            
            const results = [];
            for (let i = 0; i < batchSize; i++) {
                const startIdx = i * 12; // 12 classes
                const classProbabilities = probabilities.slice(startIdx, startIdx + 12);
                const predictedClass = predictedClasses[i];
                const confidence = classProbabilities[predictedClass];
                
                results.push({
                    gesture: this.gestureClasses[predictedClass] || 'unknown',
                    class_id: predictedClass,
                    confidence: confidence,
                    probabilities: Array.from(classProbabilities)
                });
            }
            
            inputTensor.dispose();
            predictions.dispose();
            
            return results;
            
        } catch (error) {
            console.error('Batch prediction error:', error);
            throw error;
        }
    }
    
    // Get model information
    getModelInfo() {
        if (!this.isLoaded || !this.model) {
            return {
                loaded: false,
                error: 'Model not loaded'
            };
        }
        
        return {
            loaded: true,
            inputShape: this.model.inputs[0].shape,
            outputShape: this.model.outputs[0].shape,
            backend: tf.getBackend(),
            memoryInfo: tf.memory(),
            gestureClasses: this.gestureClasses
        };
    }
    
    // Cleanup resources
    dispose() {
        if (this.model) {
            this.model.dispose();
            this.model = null;
            this.isLoaded = false;
            console.log('Model disposed');
        }
    }
    
    // Preprocess landmarks for better accuracy
    preprocessLandmarks(landmarksBuffer) {
        try {
            const processedBuffer = [];
            
            for (let frame of landmarksBuffer) {
                const processedFrame = [];
                
                // Normalize landmarks relative to wrist (landmark 0)
                const wrist = frame[0];
                
                for (let landmark of frame) {
                    const normalizedLandmark = [
                        landmark[0] - wrist[0], // Relative x
                        landmark[1] - wrist[1], // Relative y
                        landmark[2] - wrist[2]  // Relative z
                    ];
                    processedFrame.push(normalizedLandmark);
                }
                
                processedBuffer.push(processedFrame);
            }
            
            return processedBuffer;
            
        } catch (error) {
            console.error('Preprocessing error:', error);
            return landmarksBuffer; // Return original if preprocessing fails
        }
    }
    
    // Calculate hand landmarks statistics for debugging
    analyzeLandmarks(landmarksBuffer) {
        if (!landmarksBuffer || landmarksBuffer.length === 0) {
            return null;
        }
        
        try {
            const stats = {
                frames: landmarksBuffer.length,
                landmarks_per_frame: landmarksBuffer[0].length,
                coordinates_per_landmark: landmarksBuffer[0][0].length,
                x_range: { min: Infinity, max: -Infinity },
                y_range: { min: Infinity, max: -Infinity },
                z_range: { min: Infinity, max: -Infinity }
            };
            
            // Calculate coordinate ranges
            for (let frame of landmarksBuffer) {
                for (let landmark of frame) {
                    stats.x_range.min = Math.min(stats.x_range.min, landmark[0]);
                    stats.x_range.max = Math.max(stats.x_range.max, landmark[0]);
                    stats.y_range.min = Math.min(stats.y_range.min, landmark[1]);
                    stats.y_range.max = Math.max(stats.y_range.max, landmark[1]);
                    stats.z_range.min = Math.min(stats.z_range.min, landmark[2]);
                    stats.z_range.max = Math.max(stats.z_range.max, landmark[2]);
                }
            }
            
            return stats;
            
        } catch (error) {
            console.error('Landmarks analysis error:', error);
            return null;
        }
    }
}

// Enhanced gesture recognition with confidence smoothing
class EnhancedGestureRecognizer {
    constructor(modelLoader) {
        this.modelLoader = modelLoader;
        this.predictionHistory = [];
        this.maxHistoryLength = 10;
        this.confidenceThreshold = 0.7;
        this.stabilityThreshold = 0.6; // Minimum ratio of consistent predictions
    }
    
    async predict(landmarksBuffer) {
        try {
            // Preprocess landmarks
            const processedLandmarks = this.modelLoader.preprocessLandmarks(landmarksBuffer);
            
            // Get prediction
            const prediction = await this.modelLoader.predict(processedLandmarks);
            
            // Add to history
            this.predictionHistory.push(prediction);
            if (this.predictionHistory.length > this.maxHistoryLength) {
                this.predictionHistory.shift();
            }
            
            // Get stabilized prediction
            const stabilizedPrediction = this.getStabilizedPrediction();
            
            return stabilizedPrediction || prediction;
            
        } catch (error) {
            console.error('Enhanced prediction error:', error);
            throw error;
        }
    }
    
    getStabilizedPrediction() {
        if (this.predictionHistory.length < 3) {
            return null; // Not enough history
        }
        
        // Count gesture occurrences
        const gestureCounts = {};
        const confidenceSum = {};
        
        for (let prediction of this.predictionHistory) {
            if (prediction.confidence >= this.confidenceThreshold) {
                const gesture = prediction.gesture;
                gestureCounts[gesture] = (gestureCounts[gesture] || 0) + 1;
                confidenceSum[gesture] = (confidenceSum[gesture] || 0) + prediction.confidence;
            }
        }
        
        // Find most stable gesture
        let bestGesture = null;
        let bestStability = 0;
        
        for (let [gesture, count] of Object.entries(gestureCounts)) {
            const stability = count / this.predictionHistory.length;
            if (stability >= this.stabilityThreshold && stability > bestStability) {
                bestGesture = gesture;
                bestStability = stability;
            }
        }
        
        if (bestGesture) {
            const avgConfidence = confidenceSum[bestGesture] / gestureCounts[bestGesture];
            return {
                gesture: bestGesture,
                confidence: avgConfidence,
                stability: bestStability,
                stabilized: true
            };
        }
        
        return null;
    }
    
    reset() {
        this.predictionHistory = [];
    }
}

// Export for use in main application
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { GestureModelLoader, EnhancedGestureRecognizer };
} else {
    window.GestureModelLoader = GestureModelLoader;
    window.EnhancedGestureRecognizer = EnhancedGestureRecognizer;
}