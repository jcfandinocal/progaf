############################################
# PROGAF                                   #
# Projection Games Framework               #
############################################
# Camera.py                                #
############################################
#
# 2021/02/25 Initial Release (by Keko)
#
############################################
from threading import Thread
import numpy as np
import time
import cv2
import sys


class Camera:
    """ Camera class represents a camera. The class supports various frame
related operations (read, write, crop, flip, undistort, ...) Live frames are
captured from the camera device using an independent thread, that can be
started and stopped using the provided methods. The independent thread used to read actual
frames from the camera object allows the read() method to be non-blocking.
Objects of this class are not started by default. The object can also be
initialized to read frames from a video file, passing a filename to the
constructor instead of the live stream id. Framerate is not contolled or
limited when reading from a file, so do not expect 'realistic' framerates
when reading from files.

**Class Attributes**:
    **- src** contains the source stream for the object. Source can be an
    index to a video stream or a filename

    **- width** contains the frame width in pixels

    **- height** contains the frame height in pixels

    **- cameraMatrix** contains the intrinsic and extrinsic parameters for
    the camera

    **- cameraDistor** contains the distortion coefficients for the camera
    """

    def __init__(self, src, width, height, cameraMatrix, cameraDistor):
        """
        :param src: contains the source stream for the object. Source can be
               an index to a video stream (example: '0' for /dev/video0 in
               linux) or a filename (example: 'video.mp4')
        :param width: contains the frame width in pixels
        :param height: contains the frame height in pixels
        :param cameraMatrix: contains the intrinsic and extrinsic parameters
               for the camera as calculated by OpenCV
        :param cameraDistor: contains the distortion coefficients for the
               camera as calculated by OpenCV
        """

        # Class attributes
        self.isRunning = False
        self.stream = None
        self.source = None
        self.frame = None
        self.frameWidth = None
        self.frameHeight = None
        self.frameIsNew = False
        self.frameIsValid = False
        self.frameCounter = 0
        self.flip = True
        self.undist = False
        self.crop = False
        self.cropx1 = None
        self.cropx2 = None
        self.cropy1 = None
        self.cropy2 = None
        self.displayCrop = False
        self.displayGrid = False
        self.displayFPS = True
        self.capturePath = ".\\captures\\"

        self.frameIsNew = False
        self.frameIsValid = False
        self.source = None
        self.profiler = None

        # Default value for camera intrinsic/extrinsic coefficients
        if cameraMatrix is not None:
            self.cameraMatrix = cameraMatrix
        else:
            self.cameraMatrix = np.array([[500.0000000000, 0.000000000000, 500.00000000],
                                          [0.000000000000, 500.0000000000, 500.00000000],
                                          [0.000000000000, 0.000000000000, 1.0000000000]])

        # Default value for camera distortion coefficients
        if cameraDistor is not None:
            self.cameraDistor = cameraDistor
        else:
            self.cameraDistor = np.zeros(5)

        # Source selection
        # Check if we have a integer indicator as source
        if type(src) == int:
            # Initialize from Stream
            self.initFromStream(src, width, height)
        else:
            # Initialize from file
            self.initFromFile(src)

    def initFromStream(self, src, width, height):
        """
        Initialize the camera object using a camera device as a video source

        :param src:
        :param width:
        :param height:
        """

        # Check if a previous stream is active and release it
        restartUpdateIsRequired = False
        if self.stream is not None:
            # Stop the update thread
            self.stop()
            restartUpdateIsRequired = True

        # Set new source
        self.source = src

        # Initialize the camera stream and read the first frame
        if sys.platform == "linux":
            self.stream = cv2.VideoCapture(self.source, cv2.CAP_V4L2)
        elif sys.platform == "windows":
            self.stream = cv2.VideoCapture(self.source, cv2.CAP_DSHOW)

        # Check if the stream is open
        if self.stream.isOpened() is False:
            print("Error: Camera.InitFromStream" 
                  " unable to open stream {}".format(self.source))

        # Set camera parameters
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        # self.stream.set(cv2.CAP_PROP_SETTINGS, 	None)

        # Get actual camera parameters, after setting them.
        # This is required because, usually, not all resolutions are supported and
        # actual values can differ from the ones we just set before
        self.frameWidth = int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frameHeight = int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Set Crop default values if required
        if self.cropx1 is None:
            # Set Cropping default values (50 pixels border)
            self.cropx1 = 50
            self.cropx2 = self.frameWidth - 50
            self.cropy1 = 50
            self.cropy2 = self.frameHeight - 50

        # Read a first Frame and store it!!!
        # This is required for the case when the Camera.read() method
        # is called before the update thread is started and a processed frame
        # is available. In this case, a single raw frame will be available.
        # ToDo: Add error checking code here
        # self.frameIsValid, self.frame = self.stream.read()

        # Restart update thread if required
        if restartUpdateIsRequired is True:
            self.start()

    def initFromFile(self, src):
        # Initialize the camera object using video from a file

        # Check if a previous stream is opened and release it
        restartUpdateIsRequired = False
        if self.stream is not None:
            # Stop the update thread
            self.stop()
            restartUpdateIsRequired = True

        # Set new source
        self.source = src

        # Initialize the camera stream and read the first frame
        self.stream = cv2.VideoCapture(src)

        # Check if the stream is open
        if self.stream.isOpened() is False:
            print("Error: Camera.InitFromFile unable to open file {}".format(self.source))

        self.frameWidth = int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frameHeight = int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Set Crop default values if required
        if self.cropx1 is None:
            # Set Cropping default values (50 pixels border)
            self.cropx1 = 50
            self.cropx2 = self.frameWidth - 50
            self.cropy1 = 50
            self.cropy2 = self.frameHeight - 50

        # Read a first Frame and store it!!!
        # This is required for the case when the Camera.read() method
        # is called before the update thread is started and a processed frame
        # is available. In this case, a single raw frame will be available.
        # ToDo: Add error checking code here
        # self.frame = self.stream.read()
        # self.frameIsValid = False

        # Restart update thread if required
        if restartUpdateIsRequired is True:
            self.start()

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

            # Read the next frame from the stream
            ok, frame = self.stream.read()

            # Frame Pre-processing: Un-distort, Crop, Save
            if ok:

                # Flip
                if self.flip is True:
                    frame = cv2.flip(frame, 1)

                # Un-distort
                if self.undist is True:
                    frame = cv2.undistort(frame, self.cameraMatrix, self.cameraDistor)

                # Draw grid
                if self.displayGrid is True:
                    self.drawGrid(frame)

                # Display cropping area (only when frame isn't cropped)
                if self.displayCrop is True and self.crop is False:
                    self.drawCropArea(frame)

                # Crop
                if self.crop is True:
                    frame = frame[self.cropy1:self.cropy2, self.cropx1:self.cropx2]

                # FPS
                if self.displayFPS is True:
                    self.drawFPS(frame)

                # Set properties for the new frame
                self.frame = frame
                self.frameIsValid = True
                self.frameIsNew = True
                self.frameCounter += 1

            else:
                self.stop()

            # Get loop end time and update performance monitor
            if self.profiler is not None:
                end = time.time()
                self.profiler.collectFATSample(end - start)

    def drawGrid(self, frame):
        pixels = 0
        white = (255, 255, 255)
        thickness = 1
        w = self.frameWidth
        h = self.frameHeight
        # Reference Lines
        cv2.line(frame, (0 + pixels, int(h / 2)), (w - pixels, int(h / 2)), white, thickness)
        cv2.line(frame, (int(w / 2), 0 + pixels), (int(w / 2), h - pixels), white, thickness)
        # Frame Center
        cv2.drawMarker(frame, (int(w / 2), int(h / 2)), white, cv2.MARKER_SQUARE)

    def setCropArea(self, roi):
        self.cropx1 = roi[0]
        self.cropy1 = roi[1]
        self.cropx2 = roi[0] + roi[2]
        self.cropy2 = roi[1] + roi[3]

    def drawCropArea(self, frame):
        red = (0, 0, 255)
        p1 = (self.cropx1, self.cropy1)
        p2 = (self.cropx2, self.cropy2)
        cv2.rectangle(frame, p1, p2, red)

    def drawFPS(self, frame):
        white = (255, 255, 255)

        # Get actual FPS value from profiler object if available
        if self.profiler is not None:
            fps = self.profiler.cameraFramesPerSecond
        else:
            fps = 0

        # Put text over frame
        cv2.putText(frame,"FPS: {:.2f}".format(fps), (self.frameWidth-100, 20), cv2.FONT_HERSHEY_PLAIN, 1, white)


    def read(self):
        # return the last available frame read
        return self.frameIsValid, self.frame

    def writeToFile(self):
        # save last valid frame to file
        filename = "Camera {} frame {}.png".format(time.strftime("%H-%M"), self.frameCounter)
        cv2.imwrite(self.capturePath + filename, self.frame)

    def stop(self):
        if self.isRunning is False:
            return

        # Stop update thread
        self.isRunning = False

        # Stop source
        self.stream.release()
