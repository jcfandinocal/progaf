############################################
# PROGAF                                   #
# Projection Games Framework               #
############################################
# PyGameApp.py                             #
############################################
#
# 2021/04/10 Initial Release
#
############################################
from progaf.Application import Application
from collections import OrderedDict
import pygame
import time


class PyGameApp(Application):
    """Application encapsulates the Application logic"""

    def __init__(self, width, height):
        super().__init__()

        # Class Attributes
        self.screenWidth = width
        self.screenHeight = height

        # Collections for all PyGame objects and sprites used in the game.
        self.gameObjects = OrderedDict()
        self.gameSprites = pygame.sprite.Group()

        # PyGame initialization
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()

    def start(self):

        # Start framework classes
        Application.start(self)

        # Start the game loop thread
        self.isRunning = True
        self.isStopped = False
        self.gameLoop()

        # Close everything after quitting the game
        self.close()

    def gameLoop(self):
        # Keep looping infinitely until the thread is stopped
        while True:
            # Get loop starting time for performance monitoring
            start = time.time()

            # If the thread stop indicator variable is set, stop the thread
            if self.isRunning is False:
                self.isStopped = True
                return

            #################################
            # User Input Events section (UserSpace hook)
            ####################################################################
            self.gameEvents(pygame.event.get())

            #################################
            # Object update section
            ###################################################################
            # Update tracked Objects (several user-space hooks inside)
            self.updateTrackedObjects()

            # Update non tracked objects
            self.gameSprites.update()

            ###############################
            # Game logic section (Userspace hook)
            ###################################################################
            self.gameLogic()

            #################################
            # Drawing section
            ####################################################################
            # Clear screen to redraw everything for each frame
            # self.screen.fill((255, 255, 255))
            self.clearScreen()

            # Draw all the sprites in one go.
            self.gameSprites.draw(self.screen)

            # Custom drawing before display flip (user-space hook).
            self.drawPreFlip()

            # Update the screen
            pygame.display.flip()

            ###################################
            # --- Limit to 30 frames per second
            ###################################################################
            self.clock.tick(30)

            # Get loop end time and update profiler
            if self.profiler is not None:
                end = time.time()
                self.profiler.collectAPTSample(end - start)

    def updateTrackedObjects(self):
        if self.trackerUpdateFlag is not True:
            # Nothing to do...
            return

        # Different situations have to be considered here.
        # If self.gameObjects is empty... create all tracker objects with
        # new or updated status and return
        if len(self.gameObjects) == 0:
            for (id_, obj) in self.trackerObjects.items():
                if self.trackerObjectStatus[id_] == "New":
                    self.gameObjects[id_] = self.objectAdd(id_, obj)
                    if self.objectAdd(id_, obj) is not None:
                        self.gameSprites.add(self.gameObjects[id_])
                if self.trackerObjectStatus[id_] == "Updated":
                    self.gameObjects[id_] = self.objectAdd(id_, obj)
                    if self.objectAdd(id_, obj) is not None:
                        self.gameSprites.add(self.gameObjects[id_])
                return

        # Beyond this point, gameObjects is not empty so we have to update it
        # 1. Process new objects received from tracker
        for (id_, obj) in self.trackerObjects.items():
            if self.trackerObjectStatus[id_] == "New":
                self.gameObjects[id_] = self.objectAdd(id_, obj)
                if self.objectAdd(id_, obj) is not None:
                    self.gameSprites.add(self.gameObjects[id_])

        # 2. Process updated objects
        gameExistingIds = list(self.gameObjects)
        for (id_, obj) in self.trackerObjects.items():
            if self.trackerObjectStatus[id_] == "Updated":
                if id_ in gameExistingIds:
                    self.objectUpdate(id_, obj)
                else:
                    # Create a new one
                    self.gameObjects[id_] = self.objectAdd(id_, obj)
                    if self.objectAdd(id_, obj) is not None:
                        self.gameSprites.add(self.gameObjects[id_])

        # 3. Delete "Lost" objects
        trackerExistingIds = list(self.trackerObjects)
        for id_ in list(self.gameObjects):
            if id_ not in trackerExistingIds:
                self.objectDelete(id_)
                self.gameSprites.remove(self.gameObjects[id_])
                del self.gameObjects[id_]

        # Reset Tracker Update Flag
        self.trackerUpdateFlag = False

    def close(self):
        # Warning! Do not call self.close() inside main game loop or the
        # execution will block forever!.
        super().close()

        # Quit Pygame
        pygame.quit()
