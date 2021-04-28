############################################
# PROGAF                                   #
# Projection Games Framework               #
############################################
# DepthCamera.py                           #
############################################
#
# 2021/04/24 Initial Release (by Keko)
#
############################################
from progaf.Camera import Camera
from threading import Thread
import pyrealsense2 as rs
import numpy as np
import time
import cv2


class DepthCamera(Camera):
    """ Depth Camera class represents a depth camera"""

    def __init__(self, src, width, height, cameraMatrix, cameraDistor):
        # Call the parent class (Detector) constructor
        super().__init__(src, width, height, cameraMatrix, cameraDistor)

        self.depthFrame = None
        self.flip = False

    def initFromStream(self, src, width, height):
        """ Initialize the camera object using a camera device as a video source"""

        # Realsense objects
        # noinspection PyArgumentList
        pipeline = rs.pipeline()
        config = rs.config()

        # Configure color and depth frame formats
        config.enable_stream(rs.stream.depth, width, height, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, 30)
        self.frameWidth = width
        self.frameHeight = height

        # Set new source
        self.source = src

        # Start RealSense Pipeline
        self.stream = pipeline
        self.stream.start(config)

        # Set Crop default values if required
        if self.cropx1 is None:
            # Set Cropping default values (50 pixels border)
            self.cropx1 = 50
            self.cropx2 = self.frameWidth - 50
            self.cropy1 = 50
            self.cropy2 = self.frameHeight - 50

    def start(self):
        # Start the thread to read frames
        self.isRunning = True
        Thread(target=self.update, args=()).start()
        return self

    def update(self):

        # Keep looping infinitely until the thread is stopped
        while True:
            # Get update loop starting time for performance monitoring
            start = time.time()

            # Check status and stop thread if required
            if self.isRunning is False:
                return

            # Wait for a coherent pair of frames
            frames = self.stream.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            if not depth_frame or not color_frame:
                print("Waiting for a coherent pair of frames...")
                continue  # start the loop again

            # Convert images to numpy arrays
            depth_frame = np.asanyarray(depth_frame.get_data())
            color_frame = np.asanyarray(color_frame.get_data())

            # Apply colormap to depth image (image must be converted to 8-bit per pixel first)
            depth_frame = cv2.applyColorMap(cv2.convertScaleAbs(depth_frame, alpha=0.03), cv2.COLORMAP_JET)

            # Flip
            if self.flip is True:
                depth_frame = cv2.flip(depth_frame, 1)
                color_frame = cv2.flip(color_frame, 1)

            # Draw grid
            if self.displayGrid is True:
                self.drawGrid(color_frame)

            # Display cropping area (only when frame isn't cropped)
            if self.displayCrop is True and self.crop is False:
                self.drawCropArea(color_frame)

            # Crop
            if self.crop is True:
                color_frame = color_frame[self.cropy1:self.cropy2, self.cropx1:self.cropx2]
                depth_frame = depth_frame[self.cropy1:self.cropy2, self.cropx1:self.cropx2]

            # Set properties for the new frame
            self.frame = color_frame
            self.depthFrame = depth_frame
            self.frameIsValid = True
            self.frameIsNew = True
            self.frameCounter += 1

            # Get loop end time and update performance monitor
            if self.profiler is not None:
                end = time.time()
                self.profiler.collectFATSample(end - start)

    def stop(self):
        if self.isRunning is False:
            return

        # Stop update thread
        self.isRunning = False

        # Stop RealSense Stream
        self.stream.stop()

    def read(self):
        # return the last available frame read
        return self.frameIsValid, self.frame
