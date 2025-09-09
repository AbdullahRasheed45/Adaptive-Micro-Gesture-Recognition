#!/usr/bin/env python3
"""
Debug Flask Gesture Whiteboard Application Runner
"""

import os
import sys
import subprocess
import cv2

def test_camera():
    """Test if camera is working"""
    print("📹 Testing camera...")
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Camera not accessible")
            return False
        
        ret, frame = cap.read()
        if not ret:
            print("❌ Cannot read from camera")
            cap.release()
            return False
        
        print(f"✅ Camera working - Frame size: {frame.shape}")
        cap.release()
        return True
    except Exception as e:
        print(f"❌ Camera test error: {e}")
        return False

def install_requirements():
    """Install required packages"""
    try:
        print("📦 Installing requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def check_model_exists():
    """Check if the trained model exists"""
    model_path = "models/gesture_model_3d_final.tflite"
    if not os.path.exists(model_path):
        print(f"⚠️  Model not found at {model_path}")
        print("🔄 Application will use simple gesture detection as fallback")
        
        # Create models directory if it doesn't exist
        os.makedirs("models", exist_ok=True)
        print("📁 Created models/ directory")
        return False
    
    print("✅ Model found")
    return True

def create_directories():
    """Create necessary directories"""
    directories = ["models", "static/css", "static/js", "templates"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    print("📁 Created necessary directories")

def main():
    print("🚀 Starting Flask Gesture Whiteboard Application (Debug Mode)")
    print("=" * 70)
    
    # Create directories
    create_directories()
    
    # Test camera first
    if not test_camera():
        print("⚠️  Camera issues detected, but continuing...")
    
    # Check if model exists (not required for fallback mode)
    model_exists = check_model_exists()
    if not model_exists:
        print("🔄 Will use simple gesture detection (finger counting)")
    
    # Install requirements
    if not install_requirements():
        return
    
    print("\n🎨 Starting Flask Whiteboard Server...")
    print("📍 Access the whiteboard at: http://localhost:5000")
    print("📹 Make sure your camera is connected and working")
    print("🤚 Gesture Detection Methods:")
    if model_exists:
        print("   • ML Model (97% accuracy) - Primary")
        print("   • Simple Detection (finger counting) - Fallback")
    else:
        print("   • Simple Detection (finger counting) - Active")
    
    print("\n🤚 Simple Gestures Available:")
    print("   • Index finger only → Start Drawing")
    print("   • Index + Middle finger → Erase")
    print("   • Closed fist → Stop Drawing")
    print("   • Open hand (5 fingers) → Clear Canvas")
    print("   • Thumb + Index → Zoom In")
    print("   • Thumb + Pinky → Zoom Out")
    print("   • Three middle fingers → Undo")
    print("   • Thumb + Index + Middle → Change Color")
    
    print("\nPress Ctrl+C to stop the server")
    print("=" * 70)
    
    # Start the Flask application
    try:
        from app import app, socketio
        socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()
