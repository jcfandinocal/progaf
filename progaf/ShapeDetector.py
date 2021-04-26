############################################
# PROGAF                                   #
# Projection Games Framework               #
############################################
# ShapeDetector.py                         #
############################################
#
# 2021.03.24 Initial Release (by Dani)
#
############################################
from Detector import Detector, Detection
import numpy as np
import math
import cv2


class ShapeDetector(Detector):
    """
    This class performs detection of shapes contained in a predefined
    dictionary. Blobs in image are detected using connected components, and
    for each blob (except background) hu-moments are calculated and compared
    with the contents of the dictionary. Shapes in image should be white
    (or clear) over a darker background. If the case is opposite, thresholding
    parameter should be changed from cv2.THRESH_BINARY to cv2.THRESH_BINARY_INV.
    """

    def __init__(self, cam, proj):
        # Call the parent class (Detector) constructor
        super().__init__(cam, proj)

        # Detector attributes
        self.detected_shapes_and_attributes = []

        # Dictionary of shapes
        self.shapes = {'square': 3.1846, 'circle': 3.2047,
                       'triangle': 3.1227, 'rhombus': 3.1735,
                       '6-point-star': 3.1633, 'pentagon': 3.1967}

        # Tolerance applied to detected hu-moment vs dictionary hu-moment
        self.humoment_tolerance = 0.001

    def processFrame(self, frame):

        # Convert to grayscale and threshold
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # Apply connected components analysis to the threshold image
        output = cv2.connectedComponentsWithStats(thresh, 4, cv2.CV_32S)
        (numLabels, labels, stats, centroids) = output

        # Contour Selection
        # self.proj.clear()
        self.detections = []  # empty list

        # Loop over the number of unique connected component labels excluding background (index 0)
        for i in range(1, numLabels):
            w = stats[i, cv2.CC_STAT_WIDTH]
            h = stats[i, cv2.CC_STAT_HEIGHT]
            (cX, cY) = centroids[i]

            # Construct a mask for the current connected component by finding
            # pixels in the labels array that have the current connected
            # component ID
            componentMask = (labels == i).astype("uint8") * 255
            # Calculate hu-moments and take the first one in log scale
            moments = cv2.moments(componentMask)
            huMoments = cv2.HuMoments(moments)
            huMoments[0] = -1 * math.copysign(1.0, huMoments[0]) * np.log10(abs(huMoments[0]))

            # Look-up in the dictionary
            shapeType = None
            for j in range(len(self.shapes)):
                if (list(self.shapes.items())[j][1]) * int(1 + self.humoment_tolerance) >= huMoments[0] >= (
                        list(self.shapes.items())[j][1]) * int(1 - self.humoment_tolerance):
                    shapeType = str(list(self.shapes.items())[j][0])
                    break
                else:
                    shapeType = "unknown"

            # Extract shape angle
            cnt, hierarchy = cv2.findContours(componentMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            rect = cv2.minAreaRect(cnt[0])
            angle = rect[2]

            # Add shape info to debug frame
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(thresh, [box], 0, (0, 0, 255), 1)
            cv2.putText(thresh, shapeType, (int(cX + 10), int(cY)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

            # Append shape to detected objects
            # 'detection' type is tuple
            detection = (shapeType,  # shape type
                         w,          # shape width
                         h,          # shape height
                         angle)      # shape rotation
            self.detections.append(Detection(int(cX), int(cY), detection))

        # Store Detector frame for debugging purposes.
        # This frame is retrieved using self.read()
        self.frame = thresh
        self.frameIsValid = True
