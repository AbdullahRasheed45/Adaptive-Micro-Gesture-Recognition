// Import Fabric.js library
const fabric = window.fabric

class Whiteboard {
  constructor(canvasId) {
    this.canvas = new fabric.Canvas(canvasId, {
      isDrawingMode: false,
      width: window.innerWidth,
      height: window.innerHeight - 80, // Account for toolbar
      backgroundColor: "white",
    })

    // Drawing state
    this.isDrawingMode = false
    this.isErasingMode = false
    this.isPanningMode = false
    this.currentColor = "#000000"
    this.brushSize = 5
    this.zoomLevel = 1

    // History for undo/redo
    this.history = []
    this.historyIndex = -1
    this.maxHistorySize = 50

    // Color palette
    this.colorPalette = ["#000000", "#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff", "#00ffff", "#ffffff"]
    this.currentColorIndex = 0

    // Shape drawing mode
    this.shapeMode = false
    this.currentShape = "rectangle"

    this.initializeCanvas()
    this.setupEventListeners()
    this.saveState() // Initial state
  }

  initializeCanvas() {
    // Configure drawing brush
    this.canvas.freeDrawingBrush.width = this.brushSize
    this.canvas.freeDrawingBrush.color = this.currentColor

    // Handle canvas events
    this.canvas.on("path:created", () => {
      this.saveState()
    })

    this.canvas.on("object:added", () => {
      if (!this.isLoadingState) {
        this.saveState()
      }
    })

    // Resize canvas on window resize
    window.addEventListener("resize", () => {
      this.resizeCanvas()
    })

    this.resizeCanvas()
  }

  setupEventListeners() {
    // Toolbar buttons
    document.getElementById("clear-btn").addEventListener("click", () => {
      this.clearCanvas()
    })

    document.getElementById("undo-btn").addEventListener("click", () => {
      this.undo()
    })

    document.getElementById("redo-btn").addEventListener("click", () => {
      this.redo()
    })

    document.getElementById("save-btn").addEventListener("click", () => {
      this.saveDrawing()
    })

    // Color palette
    document.querySelectorAll(".color-swatch").forEach((swatch, index) => {
      swatch.addEventListener("click", () => {
        this.setColor(swatch.dataset.color, index)
      })
    })

    // Brush size
    const brushSizeSlider = document.getElementById("brush-size")
    const brushSizeValue = document.getElementById("brush-size-value")

    brushSizeSlider.addEventListener("input", (e) => {
      this.setBrushSize(Number.parseInt(e.target.value))
      brushSizeValue.textContent = e.target.value
    })

    // Zoom controls
    document.getElementById("zoom-in-btn").addEventListener("click", () => {
      this.zoomIn()
    })

    document.getElementById("zoom-out-btn").addEventListener("click", () => {
      this.zoomOut()
    })
  }

  resizeCanvas() {
    const container = document.getElementById("canvas-container")
    const rect = container.getBoundingClientRect()

    this.canvas.setDimensions({
      width: rect.width,
      height: rect.height,
    })

    this.canvas.renderAll()
  }

  // Drawing mode controls
  startDrawing() {
    if (!this.isDrawingMode) {
      this.isDrawingMode = true
      this.canvas.isDrawingMode = true
      this.updateDrawingModeDisplay("Drawing")

      // Disable other modes
      this.isErasingMode = false
      this.isPanningMode = false
      this.shapeMode = false
    }
  }

  stopDrawing() {
    if (this.isDrawingMode) {
      this.isDrawingMode = false
      this.canvas.isDrawingMode = false
      this.updateDrawingModeDisplay("Idle")
    }
  }

  startErasing() {
    this.isErasingMode = true
    this.isDrawingMode = false
    this.isPanningMode = false
    this.shapeMode = false

    this.canvas.isDrawingMode = false
    this.updateDrawingModeDisplay("Erasing")

    // Enable object selection for erasing
    this.canvas.selection = true
    this.canvas.forEachObject((obj) => {
      obj.selectable = true
    })
  }

  stopErasing() {
    this.isErasingMode = false
    this.canvas.selection = false
    this.canvas.forEachObject((obj) => {
      obj.selectable = false
    })
    this.updateDrawingModeDisplay("Idle")
  }

  startPanning() {
    this.isPanningMode = true
    this.isDrawingMode = false
    this.isErasingMode = false
    this.shapeMode = false

    this.canvas.isDrawingMode = false
    this.updateDrawingModeDisplay("Panning")

    // Enable canvas panning
    this.canvas.selection = false
    this.canvas.defaultCursor = "move"
  }

  stopPanning() {
    this.isPanningMode = false
    this.canvas.defaultCursor = "default"
    this.updateDrawingModeDisplay("Idle")
  }

  // Color management
  changeColor() {
    this.currentColorIndex = (this.currentColorIndex + 1) % this.colorPalette.length
    const newColor = this.colorPalette[this.currentColorIndex]
    this.setColor(newColor, this.currentColorIndex)
  }

  setColor(color, index) {
    this.currentColor = color
    this.currentColorIndex = index

    // Update brush color
    this.canvas.freeDrawingBrush.color = color

    // Update UI
    document.querySelectorAll(".color-swatch").forEach((swatch) => {
      swatch.classList.remove("active")
    })

    const activeSwatch = document.querySelector(`[data-color="${color}"]`)
    if (activeSwatch) {
      activeSwatch.classList.add("active")
    }
  }

  setBrushSize(size) {
    this.brushSize = size
    this.canvas.freeDrawingBrush.width = size
  }

  // Zoom controls
  zoomIn() {
    this.zoomLevel = Math.min(this.zoomLevel * 1.2, 5)
    this.canvas.setZoom(this.zoomLevel)
    this.updateZoomDisplay()
  }

  zoomOut() {
    this.zoomLevel = Math.max(this.zoomLevel / 1.2, 0.2)
    this.canvas.setZoom(this.zoomLevel)
    this.updateZoomDisplay()
  }

  updateZoomDisplay() {
    const zoomElement = document.getElementById("zoom-level")
    if (zoomElement) {
      zoomElement.textContent = `${Math.round(this.zoomLevel * 100)}%`
    }
  }

  // Shape drawing
  toggleShapeMode() {
    this.shapeMode = !this.shapeMode

    if (this.shapeMode) {
      this.isDrawingMode = false
      this.isErasingMode = false
      this.isPanningMode = false
      this.canvas.isDrawingMode = false
      this.updateDrawingModeDisplay("Shape Drawing")

      // Enable shape drawing
      this.enableShapeDrawing()
    } else {
      this.disableShapeDrawing()
      this.updateDrawingModeDisplay("Idle")
    }
  }

  enableShapeDrawing() {
    let isDrawing = false
    let startX, startY
    let shape

    this.canvas.on("mouse:down", (e) => {
      if (!this.shapeMode) return

      isDrawing = true
      const pointer = this.canvas.getPointer(e.e)
      startX = pointer.x
      startY = pointer.y

      // Create shape based on current shape type
      if (this.currentShape === "rectangle") {
        shape = new fabric.Rect({
          left: startX,
          top: startY,
          width: 0,
          height: 0,
          fill: "transparent",
          stroke: this.currentColor,
          strokeWidth: this.brushSize,
        })
      } else if (this.currentShape === "circle") {
        shape = new fabric.Circle({
          left: startX,
          top: startY,
          radius: 0,
          fill: "transparent",
          stroke: this.currentColor,
          strokeWidth: this.brushSize,
        })
      }

      this.canvas.add(shape)
    })

    this.canvas.on("mouse:move", (e) => {
      if (!isDrawing || !this.shapeMode) return

      const pointer = this.canvas.getPointer(e.e)

      if (this.currentShape === "rectangle") {
        shape.set({
          width: Math.abs(pointer.x - startX),
          height: Math.abs(pointer.y - startY),
        })
      } else if (this.currentShape === "circle") {
        const radius = Math.sqrt(Math.pow(pointer.x - startX, 2) + Math.pow(pointer.y - startY, 2)) / 2
        shape.set({ radius: radius })
      }

      this.canvas.renderAll()
    })

    this.canvas.on("mouse:up", () => {
      isDrawing = false
      this.saveState()
    })
  }

  disableShapeDrawing() {
    this.canvas.off("mouse:down")
    this.canvas.off("mouse:move")
    this.canvas.off("mouse:up")
  }

  // History management
  saveState() {
    if (this.isLoadingState) return

    const state = JSON.stringify(this.canvas.toJSON())

    // Remove future history if we're not at the end
    if (this.historyIndex < this.history.length - 1) {
      this.history = this.history.slice(0, this.historyIndex + 1)
    }

    this.history.push(state)
    this.historyIndex++

    // Limit history size
    if (this.history.length > this.maxHistorySize) {
      this.history.shift()
      this.historyIndex--
    }
  }

  undo() {
    if (this.historyIndex > 0) {
      this.historyIndex--
      this.loadState(this.history[this.historyIndex])
    }
  }

  redo() {
    if (this.historyIndex < this.history.length - 1) {
      this.historyIndex++
      this.loadState(this.history[this.historyIndex])
    }
  }

  loadState(state) {
    this.isLoadingState = true
    this.canvas.loadFromJSON(state, () => {
      this.canvas.renderAll()
      this.isLoadingState = false
    })
  }

  // Canvas operations
  clearCanvas() {
    this.canvas.clear()
    this.canvas.backgroundColor = "white"
    this.saveState()
  }

  async saveDrawing() {
    try {
      const dataURL = this.canvas.toDataURL({
        format: "png",
        quality: 1.0,
      })

      const timestamp = new Date().toISOString().replace(/[:.]/g, "-")
      const filename = `whiteboard-${timestamp}.png`

      const response = await fetch("/api/save-drawing", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          image_data: dataURL,
          filename: filename,
        }),
      })

      const result = await response.json()

      if (result.success) {
        this.showNotification("Drawing saved successfully!", "success")
      } else {
        this.showNotification("Failed to save drawing", "error")
      }
    } catch (error) {
      console.error("Error saving drawing:", error)
      this.showNotification("Error saving drawing", "error")
    }
  }

  // UI helpers
  updateDrawingModeDisplay(mode) {
    const modeElement = document.getElementById("drawing-mode")
    if (modeElement) {
      modeElement.textContent = `Mode: ${mode}`
    }

    // Update canvas cursor
    const canvasContainer = document.getElementById("canvas-container")
    canvasContainer.className = ""

    if (mode === "Drawing") {
      canvasContainer.classList.add("drawing-active")
    } else if (mode === "Erasing") {
      canvasContainer.classList.add("erasing-active")
    } else if (mode === "Panning") {
      canvasContainer.classList.add("panning-active")
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
            right: 20px;
            padding: 15px 20px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `

    if (type === "success") {
      notification.style.backgroundColor = "#27ae60"
    } else if (type === "error") {
      notification.style.backgroundColor = "#e74c3c"
    } else {
      notification.style.backgroundColor = "#3498db"
    }

    document.body.appendChild(notification)

    // Remove after 3 seconds
    setTimeout(() => {
      notification.style.animation = "slideOut 0.3s ease"
      setTimeout(() => {
        document.body.removeChild(notification)
      }, 300)
    }, 3000)
  }

  // Gesture-triggered actions
  handleGesture(gestureClass, confidence) {
    switch (gestureClass) {
      case "write_start":
        this.startDrawing()
        break

      case "write_stop":
        this.stopDrawing()
        break

      case "change_color":
        this.changeColor()
        break

      case "zoom_in":
        this.zoomIn()
        break

      case "erase":
        this.startErasing()
        break

      case "zoom_out":
        this.zoomOut()
        break

      case "undo":
        this.undo()
        break

      case "redo":
        this.redo()
        break

      case "draw_shapes":
        this.toggleShapeMode()
        break

      case "save":
        this.saveDrawing()
        break

      case "pan":
        this.startPanning()
        break

      case "clear_all":
        this.clearCanvas()
        break
    }
  }
}

// Export for use in other modules
window.Whiteboard = Whiteboard
