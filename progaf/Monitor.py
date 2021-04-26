############################################
# PROGAF                                   #
# Projection Games Framework               #
############################################
# Monitor.py                           #
############################################
#
# 2021/02/25 Initial Release (by Keko)
#
############################################
from PySide6 import QtCore, QtWidgets
from threading import Thread
import cv2


class pmafQtMainWindow(QtWidgets.QWidget):
    def __init__(self, camera, detector, projector):
        super().__init__()

        # Class attributes
        self.camera = camera
        self.detector = detector
        self.projector = projector

        # Layout
        self.layout = QtWidgets.QGridLayout(self)
        self.qLabel_CameraFPS = QtWidgets.QPushButton("-")
        self.qLabel_DetectorFPS = QtWidgets.QPushButton("-")
        self.qLabel_ProjectorFPS = QtWidgets.QPushButton("-")
        self.layout.addWidget(self.qLabel_CameraFPS, 0, 0)
        self.layout.addWidget(self.qLabel_DetectorFPS, 1, 0)
        self.layout.addWidget(self.qLabel_ProjectorFPS, 2, 0)
        self.setWindowTitle("pmafDebugWindow")

        # Child windows
        self.cameraWindow = None
        self.detectorWindow = None
        self.projectorWindow = None

        # Events
        self.qLabel_DetectorFPS.clicked.connect(self.showDetectorWindow)
        self.qLabel_ProjectorFPS.clicked.connect(self.showProjectorWindow)
        self.qLabel_CameraFPS.clicked.connect(self.showCameraWindow)

    def closeEvent(self, event):
        if self.cameraWindow is not None:
            self.cameraWindow.close()
        if self.detectorWindow is not None:
            self.detectorWindow.close()
        if self.projectorWindow is not None:
            self.projectorWindow.close()

        event.accept()

    # Slots
    @QtCore.Slot()
    def showDetectorWindow(self):
        self.detectorWindow = pmafQtDetectorWindow(self.detector)
        self.detectorWindow.show()

    @QtCore.Slot()
    def showProjectorWindow(self):
        self.projectorWindow = pmafQtProjectorWindow(self.projector)
        self.projectorWindow.show()

    @QtCore.Slot()
    def showCameraWindow(self):
        self.cameraWindow = pmafQtCameraWindow(self.camera, self.projector)
        self.cameraWindow.show()


class pmafQtDetectorWindow(QtWidgets.QWidget):
    def __init__(self, detector):
        super().__init__()

        # Class attributes
        self.detector = detector

        # Layout
        self.layout = QtWidgets.QGridLayout(self)
        self.setWindowTitle("Detector")

        self.layout.addWidget(QtWidgets.QLabel("isRunning"),		0, 0)
        self.layout.addWidget(QtWidgets.QLabel("minArea"), 			1, 0)
        self.layout.addWidget(QtWidgets.QLabel("maxArea"), 			2, 0)
        self.layout.addWidget(QtWidgets.QLabel("Aspect Ratio"), 	3, 0)
        self.layout.addWidget(QtWidgets.QLabel("Canny Min Val"), 	4, 0)
        self.layout.addWidget(QtWidgets.QLabel("Canny Max Val"), 	5, 0)
        self.layout.addWidget(QtWidgets.QLabel("Canny Kern Size"), 	6, 0)
        self.layout.addWidget(QtWidgets.QLabel("Canny L2 Grad"), 	7, 0)

        self.qTxtIsRunning = QtWidgets.QLineEdit(str(self.detector.isRunning))
        self.qTxtMinArea = QtWidgets.QLineEdit(str(self.detector.minArea))
        self.qTxtMaxArea = QtWidgets.QLineEdit(str(self.detector.maxArea))
        self.qTxtAspectRatio = QtWidgets.QLineEdit(str(self.detector.aspectRatio))
        self.qTxtCannyMinVal = QtWidgets.QLineEdit(str(self.detector.cannyMinVal))
        self.qTxtCannyMaxVal = QtWidgets.QLineEdit(str(self.detector.cannyMaxVal))
        self.qTxtCannyKernSize = QtWidgets.QLineEdit(str(self.detector.cannyKernSize))
        self.qTxtCannyL2Grad = QtWidgets.QLineEdit(str(int(self.detector.cannyL2Grad is True)))

        self.layout.addWidget(self.qTxtIsRunning,			0, 1)
        self.layout.addWidget(self.qTxtMinArea, 			1, 1)
        self.layout.addWidget(self.qTxtMaxArea,				2, 1)
        self.layout.addWidget(self.qTxtAspectRatio,			3, 1)
        self.layout.addWidget(self.qTxtCannyMinVal,			4, 1)
        self.layout.addWidget(self.qTxtCannyMaxVal,			5, 1)
        self.layout.addWidget(self.qTxtCannyKernSize,		6, 1)
        self.layout.addWidget(self.qTxtCannyL2Grad,			7, 1)

        # self.qBtnSetIsRunning 		= QtWidgets.QPushButton("Set")
        self.qBtnSetMinArea = QtWidgets.QPushButton("Set")
        self.qBtnSetMaxArea = QtWidgets.QPushButton("Set")
        self.qBtnSetAspectRatio = QtWidgets.QPushButton("Set")
        self.qBtnSetCannyMinVal = QtWidgets.QPushButton("Set")
        self.qBtnSetCannyMaxVal = QtWidgets.QPushButton("Set")
        self.qBtnSetCannyKernSize = QtWidgets.QPushButton("Set")
        self.qBtnSetCannyL2Grad = QtWidgets.QPushButton("Set")

        # self.layout.addWidget(self.qBtnSetIsRunning,		0, 2)
        self.layout.addWidget(self.qBtnSetMinArea,			1, 2)
        self.layout.addWidget(self.qBtnSetMaxArea,			2, 2)
        self.layout.addWidget(self.qBtnSetAspectRatio,		3, 2)
        self.layout.addWidget(self.qBtnSetCannyMinVal,		4, 2)
        self.layout.addWidget(self.qBtnSetCannyMaxVal,		5, 2)
        self.layout.addWidget(self.qBtnSetCannyKernSize,	6, 2)
        self.layout.addWidget(self.qBtnSetCannyL2Grad,		7, 2)

        # Events
        self.qBtnSetMinArea.clicked.connect(self.setMinArea)
        self.qBtnSetMaxArea.clicked.connect(self.setMaxArea)
        self.qBtnSetAspectRatio.clicked.connect(self.setAspectRatio)
        self.qBtnSetCannyMinVal.clicked.connect(self.setCannyMinVal)
        self.qBtnSetCannyMaxVal.clicked.connect(self.setCannyMaxVal)
        self.qBtnSetCannyKernSize.clicked.connect(self.setCannyKernSize)
        self.qBtnSetCannyL2Grad.clicked.connect(self.setCannyL2Grad)

    @QtCore.Slot()
    def setMinArea(self):
        self.detector.minArea = int(self.qTxtMinArea.text())

    @QtCore.Slot()
    def setMaxArea(self):
        self.detector.maxArea = int(self.qTxtMaxArea.text())

    @QtCore.Slot()
    def setAspectRatio(self):
        self.detector.aspectRatio = float(self.qTxtAspectRatio.text())

    @QtCore.Slot()
    def setCannyMinVal(self):
        self.detector.cannyMinVal = int(self.qTxtCannyMinVal.text())

    @QtCore.Slot()
    def setCannyMaxVal(self):
        self.detector.cannyMaxVal = int(self.qTxtCannyMaxVal.text())

    @QtCore.Slot()
    def setCannyKernSize(self):
        self.detector.cannyKernSize = int(self.qTxtCannyKernSize.text())

    @QtCore.Slot()
    def setCannyL2Grad(self):
        self.detector.cannyL2Grad = bool(int(self.qTxtCannyL2Grad.text()))


class pmafQtProjectorWindow(QtWidgets.QWidget):
    def __init__(self, projector):
        super().__init__()

        # Class attributes
        self.projector = projector

        # Layout
        self.layout = QtWidgets.QGridLayout(self)
        self.setWindowTitle("Projector")

        self.layout.addWidget(QtWidgets.QLabel("Frame Widht"),			0, 0)
        self.layout.addWidget(QtWidgets.QLabel("Frame Height"), 		1, 0)
        self.layout.addWidget(QtWidgets.QLabel("Transform Scale X"), 	2, 0)
        self.layout.addWidget(QtWidgets.QLabel("Transform Scale Y"), 	3, 0)
        self.layout.addWidget(QtWidgets.QLabel("Transform Delta X"), 	4, 0)
        self.layout.addWidget(QtWidgets.QLabel("Transform Delta Y"), 	5, 0)
        self.layout.addWidget(QtWidgets.QLabel("Layer A Active"), 		6, 0)
        self.layout.addWidget(QtWidgets.QLabel("Layer B Active"), 		7, 0)
        # self.layout.addWidget(QtWidgets.QLabel("Animation Speed"), 		8, 0)
        self.layout.addWidget(QtWidgets.QLabel("Display Grid"), 		9, 0)

        self.qTxtWidth = QtWidgets.QLineEdit(str(self.projector.width))
        self.qTxtHeight = QtWidgets.QLineEdit(str(self.projector.height))
        self.qTxtTrScaleX = QtWidgets.QLineEdit(str(self.projector.transform.affineMatrix[0, 0]))
        self.qTxtTrScaleY = QtWidgets.QLineEdit(str(self.projector.transform.affineMatrix[1, 1]))
        self.qTxtTrDeltaX = QtWidgets.QLineEdit(str(self.projector.transform.affineMatrix[0, 2]))
        self.qTxtTrDeltaY = QtWidgets.QLineEdit(str(self.projector.transform.affineMatrix[1, 2]))
        self.qTxtLayerAOn = QtWidgets.QLineEdit(str(int(self.projector.layerAIsActive is True)))
        self.qTxtLayerBOn = QtWidgets.QLineEdit(str(int(self.projector.layerBIsActive is True)))
        # self.qTxtAnimSpeed = QtWidgets.QLineEdit(str(self.projector.shapeFactory.speed))
        self.qTxtGrid = QtWidgets.QLineEdit(str(int(self.projector.gridIsActive is True)))

        self.layout.addWidget(self.qTxtWidth,			0, 1)
        self.layout.addWidget(self.qTxtHeight, 			1, 1)
        self.layout.addWidget(self.qTxtTrScaleX,		2, 1)
        self.layout.addWidget(self.qTxtTrScaleY,		3, 1)
        self.layout.addWidget(self.qTxtTrDeltaX,		4, 1)
        self.layout.addWidget(self.qTxtTrDeltaY,		5, 1)
        self.layout.addWidget(self.qTxtLayerAOn,		6, 1)
        self.layout.addWidget(self.qTxtLayerBOn,		7, 1)
        # self.layout.addWidget(self.qTxtAnimSpeed,		8, 1)
        self.layout.addWidget(self.qTxtGrid,			9, 1)

        self.qBtnMaximize = QtWidgets.QPushButton("Maxim")
        self.qBtnRestore = QtWidgets.QPushButton("Restore")
        self.qBtnSetTrScaleX = QtWidgets.QPushButton("Set")
        self.qBtnSetTrScaleY = QtWidgets.QPushButton("Set")
        self.qBtnSetTrDeltaX = QtWidgets.QPushButton("Set")
        self.qBtnSetTrDeltaY = QtWidgets.QPushButton("Set")
        self.qBtnSetLayerAOn = QtWidgets.QPushButton("Set")
        self.qBtnSetLayerBOn = QtWidgets.QPushButton("Set")
        # self.qBtnSetAnimSpeed	= QtWidgets.QPushButton("Set")
        self.qBtnSetGrid = QtWidgets.QPushButton("Set")

        self.layout.addWidget(self.qBtnMaximize,		0, 2)
        self.layout.addWidget(self.qBtnRestore,			1, 2)
        self.layout.addWidget(self.qBtnSetTrScaleX,		2, 2)
        self.layout.addWidget(self.qBtnSetTrScaleY,		3, 2)
        self.layout.addWidget(self.qBtnSetTrDeltaX,		4, 2)
        self.layout.addWidget(self.qBtnSetTrDeltaY,		5, 2)
        self.layout.addWidget(self.qBtnSetLayerAOn,		6, 2)
        self.layout.addWidget(self.qBtnSetLayerBOn,		7, 2)
        # self.layout.addWidget(self.qBtnSetAnimSpeed,	8, 2)
        self.layout.addWidget(self.qBtnSetGrid,			9, 2)

        # Events
        self.qBtnMaximize.clicked.connect(self.maximizeWindow)
        self.qBtnRestore.clicked.connect(self.restoreWindow)
        self.qBtnSetTrScaleX.clicked.connect(self.setTrScaleX)
        self.qBtnSetTrScaleY.clicked.connect(self.setTrScaleY)
        self.qBtnSetTrDeltaX.clicked.connect(self.setTrDeltaX)
        self.qBtnSetTrDeltaY.clicked.connect(self.setTrDeltaY)
        self.qBtnSetLayerAOn.clicked.connect(self.setLayerAOn)
        self.qBtnSetLayerBOn.clicked.connect(self.setLayerBOn)
        # self.qBtnSetAnimSpeed.clicked.connect(self.setAnimSpeed)
        self.qBtnSetGrid.clicked.connect(self.setGrid)

    # Qt Slots
    @QtCore.Slot()
    def maximizeWindow(self):
        cv2.setWindowProperty("Projector", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Qt Slots
    @QtCore.Slot()
    def restoreWindow(self):
        cv2.setWindowProperty("Projector", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

    @QtCore.Slot()
    def setTrScaleX(self):
        self.projector.transform.affineMatrix[0, 0] = float(self.qTxtTrScaleX.text())

    @QtCore.Slot()
    def setTrScaleY(self):
        self.projector.transform.affineMatrix[1, 1] = float(self.qTxtTrScaleY.text())

    @QtCore.Slot()
    def setTrDeltaX(self):
        self.projector.transform.affineMatrix[0, 2] = float(self.qTxtTrDeltaX.text())

    @QtCore.Slot()
    def setTrDeltaY(self):
        self.projector.transform.affineMatrix[1, 2] = float(self.qTxtTrDeltaY.text())

    @QtCore.Slot()
    def setLayerAOn(self):
        self.projector.layerAIsActive = bool(int(self.qTxtLayerAOn.text()))

    @QtCore.Slot()
    def setLayerBOn(self):
        self.projector.layerBIsActive = bool(int(self.qTxtLayerBOn.text()))

    # @QtCore.Slot()
    # def setAnimSpeed(self):
    # 	self.projector.shapeFactory.speed = int(self.qTxtAnimSpeed.text())

    @QtCore.Slot()
    def setGrid(self):
        self.projector.gridIsActive = bool(int(self.qTxtGrid.text()))


class pmafQtCameraWindow(QtWidgets.QWidget):
    def __init__(self, camera, projector):
        super().__init__()

        # Class attributes
        self.camera = camera
        self.projector = projector

        # Layout
        self.layout = QtWidgets.QGridLayout(self)
        self.setWindowTitle("Camera")

        self.layout.addWidget(QtWidgets.QLabel("isRunning"),		0, 0)
        self.layout.addWidget(QtWidgets.QLabel("Source"),			1, 0)
        self.layout.addWidget(QtWidgets.QLabel("Frame Width"),		2, 0)
        self.layout.addWidget(QtWidgets.QLabel("Frame Height"),		3, 0)
        self.layout.addWidget(QtWidgets.QLabel("Capture Path"),		4, 0)
        self.layout.addWidget(QtWidgets.QLabel("Undistort"),		5, 0)
        self.layout.addWidget(QtWidgets.QLabel("Crop"),				6, 0)
        self.layout.addWidget(QtWidgets.QLabel("Display Grid"),		7, 0)

        self.qBtnSetCropArea = QtWidgets.QPushButton("Set Crop Area")
        self.qBtnSetCropArea.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                           QtWidgets.QSizePolicy.MinimumExpanding)
        self.layout.addWidget(self.qBtnSetCropArea			,		8, 0, 1, 3)

        self.qBtnSetAffineTr = QtWidgets.QPushButton("Set Affine Transform")
        self.qBtnSetAffineTr.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                           QtWidgets.QSizePolicy.MinimumExpanding)
        self.layout.addWidget(self.qBtnSetAffineTr			,		9, 0, 1, 3)

        self.qTxtIsRunning = QtWidgets.QLineEdit(str(self.camera.isRunning))
        self.qTxtSource = QtWidgets.QLineEdit(str(self.camera.source))
        self.qTxtFrameWidth = QtWidgets.QLineEdit(str(self.camera.frameWidth))
        self.qTxtFrameHeight = QtWidgets.QLineEdit(str(self.camera.frameHeight))
        self.qTxtCapturePath = QtWidgets.QLineEdit(str(self.camera.capturePath))
        self.qTxtUndistort = QtWidgets.QLineEdit(str(int(self.camera.undist is True)))
        self.qTxtCrop = QtWidgets.QLineEdit(str(int(self.camera.crop is True)))
        self.qTxtGrid = QtWidgets.QLineEdit(str(int(self.camera.displayGrid is True)))

        self.layout.addWidget(self.qTxtIsRunning,			0, 1)
        self.layout.addWidget(self.qTxtSource,				1, 1)
        self.layout.addWidget(self.qTxtFrameWidth,			2, 1)
        self.layout.addWidget(self.qTxtFrameHeight,			3, 1)
        self.layout.addWidget(self.qTxtCapturePath,			4, 1)
        self.layout.addWidget(self.qTxtUndistort,			5, 1)
        self.layout.addWidget(self.qTxtCrop,				6, 1)
        self.layout.addWidget(self.qTxtGrid,				7, 1)

        self.qBtnCapture = QtWidgets.QPushButton("Capture")
        self.qBtnSetSource = QtWidgets.QPushButton("Set")
        self.qBtnSetPath = QtWidgets.QPushButton("Set")
        self.qBtnSetUndistort = QtWidgets.QPushButton("Set")
        self.qBtnSetCrop = QtWidgets.QPushButton("Set")
        self.qBtnSetGrid = QtWidgets.QPushButton("Set")

        # Trick required for qBtnSetSource to span over three rows
        self.qBtnSetSource.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                         QtWidgets.QSizePolicy.MinimumExpanding)

        self.layout.addWidget(self.qBtnCapture,			0, 2)
        self.layout.addWidget(self.qBtnSetSource,		1, 2, 3, 1)
        self.layout.addWidget(self.qBtnSetPath,			4, 2)
        self.layout.addWidget(self.qBtnSetUndistort,	5, 2)
        self.layout.addWidget(self.qBtnSetCrop,			6, 2)
        self.layout.addWidget(self.qBtnSetGrid,			7, 2)

        # Events
        self.qBtnCapture.clicked.connect(self.captureFrame)
        self.qBtnSetSource.clicked.connect(self.setSource)
        self.qBtnSetPath.clicked.connect(self.setCapturePath)
        self.qBtnSetUndistort.clicked.connect(self.setUndistort)
        self.qBtnSetCrop.clicked.connect(self.setCrop)
        self.qBtnSetGrid.clicked.connect(self.setGrid)
        self.qBtnSetCropArea.clicked.connect(self.setCropArea)
        self.qBtnSetAffineTr.clicked.connect(self.setAffineTr)

    @QtCore.Slot()
    def captureFrame(self):
        self.camera.writeToFile()

    @QtCore.Slot()
    def setSource(self):
        if self.qTxtSource.text().isdigit() is True:
            # if source is a digit, open the video-stream (camera)
            self.camera.initFromStream(int(self.qTxtSource.text()),
                                       int(self.qTxtFrameWidth.text()),
                                       int(self.qTxtFrameHeight.text()))
        else:
            # is source is not a digit, consider it a filename...
            self.camera.initFromFile(self.qTxtSource.text())

        # Update with the real frame resolution indicated by the source
        self.qTxtFrameWidth.setText(str(self.camera.frameWidth))
        self.qTxtFrameHeight.setText(str(self.camera.frameHeight))

    @QtCore.Slot()
    def setCapturePath(self):
        self.camera.capturePath = self.qTxtCapturePath.text()

    @QtCore.Slot()
    def setUndistort(self):
        self.camera.undist = bool(int(self.qTxtUndistort.text()))

    @QtCore.Slot()
    def setCrop(self):
        self.camera.crop = bool(int(self.qTxtCrop.text()))

    @QtCore.Slot()
    def setGrid(self):
        self.camera.displayGrid = bool(int(self.qTxtGrid.text()))

    @QtCore.Slot()
    def setCropArea(self):
        roi = cv2.selectROI("Set Cropping", self.camera.frame)
        self.camera.setCropArea(roi)
        self.camera.crop = True
        self.qTxtCrop.setText(str(int(True)))
        cv2.destroyWindow("Set Cropping")

    @QtCore.Slot()
    def setAffineTr(self):
        roi = cv2.selectROI("Select Area", self.camera.frame)
        self.projector.setTransform(roi)
        cv2.destroyWindow("Select Area")


class Monitor:
    def __init__(self, camera, detector, tracker, projector):

        self.camera = camera
        self.detector = detector
        self.tracker = tracker
        self.projector = projector
        self.app = None
        self.window = None
        self.finished = False

    def start(self):
        # Start threads
        Thread(target=self.guiThread, args=()).start()
        Thread(target=self.debugThread, args=()).start()
        return self

    def guiThread(self):
        # Display main window and start event loop
        self.app = QtWidgets.QApplication([])
        self.window = pmafQtMainWindow(self.camera, self.detector, self.projector)
        self.window.resize(200, 100)
        self.window.show()
        self.app.exec_()
        self.finished = True

    def debugThread(self):
        # Debug loop
        while True:

            # # Read camera frame (non blocking)
            # cam_ok, cam_fr = self.camera.read()

            # Read projector Frame (non blocking)
            # prj_ok, prj_fr = myApp.projector.read()

            # Read Detector Frame (non blocking)
            det_ok, det_fr = self.detector.read()

            # # Display Camera frames
            # if cam_ok is True:
            #     cv2.imshow("Camera", cam_fr)

            # Display Detector Frames
            if det_ok is True:
                cv2.imshow("Detector", det_fr)

            # # Display Projector Frames
            # if prj_ok is True:
            # 	cv2.imshow("Projector", prj_fr)

            # Quit if the user closes monitor app
            if self.finished is True:
                break

            # Process keyboard input:
            key = cv2.waitKeyEx(1)
            if key != -1:
                print(key)

            # Get LSB
            key = key & 0xFF

            # Quit if the user presses <esc>, <q> <Q> <ctrl+c> keys
            if key == 27 or key == ord("q") or key == ord("Q") or key == 3:
                break

        cv2.destroyAllWindows()
