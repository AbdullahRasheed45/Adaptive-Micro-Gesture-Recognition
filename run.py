#!/usr/bin/env python3
"""
Flask Gesture Whiteboard Application Runner
"""

import os
import sys
import subprocess

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
        print(f"❌ Model not found at {model_path}")
        print("Please ensure your trained model is placed in the models/ directory")
        
        # Create models directory if it doesn't exist
        os.makedirs("models", exist_ok=True)
        print("📁 Created models/ directory")
        print("Please place your gesture_model_3d_final.tflite file in the models/ directory")
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
    print("🚀 Starting Flask Gesture Whiteboard Application...")
    print("=" * 60)
    
    # Create directories
    create_directories()
    
    # Check if model exists
    if not check_model_exists():
        print("\n⚠️  Please add your trained model before running the application")
        return
    
    # Install requirements
    if not install_requirements():
        return
    
    print("\n🎨 Starting Flask Whiteboard Server...")
    print("📍 Access the whiteboard at: http://localhost:5000")
    print("📹 Make sure your camera is connected")
    print("🤚 Perform gestures in front of the camera to control the whiteboard")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    # Start the Flask application
    try:
        from app import app, socketio
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()
