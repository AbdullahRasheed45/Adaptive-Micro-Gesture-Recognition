// Socket.IO connection
const io = window.io // Declare the io variable
const socket = io()

// Canvas and drawing variables
let canvas, ctx
let isDrawing = false
let drawingMode = false
let erasingMode = false
let currentColor = "#FF0000"
let currentShape = "rectangle"
let zoomLevel = 1.0
let fingerPosition = null

// History for undo/redo
const canvasHistory = []
let historyIndex = -1

// Camera state
let cameraActive = false

// Initialize the application
document.addEventListener("DOMContentLoaded", () => {
  initializeCanvas()
  setupEventListeners()
  updateUI()
})

function initializeCanvas() {
  canvas = document.getElementById("whiteboard")
  ctx = canvas.getContext("2d")

  // Set canvas properties
  ctx.lineCap = "round"
  ctx.lineJoin = "round"
  ctx.lineWidth = 5
  ctx.strokeStyle = currentColor

  // Clear canvas with white background
  ctx.fillStyle = "white"
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  // Save initial state
  saveCanvasState()
}

function setupEventListeners() {
  // Camera toggle
  document.getElementById("cameraToggle").addEventListener("click", toggleCamera)

  // Socket event listeners
  socket.on("connect", handleConnect)
  socket.on("disconnect", handleDisconnect)
  socket.on("video_frame", handleVideoFrame)
  socket.on("gesture_detected", handleGestureDetected)
  socket.on("camera_status", handleCameraStatus)
  socket.on("color_changed", handleColorChanged)
  socket.on("shape_changed", handleShapeChanged)
  socket.on("zoom_changed", handleZoomChanged)
  socket.on("status", handleStatus)
}

// Socket event handlers
function handleConnect() {
  updateConnectionStatus(true)
  showStatusMessage("Connected to gesture whiteboard", "success")
}

function handleDisconnect() {
  updateConnectionStatus(false)
  showStatusMessage("Disconnected from server", "error")
}

function handleVideoFrame(data) {
  const videoFeed = document.getElementById("videoFeed")
  const videoOverlay = document.getElementById("videoOverlay")

  if (data.frame) {
    videoFeed.src = "data:image/jpeg;base64," + data.frame
    videoOverlay.classList.add("hidden")
  }

  // Update finger position for drawing
  if (data.finger_position && drawingMode) {
    fingerPosition = data.finger_position
    handleFingerDrawing()
  }

  // Update gesture display
  if (data.current_gesture) {
    document.getElementById("currentGesture").textContent = data.current_gesture.replace("_", " ").toUpperCase()
    document.getElementById("gestureConfidence").textContent = Math.round(data.confidence * 100) + "%"
  }
}

function handleGestureDetected(data) {
  const gesture = data.gesture
  const confidence = data.confidence

  console.log(`Gesture detected: ${gesture} (${Math.round(confidence * 100)}%)`)

  // Handle different gestures
  switch (gesture) {
    case "write_start":
      startDrawing()
      break
    case "write_stop":
      stopDrawing()
      break
    case "erase":
      toggleErasing()
      break
    case "zoom_in":
      zoomIn()
      break
    case "zoom_out":
      zoomOut()
      break
    case "draw_shapes":
      drawShape()
      break
    case "undo":
      undoAction()
      break
    case "redo":
      redoAction()
      break
    case "change_color":
      changeColor()
      break
    case "save":
      saveCanvas()
      break
    case "clear_all":
      clearCanvas()
      break
  }

  showStatusMessage(`Gesture: ${gesture.replace("_", " ")}`, "success")
}

function handleCameraStatus(data) {
  cameraActive = data.active
  updateCameraUI()
}

function handleColorChanged(data) {
  currentColor = data.color
  updateColorDisplay()
}

function handleShapeChanged(data) {
  currentShape = data.shape
  updateShapeDisplay()
}

function handleZoomChanged(data) {
  zoomLevel = data.zoom
  updateZoomDisplay()
  applyZoom()
}

function handleStatus(data) {
  showStatusMessage(data.message, "info")
}

// Camera functions
function toggleCamera() {
  if (cameraActive) {
    socket.emit("stop_camera")
  } else {
    socket.emit("start_camera")
  }
}

function updateCameraUI() {
  const toggleBtn = document.getElementById("cameraToggle")
  const statusDiv = document.getElementById("cameraStatus")
  const videoOverlay = document.getElementById("videoOverlay")

  if (cameraActive) {
    toggleBtn.textContent = "Stop Camera"
    toggleBtn.classList.remove("btn-primary")
    toggleBtn.classList.add("btn-danger")
    statusDiv.textContent = "Camera On"
    statusDiv.classList.add("active")
  } else {
    toggleBtn.textContent = "Start Camera"
    toggleBtn.classList.remove("btn-danger")
    toggleBtn.classList.add("btn-primary")
    statusDiv.textContent = "Camera Off"
    statusDiv.classList.remove("active")
    videoOverlay.classList.remove("hidden")
  }
}

// Drawing functions
function startDrawing() {
  drawingMode = true
  erasingMode = false
  updateDrawingModeDisplay()
  showStatusMessage("Drawing mode activated", "success")
}

function stopDrawing() {
  drawingMode = false
  isDrawing = false
  updateDrawingModeDisplay()
  showStatusMessage("Drawing mode deactivated", "info")
}

function toggleErasing() {
  erasingMode = !erasingMode
  if (erasingMode) {
    ctx.globalCompositeOperation = "destination-out"
    showStatusMessage("Eraser mode activated", "success")
  } else {
    ctx.globalCompositeOperation = "source-over"
    showStatusMessage("Drawing mode activated", "success")
  }
}

function handleFingerDrawing() {
  if (!fingerPosition || !drawingMode) return

  const rect = canvas.getBoundingClientRect()
  const x = fingerPosition.x * canvas.width
  const y = fingerPosition.y * canvas.height

  if (!isDrawing) {
    isDrawing = true
    ctx.beginPath()
    ctx.moveTo(x, y)
  } else {
    ctx.lineTo(x, y)
    ctx.stroke()
  }
}

function drawShape() {
  if (!fingerPosition) return

  const x = fingerPosition.x * canvas.width
  const y = fingerPosition.y * canvas.height
  const size = 50

  ctx.save()
  ctx.globalCompositeOperation = "source-over"
  ctx.fillStyle = currentColor

  switch (currentShape) {
    case "rectangle":
      ctx.fillRect(x - size / 2, y - size / 2, size, size)
      break
    case "circle":
      ctx.beginPath()
      ctx.arc(x, y, size / 2, 0, 2 * Math.PI)
      ctx.fill()
      break
    case "triangle":
      ctx.beginPath()
      ctx.moveTo(x, y - size / 2)
      ctx.lineTo(x - size / 2, y + size / 2)
      ctx.lineTo(x + size / 2, y + size / 2)
      ctx.closePath()
      ctx.fill()
      break
    case "line":
      ctx.beginPath()
      ctx.moveTo(x - size / 2, y)
      ctx.lineTo(x + size / 2, y)
      ctx.stroke()
      break
  }

  ctx.restore()
  saveCanvasState()
  showStatusMessage(`Drew ${currentShape}`, "success")
}

// Canvas history functions
function saveCanvasState() {
  historyIndex++
  if (historyIndex < canvasHistory.length) {
    canvasHistory.length = historyIndex
  }
  canvasHistory.push(canvas.toDataURL())
}

function undoAction() {
  if (historyIndex > 0) {
    historyIndex--
    restoreCanvasState()
    showStatusMessage("Undo performed", "info")
  }
}

function redoAction() {
  if (historyIndex < canvasHistory.length - 1) {
    historyIndex++
    restoreCanvasState()
    showStatusMessage("Redo performed", "info")
  }
}

function restoreCanvasState() {
  const img = new Image()
  img.onload = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    ctx.drawImage(img, 0, 0)
  }
  img.src = canvasHistory[historyIndex]
}

function clearCanvas() {
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  ctx.fillStyle = "white"
  ctx.fillRect(0, 0, canvas.width, canvas.height)
  saveCanvasState()
  showStatusMessage("Canvas cleared", "info")
}

function saveCanvas() {
  const link = document.createElement("a")
  link.download = `whiteboard_${new Date().toISOString().slice(0, 19).replace(/:/g, "-")}.png`
  link.href = canvas.toDataURL()
  link.click()
  showStatusMessage("Canvas saved", "success")
}

// Control functions
function changeColor() {
  socket.emit("whiteboard_action", { action: "change_color" })
}

function changeShape() {
  socket.emit("whiteboard_action", { action: "change_shape" })
}

function zoomIn() {
  socket.emit("whiteboard_action", { action: "zoom_in" })
}

function zoomOut() {
  socket.emit("whiteboard_action", { action: "zoom_out" })
}

function applyZoom() {
  canvas.style.transform = `scale(${zoomLevel})`
  canvas.style.transformOrigin = "top left"
}

// UI update functions
function updateConnectionStatus(connected) {
  const indicator = document.getElementById("statusIndicator")
  const dot = indicator.querySelector(".status-dot")
  const text = indicator.querySelector(".status-text")

  if (connected) {
    dot.classList.add("connected")
    text.textContent = "Connected"
  } else {
    dot.classList.remove("connected")
    text.textContent = "Disconnected"
  }
}

function updateDrawingModeDisplay() {
  const modeDisplay = document.getElementById("drawingMode")
  if (drawingMode) {
    modeDisplay.textContent = erasingMode ? "Erasing Mode: On" : "Drawing Mode: On"
    modeDisplay.classList.add("active")
  } else {
    modeDisplay.textContent = "Drawing Mode: Off"
    modeDisplay.classList.remove("active")
  }
}

function updateColorDisplay() {
  document.getElementById("currentColor").style.backgroundColor = currentColor
  ctx.strokeStyle = currentColor
  ctx.fillStyle = currentColor
}

function updateShapeDisplay() {
  document.getElementById("currentShape").textContent = currentShape
}

function updateZoomDisplay() {
  document.getElementById("currentZoom").textContent = Math.round(zoomLevel * 100) + "%"
}

function updateUI() {
  updateColorDisplay()
  updateShapeDisplay()
  updateZoomDisplay()
  updateDrawingModeDisplay()
}

function showStatusMessage(message, type = "info") {
  const container = document.getElementById("statusMessages")
  const messageDiv = document.createElement("div")
  messageDiv.className = `status-message ${type}`
  messageDiv.textContent = message

  container.appendChild(messageDiv)

  setTimeout(() => {
    messageDiv.remove()
  }, 3000)
}

// Add CSS for button danger class
const style = document.createElement("style")
style.textContent = `
    .btn-danger {
        background: #ef4444;
        color: white;
    }
    .btn-danger:hover {
        background: #dc2626;
    }
`
document.head.appendChild(style)
