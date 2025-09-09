import os
import shutil
from pathlib import Path

def setup_model_directory():
    """Create models directory and copy the model file"""
    
    # Create models directory if it doesn't exist
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # Instructions for the user
    print("Model Setup Instructions:")
    print("=" * 50)
    print("1. Copy your trained model file 'gesture_model_3d_final.tflite' to the 'models' directory")
    print("2. Make sure the model file path is: models/gesture_model_3d_final.tflite")
    print("3. If you don't have the model file, you'll need to train it first using your training script")
    print("\nModel directory created at:", models_dir.absolute())
    
    # Check if model exists
    model_path = models_dir / "gesture_model_3d_final.tflite"
    if model_path.exists():
        print(f"✅ Model found at: {model_path}")
    else:
        print(f"❌ Model not found. Please copy your model to: {model_path}")
        
        # Create a placeholder file with instructions
        with open(model_path.with_suffix('.txt'), 'w') as f:
            f.write("Place your gesture_model_3d_final.tflite file here\n")
            f.write("The model should be trained using your training script\n")
            f.write("Expected input shape: [1, 4, 21, 3]\n")
            f.write("Expected output shape: [1, 12]\n")

if __name__ == "__main__":
    setup_model_directory()
