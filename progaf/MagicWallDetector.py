############################################
# PROGAF                                   #
# Projection Games Framework               #
############################################
# MagicWallDetector.py                     #
############################################
#
# 2021/04/28 Initial Release (by Keko)
#
############################################

from progaf.Detector import Detector, Detection
import numpy as np
import time
import cv2


class MagicWallDetector(Detector):
    """MagicWallDetector is a combined detector designed to work with depth cameras. The class performs detection of
    objects in the color frame and checks depth value in the depth frame, detecting only objects at a predefined
    distance (depth)"""

    def __init__(self, cam, proj):
        # Call the parent class (Detector) constructor
        super().__init__(cam, proj)

        # Rect Detector attributes
        self.cannyMinVal = 150
        self.cannyMaxVal = 200
        self.cannyKernSize = 3
        self.cannyL2Grad = False

        self.minArea = 500
        self.maxArea = 5000
        self.aspectRatio = 1.0
        self.aspectRatioError = 0.1

        # Log file
        self.log = open("WallDetectorLog.txt", "a")
        self.log.write("< --- New Run ({},{},{}) --- >".format(self.minArea, self.maxArea, self.aspectRatio))

    def update(self):

        # Keep looping infinitely until the thread is stopped
        while True:

            # If the thread stop indicator variable is set, stop the thread
            if self.isRunning is False:
                return

            # Check if a new frame is available
            if self.cam.frameIsNew is True:

                # Get starting time for performance monitoring
                start = time.time()

                # Grab Frame
                color_frame = self.cam.frame
                depth_frame = self.cam.depthFrame
                self.cam.frameIsNew = False

                # Process Frame and increase frame counter
                self.processFrame(color_frame, depth_frame)

                # Display Detected Contours when required
                if self.displayDetections is True:
                    self.display()

                # Track Detected contours when required
                if self.tracker is not None:
                    self.tracker.update(self.detections)

                self.frameCounter += 1
                # Get update loop end time and update performance monitor
                if self.perfMon is not None:
                    end = time.time()
                    self.perfMon.collectCDTSample(end - start)

    def processFrame(self, color_frame, depth_frame):

        self.log.write("\n< --- Frame {} --- >".format(self.cam.frameCounter))

        # Basic Canny Edge Detection
        fr_gray = cv2.cvtColor(color_frame, cv2.COLOR_BGR2GRAY)
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
        self.detections = []  # empty list
        for cnt in cnts:
            rotRect = cv2.minAreaRect(cnt)
            if rotRect[1][1] > 0:

                # Check Size and aspect Ratio Conditions
                if (0.9 * self.aspectRatio < (rotRect[1][0] / rotRect[1][1]) < 1.1 * self.aspectRatio and
                        self.minArea < (rotRect[1][0] * rotRect[1][1]) < self.maxArea):

                    self.detections.append(Detection(int(rotRect[0][0]), int(rotRect[0][1]), ("rotatedRect", rotRect)))

                    # Check depth condition

                    # Detection Center
                    cx, cy = int(rotRect[0][0]), int(rotRect[0][1])

                    # Detection Size (width)
                    size = int(rotRect[1][0]*0.75)

                    # ROI is a straight rect: p1, p2 (upper left, lower right) having 75% of the detection size
                    p1x, p1y = cx - size, cy - size
                    p2x, p2y = cx + size, cy + size
                    meanDepth = cv2.mean(depth_frame[p1y:p2y, p1x:p2x])

                    # Display info over detector frame
                    cv2.putText(self.frame, "D: {:.2f}".format(meanDepth[0]),
                                (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (255, 255, 255), 1)

                    # Log to file
                    self.log.write("D:{:.2f};".format(meanDepth[0]))

                    # # rotRect type is tuple ((cx,xy),(w,h),a)
                    # detection = ("Ball",  # object type
                    #              rotRect[1][0],  # object width
                    #              rotRect[1][1],  # object height
                    #              rotRect[2])     # object rotation
                    # self.detections.append(Detection(int(rotRect[0][0]), int(rotRect[0][1]), detection))

    def display(self):
        ################################
        # Display detections
        # This method displays detections, for debugging purposes, over:
        # - Camera    frames when self.displayOnCamera    == True
        # - Projector frames when self.displayOnProjector == True
        ########################################################################
        # Display Centroids
        super().display()

        # Display Contours
        for detection in self.detections:
            # in this loop:
            # box  is a rotatedBox for the detected contour (type is float numpy array of four points)
            # rect ia a rotatedRect for the detected contour (type is tuple, see above)

            # Display over camera frames
            blue = (255, 0, 0)
            if self.displayOnCamera is True:
                if detection.detection[0] == "rotatedRect":
                    box = cv2.boxPoints(detection.detection[1])
                    box = np.int0(box)
                    cv2.drawContours(self.cam.frame, [box], 0, blue, 2)

            # Display over projector frames
            white = (255, 255, 255)
            if self.displayOnProjector is True:
                # self.proj.drawContours(np.int0(box), white)
                self.proj.drawCircle(detection.xpos, detection.ypos, white)
