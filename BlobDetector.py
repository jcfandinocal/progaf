############################################
# PROGAF                                   #
# Projection Games Framework               #
############################################
# BlobDetector.py                          #
############################################
#
# 2021/02/25 Initial Release (by Keko)
#
############################################

from Detector import Detector, Detection
import numpy as np
import cv2


class BlobDetector(Detector):

    def __init__(self, cam, proj):
        # Call the parent class (Detector) constructor
        super().__init__(cam, proj)

        # OpenCV Simple Blob Detector attributes
        self.detector = cv2.SimpleBlobDetector_create()

    def processFrame(self, frame):

        # Blob detection
        keyPoints = self.detector.detect(frame)

        # Generate a debug frame including detected keyPoints
        debugFrame = cv2.drawKeypoints(frame, keyPoints, np.array([]), (0, 0, 255),
                                       cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        # Store Detector frame for debugging purposes.
        # This frame is retrieved using self.read()
        self.frame = debugFrame
        self.frameIsValid = True

        self.detections = []  # empty list
        for point in keyPoints:

            detection = ("Blob",
                         int(point.size),
                         point.class_id,
                         point.response,
                         point.angle)
            self.detections.append(Detection(int(point.pt[0]), int(point.pt[1]), detection))
