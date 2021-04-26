############################################
# PROGAF                                   #
# Projection Games Framework               #
############################################
# Profiler.py                              #
############################################
#
# 2021/02/25 Initial Release (by Keko)
#
############################################
from threading import Thread
import time


class Profiler:
    """
    Profiler class is responsible for profiling all PROGAF objects. Profiling
    information is usually displayed using different formats:
        - FPS or Frames per second indicate total number of processed frames
          in one second. This indicator is relevant for objects that are
          actually processing frame information, like Camera or Detector.
        - Elapsed time (expressed in miliseconds) is an indication of the total
          amount of time that one function or method requires to be completed
    """

    def __init__(self, rate=1, cam=None, det=None, trk=None, proj=None, mon=None):

        # Class attributes
        self.isRunning = False
        self.updateRate = rate

        # Camera
        if cam is not None:
            self.cam = cam
            self.cam.perfMon = self  # FIXME: Rename perfMon to profiler
        self.cameraFramesPerSecond = 0
        self.FATsamples = 0
        self.FATnSamples = 0
        self.FATaverage = 0

        # Detector
        if det is not None:
            self.det = det
            self.det.perfMon = self
        self.detectorFramesPerSecond = 0
        self.CDTsamples = 0
        self.CDTnSamples = 0
        self.CDTaverage = 0

        # Tracker
        if trk is not None:
            self.trk = trk
            self.trk.perfMon = self
        self.OTTsamples = 0
        self.OTTnSamples = 0
        self.OTTaverage = 0

        # Projector
        if proj is not None:
            self.prj = proj
            self.prj.perfMon = self
        self.projectorFramesPerSecond = 0

        # User space applications (APT)
        self.APTsamples = 0
        self.APTnSamples = 0
        self.APTaverage = 0

        ########################
        # Performance Indicators
        #################################################
        # FPT: Frame Processing time (average)
        self.FPT = 0
        # APT: Application Processing time (average)
        self.APT = 0

        # Monitor app integration
        self.monitor = mon

    def start(self):
        # Start threads
        self.isRunning = True
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # Keep looping infinitely until the thread is stopped
        while True:
            # Check status and stop thread if required
            if self.isRunning is False:
                return

            # Get Frame Counters
            camStartFrame = self.cam.frameCounter
            detStartFrame = self.det.frameCounter
            prjStartFrame = self.prj.frameCounter

            # We just need to Sleep !!!! to ...
            time.sleep(1 / self.updateRate)

            # ... update Frame Counters
            camFinalFrame = self.cam.frameCounter
            detFinalFrame = self.det.frameCounter
            prjFinalFrame = self.prj.frameCounter

            # Obtain FPS values
            self.cameraFramesPerSecond = (camFinalFrame - camStartFrame) * self.updateRate
            self.detectorFramesPerSecond = (detFinalFrame - detStartFrame) * self.updateRate
            self.projectorFramesPerSecond = (prjFinalFrame - prjStartFrame) * self.updateRate

            ###############################
            # Obtain Processing Time values
            ###################################################################

            # FAT: Frame acquisition Time
            if self.FATnSamples > 0:
                self.FATaverage = self.FATsamples / self.FATnSamples
            else:
                self.FATaverage = 0
            self.FATsamples = 0
            self.FATnSamples = 0

            # CDT: Contour Detection Time
            if self.CDTnSamples > 0:
                self.CDTaverage = self.CDTsamples / self.CDTnSamples
            else:
                self.CDTaverage = 0
            self.CDTsamples = 0
            self.CDTnSamples = 0

            # OTT: Object Tracking Time
            if self.OTTnSamples > 0:
                self.OTTaverage = self.OTTsamples / self.OTTnSamples
            else:
                self.OTTaverage = 0
            self.OTTsamples = 0
            self.OTTnSamples = 0

            # FPT: Frame Processing Time
            self.FPT = self.FATaverage + self.CDTaverage

            # APT: Application Processing Time
            if self.APTnSamples > 0:
                self.APT = self.APTsamples / self.APTnSamples
            else:
                self.APT = 0
            self.APTsamples = 0
            self.APTnSamples = 0

            if self.FPT > 0:
                print("APT: {:.2f}ms "
                      "FPT: {:.2f}ms ["
                      "FAT: {:0>2.0f}% ({:.2f}ms) "
                      "CDT: {:0>2.0f}% ({:.2f}ms) "
                      "OTT: {:0>2.0f}% ({:.2f}ms)] ".format(self.APT * 1000,
                                                            self.FPT * 1000,
                                                            self.FATaverage / self.FPT * 100,
                                                            self.FATaverage * 1000,
                                                            (self.CDTaverage - self.OTTaverage) / self.FPT * 100,
                                                            self.CDTaverage * 1000 - self.OTTaverage * 1000,
                                                            self.OTTaverage / self.FPT * 100,
                                                            self.OTTaverage * 1000))

            # Qt GUI Support. Update GUI
            self.monitor.window.qLabel_CameraFPS.setText("Cam FPS: {}".format(self.cameraFramesPerSecond))
            self.monitor.window.qLabel_DetectorFPS.setText("Det FPS: {}".format(self.detectorFramesPerSecond))
            self.monitor.window.qLabel_ProjectorFPS.setText("Prj FPS: {}".format(self.projectorFramesPerSecond))

    def stop(self):
        # Stop update thread
        self.isRunning = False

    # FAT: Frame acquisition Time
    def collectFATSample(self, sample):
        self.FATsamples += sample
        self.FATnSamples += 1

    # CDT: Contour Detection Time
    def collectCDTSample(self, sample):
        self.CDTsamples += sample
        self.CDTnSamples += 1

    # OTT: Object Tracking Time
    def collectOTTSample(self, sample):
        self.OTTsamples += sample
        self.OTTnSamples += 1

    # APT: Application Processing Time
    def collectAPTSample(self, sample):
        self.APTsamples += sample
        self.APTnSamples += 1
