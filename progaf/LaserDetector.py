############################################
# PROGAF                                   #
# Projection Games Framework               #
############################################
# LaserDetector.py                         #
############################################
#
# 2021/02/25 Initial Release (by Keko)
#
############################################
from progaf.Detector import Detector
import numpy as np
import cv2


class LaserDetector(Detector):

    def __init__(self, cam, proj):
        # Call the parent class (Detector) constructor
        super().__init__(cam, proj)

        # Default HSV values (red laser sample)
        self.hue_min = 170
        self.hue_max = 180
        self.sat_min = 20
        self.sat_max = 30
        self.val_min = 240
        self.val_max = 255

    def processFrame(self, frame):

        frame_HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        laserL = np.array([self.hue_min, self.sat_min,  self.val_min], np.uint8)
        laserH = np.array([self.hue_max, self.sat_max, self.val_max], np.uint8)

        frame_threshold = cv2.inRange(frame_HSV, laserL, laserH)

        # Store Detector frame
        # This is a B/W Frame (No drawing allowed on it) containing just edges.
        # Usually used for debugging purposes.
        self.frame = frame_threshold
        self.frameIsValid = True
