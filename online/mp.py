from typing import List

import cv2
import mediapipe as mp
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QLabel, QDialog, QVBoxLayout
from PyQt5.QtGui import QImage, QPixmap
import sys,time

# Initialize MediaPipe
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


class HandLandmarkThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    coordinates_signal = pyqtSignal(list)  # Signal to emit coordinates
    cameraReadySignal = None
    dead_signal = pyqtSignal()  # Signal to emit coordinates
    running = True
    last_query_time = time.time()

    def __init__(self, parent = None):
        super().__init__(parent)

    def setCameraReadySignal(self,sig):
        self.cameraReadySignal = sig

    def stopRunning(self):
        self.running = False
    def run(self):
        # Start video capture (use 0 for the default webcam)
        self.last_query_time = time.time()
        cap = cv2.VideoCapture(0)
        with mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        ) as hands:
            st = time.time()
            print('cam started',st)
            self.cameraReadySignal.emit()
            while cap.isOpened() and self.running:
                if time.time() > self.last_query_time+5: # No activity for 5 seconds.
                    self.running = False
                success, image = cap.read()
                if not success:
                    continue

                # Convert image to RGB for processing
                image.flags.writeable = False
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = hands.process(image_rgb)

                # Draw hand landmarks and emit the coordinates
                image.flags.writeable = True
                image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        self.last_query_time = time.time()
                        mp_drawing.draw_landmarks(
                            image_bgr,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS,
                            mp_drawing_styles.get_default_hand_landmarks_style(),
                            mp_drawing_styles.get_default_hand_connections_style()
                        )
                        # Emit the coordinates of the index finger tip
                        image_height, image_width, _ = image.shape
                        #index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                        #coords = (index_finger_tip.x * image_width, index_finger_tip.y * image_height)
                        # Get coordinates for all landmarks
                        hand_coords = []
                        for landmark in hand_landmarks.landmark:
                            x = landmark.x * image_width
                            y = landmark.y * image_height
                            hand_coords.append((x, y))
                        self.coordinates_signal.emit(hand_coords)
                        break #only need one hand for now.

                # Convert to QImage and emit signal to update the UI
                qt_image = self.convert_cv_qt(image_bgr)
                self.change_pixmap_signal.emit(qt_image)

                if (not self.running):  # Close
                    break

        cap.release()
        self.dead_signal.emit()

    def convert_cv_qt(self, cv_img):
        """Convert from an OpenCV image to QImage for display."""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return qt_image

    def ping(self):
        self.last_query_time = time.time()

