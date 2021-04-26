############################################
# PROGAF                                   #
# Projection Games Framework               #
############################################
# Application.py                           #
############################################
#
# 2021/04/14 Initial Release (by Keko)
#
############################################
from CentroidTracker import CentroidTracker
from Projector import Projector
from Profiler import Profiler
from collections import OrderedDict
from Camera import Camera


class Application:
    """Application encapsulates the Application logic"""

    def __init__(self):
        # Class attributes
        self.isRunning = False
        self.isStopped = True
        self.camera = None
        self.detector = None
        self.tracker = None
        self.projector = None
        self.profiler = None
        self.monitor = None
        self.screen = None

        # This is the list of all objects being tracked
        self.trackerObjects = OrderedDict()
        self.trackerObjectStatus = OrderedDict()
        self.trackerUpdateFlag = False

    def setCamera(self, src, width, height, cameraMatrix=None, cameraDistor=None):
        self.camera = Camera(src, width, height, cameraMatrix, cameraDistor)

    def setProjector(self, width, height, transform=None, createShapeFactory=False):
        self.projector = Projector(width, height, transform, createShapeFactory)

    def setDetector(self, detector):
        self.detector = detector

    def setTracker(self):
        self.tracker = CentroidTracker(self.detector, self, 20)

    def enableMonitor(self, updateRate=1):
        # self.monitor = Monitor(self.camera, self.detector, self.tracker, self.projector)
        self.profiler = Profiler(updateRate, self.camera, self.detector, self.tracker, self.projector, self.monitor)

    def start(self):
        if self.camera is not None:
            self.camera.start()
        if self.detector is not None:
            self.detector.start()
        if self.projector is not None:
            self.projector.start()
        if self.monitor is not None:
            self.monitor.start()
        if self.profiler is not None:
            self.profiler.start()

        return self

    def gameLoop(self):
        # This is an abstract method to be implemented in sub-classes,
        # containing the main game loop
        return None

    def updateTrackedObjects(self):
        # This is an abstract method to be implemented in sub-classes,
        # responsible of updating tracked objects in the game application
        return None


    def stop(self):
        # Stop update thread
        self.isRunning = False

        # stop framework objects
        if self.profiler is not None:
            self.profiler.stop()
        if self.projector is not None:
            self.projector.stop()
        if self.detector is not None:
            self.detector.stop()
        if self.camera is not None:
            self.camera.stop()

    def close(self):
        # stop game loop (non blocking). Please note that calling self.stop()
        # only sets self.isRunning to false. The Game Run thread (main game
        # loop) can take some additional time to actually stop
        self.stop()

        # Wait for the game loop to actually stop before quitting pygame
        # Warning! Do not call self.close() inside main game loop or this while
        # loop will block the execution forever!.
        while self.isStopped is False:
            pass

    ##############################
    # Userspace Application Hooks
    # This a a set of abstract (empty) methods that derived classes (user space
    # applications) can implement when required by the application logic
    ############################################################################
    def gameEvents(self, events):
        # This is an abstract method to be implemented in sub-classes when
        # required. The method will be invoked by Application, passing
        # collected input events from the user (keystrokes, mouse events,
        # etc...) occurred inside the main game window
        return None

    def objectAdd(self, id_, obj):
        # This is an abstract method to be implemented in sub-classes when required
        # The method will be invoked by Application when every time a new object is detected in the game scene.
        # This method is responsible for creating a sprite for the object and return it to the framework.
        # The object received is a 'cv2.rotatedrect', resulting form the the object tracking process (performed by
        # CentroidTracker). The id received is a unique id assigned to this object by the framework
        return None

    def objectUpdate(self, id_, obj):
        # This is an abstract method to be implemented in sub-classes when required
        # The method will be invoked by Application when every time a new object position is updated in the game
        # scene. The object received is a 'cv2.rotatedrect', resulting form the the object tracking process (performed
        # by CentroidTracker). The id received is the unique id assigned to this object by the framework
        return None

    def objectDelete(self, id_):
        # This is an abstract method to be implemented in sub-classes when required
        # The method will be invoked by the Application every time an object is no longer detected (is lost) in the
        # game scene. The id received is the unique id assigned to the object by the framework.
        return None

    def clearScreen(self):
        # This is an abstract method to be implemented in sub-classes when required
        # The method will be invoked by the Application every time the screen is cleared before being updated
        return None

    def gameLogic(self):
        # This is an abstract method to be implemented in sub-classes when required
        # The method will be invoked by Application once for every game loop iteration. This method is responsible
        # for performing the game logic
        return None

    def drawPreFlip(self):
        # This is an abstract method to be implemented in sub-classes if required
        # The method will be invoked by Application before flipping the screen object
        return None
