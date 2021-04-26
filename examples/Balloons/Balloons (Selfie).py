############################################
# PROGAF                                   #
# Projection Games Framework               #
############################################
# Balls (Selfie).py                     #
############################################
#
# 2021/04/16 Initial Release (by Keko)
#
############################################
from HandDetector import HandDetector
from collections import OrderedDict
from PyGameApp import PyGameApp
from random import randint

import pygame


class myRandomBalloon(pygame.sprite.Sprite):
    """This class represents a balloon."""

    # Load sprites from disk into a static dictionary
    resource = 'Sprites/'
    image = {0: pygame.image.load(resource + 'BalloonRedSmall.png'),
             1: pygame.image.load(resource + 'BalloonRedMedium.png'),
             2: pygame.image.load(resource + 'BalloonRedLarge.png'),
             3: pygame.image.load(resource + 'BalloonYellowSmall.png'),
             4: pygame.image.load(resource + 'BalloonYellowMedium.png'),
             5: pygame.image.load(resource + 'BalloonYellowLarge.png'),
             6: pygame.image.load(resource + 'BalloonBlueSmall.png'),
             7: pygame.image.load(resource + 'BalloonBlueMedium.png'),
             8: pygame.image.load(resource + 'BalloonBlueLarge.png'),
             9: pygame.image.load(resource + 'BalloonGreenSmall.png'),
             10: pygame.image.load(resource + 'BalloonGreenMedium.png'),
             11: pygame.image.load(resource + 'BalloonGreenLarge.png'),
             12: pygame.image.load(resource + 'BalloonPinkSmall.png'),
             13: pygame.image.load(resource + 'BalloonPinkMedium.png'),
             14: pygame.image.load(resource + 'BalloonPinkLarge.png')}

    def __init__(self):
        # Call the parent class (Sprite) constructor
        super().__init__()

        # Get random image
        randImage = randint(0, 14)
        self.image = myRandomBalloon.image[randImage]

        # Set mask for efficient collision detection
        self.mask = pygame.mask.from_surface(self.image)

        # Fetch the rectangle object that has the dimensions of the image
        # and set initial position for the sprite
        self.rect = self.image.get_rect()
        self.rect.x = randint(0, 848)
        self.rect.y = 480

        self.speed = 10/((randImage % 3) + 1)
        self.height = self.image.get_height()

    def update(self):
        self.rect.y -= self.speed


class myFingerTip(pygame.sprite.Sprite):

    def __init__(self, xpos, ypos):
        # Call the parent class (pmafApplication) constructor
        super().__init__()

        # Set the background color and set it to be transparent
        self.image = pygame.Surface([10, 10])
        self.image.fill((0, 0, 0))
        self.image.set_colorkey((0, 0, 0))

        # Draw fingertip area
        pygame.draw.circle(self.image, (0, 0, 255), (5, 5), 5)

        # Fetch the rectangle object that has the dimensions of the image.
        self.rect = self.image.get_rect()

        # Set initial position
        self.rect.x = xpos
        self.rect.y = ypos


class Balloons(PyGameApp):

    def __init__(self, width, height):
        # Call the parent class (pmafApplication) constructor
        super().__init__(width, height)

        # Game Objects
        self.tick = 0
        self.nextBalloon = 0
        self.balloons = OrderedDict()
        self.popSound = pygame.mixer.Sound('Sounds/pop.wav')

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
        """This method is invoked by pmafApplication every time a new object (fingertip) is detected in the game scene.

        :param id_:
        :param obj:
        :return:
        """
        # Create a new pad, using the only the x coordinate of the detected
        # object
        newObject = myFingerTip(obj.xpos, obj.ypos)
        return newObject

    def objectUpdate(self, id_, obj):
        """This method is invoked by pmafApplication every time a object (fingertip) position is updated in the game scene

        :param id_:
        :param obj:
        :return:
        """
        self.gameObjects[id_].rect.x = int(obj.xpos)
        self.gameObjects[id_].rect.y = int(obj.ypos)

    ##############
    # gameEvents. This is the user input event handler of PyGameApp class
    ############################################################################
    def gameEvents(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    # Stop the game loop
                    self.isRunning = False

    ##############
    # gameLogic. This is the user space hook for game logic of PyGameApp class
    ############################################################################
    def gameLogic(self):

        # Add a new balloon every 25 frames
        self.tick += 1
        if self.tick == 25:
            self.addBalloon()
            self.tick = 0

        # Delete Balloons outside of game area
        for balloon in list(self.balloons):
            obj = self.balloons[balloon]
            if obj.rect.y + obj.height <= 0:
                self.deleteBalloon(balloon)

        # Test Collisions
        for hand in list(self.gameObjects):
            for balloon in list(self.balloons):
                if pygame.sprite.collide_mask(self.gameObjects[hand], self.balloons[balloon]):
                    self.popSound.play()
                    self.deleteBalloon(balloon)

    def addBalloon(self):
        self.balloons[self.nextBalloon] = myRandomBalloon()
        self.gameSprites.add(self.balloons[self.nextBalloon])
        self.nextBalloon += 1

    def deleteBalloon(self, balloon):
        self.gameSprites.remove(self.balloons[balloon])
        del self.balloons[balloon]

    #################################
    # clearScreen is the user space hook for drawing at the beginning of each
    # frame
    ####################################################################
    def clearScreen(self):
        # Draw captured camera frames in the game background
        self.screen.fill((0, 0, 0))
        if self.detector.frameIsValid is True:
            background = pygame.image.frombuffer(self.detector.frame.tobytes(),
                                                 self.detector.frame.shape[1::-1],
                                                 "BGR")
            self.screen.blit(background, (0, 0))


def main():
    app = Balloons(1280, 720)
    app.setCamera(0, 1280, 720)

    det = HandDetector(app.camera, app.projector)
    app.setDetector(det)

    app.setTracker()
    app.enableMonitor(1)

    # Blocking in pmaf_0.1.2
    app.start()

    app.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
