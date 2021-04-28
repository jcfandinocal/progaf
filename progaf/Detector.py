############################################
# PROGAF                                   #
# Projection Games Framework               #
############################################
# Detector.py                              #
############################################
#
# 2021/02/25 Initial Release (by Keko)
#
############################################
from threading import Thread
import time
import cv2


class Detection:
    """ Base class for all Object Detections."""
    def __init__(self, xpos, ypos, obj):
        self.xpos = xpos
        self.ypos = ypos

        self.detection = obj
        # 'object' contains a tuple, with object attributes, depending on the
        # type of the detected object. Check different detectors for the actual
        # information included. Some examples:
        # ("RotatedRect", width, height, angle)
        # ("Blob", size, class_id, response, angle)


class Detector:
    """ Base class for all Detectors."""

    def __init__(self, cam, proj):
        # Initialize the detector
        self.cam = cam
        self.proj = proj

        # Initialize class attributes
        self.detections = None
        self.isRunning = False
        self.frameCounter = 0
        self.frame = None
        self.frameIsValid = False

        self.displayDetections = True
        self.displayOnCamera = True
        self.displayOnProjector = False

        self.perfMon = None

        # Initialize the Tracker
        self.tracker = None

    def start(self):
        # Start the thread to read frames
        self.isRunning = True
        Thread(target=self.update, args=()).start()
        return self

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
                local_frame = self.cam.frame
                self.cam.frameIsNew = False

                # Process Frame and increase frame counter
                self.processFrame(local_frame)

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

    def processFrame(self, frame):
        # This is an abstract method to be implemented in sub-classes when
        # required. The method will be invoked by Detector, passing
        # the actual camera frames as a parameter.
        return None

    def display(self):
        ################################
        # Display detections
        # This method displays detections, for debugging purposes, over:
        # - Camera    frames when self.displayOnCamera    == True
        # - Projector frames when self.displayOnProjector == True
        ########################################################################

        # Display detected contours
        for detection in self.detections:
            # in this loop:
            # box  is a rotatedBox for the detected contour (type is float numpy array of four points)
            # rect ia a rotatedRect for the detected contour (type is tuple, see above)

            # Display over camera frames
            blue = (255, 0, 0)
            if self.displayOnCamera is True:
                cv2.circle(self.cam.frame, (detection.xpos, detection.ypos), 5, blue, -1)

            # Display over projector frames
            white = (255, 255, 255)
            if self.displayOnProjector is True:
                # self.proj.drawContours(np.int0(box), white)
                self.proj.drawCircle(detection.xpos, detection.ypos, white)

    def read(self):
        ################################
        # This method returns the last processed frame. The frame is actually
        # stored inside processFrame method.
        ########################################################################
        return self.frameIsValid, self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.isRunning = False
