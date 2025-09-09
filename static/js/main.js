class GestureWhiteboardApp {
  constructor() {
    this.gestureRecognition = null
    this.whiteboard = null
    this.isInitialized = false

    // Performance monitoring
    this.frameCount = 0
    this.lastFrameTime = 0
    this.fps = 0

    this.init()
  }

  async init() {
    try {
      console.log("Initializing Gesture Whiteboard App...")

      // Show loading overlay
      this.showLoadingOverlay(true)

      // Check for required APIs
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error("Camera access not supported in this browser")
      }

      // Initialize whiteboard first (doesn't require async)
      this.initializeWhiteboard()

      // Initialize gesture recognition
      const gestureSuccess = await this.initializeGestureRecognition()

      if (!gestureSuccess) {
        console.warn("Gesture recognition failed to initialize, running in fallback mode")
        this.showNotification("Gesture recognition unavailable. Using keyboard/mouse controls only.", "warning")
      }

      // Setup UI event listeners
      this.setupUIEventListeners()

      // Start main loop
      this.startMainLoop()

      // Hide loading overlay
      this.showLoadingOverlay(false)

      this.isInitialized = true
      console.log("App initialized successfully!")

      this.showNotification("Application loaded successfully!", "success")
    } catch (error) {
      console.error("Failed to initialize app:", error)
      this.showError(`Failed to initialize: ${error.message}`)
    }
  }

  initializeWhiteboard() {
    console.log("Initializing whiteboard...")

    try {
      // Check if Fabric.js is loaded
      const fabric = window.fabric // Declare fabric variable
      if (typeof fabric === "undefined") {
        throw new Error("Fabric.js library not loaded")
      }

      this.whiteboard = new window.Whiteboard("whiteboard-canvas")
      console.log("Whiteboard initialized successfully")
    } catch (error) {
      console.error("Failed to initialize whiteboard:", error)
      throw error
    }
  }

  async initializeGestureRecognition() {
    console.log("Initializing gesture recognition...")

    try {
      // Check if GestureRecognition class is available
      if (typeof window.GestureRecognition === "undefined") {
        throw new Error("GestureRecognition class not loaded")
      }

      this.gestureRecognition = new window.GestureRecognition()

      // Set up gesture callback
      this.gestureRecognition.setGestureCallback((gesture, confidence) => {
        this.handleGestureDetection(gesture, confidence)
      })

      // Set up hands callback for additional processing
      this.gestureRecognition.setHandsCallback((landmarks) => {
        this.handleHandsDetection(landmarks)
      })

      // Initialize the gesture recognition system
      const success = await this.gestureRecognition.initialize()

      if (success) {
        console.log("Gesture recognition initialized successfully")
      }

      return success
    } catch (error) {
      console.error("Failed to initialize gesture recognition:", error)
      return false
    }
  }

  setupUIEventListeners() {
    // Camera toggle
    const toggleCameraBtn = document.getElementById("toggle-camera")
    if (toggleCameraBtn) {
      toggleCameraBtn.addEventListener("click", () => {
        this.toggleCamera()
      })
    }

    // Gesture legend toggle
    const legendToggle = document.getElementById("legend-toggle")
    const gestureLegend = document.getElementById("gesture-legend")

    if (legendToggle && gestureLegend) {
      legendToggle.addEventListener("click", () => {
        gestureLegend.classList.toggle("collapsed")
      })
    }

    // Keyboard shortcuts
    document.addEventListener("keydown", (e) => {
      this.handleKeyboardShortcuts(e)
    })

    // Prevent context menu on canvas
    const canvas = document.getElementById("whiteboard-canvas")
    if (canvas) {
      canvas.addEventListener("contextmenu", (e) => {
        e.preventDefault()
      })
    }

    // Handle window beforeunload
    window.addEventListener("beforeunload", () => {
      this.cleanup()
    })

    console.log("UI event listeners setup completed")
  }

  handleGestureDetection(gesture, confidence) {
    // Add visual feedback
    this.addGestureFeedback(gesture)

    // Forward to whiteboard
    if (this.whiteboard) {
      this.whiteboard.handleGesture(gesture, confidence)
    }

    // Log for debugging
    console.log(`Gesture: ${gesture}, Confidence: ${(confidence * 100).toFixed(1)}%`)
  }

  handleHandsDetection(landmarks) {
    // Additional hand processing can be done here
    // For example, cursor tracking, hand position analysis, etc.

    // Update frame count for performance monitoring
    this.frameCount++
    const currentTime = performance.now()

    if (currentTime - this.lastFrameTime >= 1000) {
      this.fps = this.frameCount
      this.frameCount = 0
      this.lastFrameTime = currentTime

      // Update FPS display (if you want to show it)
      // console.log(`FPS: ${this.fps}`);
    }
  }

  addGestureFeedback(gesture) {
    // Add visual feedback when gesture is detected
    const cameraOverlay = document.getElementById("camera-overlay")
    if (cameraOverlay) {
      cameraOverlay.classList.add("gesture-detected")

      setTimeout(() => {
        cameraOverlay.classList.remove("gesture-detected")
      }, 500)
    }
  }

  handleKeyboardShortcuts(e) {
    // Prevent default for our shortcuts
    const shortcuts = ["KeyZ", "KeyY", "KeyC", "KeyS", "Delete", "Escape"]

    if (shortcuts.includes(e.code) && (e.ctrlKey || e.metaKey)) {
      e.preventDefault()
    }

    if (!this.whiteboard) return

    // Handle shortcuts
    if (e.ctrlKey || e.metaKey) {
      switch (e.code) {
        case "KeyZ":
          if (e.shiftKey) {
            this.whiteboard.redo()
          } else {
            this.whiteboard.undo()
          }
          break

        case "KeyY":
          this.whiteboard.redo()
          break

        case "KeyS":
          this.whiteboard.saveDrawing()
          break

        case "KeyC":
          this.whiteboard.changeColor()
          break
      }
    }

    // Other shortcuts
    switch (e.code) {
      case "Delete":
        this.whiteboard.clearCanvas()
        break

      case "Escape":
        // Stop all drawing modes
        this.whiteboard.stopDrawing()
        this.whiteboard.stopErasing()
        this.whiteboard.stopPanning()
        break
    }
  }

  toggleCamera() {
    const cameraOverlay = document.getElementById("camera-overlay")

    if (cameraOverlay.style.display === "none") {
      cameraOverlay.style.display = "block"
    } else {
      cameraOverlay.style.display = "none"
    }
  }

  startMainLoop() {
    // Main application loop using requestAnimationFrame
    const loop = () => {
      if (this.isInitialized) {
        // Perform any continuous updates here
        // The gesture recognition runs in its own loop

        // Continue loop
        requestAnimationFrame(loop)
      }
    }

    requestAnimationFrame(loop)
  }

  showLoadingOverlay(show) {
    const overlay = document.getElementById("loading-overlay")
    if (overlay) {
      overlay.style.display = show ? "flex" : "none"
    }
  }

  showNotification(message, type = "info") {
    // Create notification element
    const notification = document.createElement("div")
    notification.className = `notification ${type}`
    notification.textContent = message
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      left: 50%;
      transform: translateX(-50%);
      padding: 15px 20px;
      border-radius: 5px;
      color: white;
      font-weight: bold;
      z-index: 10000;
      animation: slideIn 0.3s ease;
      max-width: 400px;
      text-align: center;
    `

    if (type === "success") {
      notification.style.backgroundColor = "#27ae60"
    } else if (type === "error") {
      notification.style.backgroundColor = "#e74c3c"
    } else if (type === "warning") {
      notification.style.backgroundColor = "#f39c12"
    } else {
      notification.style.backgroundColor = "#3498db"
    }

    document.body.appendChild(notification)

    // Remove after 4 seconds
    setTimeout(() => {
      notification.style.animation = "slideOut 0.3s ease"
      setTimeout(() => {
        if (document.body.contains(notification)) {
          document.body.removeChild(notification)
        }
      }, 300)
    }, 4000)
  }

  showError(message) {
    // Hide loading overlay
    this.showLoadingOverlay(false)

    // Show error message
    const errorDiv = document.createElement("div")
    errorDiv.className = "error-message"
    errorDiv.innerHTML = `
      <div style="
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: #e74c3c;
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        z-index: 10000;
        max-width: 500px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
      ">
        <h3 style="margin-bottom: 15px;">⚠️ Error</h3>
        <p style="margin-bottom: 20px;">${message}</p>
        <button onclick="location.reload()" style="
          background: white;
          color: #e74c3c;
          border: none;
          padding: 10px 20px;
          border-radius: 5px;
          cursor: pointer;
          font-weight: bold;
        ">🔄 Reload Page</button>
      </div>
    `

    document.body.appendChild(errorDiv)
  }

  cleanup() {
    console.log("Cleaning up application...")

    if (this.gestureRecognition) {
      this.gestureRecognition.destroy()
    }

    this.isInitialized = false
  }
}

// Initialize the application when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  console.log("DOM loaded, initializing app...")
  window.app = new GestureWhiteboardApp()
})

// Handle page visibility changes
document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    console.log("Page hidden, pausing operations...")
  } else {
    console.log("Page visible, resuming operations...")
  }
})

// Global error handler
window.addEventListener("error", (e) => {
  console.error("Global error:", e.error)
})

window.addEventListener("unhandledrejection", (e) => {
  console.error("Unhandled promise rejection:", e.reason)
})
