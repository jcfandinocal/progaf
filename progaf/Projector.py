############################################
# PROGAF                                   #
# Projection Games Framework               #
############################################
# Projector.py                             #
############################################
#
# 2021/02/25 Initial Release (by Keko)
#
############################################
from progaf.ShapeFactory import ShapeFactory
from threading import Thread
import numpy as np
import cv2


class Projector:

    def __init__(self, width, height, affineMatrix=None, createShapeFactory=False):
        self.width = width
        self.height = height
        self.frame = np.zeros((height, width, 3), np.uint8)
        self.frameCounter = 0
        self.isRunning = False
        self.shapeFactory = None
        self.gridIsActive = True
        self.gridBorderOffset = 15

        # Affine transformation matrix default value
        if affineMatrix is not None:
            self.transform = Transform(affineMatrix)
        else:
            # Default Value
            affineMatrix = np.array([[1, 0, 0],
                                     [0, 1, 0]])
            self.transform = Transform(affineMatrix)

        # Layers Support
        self.layerAFrame = np.zeros((height, width, 3), np.uint8)
        self.layerBFrame = np.zeros((height, width, 3), np.uint8)
        self.layerAIsActive = True
        self.layerBIsActive = True
        self.layerCIsActive = False

        # shapeFactory initialization
        if createShapeFactory is True:
            self.shapeFactory = ShapeFactory(self.width, self.height)

        for i in range(0, 0):
            self.shapeFactory.createRandomObject()

    def start(self):
        self.isRunning = True
        Thread(target=self.update, args=()).start()
        return self

    def update(self):

        # Keep looping infinitely until the thread is stopped
        while True:
            # If the thread stop indicator variable is set, stop the thread
            if self.isRunning is False:
                return

            # Shape Factory integration
            # uses Layer A frame
            if self.shapeFactory is not None:
                # Update Shape Factory objects on the frame
                self.layerAFrame = self.shapeFactory.update()

            # If Grid Is active, uses Layer A
            if self.gridIsActive is True:
                self.drawGrid(self.layerAFrame)

            # Fuse Layers as required
            # OpenCV addition is a saturated operation
            # 250+10 = 260 => 255
            if self.layerAIsActive is True and self.layerBIsActive is True:
                self.frame = cv2.add(self.layerAFrame, self.layerBFrame)
            elif self.layerAIsActive is True:
                self.frame = self.layerAFrame
            else:
                self.frame = self.layerBFrame

            # Delay
            # time.sleep(0.1)

            # Increase Frame Counter
            self.frameCounter += 1

    def read(self):
        return True, self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.isRunning = False

    #
    # Drawing operations used by Detector and CentroidTracker use Layer B
    #
    def clear(self):
        self.layerBFrame = np.zeros((self.height, self.width, 3), np.uint8)

    def drawContours(self, box, colour):
        tbox = self.transform.Box(box)
        cv2.drawContours(self.layerBFrame, [tbox], 0, colour, 2)

    def drawCircle(self, x, y, colour):
        cv2.circle(self.layerBFrame, (self.transform.Point(x, y)), 5, colour, -1)

    def drawText(self, text, x, y, colour):
        cv2.putText(self.layerBFrame, text, (self.transform.Point(x, y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colour, 1)

    #
    # Grid
    #
    def drawGrid(self, frame):

        pixels = self.gridBorderOffset
        white = (255, 255, 255)
        th = 1
        cv2.line(frame, (0 + pixels, 0 + pixels), (self.width - pixels, 0 + pixels), white, th)
        cv2.line(frame, (0 + pixels, self.height - pixels), (self.width - pixels, self.height - pixels), white, th)
        cv2.line(frame, (0 + pixels, 0 + pixels), (0 + pixels, self.height - pixels), white, th)
        cv2.line(frame, (self.width - pixels, 0 + pixels), (self.width - pixels, self.height - pixels), white, th)
        cv2.line(frame, (0 + pixels, int(self.height / 2)), (self.width - pixels, int(self.height / 2)), white, th)
        cv2.line(frame, (int(self.width / 2), 0 + pixels), (int(self.width / 2), self.height - pixels), white, th)

        cv2.drawMarker(frame, (int(self.width / 2), int(self.height / 2)), cv2.MARKER_CROSS)

    #
    # Set Transform
    #
    def setTransform(self, roi):

        # Calculate Camera Plane points
        cameraP1 = (roi[0], roi[1])
        cameraP2 = (roi[0] + roi[2], roi[1])
        cameraP3 = (roi[0] + roi[2], roi[1] + roi[3])

        # Calculate Projector Plane points
        pixels = self.gridBorderOffset
        projectorP1 = (pixels, pixels)
        projectorP2 = (self.width - pixels, pixels)
        projectorP3 = (self.width - pixels, self.height - pixels)

        # Create numpy arrays
        cam_plane = np.array((cameraP1, cameraP2, cameraP3)).astype(np.float32)
        prj_plane = np.array((projectorP1, projectorP2, projectorP3)).astype(np.float32)

        # Calculate affine transformation matrix
        affineMatrix = cv2.getAffineTransform(cam_plane, prj_plane)

        # Set the new affine transformation matrix
        self.transform.affineMatrix = affineMatrix


class Transform:

    def __init__(self, affineMatrix):
        self.affineMatrix = affineMatrix

    def Point(self, x, y):
        p = np.float32([x, y, 1])
        p_proy = self.affineMatrix.dot(p)
        p_proy = p_proy[:2]
        return int(p_proy[0]), int(p_proy[1])

    def Box(self, box):
        r = np.asarray(((self.Point(int(box[0][0]), int(box[0][1]))),
                        (self.Point(int(box[1][0]), int(box[1][1]))),
                        (self.Point(int(box[2][0]), int(box[2][1]))),
                        (self.Point(int(box[3][0]), int(box[3][1])))
                        ))
        return r
