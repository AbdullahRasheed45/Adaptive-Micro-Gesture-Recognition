# # import os
# # import cv2
# # import mediapipe as mp

# # def create_directories():   
# #     dirs = ['data', 'models', 'app', 'templates', 'static']
# #     for d in dirs:
# #         os.makedirs(d, exist_ok=True)

# # def test_mediapipe():
# #     mp_hands = mp.solutions.hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
# #     mp_drawing = mp.solutions.drawing_utils
# #     cap = cv2.VideoCapture(0)
# #     if not cap.isOpened():
# #         print("Error: Could not open webcam.")
# #         return
# #     while cap.isOpened():
# #         ret, frame = cap.read()
# #         if not ret:
# #             print("Error: Could not read frame.")
# #             break
# #         frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
# #         results = mp_hands.process(frame_rgb)
# #         if results.multi_hand_landmarks:
# #             for hand_landmarks in results.multi_hand_landmarks:
# #                 mp_drawing.draw_landmarks(frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)
# #         cv2.imshow('MediaPipe Hand Tracking Test', frame)
# #         if cv2.waitKey(1) & 0xFF == ord('q'):
# #             break
# #     cap.release()
# #     cv2.destroyAllWindows()

# # if __name__ == "__main__":
# #     create_directories()
# #     print("Directory structure created.")
# #     print("Testing MediaPipe hand tracking. Press 'q' to quit.")
# #     test_mediapipe()

# # import cv2
# # img = cv2.imread('data/leapgestrecog/leapGestRecog/00/01_palm/frame_00_01_0001.png')
# # print(img.shape if img is not None else "Image not loaded")

# # import cv2
# # import mediapipe as mp
# # mp_hands = mp.solutions.hands.Hands(max_num_hands=1, min_detection_confidence=0.5)
# # img = cv2.imread('data/leapgestrecog/leapGestRecog/00/01_palm/frame_00_01_0001.png')
# # results = mp_hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
# # print(len(results.multi_hand_landmarks[0].landmark) if results.multi_hand_landmarks else "No landmarks detected")

# import pandas as pd
# df = pd.read_csv('.\data\processed\micro_gestures.csv')
# print(df.shape)
# print(df['label'].value_counts())
import pandas as pd
df = pd.read_csv('D:\\Generative AI\\Project\\Adaptive-Micro-Gesture-Recognition\\data\\processed\\micro_gestures.csv')
print("Unique labels:", sorted(df['label'].unique()))
print("Label distribution:\n", df['label'].value_counts())