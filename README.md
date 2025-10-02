# Adaptive Micro-Gesture Recognition for Accessibility
## AI System for Motor-Impaired Users Using 3D CNNs

<div align="center">

![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=TensorFlow&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/opencv-%23white.svg?style=for-the-badge&logo=opencv&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

[![Research Paper](https://img.shields.io/badge/Research-Paper-red?style=for-the-badge&logo=adobeacrobatreader)](https://drive.google.com/file/d/1txAz5fShMmEUoBP0YLINVLcLyi-aDI2s/view?usp=sharing)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://choosealicense.com/licenses/mit/)
[![Accuracy](https://img.shields.io/badge/Accuracy-94.6%25-brightgreen?style=for-the-badge)]()
[![F1 Score](https://img.shields.io/badge/F1--Score-94.5%25-brightgreen?style=for-the-badge)]()

**Master's Thesis Research Project** | Anglia Ruskin University (2022)

</div>

---

> A research prototype that recognizes subtle hand movements and converts them into computer commands, designed to enhance accessibility for individuals with motor impairments through 3D Convolutional Neural Network technology.

## Overview

This system implements an adaptive micro-gesture recognition approach designed to enhance computer accessibility for users with motor impairments. Unlike traditional gesture recognition systems that focus on large movements, this research detects subtle hand and finger movements with minimal amplitude, enabling individuals with limited mobility to interact with digital systems.

**Research Context:** MSc Data Science thesis supervised by Prof. Man Fai Leung at Anglia Ruskin University's School of Computing and Information Science.

---

## Key Features

### 3D CNN Architecture
- **Spatio-temporal Deep Learning:** Custom 3D Convolutional Neural Network processes sequences of 8 frames
- **Lightweight Deployment:** 1.2MB TensorFlow Lite model using 8-bit quantization

### Micro-Gesture Support
The system recognizes 10 gesture classes designed for users with limited motor control:

| Gesture | Function | Accessibility Design |
|---------|----------|---------------------|
| Palm (Open) | Stop/Neutral | Natural resting position |
| Fist (Closed) | Draw/Select | Minimal finger movement |
| Point (Index) | Tool Selection | Single finger extension |
| OK Sign | Confirm/Erase | Reduced fine motor demands |
| Thumbs Up | Undo Action | Gross motor movement |
| Thumbs Down | Redo Action | Intuitive mapping |
| Victory/Peace | Mode Switch | Binary state control |
| Swipe Left/Right | Navigation | Micro-movement detection |
| Pinch | Zoom/Resize | Adaptive thresholds |

### Adaptive Interface
- **Cross-platform:** Web client (Fabric.js) and Desktop application (OpenCV)
- **Personalized Calibration:** Adjustable gesture thresholds for varying motor abilities
- **Drawing Tools:** Canvas interaction, shapes, undo/redo, zoom/pan, color selection

---

## Research Performance

### Overall Metrics
```
Overall Accuracy:     94.6%
F1-Score:            94.5%
Precision:           94.9%
Recall:              94.6%
Cross-dataset Test:  92.0%
Inference Speed:     >20 FPS (40ms latency)
Model Size:          1.2MB
```

### Per-Class Results (Test Set)
| Gesture Class | Precision | Recall | F1-Score |
|---------------|-----------|---------|----------|
| Palm | 95.2% | 96.7% | 95.9% |
| Fist | 97.1% | 94.3% | 95.7% |
| Point | 93.5% | 91.0% | 92.2% |
| OK Sign | 94.4% | 93.7% | 94.0% |
| Thumbs Up | 98.0% | 97.5% | 97.7% |
| Thumbs Down | 98.3% | 96.1% | 97.2% |
| Victory | 92.0% | 90.2% | 91.1% |

### Comparison with Baseline Models
| Model | Accuracy | Inference Time |
|-------|----------|----------------|
| **3D CNN (This Research)** | **94.6%** | **40ms** |
| 2D CNN + LSTM | 87.3% | 125ms |
| MediaPipe + MLP | 82.1% | 15ms |
| 2D CNN (Single Frame) | 78.9% | 12ms |

---

## Technical Architecture

### 3D CNN Model Design

```python
Input: 8-frame sequences (64×64×3×8 tensor)
    ↓
Conv3D Layer 1 (32 filters, kernel 3×3×3)
    + BatchNormalization + ReLU
    ↓
MaxPooling3D (2×2×2)
    ↓
Conv3D Layer 2 (64 filters, kernel 3×3×3)
    + BatchNormalization + ReLU
    ↓
Conv3D Layer 3 (128 filters, kernel 3×3×2)
    + BatchNormalization + ReLU
    ↓
MaxPooling2D (Spatial only)
    ↓
Flatten + Dropout (50%)
    ↓
Dense Layer (256 units) + ReLU
    ↓
Dense Layer (128 units) + ReLU
    ↓
Output: Softmax (11 classes)
```

**Key Design Choices:**
- Temporal receptive field of 3-5 frames captures short motion patterns
- Progressive spatial downsampling reduces computational cost
- Dropout prevents overfitting given limited real micro-gesture data
- Final layers collapsed in time before fully connected processing

### Data Pipeline

#### HaGRID Dataset Integration
- **Source:** Hand Gesture Recognition Image Dataset (Kapitanov et al., 2024)
- **Selected Classes:** 7 gesture types relevant to accessibility applications
- **Scale:** ~180K real images across 10 gesture classes
- **Split Protocol:** Person-independent (70% train / 15% validation / 15% test by subject ID)

#### Synthetic Micro-Gesture Augmentation
Novel contribution: synthetic data generation pipeline simulating motor-impaired gestures

```python
Augmentation Techniques:
├── Random cropping → reduced amplitude gestures
├── Scale transformations → minimal motion simulation
├── Temporal subsampling → subtle movement patterns
├── Mini-swipe generation → micro-translations (5-10 pixels)
└── Pinch synthesis → finger distance variations

Result: 268K synthetic sequences + 180K real images
Total Training Data: ~448K gesture sequences
```

This synthetic pipeline addresses the lack of real micro-gesture training data and improves model generalization to users with varying motor capabilities.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Input Capture Layer                      │
│              (Webcam / Browser Camera API)                  │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│             MediaPipe Hand Tracking                         │
│        • Hand detection and localization                    │
│        • 21-point hand landmark extraction                  │
│        • Bounding box generation                            │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│            3D CNN Gesture Classifier                        │
│        • 8-frame sequence buffer                            │
│        • TensorFlow Lite inference engine                   │
│        • Real-time prediction (<40ms)                       │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│           Application Interface Layer                       │
│    ┌─────────────────────┬─────────────────────┐            │
│    │   Web Client        │  Desktop Client     │            │
│    │   (Fabric.js)       │   (OpenCV)          │            │
│    │   • Browser-based   │   • Native Python   │            │
│    │   • WebRTC camera   │   • Direct capture  │            │
│    └─────────────────────┴─────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

---

## Installation

### Prerequisites
```bash
Python 3.8+
Node.js 14+ (for web client)
Webcam/camera access
GPU (optional, for training)
```

### Backend Setup (Flask API)

```bash
# Clone repository
git clone https://github.com/AbdullahRasheed45/Adaptive-Micro-Gesture-Recognition.git
cd Adaptive-Micro-Gesture-Recognition

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Download pre-trained TFLite model
# Place gesture_model_3d_final.tflite in backend/model/

# Start Flask server
python backend/app.py
# API available at http://localhost:5000
```

### Web Frontend Setup

```bash
# Navigate to web client directory
cd frontend/web

# Install Node.js dependencies
npm install

# Start development server
npm start
# Application available at http://localhost:3000
```

### Desktop Client Setup

```bash
# Navigate to desktop client directory
cd frontend/desktop

# Install dependencies (if not already installed)
pip install opencv-python mediapipe numpy

# Run desktop application
python main.py
```

---

## Usage

### Interactive Drawing Interface

The system provides a gesture-controlled whiteboard with the following workflow:

**Basic Drawing:**
1. **Point Gesture** - Select drawing tool
2. **Fist Gesture** - Activate drawing mode
3. **Palm Gesture** - Stop drawing / neutral state
4. **OK Gesture** - Switch to eraser
5. **Thumbs Up** - Undo last action
6. **Thumbs Down** - Redo previous action

**Navigation (Advanced):**
- **Swipe Left/Right** - Pan canvas horizontally
- **Pinch Gesture** - Zoom in/out (requires calibration)
- **Victory Gesture** - Switch between drawing modes

### Adaptive Calibration

For users with varying motor abilities, the system supports personalized threshold adjustment:

```python
# Example calibration API call
POST /calibrate
{
    "user_id": "user123",
    "gesture": "pinch",
    "sensitivity": 0.75,  # Range: 0.5-1.0
    "samples": 10         # Number of calibration samples
}
```

---

## Research Contributions

### Novel Methodologies

1. **Synthetic Micro-Gesture Pipeline:** First systematic approach to generating training data for motor-impaired gesture patterns through controlled image transformations

2. **Adaptive Threshold Calibration:** User-specific gesture sensitivity adjustment enabling personalization to individual motor capabilities

3. **3D CNN Optimization for Accessibility:** Demonstrated that spatio-temporal CNNs can be optimized for edge deployment while maintaining high accuracy on subtle gestures

4. **Cross-Dataset Validation:** Achieved 92% accuracy on external micro-gesture data, demonstrating generalization beyond training distribution

### Academic Impact

**Research Paper:** "Adaptive Micro-Gesture Recognition for Accessibility"
- **Author:** Muhammad Abdullah Rasheed
- **Institution:** Anglia Ruskin University
- **Year:** 2022
- **Supervisor:** Prof. Man Fai Leung
- **Degree:** MSc Data Science

**Key Findings:**
- 3D CNNs outperform 2D CNN + LSTM approaches by 7.3% on micro-gesture recognition
- Synthetic augmentation improves generalization by 8-12% on cross-dataset tests
- TFLite quantization incurs <1% accuracy loss while reducing model size by 75%
- Real-time performance is achievable on commodity smartphones without cloud processing

---

## Applications

### Healthcare & Rehabilitation
- Motor function assessment through objective gesture tracking
- Rehabilitation progress monitoring
- Alternative input methods for therapy software

### Educational Technology
- Accessible learning interfaces for students with disabilities
- Interactive STEM education platforms
- Customizable educational software controls

### Workplace Accessibility
- Alternative computer interaction for professional environments
- Accessible design and creative tools
- Enhanced remote work capabilities for individuals with motor impairments

---

## Limitations

The research identified several constraints and areas for future improvement:

1. **Single Hand Assumption:** Current system processes one hand at a time; multi-hand support requires architectural changes

2. **Lighting Sensitivity:** Performance degrades in very low light or harsh backlighting conditions

3. **Tremor Filtering:** Distinguishing intentional micro-gestures from involuntary tremors remains challenging for users with severe spastic conditions

4. **Gesture Vocabulary:** Limited to 10 gestures; scaling to larger vocabularies may require hierarchical classification

5. **User Studies:** Limited validation with actual motor-impaired users; clinical trials needed for real-world impact assessment

---

## Future Directions

### Technical Enhancements
- Multi-hand gesture recognition for bilateral interaction
- Integration of depth sensors for 3D spatial gestures
- Temporal gesture detection for continuous video streams
- Transformer-based architectures for longer temporal context
- Multi-modal fusion (gesture + eye-tracking + voice)

### Accessibility Research
- Clinical validation studies with motor-impaired participants
- Personalization through continual learning and adaptation
- Cross-cultural gesture vocabulary development
- Age-specific optimization (pediatric and geriatric populations)
- Integration with assistive robotics and smart home systems

### Deployment Scaling
- Native mobile applications (iOS/Android)
- Cloud API service for scalable deployment
- Wearable device integration (smartwatches, AR glasses)
- Embedded system optimization for assistive devices

---

## Citation

If you use this work in your research, please cite:

```bibtex
@mastersthesis{rasheed2022adaptive,
  title={Adaptive Micro-Gesture Recognition for Accessibility},
  author={Rasheed, Muhammad Abdullah},
  year={2022},
  school={Anglia Ruskin University},
  type={MSc Data Science Thesis},
  note={Supervised by Prof. Man Fai Leung}
}
```

---

## Contributing

This research project welcomes contributions in the following areas:

**Academic Collaboration:**
- Extension studies with motor-impaired user populations
- Clinical validation partnerships with healthcare institutions
- Cross-cultural gesture vocabulary expansion
- Multi-modal accessibility interface research

**Technical Development:**
- Model architecture improvements and optimization
- Platform expansion (mobile apps, embedded systems)
- Accessibility feature enhancements
- Performance benchmarking and ablation studies

**Dataset Contributions:**
- Real micro-gesture video collection
- Diverse user population samples
- Cross-cultural gesture annotations
- Longitudinal motor function tracking data

---

## Acknowledgments

This research was conducted at Anglia Ruskin University's School of Computing and Information Science. Special thanks to:

- **Prof. Man Fai Leung** for thesis supervision and guidance
- **Anglia Ruskin University** for research facilities and resources
- **HaGRID Dataset Creators** (Kapitanov et al.) for the foundational gesture dataset
- **TensorFlow Team** for model optimization tools and documentation
- **MediaPipe Team** for hand tracking infrastructure

---

## License

This project is released under the MIT License. See LICENSE file for details.

---

## Contact

**Researcher:** Muhammad Abdullah Rasheed

[![Portfolio](https://img.shields.io/badge/Portfolio-000000?style=for-the-badge&logo=About.me&logoColor=white)](https://techvibes360.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/abdullahrasheed-/)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:abdullahrasheed45@gmail.com)
[![Research Paper](https://img.shields.io/badge/Read-Research%20Paper-red?style=for-the-badge&logo=adobeacrobatreader)](https://drive.google.com/file/d/1txAz5fShMmEUoBP0YLINVLcLyi-aDI2s/view?usp=sharing)

For research collaboration, technical questions, or accessibility technology discussions, please reach out via the channels above.

---

<div align="center">

**Supporting accessible technology research through open collaboration**

*"Technology should adapt to human diversity, not force conformity"*

</div>
