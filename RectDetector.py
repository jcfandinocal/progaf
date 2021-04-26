############################################
# PROGAF                                   #
# Projection Games Framework               #
############################################
# RectDetector.py                          #
############################################
#
# 2021/02/25 Initial Release (by Keko)
#
############################################
from Detector import Detector, Detection
import cv2


class RectDetector(Detector):

    def __init__(self, cam, proj):
        # Call the parent class (Detector) constructor
        super().__init__(cam, proj)

        # Rect Detector attributes
        self.cannyMinVal = 150
        self.cannyMaxVal = 200
        self.cannyKernSize = 3
        self.cannyL2Grad = False

        self.minArea = 500
        self.maxArea = 50000
        self.aspectRatio = 1.0
        self.aspectRatioError = 0.1

    def processFrame(self, frame):

        # Basic Canny Edge Detection
        fr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        fr_edges = cv2.Canny(fr_gray, self.cannyMinVal, self.cannyMaxVal, None, self.cannyKernSize, self.cannyL2Grad)

        # Store Detector frame
        # This is a B/W Frame (No drawing allowed on it) containing just edges.
        # Usually used for debugging purposes. Can be retrieved using
        # RectDetector.read()
        self.frame = fr_edges
        self.frameIsValid = True

        # Find and sort Contours
        cnts, hierarchy = cv2.findContours(fr_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[0:100]

        # Contour Selection
        # self.proj.clear()
        self.detections = []  # empty list
        for cnt in cnts:
            rotRect = cv2.minAreaRect(cnt)
            if rotRect[1][1] > 0:
                if (0.9 * self.aspectRatio < (rotRect[1][0] / rotRect[1][1]) < 1.1 * self.aspectRatio and
                        self.minArea < (rotRect[1][0] * rotRect[1][1]) < self.maxArea):

                    # rotRect type is tuple ((cx,xy),(w,h),a)
                    detection = ("RotatedRect",  # object type
                                 rotRect[1][0],  # object width
                                 rotRect[1][1],  # object height
                                 rotRect[2])     # object rotation
                    self.detections.append(Detection(int(rotRect[0][0]), int(rotRect[0][1]), detection))
