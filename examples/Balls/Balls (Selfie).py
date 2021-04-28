############################################
# PROGAF                                   #
# Projection Games Framework               #
############################################
# Balls (Selfie).py                        #
############################################
#
# 2021/04/18 Initial Release (by Keko)
#
############################################
from progaf.HandDetector import HandDetector
from progaf.PyGameApp import PyGameApp
from collections import OrderedDict
from random import randint
import pygame


class myRandomGhost(pygame.sprite.Sprite):
    """This class represents a ghost."""

    # Load sprites from disk into a static dictionary
    resource = 'themes/Spooky/Sprites/'
    image = {0: pygame.image.load(resource + 'Ghost00.png'),
             1: pygame.image.load(resource + 'Ghost01.png'),
             2: pygame.image.load(resource + 'Ghost02.png'),
             3: pygame.image.load(resource + 'Ghost03.png'),
             4: pygame.image.load(resource + 'Ghost04.png'),
             5: pygame.image.load(resource + 'Ghost05.png'),
             6: pygame.image.load(resource + 'Ghost06.png'),
             7: pygame.image.load(resource + 'Ghost07.png'),
             8: pygame.image.load(resource + 'Ghost08.png'),
             9: pygame.image.load(resource + 'Ghost09.png'),
             10: pygame.image.load(resource + 'Ghost10.png'),
             11: pygame.image.load(resource + 'Ghost11.png'),
             12: pygame.image.load(resource + 'Ghost12.png')}

    # Progressive alpha values make ghosts appear slowly
    alpha = {9: 150,
             10: 200,
             30: 255,
             35: 220,
             40: 200,
             45: 150,
             50: 100}

    def __init__(self):
        # Call the parent class (Sprite) constructor
        super().__init__()

        # Frames Left
        self.framesLeft = 50

        # Get random image
        randImage = randint(0, 12)
        self.image = myRandomGhost.image[randImage].convert_alpha()
        self.image.set_alpha(100)

        # Set mask for efficient collision detection
        self.mask = pygame.mask.from_surface(self.image)

        # Fetch the rectangle object that has the dimensions of the image
        # and set initial position for the sprite
        self.rect = self.image.get_rect()
        self.rect.x = randint(20, 1600)
        self.rect.y = randint(0, 800)

    def update(self):
        self.framesLeft -= 1
        try:
            self.image.set_alpha(myRandomGhost.alpha[self.framesLeft])
        except:
            pass


class myBroom(pygame.sprite.Sprite):

    def __init__(self, xpos, ypos):
        # Call the parent class (pmafApplication) constructor
        super().__init__()

        # Set the background color and set it to be transparent
        resource = 'Themes/Spooky/Sprites/'
        self.image = pygame.image.load(resource + 'Broom00.png')

        # Fetch the rectangle object that has the dimensions of the image.
        self.rect = self.image.get_rect()

        # Set initial position
        self.rect.x = xpos
        self.rect.y = ypos


class Balls(PyGameApp):

    resource = 'themes/spooky/background/'
    background = pygame.image.load(resource + 'background.jpg')

    def __init__(self, width, height):
        # Call the parent class (pmafApplication) constructor
        super().__init__(width, height)

        # Game Objects
        self.tick = 0
        self.nextGhost = 0
        self.ghosts = OrderedDict()
        self.popSound = pygame.mixer.Sound('sounds/pop.wav')

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
        """This method is invoked by pmafApplication every time a new object
        (fingertip) is detected in the game scene
        """
        newObject = myBroom(obj.xpos * 1920 / 1280, obj.ypos * 1080 / 720)
        return newObject

    def objectUpdate(self, id_, obj):
        """This method is invoked by pmafApplication every time a object
        (fingertip) position is updated in the game scene
        """
        self.gameObjects[id_].rect.x = int(obj.xpos * 1920 / 1280)
        self.gameObjects[id_].rect.y = int(obj.ypos * 1080 / 720)

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

        # Add new ghosts
        self.tick += 1
        if self.tick == 15:
            self.newGhost()
            self.tick = 0

        # Delete old ghosts
        for ghost in list(self.ghosts):
            obj = self.ghosts[ghost]
            if obj.framesLeft <= 0:
                self.deleteGhost(ghost)

        # Test Collisions
        for broom in list(self.gameObjects):
            for ghost in list(self.ghosts):
                if pygame.sprite.collide_mask(self.gameObjects[broom], self.ghosts[ghost]):
                    self.popSound.play()
                    self.deleteGhost(ghost)

    def newGhost(self):
        self.ghosts[self.nextGhost] = myRandomGhost()
        self.gameSprites.add(self.ghosts[self.nextGhost])
        self.nextGhost += 1

    def deleteGhost(self, ghost):
        self.gameSprites.remove(self.ghosts[ghost])
        del self.ghosts[ghost]

    #################################
    # clearScreen is the user space hook for drawing at the beginning of each
    # frame
    ####################################################################
    def clearScreen(self):
        self.screen.blit(Balls.background, (0, 0))


def main():
    app = Balls(1920, 1080)
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
