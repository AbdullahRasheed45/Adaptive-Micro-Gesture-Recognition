#!/usr/bin/env python3
"""
TensorFlow Lite to TensorFlow.js Model Converter

This script helps convert your .tflite model to TensorFlow.js format
so it can be used in the browser-based gesture recognition system.
"""

import os
import sys
import subprocess
import argparse

def check_tensorflowjs_installed():
    """Check if tensorflowjs is installed"""
    try:
        result = subprocess.run(['tensorflowjs_converter', '--help'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_tensorflowjs():
    """Install tensorflowjs converter"""
    print("Installing tensorflowjs...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'tensorflowjs'], 
                      check=True)
        print("✅ tensorflowjs installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install tensorflowjs")
        return False

def convert_tflite_to_tfjs(input_path, output_dir):
    """Convert .tflite model to TensorFlow.js format"""
    
    if not os.path.exists(input_path):
        print(f"❌ Input file not found: {input_path}")
        return False
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Created output directory: {output_dir}")
    
    print(f"🔄 Converting {input_path} to TensorFlow.js format...")
    
    try:
        # Convert .tflite to TensorFlow.js
        cmd = [
            'tensorflowjs_converter',
            '--input_format=tf_lite',
            '--output_format=tfjs_graph_model',
            input_path,
            output_dir
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        print("✅ Conversion successful!")
        print(f"📁 Output files saved to: {output_dir}")
        
        # List generated files
        files = os.listdir(output_dir)
        print("\n📋 Generated files:")
        for file in files:
            print(f"  - {file}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Conversion failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Convert TFLite model to TensorFlow.js')
    parser.add_argument('input', help='Path to input .tflite file')
    parser.add_argument('--output', '-o', default='./static/', 
                       help='Output directory (default: ./static/)')
    
    args = parser.parse_args()
    
    print("🚀 TensorFlow Lite to TensorFlow.js Converter")
    print("=" * 50)
    
    # Check if tensorflowjs is installed
    if not check_tensorflowjs_installed():
        print("⚠️  tensorflowjs not found. Installing...")
        if not install_tensorflowjs():
            print("❌ Please install tensorflowjs manually:")
            print("   pip install tensorflowjs")
            return 1
    
    # Convert the model
    success = convert_tflite_to_tfjs(args.input, args.output)
    
    if success:
        print("\n🎉 Conversion completed successfully!")
        print("\n📋 Next steps:")
        print("1. The converted model files are in the static/ directory")
        print("2. Restart your Flask application")
        print("3. The app will automatically detect and load the converted model")
        print("\n💡 The main model file should be 'model.json'")
        return 0
    else:
        print("\n❌ Conversion failed. Please check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
