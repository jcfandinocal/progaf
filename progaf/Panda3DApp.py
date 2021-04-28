############################################
# PROGAF                                   #
# Projection Games Framework               #
############################################
# panda3DApp.py                            #
############################################
#
# 2021/04/10 Initial Release
#
############################################
from direct.showbase.ShowBase import ShowBase
from direct.showbase import DirectObject
from progaf.Application import Application
from panda3d.core import LVecBase4f
from collections import OrderedDict
import time


class Panda3DApp(Application, DirectObject.DirectObject):
    """Application encapsulates the Application logic"""

    def __init__(self):
        Application.__init__(self)

        # Create ShowBase Object for Panda3D Rendering and event handling
        self.base = ShowBase()

        # Set Some defaults
        white = LVecBase4f(1, 1, 1, 1)
        self.base.setBackgroundColor(white)
        self.base.setFrameRateMeter(True)

        # Set Some Common KeyBindings. (Un)Comment as required! ;)
        self.accept("w", self.toogleWireFrame)

        # Collections for all objects and sprites used in the game.
        self.gameObjects = OrderedDict()
        # self.gameSprites = pygame.sprite.Group()

    def toogleWireFrame(self):
        self.base.toggleWireframe()

    def start(self):

        # Start framework classes
        Application.start(self)

        # Start application using Panda3D ShowBase.run method as the
        # game main loop
        self.base.spawnPGLoop(self.gameLoop)
        self.isRunning = True
        self.isStopped = False
        self.gameLoop(self.base)
        # self.base.run()

    def gameLoop(self, base):
        # Keep looping infinitely
        while True:
            # Get loop starting time for performance monitoring
            start = time.time()

            # If the stop indicator variable is set, exit the loop
            if self.isRunning is False:
                self.isStopped = True
                break

            #################################
            # User Input Events section (UserSpace hook)
            ####################################################################
            # self.gameEvents(pygame.event.get())

            #################################
            # Object update section
            ###################################################################
            # Update tracked Objects (several user-space hooks inside)
            self.updateTrackedObjects()

            # Update non tracked objects
            # self.gameSprites.update()

            ###############################
            # Game logic section (Userspace hook)
            ###################################################################
            # self.gameLogic()

            #################################
            # Drawing section
            ####################################################################
            # Clear screen to redraw everything for each frame
            # self.screen.fill((255, 255, 255))

            # Draw all the sprites in one go.
            # self.gameSprites.draw(self.screen)

            # Custom drawing before display flip (user-space hook).
            # self.drawPreFlip()

            # Update the screen
            # pygame.display.flip()

            ###################################
            # --- Limit to 30 frames per second
            ###################################################################
            # self.clock.tick(30)

            # Callback to Panda3D for frame rendering
            base.pgCallBack()

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
                    # self.gameSprites.add(self.gameObjects[id_])
                if self.trackerObjectStatus[id_] == "Updated":
                    self.gameObjects[id_] = self.objectAdd(id_, obj)
                    # self.gameSprites.add(self.gameObjects[id_])
                return

        # Beyond this point, gameObjects is not empty so we have to update it
        # 1. Process new objects received from tracker
        for (id_, obj) in self.trackerObjects.items():
            if self.trackerObjectStatus[id_] == "New":
                self.gameObjects[id_] = self.objectAdd(id_, obj)
                # self.gameSprites.add(self.gameObjects[id_])

        # 2. Process updated objects
        gameExistingIds = list(self.gameObjects)
        for (id_, obj) in self.trackerObjects.items():
            if self.trackerObjectStatus[id_] == "Updated":
                if id_ in gameExistingIds:
                    self.objectUpdate(id_, obj)
                else:
                    # Create a new one
                    self.gameObjects[id_] = self.objectAdd(id_, obj)
                    # self.gameSprites.add(self.gameObjects[id_])

        # 3. Delete "Lost" objects
        trackerExistingIds = list(self.trackerObjects)
        for id_ in list(self.gameObjects):
            if id_ not in trackerExistingIds:
                self.objectDelete(id_)
                # self.gameSprites.remove(self.gameObjects[id_])
                del self.gameObjects[id_]

        # Reset Tracker Update Flag
        self.trackerUpdateFlag = False

    def close(self):
        # Warning! Do not call self.close() inside main game loop or the
        #
        # execution will block forever!.
        super().close()

        # Quit Pygame
        # pygame.quit()
