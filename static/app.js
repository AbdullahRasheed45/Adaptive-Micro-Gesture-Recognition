class GestureWhiteboardApp {
  constructor() {
    this.whiteboard = null
    this.gestureRecognition = null
    this.isInitialized = false

    // Gesture mapping
    this.gestureActions = {
      write_start: () => this.whiteboard.startDrawing(),
      write_stop: () => this.whiteboard.stopDrawing(),
      change_color: () => this.whiteboard.cycleColor(),
      zoom_in: () => this.whiteboard.zoomIn(),
      erase: () => this.whiteboard.toggleEraseMode(),
      zoom_out: () => this.whiteboard.zoomOut(),
      undo: () => this.whiteboard.undo(),
      redo: () => this.whiteboard.redo(),
      draw_shapes: () => this.whiteboard.toggleShapeMode(),
      save: () => this.whiteboard.saveDrawing(),
      pan: () => this.whiteboard.startPanning(),
      clear_all: () => this.whiteboard.clearCanvas(),
    }

    this.init()
  }

  async init() {
    try {
      console.log("Initializing Gesture Whiteboard App...")

      // Initialize whiteboard - access from global window object
      this.whiteboard = new window.Whiteboard("whiteboard-canvas")
      console.log("Whiteboard initialized")

      // Initialize gesture recognition - access from global window object
      this.gestureRecognition = new window.GestureRecognition()

      // Set up gesture callback
      this.gestureRecognition.setGestureCallback((gestureName, confidence) => {
        this.handleGesture(gestureName, confidence)
      })

      // Initialize gesture recognition system
      await this.gestureRecognition.initialize()
      console.log("Gesture recognition initialized")

      // Set up UI event listeners
      this.setupUIEventListeners()

      this.isInitialized = true
      console.log("App initialization complete")
    } catch (error) {
      console.error("Failed to initialize app:", error)
      this.showError("Failed to initialize the application. Please check your camera permissions and try again.")
    }
  }

  handleGesture(gestureName, confidence) {
    console.log(`Processing gesture: ${gestureName} (${(confidence * 100).toFixed(1)}%)`)

    // Execute gesture action
    if (this.gestureActions[gestureName]) {
      try {
        this.gestureActions[gestureName]()
        this.showGestureConfirmation(gestureName)
      } catch (error) {
        console.error(`Error executing gesture ${gestureName}:`, error)
      }
    } else {
      console.warn(`Unknown gesture: ${gestureName}`)
    }
  }

  setupUIEventListeners() {
    // Gesture legend toggle
    const legendToggle = document.getElementById("legend-toggle")
    const gestureeLegend = document.getElementById("gesture-legend")

    legendToggle.addEventListener("click", () => {
      gestureeLegend.classList.toggle("collapsed")
    })

    // Keyboard shortcuts
    document.addEventListener("keydown", (e) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case "z":
            e.preventDefault()
            if (e.shiftKey) {
              this.whiteboard.redo()
            } else {
              this.whiteboard.undo()
            }
            break
          case "s":
            e.preventDefault()
            this.whiteboard.saveDrawing()
            break
          case "a":
            e.preventDefault()
            this.whiteboard.clearCanvas()
            break
        }
      }

      // ESC to stop current mode
      if (e.key === "Escape") {
        this.whiteboard.stopDrawing()
        this.whiteboard.toggleEraseMode()
        this.whiteboard.stopPanning()
      }
    })

    // Handle visibility change (pause/resume when tab is not active)
    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        console.log("App paused (tab not visible)")
      } else {
        console.log("App resumed (tab visible)")
      }
    })

    // Handle beforeunload
    window.addEventListener("beforeunload", (e) => {
      if (this.gestureRecognition) {
        this.gestureRecognition.destroy()
      }
    })
  }

  showGestureConfirmation(gestureName) {
    // Visual feedback for gesture execution
    const indicator = document.getElementById("drawing-mode-indicator")
    const originalBackground = indicator.style.background

    indicator.style.background = "rgba(46, 204, 113, 0.9)"
    indicator.style.transform = "scale(1.05)"

    setTimeout(() => {
      indicator.style.background = originalBackground
      indicator.style.transform = "scale(1)"
    }, 200)
  }

  showError(message) {
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
                max-width: 400px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            ">
                <h3>⚠️ Error</h3>
                <p>${message}</p>
                <button onclick="location.reload()" style="
                    background: white;
                    color: #e74c3c;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    margin-top: 10px;
                    cursor: pointer;
                    font-weight: bold;
                ">Reload Page</button>
            </div>
        `

    document.body.appendChild(errorDiv)

    // Hide loading overlay
    document.getElementById("loading-overlay").classList.add("hidden")
  }

  // Public methods for external control
  enableDrawing() {
    this.whiteboard.startDrawing()
  }

  disableDrawing() {
    this.whiteboard.stopDrawing()
  }

  getCurrentMode() {
    return {
      drawing: this.whiteboard.isDrawingEnabled,
      erasing: this.whiteboard.isErasing,
      panning: this.whiteboard.isPanning,
      shapes: this.whiteboard.shapeMode,
    }
  }

  getStats() {
    return {
      initialized: this.isInitialized,
      fps: this.gestureRecognition ? this.gestureRecognition.fps : 0,
      zoomLevel: this.whiteboard ? this.whiteboard.zoomLevel : 1,
      historySize: this.whiteboard ? this.whiteboard.history.length : 0,
    }
  }
}

// Initialize the app when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  window.app = new GestureWhiteboardApp()
})

// Export for debugging
window.GestureWhiteboardApp = GestureWhiteboardApp
