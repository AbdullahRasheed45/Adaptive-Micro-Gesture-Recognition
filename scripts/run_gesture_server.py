#!/usr/bin/env python3
"""
Gesture Recognition Server Runner
Run this script to start the gesture recognition backend
"""

import sys
import os
import subprocess

def install_requirements():
    """Install required packages"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False
    return True

def check_model_exists():
    """Check if the trained model exists"""
    model_path = "models/gesture_model_3d_final.tflite"
    if not os.path.exists(model_path):
        print(f"❌ Model not found at {model_path}")
        print("Please ensure your trained model is placed in the models/ directory")
        return False
    print("✅ Model found")
    return True

def main():
    print("🚀 Starting Gesture Recognition Server...")
    
    # Check if model exists
    if not check_model_exists():
        return
    
    # Install requirements
    if not install_requirements():
        return
    
    # Start the server
    try:
        from gesture_backend import main as start_server
        import asyncio
        asyncio.run(start_server())
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()
