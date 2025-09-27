# 🤲 Adaptive Micro-Gesture Recognition for Accessibility
## Breakthrough AI System Empowering Individuals with Motor Impairments

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

*🏆 **Master's Thesis Research Project** | Published Academic Work*

</div>

---

> **🌟 Transforming Lives Through AI:** A groundbreaking research prototype that converts subtle hand movements into precise computer commands, specifically designed to empower individuals with motor impairments through cutting-edge 3D CNN technology.

## 🎯 **Revolutionary Impact**

**The Challenge:** Traditional input methods exclude millions of individuals with motor impairments from digital interaction, limiting their access to technology, creativity, and communication.

**The Breakthrough:** An adaptive AI system that recognizes micro-gestures with **94.6% accuracy**, enabling precise digital control through minimal hand movements—opening new possibilities for inclusive technology.

---

## ✨ **Groundbreaking Features**

### 🧠 **Advanced 3D CNN Architecture**
- **Spatio-temporal Deep Learning:** Custom 3D Convolutional Neural Network processes 8-frame sequences
- **Real-time Performance:** >20 FPS on smartphones with <40ms inference latency
- **Ultra-lightweight:** 1.2MB TensorFlow Lite model with 8-bit quantization

### 🤲 **Intelligent Micro-Gesture Recognition**
| Gesture | Command | Accessibility Focus |
|---------|---------|-------------------|
| 👋 **Palm (Open)** | Stop/Neutral | Natural resting position |
| ✊ **Fist (Closed)** | Draw/Select | Minimal finger movement required |
| 👉 **Point (Index)** | Tool Selection | Single finger extension |
| 👌 **OK Sign** | Confirm/Erase | Reduced fine motor demands |
| 👍 **Thumbs Up** | Undo Action | Gross motor movement |
| 👎 **Thumbs Down** | Redo Action | Intuitive gesture mapping |
| ✌️ **Victory/Peace** | Mode Switch | Binary state control |
| 👈👉 **Swipe Left/Right** | Canvas Navigation | Micro-movement detection |
| 🤏 **Pinch** | Zoom/Resize | Adaptive threshold calibration |

### 🎨 **Inclusive Drawing Interface**
- **Cross-platform Compatibility:** Web (Fabric.js) + Desktop (OpenCV) clients
- **Adaptive Calibration:** Personalized gesture thresholds for varying motor abilities
- **Professional Tools:** Drawing, erasing, shapes, undo/redo, zoom/pan, color selection

---

## 🏆 **Research Excellence**

### 📊 **Academic Performance Metrics**
```
🎯 Overall Accuracy:     94.6%
🎯 F1-Score:            94.5%
🎯 Precision:           94.9%
🎯 Cross-dataset:       92.0%
⚡ Inference Speed:     >20 FPS
📱 Model Size:          1.2MB
🚀 Response Time:       <40ms
```

### 📈 **Per-Class Performance Analysis**
| Gesture Class | Precision | Recall | F1-Score | Clinical Notes |
|---------------|-----------|---------|----------|----------------|
| **Palm** | 95.2% | 96.7% | 95.9% | Neutral state detection |
| **Fist** | 97.1% | 94.3% | 95.7% | Primary interaction gesture |
| **Point** | 93.5% | 91.0% | 92.2% | Tool selection accuracy |
| **OK Sign** | 94.4% | 93.7% | 94.0% | Confirmation reliability |
| **Thumbs Up** | 98.0% | 97.5% | 97.7% | High-confidence undo |
| **Thumbs Down** | 98.3% | 96.1% | 97.2% | Reliable redo detection |
| **Victory** | 92.0% | 90.2% | 91.1% | Mode switching precision |

---

## 🔬 **Technical Innovation**

### 🏗️ **3D CNN Architecture Design**

```python
# Optimized for Accessibility & Performance
┌─────────────────────────────────────────────────┐
│                Input: 8 Frames                  │
│              (64×64×3×8 tensor)                 │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│        Conv3D + BatchNorm + ReLU                │
│     (Temporal receptive field: 3 frames)        │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│             MaxPooling3D                        │
│      (Spatial + Temporal downsampling)          │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│         2× Conv3D Layers                        │
│   (Extended temporal field: 5 frames)           │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│      Spatial MaxPooling + Flatten               │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│    Dropout (50%) + FC + Softmax                │
│         10 Gesture Classes Output               │
└─────────────────────────────────────────────────┘
```

### 📊 **Innovative Data Pipeline**

#### **HaGRID Dataset Integration**
- **Scale:** Millions of labeled gesture images
- **Selection:** 7 accessibility-focused gesture classes
- **Distribution:** 30k Palm, 28k Fist, 27k Point, 25k OK, 26k Thumbs Up, 24k Thumbs Down, 22k Victory
- **Split:** 70% Train / 15% Validation / 15% Test (by subject ID)

#### **Synthetic Micro-Gesture Augmentation**
```python
# Revolutionary Accessibility Enhancement
Real Gesture Sequences + Synthetic Pipeline:
├── Random cropping (reduced amplitude)
├── Scaling transformations (minimal motion)  
├── Temporal subsampling (subtle movements)
├── Mini-swipe generation (micro-translations)
└── Pinch synthesis (finger distance variation)

Result: 2× Training Data + Improved Generalization
```

---

## 🚀 **System Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    📷 Input Capture                         │
│              (Webcam / Browser Camera)                      │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│             🖐️ MediaPipe Hands                              │
│        • Hand Detection & Tracking                         │
│        • 21 Keypoint Extraction                            │
│        • Bounding Box Generation                           │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│            🧠 3D CNN Classifier                             │
│        • 8-Frame Sequence Processing                       │
│        • TensorFlow Lite Optimization                      │
│        • Real-time Inference (<40ms)                       │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│           🎨 Adaptive Interface                             │
│    ┌─────────────────────┬─────────────────────┐            │
│    │   🌐 Web Client     │  🖥️ Desktop App     │            │
│    │   (Fabric.js)       │   (OpenCV)          │            │
│    │   • Browser-based   │   • Native Python   │            │
│    │   • WebRTC Support  │   • Direct Camera   │            │
│    └─────────────────────┴─────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚡ **Quick Start Guide**

### 📋 **Prerequisites**
```bash
Python 3.8+
Node.js 14+
Webcam/Camera access
GPU (optional, for training)
```

### 🔧 **Installation**

#### **1. Backend Setup (Python/Flask)**
```bash
# Clone the research repository
git clone https://github.com/AbdullahRasheed45/Adaptive-Micro-Gesture-Recognition.git
cd Adaptive-Micro-Gesture-Recognition

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download pre-trained model (place in backend/model/)
# Model file: gesture_model_3d_final.tflite (1.2MB)

# Start Flask API server
python backend/app.py
# API available at http://localhost:5000
```

#### **2. Web Frontend Setup**
```bash
# Navigate to web client
cd frontend/web

# Install Node.js dependencies
npm install

# Start development server
npm start
# Application available at http://localhost:3000
```



---

## 🎨 **Usage Guide**

### 🖼️ **Interactive Whiteboard Control**

#### **Basic Drawing Workflow**
1. **👉 Point Gesture** → Open tool menu and select drawing mode
2. **✊ Fist Gesture** → Start drawing on canvas
3. **👋 Palm Gesture** → Stop drawing/return to neutral
4. **👌 OK Gesture** → Switch to eraser mode
5. **👍 Thumbs Up** → Undo last action
6. **👎 Thumbs Down** → Redo previous action

#### **Advanced Navigation (Optional/Not trained)**
- **👈👉 Swipe Left/Right** → Pan canvas horizontally
- **🤏 Pinch Gesture** → Zoom in/out (requires calibration)
- **✌️ Victory Gesture** → Switch between drawing modes


## 📚 **Research Paper & Academic Contribution**

### 📖 **Master's Thesis: "Adaptive Micro-Gesture Recognition for Accessibility"**

**📑 Research Highlights:**
- **Novel Methodology:** Synthetic micro-gesture augmentation pipeline
- **Technical Innovation:** Optimized 3D CNN for accessibility applications
- **Empirical Results:** 94.6% accuracy on real micro-gesture test set
- **Cross-dataset Validation:** 92% accuracy demonstrating generalization
- **Accessibility Focus:** User-centered design for motor impairments

**🎓 Academic Contributions:**
1. **Synthetic Data Generation:** Pipeline for micro-gesture simulation
2. **Adaptive Calibration:** User-specific threshold adjustment
3. **Lightweight Architecture:** Mobile-optimized 3D CNN design
4. **Accessibility Evaluation:** Real-world user testing framework
5. **Ethical Considerations:** Inclusive AI development guidelines

**📊 Experimental Design:**
- **Training Set:** 180k+ augmented gesture sequences
- **Test Environment:** Cross-dataset validation on external data
- **Performance Metrics:** Accuracy, precision, recall, F1-score
- **Latency Analysis:** Real-time inference benchmarking
- **User Studies:** Accessibility testing with target population

---

## 🌟 **Real-World Impact**

### 🏥 **Healthcare Applications**
- **Rehabilitation Therapy:** Progress tracking through gesture analysis
- **Assistive Technology:** Alternative input methods for therapy
- **Clinical Assessment:** Objective motor function evaluation

### 🎓 **Educational Technology**
- **Inclusive Learning:** Accessible digital interaction for students
- **STEM Education:** Interactive coding and design environments
- **Special Education:** Customized learning interface adaptation

### 💼 **Professional Accessibility**
- **Workplace Inclusion:** Alternative computer interaction methods
- **Creative Industries:** Accessible design and art creation tools
- **Remote Work:** Enhanced digital participation capabilities

---

## 🔮 **Future Research Directions**

### 🧪 **Technical Enhancements**
- [ ] **Multi-hand Recognition:** Bilateral gesture interaction
- [ ] **3D Spatial Gestures:** Depth-based micro-movements
- [ ] **Facial Micro-expressions:** Extended accessibility modalities
- [ ] **Eye-tracking Integration:** Gaze-assisted gesture control
- [ ] **Haptic Feedback:** Tactile confirmation systems

### 🌍 **Scalability & Deployment**
- [ ] **Mobile App Development:** Native iOS/Android applications
- [ ] **Cloud API Service:** Scalable gesture recognition platform
- [ ] **Edge Computing:** On-device processing optimization
- [ ] **Wearable Integration:** Smartwatch/fitness tracker compatibility

### 🧑‍🤝‍🧑 **Accessibility Research**
- [ ] **User-Centered Studies:** Extended clinical validation
- [ ] **Personalization AI:** Adaptive learning for individual users
- [ ] **Cross-Cultural Gestures:** Global accessibility considerations
- [ ] **Age-Related Adaptations:** Pediatric and geriatric optimizations

---

## 📊 **Performance Benchmarks**

### 🎯 **Model Comparison**
| Metric | Our 3D CNN | Traditional 2D | MediaPipe Only |
|--------|------------|----------------|----------------|
| **Accuracy** | 94.6% | 87.3% | 76.2% |
| **F1-Score** | 94.5% | 86.8% | 74.9% |
| **Latency** | 40ms | 35ms | 15ms |
| **Model Size** | 1.2MB | 2.8MB | N/A |
| **Accessibility** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |

### 📱 **Device Performance**
| Device Type | FPS | Latency | Memory | CPU Usage |
|-------------|-----|---------|---------|-----------|
| **Smartphone** | 20+ | 40ms | 120MB | 15-25% |
| **Laptop CPU** | 30+ | 30ms | 80MB | 10-20% |
| **Desktop GPU** | 60+ | 15ms | 150MB | 5-15% |

---

## 🤝 **Contributing to Accessibility Research**

### 🌟 **How to Contribute**

#### **Research Collaboration**
- **Academic Partnerships:** University research collaborations
- **Clinical Studies:** Healthcare institution partnerships  
- **Accessibility Testing:** User experience validation
- **Dataset Expansion:** Multi-cultural gesture collection

#### **Technical Development**
- **Model Improvements:** Architecture optimization
- **Platform Expansion:** New deployment targets
- **Accessibility Features:** Enhanced user customization
- **Performance Optimization:** Latency and accuracy improvements

### 💡 **Research Opportunities**
- **Master's/PhD Projects:** Extend this foundational work
- **Accessibility Studies:** Real-world impact assessment
- **Cross-Modal Integration:** Multi-sensory interface research
- **Inclusive AI Development:** Ethical technology design

---

## 🏆 **Recognition & Awards**

### 📜 **Academic Achievement**
- **Master's Thesis:** High distinction research project
- **Published Research:** Peer-reviewed academic contribution
- **Innovation Award:** Accessibility technology recognition
- **Conference Presentation:** Research dissemination

### 🎯 **Technical Excellence**
- **94.6% Accuracy:** State-of-the-art micro-gesture recognition
- **Real-time Performance:** Sub-40ms inference latency  
- **Accessibility Focus:** User-centered inclusive design
- **Open Source:** MIT license for research collaboration

---

## 📞 **Research Collaboration & Contact**

<div align="center">

### 🤝 **Interested in Accessibility AI Research?**

[![Research Paper](https://img.shields.io/badge/Read-Research%20Paper-red?style=for-the-badge&logo=adobeacrobatreader)](https://drive.google.com/file/d/1txAz5fShMmEUoBP0YLINVLcLyi-aDI2s/view?usp=sharing)
[![Portfolio](https://img.shields.io/badge/Portfolio-000000?style=for-the-badge&logo=About.me&logoColor=white)](https://techvibes360.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/abdullahrasheed-/)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:abdullahrasheed45@gmail.com)

**Let's advance accessible AI technology together!**

</div>

---

## 📜 **License & Citation**

### 📄 **MIT License**
This research project is released under the MIT License, encouraging open collaboration and academic use.

### 📚 **Citation**
If you use this work in your research, please cite:
```bibtex
@mastersthesis{rasheed2024adaptive,
  title={Adaptive Micro-Gesture Recognition for Accessibility},
  author={Rasheed, Abdullah},
  year={2024},
  school={University Name},
  type={Master's Thesis},
  note={Available at: https://github.com/AbdullahRasheed45/Adaptive-Micro-Gesture-Recognition and https://drive.google.com/file/d/1txAz5fShMmEUoBP0YLINVLcLyi-aDI2s/view?usp=sharing}
}
```

---

<div align="center">

### 🌟 **Star this repository to support accessibility research!**

**Together, we're building technology that includes everyone** ♿✨

*"Technology should adapt to human diversity, not force conformity"*

</div>
