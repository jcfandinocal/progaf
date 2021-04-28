############################################
# PROGAF                                   #
# Projection Games Framework               #
############################################
# PhotoBooth (Selfie).py                   #
############################################
#
# 2021/04/16 Initial Release (by Keko)
#
############################################
from progaf.FaceDetector import FaceDetector
from progaf.PyGameApp import PyGameApp
import pygame
import math


class smartGlasses(pygame.sprite.Sprite):

    # Manual offset adjust
    xOffset = 100
    yOffset = 100

    def __init__(self, det):
        # Call the parent class (pmafApplication) constructor
        super().__init__()

        self.baseImage = pygame.image.load('sprites/GlassesParty02Blue.png')

        self.rotation = 0
        self.scale = 1

        # Fit
        self.fit(det)

    def fit(self, det):
        # detection = ("Face",               # det[0] object type
        #              (Nx, Ny),             # det[1] Nose (Nx,Ny)
        #              ((Lx, Ly), (Rx, Ry))  # det[2] Eyes ((Lx,Ly), (Rx, Ry))

        # 1. Extract key points
        #    Left Eye is (x1, y1)
        #    Right Eye is (x2, y2)
        x1 = det[2][0][0]
        y1 = det[2][0][1]
        x2 = det[2][1][0]
        y2 = det[2][1][1]

        # Rotation
        dx = x2 - x1
        dy = y2 - y1
        self.rotation = math.degrees(math.atan2(dy, dx))

        # Scale Factor
        self.scale = math.dist((x1, y1), (x2, y2))/250

        # Transform and set sprite image
        self.image = pygame.transform.rotozoom(self.baseImage, - self.rotation, self.scale)
        self.rect = self.image.get_rect()

        # Set position
        self.rect.x = x1 - smartGlasses.xOffset
        self.rect.y = y1 - smartGlasses.yOffset


class PhotoBooth(PyGameApp):

    def __init__(self, width, height):
        # Call the parent class (pmafApplication) constructor
        super().__init__(width, height)

        # Game Objects

        # Display Splash Screen
        self.splash()

        # Display Calibration Screen
        self.doCalibration()

    # Display splash screen
    def splash(self):
        return None

    # Display Calibration screen
    def doCalibration(self):
        return None

    ##############
    # Game Tracked Objects Update
    ##############################################################################
    def objectAdd(self, id_, obj):
        """This method is invoked by pmafApplication every time a new object (face) is detected in the game scene."""
        # Create smartGlasses!
        detection = obj.detection
        newObject = smartGlasses(detection)
        return newObject

    def objectUpdate(self, id_, obj):
        """This method is invoked by pmafApplication every time a object (face) position is updated in the game scene"""
        # Update smartGlasses
        detection = obj.detection
        self.gameObjects[id_].fit(detection)

    ##############
    # gameEvents. This is the user input event handler of PyGameApp class
    ############################################################################
    def gameEvents(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    # Stop the game loop
                    self.isRunning = False
                if event.key == pygame.K_UP:
                    smartGlasses.yOffset += 5
                if event.key == pygame.K_DOWN:
                    smartGlasses.yOffset -= 5
                if event.key == pygame.K_RIGHT:
                    smartGlasses.xOffset -= 5
                if event.key == pygame.K_LEFT:
                    smartGlasses.xOffset += 5

    #################################
    # clearScreen. User space hook for drawing at the beginning of each frame
    #########################################################################
    def clearScreen(self):
        # Draw captured camera frames in the game background
        self.screen.fill((0, 0, 0))
        if self.detector.frameIsValid is True:
            background = pygame.image.frombuffer(self.detector.frame.tobytes(),
                                                 self.detector.frame.shape[1::-1],
                                                 "BGR")
            self.screen.blit(background, (0, 0))


def main():
    app = PhotoBooth(848, 480)
    app.setCamera(0, 848, 480)
    app.setProjector(848, 480)

    # det = FaceMeshDetector(app.camera, app.projector)
    det = FaceDetector(app.camera, app.projector)
    app.setDetector(det)

    app.setTracker()
    app.enableMonitor(1)

    # Blocking in pmaf_0.1.2
    app.start()

    app.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
