############################################
# PROGAF                                   #
# Projection Games Framework               #
############################################
# HandPong (Selfie).py                     #
############################################
#
# 2021/04/23 Initial Release (by Keko)
#
############################################
from progaf.HandDetector import HandDetector
from progaf.PyGameApp import PyGameApp
from collections import OrderedDict
from random import randint

import pygame


class myPad(pygame.sprite.Sprite):
    """This class represents a pad."""

    def __init__(self, xpos):
        # Call the parent class (Sprite) constructor
        super().__init__()

        # Set the background color and set it to be transparent
        self.image = pygame.image.load('sprites/bat.png')

        # Fetch the rectangle object that has the dimensions of the image.
        self.rect = self.image.get_rect()

        # Set mask for efficient collision detection
        self.mask = pygame.mask.from_surface(self.image)

        # Set initial position
        self.rect.x = xpos
        self.rect.y = 560


class myBall(pygame.sprite.Sprite):
    """This class represents a bouncing ball."""

    def __init__(self, xpos, ypos):
        # Call the parent class (Sprite) constructor
        super().__init__()

        self.image = pygame.image.load('sprites/ball.png')

        # Set mask for efficient collision detection
        self.mask = pygame.mask.from_surface(self.image)

        # Set initial Velocity
        self.velocity = [randint(-10, 10), randint(-10, -5)]

        # Fetch the rectangle object that has the dimensions of the image
        # and set initial position for the sprite
        self.rect = self.image.get_rect()
        self.rect.x = xpos
        self.rect.y = ypos

    def bounce(self):
        self.velocity[1] = -self.velocity[1]
        self.rect.y -= 20

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]


class HandPong(PyGameApp):

    def __init__(self, width, height):
        # Call the parent class (pmafApplication) constructor
        super().__init__(width, height)

        # Game Objects
        self.cheat = True
        self.score = 0
        self.nBalls = 0
        self.ball = OrderedDict()
        pixels = 30
        for n in range(0, 10):
            self.addBall(randint(pixels, width-pixels), randint(pixels, height-pixels))

    ##############
    # Keyboard Input Events
    ############################################################################
    def gameEvents(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    # Stop the game loop
                    self.isRunning = False

    ##############
    # Game Tracked Objects Update
    ##############################################################################
    def objectAdd(self, id_, obj):
        """This method is invoked by pmafApplication every time a new object is detected in the game scene. This method
        is responsible for creating a pygame.sprite for the object and return it to the framework (pygameApp)."""

        # Create a new object in the game
        newObject = myPad(obj.xpos)
        return newObject

    def objectUpdate(self, id_, obj):
        """This method is invoked by pmafApplication every time a new object position is updated in the game scene."""

        self.gameObjects[id_].rect.x = int(obj.xpos)
        self.gameObjects[id_].rect.y = self.screenHeight - self.gameObjects[id_].rect.height

    ##############
    # Game logic
    ##############################################################################
    def gameLogic(self):

        # Check screen limits
        for ballID in list(self.ball):
            obj = self.ball[ballID]
            if obj.rect.x >= self.screenWidth-obj.rect.width:
                obj.velocity[0] = -obj.velocity[0]
            if obj.rect.x <= 0:
                obj.velocity[0] = -obj.velocity[0]
            if obj.rect.y <= 0:
                obj.velocity[1] = -obj.velocity[1]
            if obj.rect.y >= self.screenHeight:
                self.deleteBall(ballID)

        # Check bounces
        for (id_, pad) in self.gameObjects.items():
            for ballID in list(self.ball):
                # Check only bounces for balls where ball.rect.y > 550
                # reason: pad is always at y = 560
                # Additional optimization is available for x coordinate (ToDo)
                if self.ball[ballID].rect.y > 430:
                    if pygame.sprite.collide_mask(self.ball[ballID], pad):
                        self.ball[ballID].bounce()
                        self.addBall(self.ball[ballID].rect.x, self.ball[ballID].rect.y)

    def addBall(self, xpos, ypos):
        self.ball[self.nBalls] = myBall(xpos, ypos)
        self.gameSprites.add(self.ball[self.nBalls])
        self.nBalls += 1
        self.score += 1

    def deleteBall(self, id_):
        self.gameSprites.remove(self.ball[id_])
        del self.ball[id_]
        self.score -= 1
        if self.score <= 0:
            self.gameOver()

    def gameOver(self):
        pixels=30
        if self.cheat is True:
            for n in range(0, 10):
                self.addBall(randint(pixels, self.screenWidth-pixels), randint(pixels, self.screenHeight-pixels))
        else:
            print("GameOver")
        return

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

    ##############
    # Static Display logic
    ##############################################################################
    def drawPreFlip(self):
        # Display scores:
        font = pygame.font.SysFont('Arial', 35)
        text = font.render("Score: {:0>2}".format(self.score), True, (0, 0, 0))
        self.screen.blit(text, (650, 20))


def main():
    app = HandPong(1280, 720)
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
