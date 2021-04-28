############################################
# PROGAF                                   #
# Projection Games Framework               #
############################################
# FaceMeshDetector.py                      #
############################################
#
# 2021/04/16 Initial Release (by Keko)
#
############################################
from progaf.Detector import Detector
import mediapipe as mp
import cv2


class FaceMeshDetector(Detector):

    def __init__(self, cam, proj):
        # Call the parent class (Detector) constructor
        super().__init__(cam, proj)

        # Face Detector attributes
        self.mpFace = mp.solutions.face_mesh
        self.mpDraw = mp.solutions.drawing_utils
        self.faceDetector = self.mpFace.FaceMesh(min_detection_confidence=0.5,
                                                 min_tracking_confidence=0.5)

    def processFrame(self, frame):

        # Convert to RGB
        fr_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect Face
        fr_rgb.flags.writeable = False
        result = self.faceDetector.process(fr_rgb)

        # Extract Face Mesh. Store on detector frame for debugging
        self.detections = []  # empty list
        self.frame = frame
        drawing_spec = self.mpDraw.DrawingSpec(thickness=1, circle_radius=1)
        if result.multi_face_landmarks is not None:
            for landmark in result.multi_face_landmarks:
                self.mpDraw.draw_landmarks(
                    image=self.frame,
                    landmark_list=landmark,
                    connections=self.mpFace.FACE_CONNECTIONS,
                    landmark_drawing_spec=drawing_spec,
                    connection_drawing_spec=drawing_spec)

        self.frameIsValid = True
