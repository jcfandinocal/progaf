############################################
# PROGAF                                   #
# Projection Games Framework               #
############################################
# FaceDetector.py                          #
############################################
#
# 2021/04/16 Initial Release (by Keko)
#
############################################
from progaf.Detector import Detector, Detection
import mediapipe as mp
import cv2


class FaceDetector(Detector):

    def __init__(self, cam, proj):
        # Call the parent class (Detector) constructor
        super().__init__(cam, proj)

        # Face Detector attributes
        self.mpFace = mp.solutions.face_detection
        self.mpDraw = mp.solutions.drawing_utils
        self.faceDetector = self.mpFace.FaceDetection(min_detection_confidence=0.5)

    def processFrame(self, frame):

        # Convert to RGB
        fr_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect Face
        fr_rgb.flags.writeable = False
        result = self.faceDetector.process(fr_rgb)

        # One bounding box and Six relative key points are detected. Key points are:
        # left eye, right eye, nose tip, mouth center, right ear region, and left ear region.
        #
        # Keypoint can be accessed using:
        # result.detections[0].location_data.relative_keypoints[0]
        #
        # Each key point is composed of x and y, which are normalized to [0.0, 1.0] by the image width and height

        # Extract Face Mesh. Store on detector frame for debugging
        self.detections = []  # empty list
        self.frame = frame
        drawing_spec = self.mpDraw.DrawingSpec(thickness=1, circle_radius=1)
        if result.detections is not None:
            for face in result.detections:
                #self.mpDraw.draw_detection(image=self.frame, detection=face)

                # Store detections (in absolute pixel coordinates)
                Nx = int(face.location_data.relative_keypoints[2].x * self.cam.frameWidth)
                Ny = int(face.location_data.relative_keypoints[2].y * self.cam.frameHeight)
                Lx = int(face.location_data.relative_keypoints[0].x * self.cam.frameWidth)
                Ly = int(face.location_data.relative_keypoints[0].y * self.cam.frameHeight)
                Rx = int(face.location_data.relative_keypoints[1].x * self.cam.frameWidth)
                Ry = int(face.location_data.relative_keypoints[1].y * self.cam.frameHeight)

                detection = ("Face",                # object type
                             (Nx, Ny),              # Nose (Nx,Ny)
                             ((Lx, Ly), (Rx, Ry))   # Eyes ((Lx,Ly), (Rx, Ry))
                             )
                self.detections.append(Detection(int(Nx), int(Ny), detection))

        self.frameIsValid = True
