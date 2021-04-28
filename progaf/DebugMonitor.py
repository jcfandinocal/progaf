############################################
# PROGAF                                   #
# Projection Games Framework               #
############################################
# Monitor.py                               #
############################################
#
# 2021/02/25 Initial Release (by Keko)
# 2021/04/28 Removed GUI / QT dependencies
#
############################################
from threading import Thread
import cv2

class DebugMonitor:

    def __init__(self, camera, detector):
        self.camera = camera
        self.detector = detector
        self.isRunning = False

    def start(self):
        # Start Thread
        self.isRunning = True
        Thread(target=self.debugThread, args=()).start()
        return self

    def debugThread(self):
        while True:

            # Check status and stop thread if required
            if self.isRunning is False:
                return

            # Read camera frame (non blocking)
            cam_ok, cam_fr = self.camera.read()

            # Read Detector Frame (non blocking)
            det_ok, det_fr = self.detector.read()

            # Display Camera frames
            if cam_ok is True:
                cv2.imshow("Camera", cam_fr)

            # Display Detector Frames
            if det_ok is True:
                cv2.imshow("Detector", det_fr)

            # Process keyboard input:
            key = cv2.waitKeyEx(1)
            if key != -1:
                print(key)

            # Get LSB
            key = key & 0xFF

            # Quit if the user presses <esc>, <q> <Q> <ctrl+c> keys
            if key == 27 or key == ord("q") or key == ord("Q") or key == 3:
                break

    def close(self):
        self.stop()

    def stop(self):
        self.isRunning = False
        cv2.destroyAllWindows()
