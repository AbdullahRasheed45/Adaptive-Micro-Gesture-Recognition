import os
import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
from pathlib import Path
from imblearn.over_sampling import SMOTE

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Initialize MediaPipe Hands with lower confidence for better detection
mp_hands = mp.solutions.hands.Hands(max_num_hands=1, min_detection_confidence=0.2, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

def preprocess_image(image):
    """Preprocess image for better MediaPipe detection."""
    if image is None or image.size == 0:
        print("Error: Invalid or empty image")
        return None
    
    # Convert to RGB if needed
    if len(image.shape) == 3 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    elif len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    
    # Normalize
    image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    return image

def extract_keypoints(image, debug=False, img_path=""):
    """Extract 21 hand landmarks from an image."""
    processed_image = preprocess_image(image)
    if processed_image is None:
        print(f"Warning: Preprocessing failed for {img_path}")
        return None
    
    results = mp_hands.process(processed_image)
    
    if results.multi_hand_landmarks:
        landmarks = results.multi_hand_landmarks[0].landmark
        
        if debug:
            try:
                img_copy = cv2.cvtColor(processed_image, cv2.COLOR_RGB2BGR)
                if img_copy is not None and img_copy.size > 0:
                    mp_drawing.draw_landmarks(
                        img_copy, 
                        results.multi_hand_landmarks[0], 
                        mp.solutions.hands.HAND_CONNECTIONS
                    )
                    cv2.imshow(f"Landmarks: {Path(img_path).name}", img_copy)
                    cv2.waitKey(1)
            except Exception as e:
                print(f"Debug display error for {img_path}: {e}")
        
        return np.array([[lm.x, lm.y, lm.z] for lm in landmarks]).flatten()
    
    print(f"Warning: No landmarks detected in {img_path}")
    return None

def simulate_micro_gesture(keypoints, scale=0.3, tremor_freq=5):
    """Simulate micro-gestures with tremor noise."""
    if keypoints is None:
        return None
    keypoints = keypoints * scale
    noise = np.random.normal(0, 0.01, keypoints.shape) * np.sin(2 * np.pi * tremor_freq * np.arange(len(keypoints)) / 30)
    return keypoints + noise

def generate_sequence(keypoints, num_frames=10):
    """Create a 10-frame sequence with slight variations."""
    if keypoints is None:
        return None
    sequence = []
    for _ in range(num_frames):
        variation = np.random.normal(0, 0.005, keypoints.shape)
        sequence.append(keypoints + variation)
    return np.array(sequence)

def augment_sequence(sequence, num_augmented=5):
    """Generate augmented versions of a sequence."""
    if sequence is None:
        return []
    augmented = []
    for _ in range(num_augmented):
        scale = np.random.uniform(0.8, 1.2)
        noise = np.random.normal(0, 0.01, sequence.shape)
        rotation = np.random.uniform(-0.1, 0.1)
        augmented_seq = sequence * scale + noise
        for frame in augmented_seq:
            for i in range(0, frame.shape[0], 3):
                x, y = frame[i], frame[i + 1]
                frame[i] = x * np.cos(rotation) - y * np.sin(rotation)
                frame[i + 1] = x * np.sin(rotation) + y * np.cos(rotation)
        augmented.append(augmented_seq)
    return augmented

def generate_synthetic_sequence(label_idx, num_frames=10):
    """Generate a synthetic sequence for a missing class."""
    # Create a base sequence with random keypoints
    keypoints = np.random.uniform(0, 1, (21, 3))  # 21 landmarks, (x, y, z)
    micro_keypoints = simulate_micro_gesture(keypoints)
    sequence = generate_sequence(micro_keypoints, num_frames)
    if sequence is None:
        return None
    # Apply class-specific modifications
    if label_idx == 0:  # write_start: mimic single finger
        sequence[:, 3:6] *= 1.3  # Emphasize finger 1
    elif label_idx == 3:  # zoom_in: mimic two fingers
        sequence[:, 3:9] *= 0.8  # Reduce distance for fingers 1-2
    elif label_idx == 6:  # undo: mimic two fingers
        sequence[:, 6:12] *= 1.2  # Emphasize fingers 2-3
    elif label_idx == 7:  # redo: mimic inverted two fingers
        sequence[:, 6:12] *= 1.2
        sequence[:, 6:12] += np.random.normal(0, 0.02, (sequence.shape[0], 6))
    elif label_idx == 8:  # draw_shapes: mimic three fingers
        sequence[:, 6:15] *= 1.1  # Emphasize fingers 2-4
    elif label_idx == 10:  # pan: mimic single finger (free drawing)
        sequence[:, 3:6] *= 1.3  # Emphasize finger 1
    elif label_idx == 11:  # clear_all: mimic open hand
        sequence *= 1.2  # Spread all landmarks
    return sequence

def process_hagrid(data_dir, output_file, max_samples_per_gesture=1000, debug=False):
    """Process HaGRID dataset to create synthetic micro-gesture dataset with all 12 classes."""
    data = []
    labels = ['write_start', 'write_stop', 'change_color', 'zoom_in', 'erase', 'zoom_out', 
              'undo', 'redo', 'draw_shapes', 'save', 'pan', 'clear_all']
    gesture_dirs = ['one', 'fist', 'stop', 'peace', 'palm', 'peace_inverted', 
                    'two_up', 'peace_inverted', 'three', 'call', 'one', 'stop_inverted']
    
    data_dir = Path(data_dir)
    if not data_dir.exists():
        print(f"Error: Dataset directory {data_dir} does not exist")
        return
    
    sample_counts = {label: 0 for label in labels}
    
    for label_idx, gesture in enumerate(gesture_dirs):
        gesture_dir = data_dir / gesture
        if not gesture_dir.exists():
            print(f"Error: Directory {gesture_dir} not found. Generating synthetic data for {labels[label_idx]}.")
            for _ in range(max_samples_per_gesture):
                sequence = generate_synthetic_sequence(label_idx)
                if sequence is None:
                    continue
                data.append(np.append(sequence.flatten(), label_idx))
                sample_counts[labels[label_idx]] += 1
            print(f"Generated {sample_counts[labels[label_idx]]} synthetic samples for {labels[label_idx]}")
            continue
        
        images = list(gesture_dir.glob('*.jpg')) + list(gesture_dir.glob('*.jpeg')) + list(gesture_dir.glob('*.png'))
        if not images:
            print(f"Warning: No images found in {gesture_dir}. Generating synthetic data for {labels[label_idx]}.")
            for _ in range(max_samples_per_gesture):
                sequence = generate_synthetic_sequence(label_idx)
                if sequence is None:
                    continue
                data.append(np.append(sequence.flatten(), label_idx))
                sample_counts[labels[label_idx]] += 1
            print(f"Generated {sample_counts[labels[label_idx]]} synthetic samples for {labels[label_idx]}")
            continue
        
        print(f"Processing gesture {labels[label_idx]} ({gesture_dir})...")
        for img_file in images:
            if sample_counts[labels[label_idx]] >= max_samples_per_gesture:
                break
            
            img = cv2.imread(str(img_file))
            if img is None or img.size == 0:
                print(f"Warning: Could not read image {img_file}")
                continue
            
            keypoints = extract_keypoints(img, debug=debug, img_path=str(img_file))
            if keypoints is None:
                continue
            
            micro_keypoints = simulate_micro_gesture(keypoints)
            if micro_keypoints is None:
                continue
            
            sequence = generate_sequence(micro_keypoints)
            if sequence is None:
                continue
            
            data.append(np.append(sequence.flatten(), label_idx))
            sample_counts[labels[label_idx]] += 1
            
            # Augment all classes to ensure sufficient samples
            augmented_sequences = augment_sequence(sequence, num_augmented=5)
            for aug_seq in augmented_sequences:
                if sample_counts[labels[label_idx]] >= max_samples_per_gesture:
                    break
                data.append(np.append(aug_seq.flatten(), label_idx))
                sample_counts[labels[label_idx]] += 1
            
            if sample_counts[labels[label_idx]] % 100 == 0:
                print(f"Processed {sample_counts[labels[label_idx]]} samples for gesture {labels[label_idx]}")
        
        print(f"Completed: Processed {sample_counts[labels[label_idx]]} samples for gesture {labels[label_idx]}")
    
    if not data:
        print("Error: No data processed. Check dataset path and images.")
        if debug:
            cv2.destroyAllWindows()
        return
    
    # Convert to DataFrame
    columns = [f'kp_{i}' for i in range(630)] + ['label']
    df = pd.DataFrame(data, columns=columns)
    
    # Log initial distribution
    print("Initial label distribution:\n", df['label'].value_counts())
    
    # Apply SMOTE to balance classes
    X = df.drop('label', axis=1).values
    y = df['label'].values
    smote = SMOTE(random_state=42, k_neighbors=1)
    try:
        X_balanced, y_balanced = smote.fit_resample(X, y)
        df = pd.DataFrame(np.column_stack((X_balanced, y_balanced)), columns=columns)
        print("Applied SMOTE to balance classes")
        print("Final label distribution:\n", df['label'].value_counts())
    except ValueError as e:
        print(f"SMOTE failed: {e}. Proceeding with original data.")
    
    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"Saved dataset to {output_file}. Total samples: {len(df)}")
    
    if debug:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    data_dir = Path('D:\\Generative AI\\Project\\Adaptive-Micro-Gesture-Recognition\\data\\hagrid')
    output_file = Path('D:\\Generative AI\\Project\\Adaptive-Micro-Gesture-Recognition\\data\\processed\\micro_gestures.csv')
    process_hagrid(data_dir, output_file, debug=False)