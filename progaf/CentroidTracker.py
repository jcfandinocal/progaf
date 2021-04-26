############################################
# PROGAF                                   #
# Projection Games Framework               #
############################################
# CentroidTracker.py                       #
############################################
from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np
import copy
import time
import cv2


class CentroidTracker:

    def __init__(self, detector, application, maxMissCount=50):

        self.det = detector
        self.det.tracker = self
        self.app = application

        self.nextObjectID = 0
        self.maxMissCount = maxMissCount

        # Properties of the tracked objects
        self.objectCentroids = OrderedDict()
        self.objectDets = OrderedDict()
        self.objectTrackStatus = OrderedDict()
        self.objectMissCount = OrderedDict()

        self.displayIDs = True
        self.displayCentroids = False
        self.displayObjects = False

        self.displayOnCamera = False
        self.displayOnProjector = False

        self.perfMon = None

    def registerDetection(self, centroid, det):
        # when registering an object we use the next available object
        # ID to store the centroid
        self.objectCentroids[self.nextObjectID] = centroid
        self.objectDets[self.nextObjectID] = copy.copy(det)
        self.objectTrackStatus[self.nextObjectID] = "New"
        self.objectMissCount[self.nextObjectID] = 0
        self.nextObjectID += 1

    def deregisterDetection(self, objectID):
        # to de-register an object ID we delete the object ID from
        # both of our respective dictionaries and remove it from the
        # main application
        del self.objectCentroids[objectID]
        del self.objectDets[objectID]
        del self.objectTrackStatus[objectID]
        del self.objectMissCount[objectID]

    def update(self, detections):

        # Get update starting time for performance monitoring
        start = time.time()

        # Check to see if the list of input detections is empty.
        if len(detections) == 0:
            # loop over any existing tracked objects and increment their
            # miss count
            for objectID in list(self.objectMissCount.keys()):
                self.objectMissCount[objectID] += 1
                self.objectTrackStatus[objectID] = "Trouble"
                # if we have reached a maximum number of consecutive
                # frames where a given object has been marked as
                # missing (troubled), de-register it
                if self.objectMissCount[objectID] > self.maxMissCount:
                    self.deregisterDetection(objectID)

            # Update application with tracking information.
            self.updateApplication()

            # Display update is required.
            self.display()

            # Get end time and update performance monitor
            if self.perfMon is not None:
                end = time.time()
                self.perfMon.collectOTTSample(end - start)

            # Early return, there are no objects to update.
            return

        ##########################
        # Try to assign detection centroids to tracked objects
        ########################################################################
        # If we are currently not tracking any objects, we need to register all
        # detections as new objects
        if len(self.objectCentroids) == 0:
            for detection in detections:
                self.registerDetection((detection.xpos, detection.ypos),
                                       detection)

        # Otherwise, we are currently tracking objects so we need to
        # try to match the input detection centroids to existing
        # tracked object centroids
        else:
            # Grab the set of tracked object IDs and corresponding centroids
            objectIDs = list(self.objectCentroids.keys())
            objectCentroids = list(self.objectCentroids.values())

            # Grab the set of input centroids and associated detections
            inputCentroid = np.zeros((len(detections), 2), dtype="int")
            inputObjectDet = OrderedDict()
            for (i, detection) in enumerate(detections):
                inputCentroid[i] = (detection.xpos, detection.ypos)
                inputObjectDet[i] = detection

            # Compute the distance between each pair of object
            # centroids and detection (input) centroids, respectively -- our
            # goal will be to match an input centroid to an existing
            # object centroid
            D = dist.cdist(np.array(objectCentroids), inputCentroid)
            # in order to perform this matching we must (1) find the
            # smallest value in each row and then (2) sort the row
            # indexes based on their minimum values so that the row
            # with the smallest value is at the *front* of the index
            # list
            rows = D.min(axis=1).argsort()
            # next, we perform a similar process on the columns by
            # finding the smallest value in each column and then
            # sorting using the previously computed row index list
            cols = D.argmin(axis=1)[rows]
            # in order to determine if we need to update, register,
            # or de-register an object we need to keep track of which
            # of the rows and column indexes we have already examined
            usedRows = set()
            usedCols = set()
            # loop over the combination of the (row, column) index
            # tuples
            for (row, col) in zip(rows, cols):
                # if we have already examined either the row or
                # column value before, ignore it
                if row in usedRows or col in usedCols:
                    continue
                # otherwise, grab the object ID for the current row,
                # set its new centroid, and reset the missed detection
                # counter
                objectID = objectIDs[row]
                self.objectCentroids[objectID] = inputCentroid[col]
                self.objectDets[objectID] = copy.copy(inputObjectDet[col])
                self.objectTrackStatus[objectID] = "Updated"
                self.objectMissCount[objectID] = 0

                # indicate that we have examined each of the row and
                # column indexes, respectively
                usedRows.add(row)
                usedCols.add(col)
            # compute both the row and column index we have NOT yet
            # examined
            unusedRows = set(range(0, D.shape[0])).difference(usedRows)
            unusedCols = set(range(0, D.shape[1])).difference(usedCols)
            # in the event that the number of object centroids is
            # equal or greater than the number of input centroids
            # we need to check and see if some of these objects have
            # potentially disappeared
            if D.shape[0] >= D.shape[1]:
                # loop over the unused row indexes
                for row in unusedRows:
                    # grab the object ID for the corresponding row
                    # index and increment the missed detection counter
                    objectID = objectIDs[row]
                    self.objectMissCount[objectID] += 1
                    self.objectTrackStatus[objectID] = "Trouble"
                    # check to see if the number of consecutive
                    # frames the object detection has been missed
                    # requires de-registering the object
                    if self.objectMissCount[objectID] > self.maxMissCount:
                        self.deregisterDetection(objectID)
            # otherwise, if the number of input centroids is greater
            # than the number of existing object centroids we need to
            # register each new input centroid as a trackable object
            else:
                for col in unusedCols:
                    self.registerDetection(inputCentroid[col], inputObjectDet[col])

        # Update application with tracking information
        self.updateApplication()

        # Display Tracked Objects (for debugging)
        self.display()

        # Get end time and update performance monitor
        if self.perfMon is not None:
            end = time.time()
            self.perfMon.collectOTTSample(end - start)

        # "Late" return (see "early" return above)
        return

    def updateApplication(self):
        ################
        # Copy tracked objects to game application
        self.app.trackerObjects = copy.deepcopy(self.objectDets)
        self.app.trackerObjectStatus = copy.deepcopy(self.objectTrackStatus)
        self.app.trackerUpdateFlag = True

    def display(self):
        ################
        # Display tracked objects
        # This method displays tracked objects, for debugging purposes, over:
        # - Camera    frames when self.displayOnCamera    == True
        # - Projector frames when self.displayOnProjector == True
        ########################################################################

        for (objectID, centroid) in self.objectCentroids.items():
            text = "ID:{}".format(objectID)

            green = (0, 255, 0)
            yellow = (0, 255, 255)
            red = (0, 0, 255)

            colour = green
            if self.objectMissCount[objectID] > 30:
                colour = red
            elif self.objectMissCount[objectID] > 10:
                colour = yellow

            # Display over camera frames
            if self.displayOnCamera is True:
                cv2.circle(self.det.cam.frame, (centroid[0], centroid[1]), 5, colour, -1)
                cv2.putText(self.det.cam.frame, text, (centroid[0] + 5, centroid[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            colour, 1)

            # Display over projector frames
            if self.displayOnProjector is True:
                self.det.proj.drawCircle(centroid[0], centroid[1], colour)
                self.det.proj.drawText(text, centroid[0] + 5, centroid[1] - 5, colour)

