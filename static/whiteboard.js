// Import fabric library
const fabric = window.fabric

class Whiteboard {
  constructor(canvasId) {
    this.canvas = new fabric.Canvas(canvasId, {
      isDrawingMode: false,
      width: window.innerWidth - 340, // Account for camera and margins
      height: window.innerHeight - 120, // Account for toolbar
    })

    // Drawing state
    this.isDrawingEnabled = false
    this.isErasing = false
    this.isPanning = false
    this.currentColor = "#000000"
    this.brushSize = 5

    // History for undo/redo
    this.history = []
    this.historyIndex = -1
    this.maxHistorySize = 50

    // Shape drawing mode
    this.shapeMode = false
    this.currentShape = "rectangle"

    // Zoom settings
    this.zoomLevel = 1
    this.minZoom = 0.1
    this.maxZoom = 5

    this.initializeCanvas()
    this.setupEventListeners()
    this.saveState() // Initial state
  }

  initializeCanvas() {
    // Set canvas background
    this.canvas.backgroundColor = "#ffffff"

    // Configure drawing brush
    this.canvas.freeDrawingBrush.width = this.brushSize
    this.canvas.freeDrawingBrush.color = this.currentColor

    // Disable object selection by default
    this.canvas.selection = false
    this.canvas.forEachObject((obj) => {
      obj.selectable = false
    })

    // Handle canvas events
    this.canvas.on("path:created", () => {
      if (this.isDrawingEnabled) {
        this.saveState()
      }
    })

    this.canvas.on("object:added", () => {
      this.updateUI()
    })

    // Handle window resize
    window.addEventListener("resize", () => {
      this.resizeCanvas()
    })
  }

  setupEventListeners() {
    // Color palette
    document.querySelectorAll(".color-option").forEach((option) => {
      option.addEventListener("click", (e) => {
        this.changeColor(e.target.dataset.color)
        this.updateColorPalette(e.target)
      })
    })

    // Brush size
    const brushSizeSlider = document.getElementById("brush-size")
    const brushSizeValue = document.getElementById("brush-size-value")

    brushSizeSlider.addEventListener("input", (e) => {
      this.brushSize = Number.parseInt(e.target.value)
      this.canvas.freeDrawingBrush.width = this.brushSize
      brushSizeValue.textContent = `${this.brushSize}px`
    })

    // Toolbar buttons
    document.getElementById("undo-btn").addEventListener("click", () => this.undo())
    document.getElementById("redo-btn").addEventListener("click", () => this.redo())
    document.getElementById("clear-btn").addEventListener("click", () => this.clearCanvas())
    document.getElementById("save-btn").addEventListener("click", () => this.saveDrawing())
  }

  // Gesture-controlled methods
  startDrawing() {
    if (!this.isDrawingEnabled) {
      this.isDrawingEnabled = true
      this.canvas.isDrawingMode = true
      this.updateModeIndicator("Drawing", "drawing", "✏️")
      console.log("Drawing mode enabled")
    }
  }

  stopDrawing() {
    if (this.isDrawingEnabled) {
      this.isDrawingEnabled = false
      this.canvas.isDrawingMode = false
      this.updateModeIndicator("Ready", "", "✋")
      console.log("Drawing mode disabled")
    }
  }

  toggleEraseMode() {
    this.isErasing = !this.isErasing

    if (this.isErasing) {
      this.canvas.isDrawingMode = true
      this.canvas.freeDrawingBrush.color = "#ffffff" // White for erasing
      this.updateModeIndicator("Erasing", "erasing", "🧽")
    } else {
      this.canvas.freeDrawingBrush.color = this.currentColor
      this.updateModeIndicator("Ready", "", "✋")
    }
  }

  changeColor(color) {
    this.currentColor = color
    if (!this.isErasing) {
      this.canvas.freeDrawingBrush.color = color
    }
    console.log(`Color changed to: ${color}`)
  }

  cycleColor() {
    const colors = ["#000000", "#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff", "#00ffff", "#ffffff"]
    const currentIndex = colors.indexOf(this.currentColor)
    const nextIndex = (currentIndex + 1) % colors.length
    const nextColor = colors[nextIndex]

    this.changeColor(nextColor)
    this.updateColorPalette(document.querySelector(`[data-color="${nextColor}"]`))
  }

  updateColorPalette(activeElement) {
    document.querySelectorAll(".color-option").forEach((option) => {
      option.classList.remove("active")
    })
    if (activeElement) {
      activeElement.classList.add("active")
    }
  }

  zoomIn() {
    const newZoom = Math.min(this.zoomLevel * 1.2, this.maxZoom)
    this.setZoom(newZoom)
  }

  zoomOut() {
    const newZoom = Math.max(this.zoomLevel / 1.2, this.minZoom)
    this.setZoom(newZoom)
  }

  setZoom(zoom) {
    this.zoomLevel = zoom
    this.canvas.setZoom(zoom)
    this.canvas.renderAll()
    console.log(`Zoom level: ${(zoom * 100).toFixed(0)}%`)
  }

  undo() {
    if (this.historyIndex > 0) {
      this.historyIndex--
      this.loadState(this.history[this.historyIndex])
      console.log("Undo performed")
    }
  }

  redo() {
    if (this.historyIndex < this.history.length - 1) {
      this.historyIndex++
      this.loadState(this.history[this.historyIndex])
      console.log("Redo performed")
    }
  }

  clearCanvas() {
    this.canvas.clear()
    this.canvas.backgroundColor = "#ffffff"
    this.saveState()
    console.log("Canvas cleared")
  }

  toggleShapeMode() {
    this.shapeMode = !this.shapeMode

    if (this.shapeMode) {
      this.canvas.isDrawingMode = false
      this.updateModeIndicator("Shape Mode", "shapes", "🔷")
      this.enableShapeDrawing()
    } else {
      this.canvas.isDrawingMode = this.isDrawingEnabled
      this.updateModeIndicator("Ready", "", "✋")
      this.disableShapeDrawing()
    }
  }

  enableShapeDrawing() {
    // Enable object selection for shape manipulation
    this.canvas.selection = true

    // Add a sample rectangle for demonstration
    const rect = new fabric.Rect({
      left: 100,
      top: 100,
      width: 100,
      height: 100,
      fill: "transparent",
      stroke: this.currentColor,
      strokeWidth: 2,
      selectable: true,
    })

    this.canvas.add(rect)
    this.saveState()
  }

  disableShapeDrawing() {
    this.canvas.selection = false
    this.canvas.forEachObject((obj) => {
      obj.selectable = false
    })
  }

  startPanning() {
    this.isPanning = true
    this.canvas.isDragging = true
    this.canvas.selection = false
    this.updateModeIndicator("Panning", "panning", "👋")
  }

  stopPanning() {
    this.isPanning = false
    this.canvas.isDragging = false
    this.updateModeIndicator("Ready", "", "✋")
  }

  async saveDrawing() {
    try {
      const dataURL = this.canvas.toDataURL({
        format: "png",
        quality: 1.0,
      })

      const response = await fetch("/api/save-drawing", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          image_data: dataURL,
          filename: `whiteboard_${new Date().toISOString().slice(0, 19).replace(/:/g, "-")}.png`,
        }),
      })

      const result = await response.json()

      if (result.success) {
        this.showNotification("Drawing saved successfully!", "success")
        console.log("Drawing saved:", result.filename)
      } else {
        this.showNotification("Failed to save drawing", "error")
      }
    } catch (error) {
      console.error("Save error:", error)
      this.showNotification("Error saving drawing", "error")
    }
  }

  // State management
  saveState() {
    const state = JSON.stringify(this.canvas.toJSON())

    // Remove states after current index (for redo functionality)
    this.history = this.history.slice(0, this.historyIndex + 1)

    // Add new state
    this.history.push(state)
    this.historyIndex++

    // Limit history size
    if (this.history.length > this.maxHistorySize) {
      this.history.shift()
      this.historyIndex--
    }
  }

  loadState(state) {
    this.canvas.loadFromJSON(state, () => {
      this.canvas.renderAll()
      this.updateUI()
    })
  }

  // UI helpers
  updateModeIndicator(text, className, icon) {
    const indicator = document.getElementById("drawing-mode-indicator")
    const modeText = document.getElementById("mode-text")
    const modeIcon = document.getElementById("mode-icon")

    modeText.textContent = text
    modeIcon.textContent = icon

    // Reset classes
    indicator.className = ""
    if (className) {
      indicator.classList.add(className)
    }
  }

  updateUI() {
    // Update undo/redo button states
    document.getElementById("undo-btn").disabled = this.historyIndex <= 0
    document.getElementById("redo-btn").disabled = this.historyIndex >= this.history.length - 1
  }

  showNotification(message, type = "info") {
    // Create notification element
    const notification = document.createElement("div")
    notification.className = `notification ${type}`
    notification.textContent = message
    notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: ${type === "success" ? "#27ae60" : type === "error" ? "#e74c3c" : "#3498db"};
            color: white;
            border-radius: 5px;
            z-index: 10000;
            font-weight: bold;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `

    document.body.appendChild(notification)

    // Animate in
    setTimeout(() => {
      notification.style.transform = "translateX(0)"
    }, 100)

    // Remove after delay
    setTimeout(() => {
      notification.style.transform = "translateX(100%)"
      setTimeout(() => {
        document.body.removeChild(notification)
      }, 300)
    }, 3000)
  }

  resizeCanvas() {
    const container = document.getElementById("canvas-container")
    const rect = container.getBoundingClientRect()

    this.canvas.setDimensions({
      width: rect.width - 20,
      height: rect.height - 20,
    })
  }
}

// Export for use in other modules
window.Whiteboard = Whiteboard
