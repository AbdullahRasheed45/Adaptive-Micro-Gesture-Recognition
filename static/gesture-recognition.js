// Import necessary libraries
import { Hands } from "@mediapipe/hands"
import { Camera } from "@mediapipe/camera_utils"
import * as tf from "@tensorflow/tfjs"

// Replace with direct access to global objects
class GestureRecognition {
  constructor() {
    this.hands = null
    this.camera = null
    this.model = null
    this.isInitialized = false

    // Gesture configuration
    this.gestureClasses = [
      "write_start", // 0: index finger
      "write_stop", // 1: fist
      "change_color", // 2: stop
      "zoom_in", // 3: peace
      "erase", // 4: palm
      "zoom_out", // 5: peace_inverted
      "undo", // 6: two_up
      "redo", // 7: peace_inverted (with noise)
      "draw_shapes", // 8: three
      "save", // 9: call
      "pan", // 10: one (index finger, reused)
      "clear_all", // 11: stop_inverted
    ]

    // Landmark buffer for temporal data
    this.landmarkBuffer = []
    this.bufferSize = 4
    this.confidenceThreshold = 0.7

    // Smoothing and debouncing
    this.predictionHistory = []
    this.historySize = 5
    this.lastGestureTime = {}
    this.debounceDelay = 500 // ms

    // Performance tracking
    this.frameCount = 0
    this.lastFpsTime = Date.now()
    this.fps = 0

    // Callbacks
    this.onGestureDetected = null
    this.onHandLandmarks = null
  }

  async initialize() {
    try {
      console.log("Initializing gesture recognition...")

      // Initialize MediaPipe Hands
      this.hands = new Hands({
        locateFile: (file) => {
          return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
        },
      })

      this.hands.setOptions({
        maxNumHands: 1,
        modelComplexity: 1,
        minDetectionConfidence: 0.7,
        minTrackingConfidence: 0.5,
      })

      this.hands.onResults(this.onResults.bind(this))

      // Initialize camera
      const videoElement = document.getElementById("camera-feed")
      this.camera = new Camera(videoElement, {
        onFrame: async () => {
          await this.hands.send({ image: videoElement })
        },
        width: 640,
        height: 480,
      })

      // Load TensorFlow.js model (mock for now - replace with your actual model)
      await this.loadModel()

      // Start camera
      await this.camera.start()

      this.isInitialized = true
      console.log("Gesture recognition initialized successfully")

      // Update UI
      document.getElementById("connection-status").classList.add("online")
      document.getElementById("loading-overlay").classList.add("hidden")
    } catch (error) {
      console.error("Failed to initialize gesture recognition:", error)
      throw error
    }
  }

  async loadModel() {
    try {
      console.log("Loading gesture recognition model...")

      // Load your JSON model
      this.model = await tf.loadLayersModel("/static/model.json")

      console.log("Model loaded successfully")
    } catch (error) {
      console.error("Failed to load model:", error)
      // Fallback to mock model for development
      this.model = {
        predict: (input) => {
          const mockProbabilities = new Array(12).fill(0).map(() => Math.random() * 0.1)
          const maxIndex = Math.floor(Math.random() * 12)
          mockProbabilities[maxIndex] = 0.8 + Math.random() * 0.2
          return tf.tensor1d(mockProbabilities)
        },
      }
      console.log("Using mock model for development")
    }
  }

  onResults(results) {
    this.updateFPS()

    const canvas = document.getElementById("camera-overlay")
    const ctx = canvas.getContext("2d")

    // Clear previous drawings
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
      const landmarks = results.multiHandLandmarks[0]

      // Draw hand landmarks
      this.drawHandLandmarks(ctx, landmarks)

      // Process landmarks for gesture recognition
      this.processLandmarks(landmarks)

      // Callback for hand landmarks
      if (this.onHandLandmarks) {
        this.onHandLandmarks(landmarks)
      }
    } else {
      // No hands detected
      this.updateGestureDisplay("No hand detected", 0)
    }
  }

  drawHandLandmarks(ctx, landmarks) {
    const canvas = ctx.canvas
    ctx.fillStyle = "#00ff00"
    ctx.strokeStyle = "#00ff00"
    ctx.lineWidth = 2

    // Draw landmarks
    landmarks.forEach((landmark, index) => {
      const x = landmark.x * canvas.width
      const y = landmark.y * canvas.height

      ctx.beginPath()
      ctx.arc(x, y, 3, 0, 2 * Math.PI)
      ctx.fill()
    })

    // Draw connections (simplified)
    const connections = [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 4], // Thumb
      [0, 5],
      [5, 6],
      [6, 7],
      [7, 8], // Index
      [0, 9],
      [9, 10],
      [10, 11],
      [11, 12], // Middle
      [0, 13],
      [13, 14],
      [14, 15],
      [15, 16], // Ring
      [0, 17],
      [17, 18],
      [18, 19],
      [19, 20], // Pinky
    ]

    connections.forEach(([start, end]) => {
      const startPoint = landmarks[start]
      const endPoint = landmarks[end]

      ctx.beginPath()
      ctx.moveTo(startPoint.x * canvas.width, startPoint.y * canvas.height)
      ctx.lineTo(endPoint.x * canvas.width, endPoint.y * canvas.height)
      ctx.stroke()
    })
  }

  processLandmarks(landmarks) {
    // Convert landmarks to the required format [x, y, z] for each of 21 points
    const landmarkArray = landmarks.map((landmark) => [landmark.x, landmark.y, landmark.z || 0])

    // Add to buffer
    this.landmarkBuffer.push(landmarkArray)

    // Maintain buffer size
    if (this.landmarkBuffer.length > this.bufferSize) {
      this.landmarkBuffer.shift()
    }

    // Only predict when we have enough frames
    if (this.landmarkBuffer.length === this.bufferSize) {
      this.predictGesture()
    }
  }

  predictGesture() {
    try {
      // Prepare input tensor [1, 4, 21, 3]
      const inputTensor = tf.tensor4d(this.landmarkBuffer.flat().flat(), [1, 4, 21, 3])

      // Run inference
      const prediction = this.model.predict(inputTensor)
      const probabilities = prediction.dataSync()

      // Clean up tensor
      inputTensor.dispose()
      prediction.dispose()

      // Find the class with highest probability
      const maxIndex = probabilities.indexOf(Math.max(...probabilities))
      const confidence = probabilities[maxIndex]

      // Add to prediction history for smoothing
      this.predictionHistory.push({ class: maxIndex, confidence })
      if (this.predictionHistory.length > this.historySize) {
        this.predictionHistory.shift()
      }

      // Apply majority vote smoothing
      const smoothedPrediction = this.applySmoothingFilter()

      if (smoothedPrediction.confidence >= this.confidenceThreshold) {
        this.handleGestureDetection(smoothedPrediction)
      }

      // Update display
      this.updateGestureDisplay(this.gestureClasses[smoothedPrediction.class], smoothedPrediction.confidence)
    } catch (error) {
      console.error("Prediction error:", error)
    }
  }

  applySmoothingFilter() {
    if (this.predictionHistory.length === 0) {
      return { class: 0, confidence: 0 }
    }

    // Count occurrences of each class
    const classCounts = {}
    let totalConfidence = 0

    this.predictionHistory.forEach((pred) => {
      if (!classCounts[pred.class]) {
        classCounts[pred.class] = { count: 0, totalConfidence: 0 }
      }
      classCounts[pred.class].count++
      classCounts[pred.class].totalConfidence += pred.confidence
      totalConfidence += pred.confidence
    })

    // Find the most frequent class
    let maxCount = 0
    let bestClass = 0
    let bestConfidence = 0

    Object.keys(classCounts).forEach((classId) => {
      const classData = classCounts[classId]
      if (classData.count > maxCount) {
        maxCount = classData.count
        bestClass = Number.parseInt(classId)
        bestConfidence = classData.totalConfidence / classData.count
      }
    })

    return { class: bestClass, confidence: bestConfidence }
  }

  handleGestureDetection(prediction) {
    const gestureName = this.gestureClasses[prediction.class]
    const currentTime = Date.now()

    // Check debouncing
    if (this.lastGestureTime[gestureName] && currentTime - this.lastGestureTime[gestureName] < this.debounceDelay) {
      return
    }

    // Update last gesture time
    this.lastGestureTime[gestureName] = currentTime

    // Trigger callback
    if (this.onGestureDetected) {
      this.onGestureDetected(gestureName, prediction.confidence)
    }

    console.log(`Gesture detected: ${gestureName} (${(prediction.confidence * 100).toFixed(1)}%)`)
  }

  updateGestureDisplay(gestureName, confidence) {
    document.getElementById("current-gesture").textContent = gestureName || "No gesture"
    document.getElementById("confidence-score").textContent = `${(confidence * 100).toFixed(1)}%`
  }

  updateFPS() {
    this.frameCount++
    const currentTime = Date.now()

    if (currentTime - this.lastFpsTime >= 1000) {
      this.fps = Math.round((this.frameCount * 1000) / (currentTime - this.lastFpsTime))
      document.getElementById("fps-counter").textContent = `FPS: ${this.fps}`

      this.frameCount = 0
      this.lastFpsTime = currentTime
    }
  }

  setGestureCallback(callback) {
    this.onGestureDetected = callback
  }

  setHandLandmarksCallback(callback) {
    this.onHandLandmarks = callback
  }

  destroy() {
    if (this.camera) {
      this.camera.stop()
    }
    if (this.hands) {
      this.hands.close()
    }
  }
}

// Export for use in other modules
window.GestureRecognition = GestureRecognition
