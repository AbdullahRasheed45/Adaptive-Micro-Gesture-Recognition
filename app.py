from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import base64
from datetime import datetime
import json

app = Flask(__name__)

# Configure upload folder for saved drawings
UPLOAD_FOLDER = 'saved_drawings'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    """Serve the main whiteboard application"""
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

@app.route('/api/save-drawing', methods=['POST'])
def save_drawing():
    """Save drawing as image file"""
    try:
        data = request.json
        image_data = data.get('image_data')
        filename = data.get('filename', f'drawing_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        
        # Remove data URL prefix
        if image_data.startswith('data:image/png;base64,'):
            image_data = image_data.replace('data:image/png;base64,', '')
        
        # Decode and save
        image_bytes = base64.b64decode(image_data)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'message': 'Drawing saved successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/gesture-predict', methods=['POST'])
def gesture_predict():
    """Fallback API endpoint for gesture prediction if browser inference fails"""
    try:
        data = request.json
        landmarks_buffer = data.get('landmarks_buffer')
        
        # This would be where you'd run your TFLite model
        # For now, returning a mock response
        # In production, you'd load and run your actual model here
        
        mock_prediction = {
            'gesture_class': 0,
            'confidence': 0.85,
            'gesture_name': 'write_start',
            'probabilities': [0.85, 0.05, 0.03, 0.02, 0.01, 0.01, 0.01, 0.01, 0.01, 0.0, 0.0, 0.0]
        }
        
        return jsonify(mock_prediction)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/static/model.json')
def serve_model():
    """Serve the model JSON file"""
    return send_from_directory('static', 'model.json')

@app.route('/static/model.weights.bin')
def serve_weights():
    """Serve the model weights file"""
    return send_from_directory('static', 'model.weights.bin')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
