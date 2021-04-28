############################################
# PROGAF                                   #
# Projection Games Framework               #
############################################
# HandDetector.py                          #
############################################
#
# 2021/04/14 Initial Release (by Keko)
#
############################################
from progaf.Detector import Detector, Detection
import mediapipe as mp
import cv2


class HandDetector(Detector):

    def __init__(self, cam, proj):
        # Call the parent class (Detector) constructor
        super().__init__(cam, proj)

        # Hands Detector attributes
        self.mpHands = mp.solutions.hands
        self.mpDraw = mp.solutions.drawing_utils
        self.hands = self.mpHands.Hands()

    def processFrame(self, frame):

        # Convert to RGB
        fr_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect Hands
        result = self.hands.process(fr_rgb)

        # Extract hands. Store on detector frame for debugging
        self.detections = []  # empty list
        self.frame = frame
        if result.multi_hand_landmarks is not None:
            for hand in result.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(frame, hand, self.mpHands.HAND_CONNECTIONS)

                # Store detections
                detection = ("FingerTip",       # object type
                             "Index Finger")    # object type
                x = hand.landmark[12].x * self.cam.frameWidth
                y = hand.landmark[12].y * self.cam.frameHeight
                self.detections.append(Detection(int(x), int(y), detection))

        self.frameIsValid = True
