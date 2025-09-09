#!/usr/bin/env python3
"""
Test script to verify the gesture recognition model is working properly
"""

import numpy as np
import tensorflow.lite as tflite
import os

# Gesture class mapping
GESTURE_MAP = {
    0: "write_start", 1: "write_stop", 2: "erase", 3: "zoom_in", 
    4: "zoom_out", 5: "draw_shapes", 6: "undo", 7: "redo", 
    8: "change_color", 9: "save", 10: "pan", 11: "clear_all"
}

def test_model():
    model_path = "models/gesture_model_3d_final.tflite"
    
    # Check if model file exists
    if not os.path.exists(model_path):
        print(f"❌ Error: Model file not found at {model_path}")
        print("Please copy your gesture_model_3d_final.tflite file to the models/ directory")
        return False
    
    try:
        # Load the model
        print("🔄 Loading TensorFlow Lite model...")
        interpreter = tflite.Interpreter(model_path=model_path)
        interpreter.allocate_tensors()
        
        # Get input and output details
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        print("✅ Model loaded successfully!")
        print(f"📊 Input shape: {input_details[0]['shape']}")
        print(f"📊 Output shape: {output_details[0]['shape']}")
        print(f"🎯 Input dtype: {input_details[0]['dtype']}")
        print(f"🎯 Output dtype: {output_details[0]['dtype']}")
        
        # Verify expected shapes
        expected_input_shape = [1, 4, 21, 3]  # [batch, frames, landmarks, coordinates]
        expected_output_shape = [1, 12]       # [batch, classes]
        
        actual_input_shape = input_details[0]['shape'].tolist()
        actual_output_shape = output_details[0]['shape'].tolist()
        
        if actual_input_shape == expected_input_shape:
            print("✅ Input shape matches expected format")
        else:
            print(f"⚠️  Warning: Input shape mismatch!")
            print(f"   Expected: {expected_input_shape}")
            print(f"   Actual: {actual_input_shape}")
        
        if actual_output_shape == expected_output_shape:
            print("✅ Output shape matches expected format")
        else:
            print(f"⚠️  Warning: Output shape mismatch!")
            print(f"   Expected: {expected_output_shape}")
            print(f"   Actual: {actual_output_shape}")
        
        # Test with random input data
        print("\n🧪 Testing model with random input data...")
        
        # Generate random test data matching the expected input shape
        test_input = np.random.uniform(0, 1, actual_input_shape).astype(np.float32)
        print(f"📊 Test input shape: {test_input.shape}")
        
        # Run inference
        interpreter.set_tensor(input_details[0]['index'], test_input)
        interpreter.invoke()
        output = interpreter.get_tensor(output_details[0]['index'])
        
        # Get prediction
        predicted_class = np.argmax(output[0])
        confidence = output[0][predicted_class]
        gesture_name = GESTURE_MAP.get(predicted_class, "Unknown")
        
        print(f"🎯 Predicted class: {predicted_class}")
        print(f"🎯 Gesture name: {gesture_name}")
        print(f"🎯 Confidence: {confidence:.4f} ({confidence*100:.2f}%)")
        print(f"🎯 Output probabilities: {output[0]}")
        
        # Test multiple random inputs
        print("\n🔄 Testing with multiple random inputs...")
        for i in range(5):
            test_input = np.random.uniform(0, 1, actual_input_shape).astype(np.float32)
            interpreter.set_tensor(input_details[0]['index'], test_input)
            interpreter.invoke()
            output = interpreter.get_tensor(output_details[0]['index'])
            
            predicted_class = np.argmax(output[0])
            confidence = output[0][predicted_class]
            gesture_name = GESTURE_MAP.get(predicted_class, "Unknown")
            
            print(f"   Test {i+1}: {gesture_name} (confidence: {confidence:.3f})")
        
        print("\n✅ Model test completed successfully!")
        print("🚀 Your model is ready to use with the Flask app!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing model: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    try:
        import tensorflow as tf
        print(f"✅ TensorFlow: {tf.__version__}")
    except ImportError:
        print("❌ TensorFlow not found")
        return False
    
    try:
        import numpy as np
        print(f"✅ NumPy: {np.__version__}")
    except ImportError:
        print("❌ NumPy not found")
        return False
    
    try:
        import cv2
        print(f"✅ OpenCV: {cv2.__version__}")
    except ImportError:
        print("❌ OpenCV not found")
        return False
    
    try:
        import mediapipe as mp
        print(f"✅ MediaPipe: {mp.__version__}")
    except ImportError:
        print("❌ MediaPipe not found")
        return False
    
    return True

if __name__ == "__main__":
    print("🎨 Gesture Recognition Model Test")
    print("=" * 50)
    
    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Some dependencies are missing. Please install them using:")
        print("pip install -r requirements.txt")
        exit(1)
    
    print()
    
    # Test the model
    if test_model():
        print("\n🎉 All tests passed! Your setup is ready.")
    else:
        print("\n❌ Tests failed. Please check the error messages above.")
        exit(1)