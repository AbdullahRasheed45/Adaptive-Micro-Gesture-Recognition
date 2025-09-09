import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import precision_recall_fscore_support, classification_report
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, Input, MultiHeadAttention, LayerNormalization, Reshape
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import ReduceLROnPlateau, EarlyStopping
import keras_tuner as kt
import tensorflow as tf
from collections import Counter

# Load data
df = pd.read_csv('D:\\Generative AI\\Project\\Adaptive-Micro-Gesture-Recognition\\data\\processed\\micro_gestures.csv')
print("Unique labels:", sorted(df['label'].unique()))
print("Label distribution:\n", df['label'].value_counts())
# Clean and validate labels
df = df.dropna(subset=['label'])
df['label'] = pd.to_numeric(df['label'], errors='coerce')
df = df.dropna(subset=['label'])
df['label'] = df['label'].astype(int)

# Drop rare classes (fewer than 2 samples)
label_counts = Counter(df['label'])
df = df[df['label'].map(label_counts) >= 2]

# Check label value ranges
if df['label'].min() < 0 or df['label'].max() >= 12:
    raise ValueError(f"Labels must be in the range 0–11. Found labels: {df['label'].unique()}")

# Extract features and labels
X = df.drop('label', axis=1).values
y = df['label'].values
y = to_categorical(y, num_classes=12)

# Reshape for 2D CNN (samples, frames, landmarks, coords) with 10 frames
coords = 3
landmarks = 21  # Based on 630 features (10 * 21 * 3)
X_base = X.reshape((X.shape[0], 10, landmarks, coords))

# Compute class weights with emphasis on underrepresented classes
class_weights = compute_class_weight('balanced', classes=np.unique(df['label']), y=df['label'])
class_weight_dict = {i: weight * 1.45 if i in [5, 6, 7] else weight for i, weight in enumerate(class_weights)}

# Adaptive frame sampling
def adaptive_sample(landmarks_seq, min_frames=4, max_frames=10):
    variances = np.var(landmarks_seq, axis=0)
    frame_count = min(max_frames, max(min_frames, int(np.mean(variances) * 5)))
    return landmarks_seq[:frame_count] if frame_count < 10 else landmarks_seq

X_processed = np.array([adaptive_sample(seq) for seq in X_base])
max_frames = max([x.shape[0] for x in X_processed])
X_padded = np.array([np.pad(x, ((0, max_frames - x.shape[0]), (0, 0), (0, 0)), 'constant') for x in X_processed])

print("Shapes in X_processed:", [x.shape for x in X_processed])
print("max_frames:", max_frames)
print("X_padded shape:", X_padded.shape)

# Define hypermodel
def build_model(hp):
    inputs = Input(shape=(max_frames, landmarks, coords))
    x = Conv2D(filters=hp.Int('conv1_filters', 16, 96, step=16), kernel_size=(3, 3), activation='relu', padding='same')(inputs)
    x = MaxPooling2D((1, 1), padding='same')(x)
    x = Conv2D(filters=hp.Int('conv2_filters', 8, 48, step=8), kernel_size=(3, 3), activation='relu', padding='same')(x)
    x = MaxPooling2D((1, 1), padding='same')(x)
    x = Reshape((-1, hp.Int('conv2_filters', 8, 48, step=8) * max_frames))(x)
    attn_output = MultiHeadAttention(key_dim=hp.Int('key_dim', 16, 64, step=16), num_heads=2)(x, x)
    x = LayerNormalization(epsilon=1e-6)(attn_output + x)
    x = Flatten()(x)
    x = Dense(units=hp.Int('dense_units', 32, 224, step=32), activation='relu')(x)
    x = Dropout(rate=hp.Float('dropout_rate', 0.1, 0.3, step=0.1))(x)
    x = Dense(12, activation='softmax')(x)

    model = Model(inputs=inputs, outputs=x)
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

# Hyperparameter tuning
tuner = kt.RandomSearch(build_model, objective='val_accuracy', max_trials=25, executions_per_trial=2,
                        directory='tuner_dir', project_name='gesture_tuning_hybrid', overwrite=True)

# Split for tuning
X_train, X_test, y_train, y_test = train_test_split(X_padded, y, test_size=0.2, random_state=42)
tuner.search(X_train, y_train, epochs=40, batch_size=32, validation_split=0.2,
             callbacks=[EarlyStopping(monitor='val_loss', patience=5)])

# Get best hyperparameters
best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]

# Build best model
def build_best_model(hps):
    inputs = Input(shape=(max_frames, landmarks, coords))
    x = Conv2D(filters=hps.get('conv1_filters'), kernel_size=(3, 3), activation='relu', padding='same')(inputs)
    x = MaxPooling2D((1, 1), padding='same')(x)
    x = Conv2D(filters=hps.get('conv2_filters'), kernel_size=(3, 3), activation='relu', padding='same')(x)
    x = MaxPooling2D((1, 1), padding='same')(x)
    x = Reshape((-1, hps.get('conv2_filters') * max_frames))(x)
    attn_output = MultiHeadAttention(key_dim=hps.get('key_dim'), num_heads=2)(x, x)
    x = LayerNormalization(epsilon=1e-6)(attn_output + x)
    x = Flatten()(x)
    x = Dense(units=hps.get('dense_units'), activation='relu')(x)
    x = Dropout(rate=hps.get('dropout_rate'))(x)
    x = Dense(12, activation='softmax')(x)

    model = Model(inputs=inputs, outputs=x)
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

best_model = build_best_model(best_hps)

# Cross-validation
kfold = KFold(n_splits=5, shuffle=True, random_state=42)
accuracies, precisions, recalls, f1s = [], [], [], []

class_names = [
    'write_start', 'write_stop', 'erase', 'zoom_in', 'zoom_out', 'draw_shapes',
    'undo', 'redo', 'change_color', 'save', 'pan', 'clear_all'
]
labels = list(range(12))

for fold, (train_idx, val_idx) in enumerate(kfold.split(X_padded)):
    print(f'\nFold {fold + 1}/5')
    X_train, X_val = X_padded[train_idx], X_padded[val_idx]
    y_train, y_val = y[train_idx], y[val_idx]

    history = best_model.fit(X_train, y_train, epochs=60, batch_size=32,
                             validation_data=(X_val, y_val),
                             callbacks=[ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=5),
                                        EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)],
                             class_weight=class_weight_dict,
                             verbose=1)

    y_pred = best_model.predict(X_val)
    y_pred_classes = np.argmax(y_pred, axis=1)
    y_val_classes = np.argmax(y_val, axis=1)

    metrics = precision_recall_fscore_support(y_val_classes, y_pred_classes, average='weighted')
    loss, accuracy = best_model.evaluate(X_val, y_val)
    print(f'Validation Accuracy for fold {fold + 1}: {accuracy:.4f}')
    print(f'Precision: {metrics[0]:.4f}, Recall: {metrics[1]:.4f}, F1-Score: {metrics[2]:.4f}')

    print(classification_report(
        y_val_classes, y_pred_classes,
        labels=labels,
        target_names=class_names,
        zero_division=0  # Prevents warnings when a class has no support
    ))

    accuracies.append(accuracy)
    precisions.append(metrics[0])
    recalls.append(metrics[1])
    f1s.append(metrics[2])

# Report average metrics
print(f'\nMean Validation Accuracy across 5 folds: {np.mean(accuracies):.4f}')
print(f'Mean Precision: {np.mean(precisions):.4f}, Mean Recall: {np.mean(recalls):.4f}, Mean F1-Score: {np.mean(f1s):.4f}')

# Train on all data
best_model.fit(X_padded, y, epochs=80, batch_size=32,
               callbacks=[ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=5),
                          EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)],
               class_weight=class_weight_dict,
               verbose=1)

# Evaluate on test data
loss, accuracy = best_model.evaluate(X_test, y_test)
y_pred = best_model.predict(X_test)
y_pred_classes = np.argmax(y_pred, axis=1)
y_test_classes = np.argmax(y_test, axis=1)
metrics = precision_recall_fscore_support(y_test_classes, y_pred_classes, average='weighted')

print(f'\nFinal Test Accuracy: {accuracy:.4f}')
print(f'Final Precision: {metrics[0]:.4f}, Final Recall: {metrics[1]:.4f}, Final F1-Score: {metrics[2]:.4f}')
print(classification_report(y_test_classes, y_pred_classes, labels=labels, target_names=class_names, zero_division=0))

# Export to TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(best_model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()
with open(r'D:\Generative AI\Project\Adaptive-Micro-Gesture-Recognition\models\gesture_model_3d_final.tflite', 'wb') as f:
    f.write(tflite_model)

# Save full Keras model
best_model.save(r'D:\Generative AI\Project\Adaptive-Micro-Gesture-Recognition\models\gesture_model_3d_final.keras')
