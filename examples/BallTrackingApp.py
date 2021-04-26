############################################
# PROGAF                                   #
# Projection Games Framework               #
############################################
# BallTrackingApp_r00.py                   #
############################################
#
# 2021/04/22 Initial Release (by Keko)
#
#  Ball tracking using a depth camera
############################################

from DepthCamera import DepthCamera
from PyGameApp import PyGameApp
from BallDetector import BallDetector


class BallTracking(PyGameApp):

    def __init__(self, width, height):
        # Call the parent class (pmafApplication) constructor
        super().__init__(width, height)

    def setCamera(self, src, width, height, cameraMatrix=None, cameraDistor=None):
        self.camera = DepthCamera(src, width, height, cameraMatrix, cameraDistor)

def main():
    app = BallTracking(640,480)
    app.setCamera(0, 640, 480)
    app.setProjector(640, 480)

    # Ball detector
    det = BallDetector(app.camera, app.projector)
    app.setDetector(det)

    # app.setTracker()
    app.enableMonitor(1)

    # Blocking in pmaf_0.1.2
    app.start()

    app.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
