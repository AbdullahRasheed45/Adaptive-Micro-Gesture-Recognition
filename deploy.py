#!/usr/bin/env python3
"""
Deployment script for Gesture-Controlled Whiteboard
Handles setup, validation, and deployment tasks
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

class WhiteboardDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.required_dirs = [
            'templates',
            'static/js',
            'static/models',
            'static/uploads'
        ]
        self.required_files = [
            'app.py',
            'requirements.txt',
            'templates/index.html',
            'static/js/whiteboard.js',
            'static/js/model-loader.js'
        ]
        
    def setup_directories(self):
        """Create required directory structure"""
        print("📁 Setting up directory structure...")
        
        for directory in self.required_dirs:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ Created: {directory}")
            
    def validate_files(self):
        """Validate that all required files exist"""
        print("\n🔍 Validating project files...")
        
        missing_files = []
        for file_path in self.required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"  ✓ Found: {file_path}")
            else:
                print(f"  ✗ Missing: {file_path}")
                missing_files.append(file_path)
                
        if missing_files:
            print(f"\n❌ Missing {len(missing_files)} required files!")
            print("Please ensure all files are in the correct locations.")
            return False
            
        return True
        
    def check_model(self):
        """Check if the ML model is present"""
        print("\n🧠 Checking ML model...")
        
        model_path = self.project_root / 'static/models/gesture_model.tflite'
        if model_path.exists():
            model_size = model_path.stat().st_size / (1024 * 1024)  # MB
            print(f"  ✓ Model found: {model_size:.2f} MB")
            return True
        else:
            print("  ⚠️  Model not found: static/models/gesture_model.tflite")
            print("     The application will run in backend-only mode.")
            print("     Place your trained .tflite model in static/models/")
            return False
            
    def install_dependencies(self):
        """Install Python dependencies"""
        print("\n📦 Installing dependencies...")
        
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ], check=True, cwd=self.project_root)
            print("  ✓ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Failed to install dependencies: {e}")
            return False
            
    def run_tests(self):
        """Run basic functionality tests"""
        print("\n🧪 Running basic tests...")
        
        try:
            # Test Flask app import
            sys.path.insert(0, str(self.project_root))
            import app
            print("  ✓ Flask app imports successfully")
            
            # Test model loading
            model_info = app.gesture_model.interpreter is not None
            print(f"  {'✓' if model_info else '⚠️'} Model loader: {'Working' if model_info else 'Backend only'}")
            
            return True
            
        except Exception as e:
            print(f"  ✗ Tests failed: {e}")
            return False
            
    def create_startup_script(self):
        """Create startup scripts for different platforms"""
        print("\n🚀 Creating startup scripts...")
        
        # Unix/Linux/macOS startup script
        unix_script = self.project_root / 'start.sh'
        with open(unix_script, 'w') as f:
            f.write("""#!/bin/bash
# Gesture-Controlled Whiteboard Startup Script

echo "🎨 Starting Gesture-Controlled Whiteboard..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
fi

# Start the Flask application
echo "🚀 Starting server on http://localhost:5000"
python app.py
""")
        unix_script.chmod(0o755)
        print("  ✓ Created: start.sh")
        
        # Windows startup script
        win_script = self.project_root / 'start.bat'
        with open(win_script, 'w') as f:
            f.write("""@echo off
REM Gesture-Controlled Whiteboard Startup Script

echo 🎨 Starting Gesture-Controlled Whiteboard...

REM Activate virtual environment if it exists
if exist venv\\Scripts\\activate.bat (
    call venv\\Scripts\\activate.bat
    echo ✓ Virtual environment activated
)

REM Start the Flask application
echo 🚀 Starting server on http://localhost:5000
python app.py
pause
""")
        print("  ✓ Created: start.bat")
        
    def create_docker_files(self):
        """Create Docker deployment files"""
        print("\n🐳 Creating Docker files...")
        
        # Dockerfile
        dockerfile = self.project_root / 'Dockerfile'
        with open(dockerfile, 'w') as f:
            f.write("""FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    libglib2.0-0 \\
    libsm6 \\
    libxext6 \\
    libxrender-dev \\
    libgomp1 \\
    libgtk-3-0 \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create uploads directory
RUN mkdir -p static/uploads

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:5000/api/health || exit 1

# Start application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "120", "app:app"]
""")
        print("  ✓ Created: Dockerfile")
        
        # Docker Compose
        compose_file = self.project_root / 'docker-compose.yml'
        with open(compose_file, 'w') as f:
            f.write("""version: '3.8'

services:
  whiteboard:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./static/uploads:/app/static/uploads
      - ./static/models:/app/static/models
    environment:
      - FLASK_ENV=production
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - whiteboard
    restart: unless-stopped
""")
        print("  ✓ Created: docker-compose.yml")
        
    def deploy(self):
        """Run complete deployment process"""
        print("🎨 Gesture-Controlled Whiteboard Deployment")
        print("=" * 50)
        
        success = True
        
        # Setup
        self.setup_directories()
        
        # Validation
        if not self.validate_files():
            return False
            
        # Check model
        self.check_model()
        
        # Install dependencies
        if not self.install_dependencies():
            success = False
            
        # Run tests
        if not self.run_tests():
            success = False
            
        # Create scripts
        self.create_startup_script()
        self.create_docker_files()
        
        print("\n" + "=" * 50)
        if success:
            print("✅ Deployment completed successfully!")
            print("\n🚀 To start the application:")
            print("   • Linux/macOS: ./start.sh")
            print("   • Windows: start.bat")
            print("   • Docker: docker-compose up")
            print("\n🌐 Access at: http://localhost:5000")
        else:
            print("❌ Deployment completed with warnings!")
            print("   The application may still work, but some features might be limited.")
            
        return success

def main():
    deployer = WhiteboardDeployer()
    deployer.deploy()

if __name__ == '__main__':
    main()