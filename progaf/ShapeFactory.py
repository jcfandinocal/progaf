############################################
# PROGAF                                   #
# Projection Games Framework               #
############################################
# ShapeFactory.py                          #
############################################
#
# 2021/02/25 Initial Release (by Keko)
#
############################################
from collections import OrderedDict
import numpy as np
import random
import cv2


class RandomRect:

	def __init__(self, w, h):
		self.p1x = random.randint(0, w)
		self.p1y = random.randint(0, h)
		# self.p2x = self.p1x + random.randint(100,300)
		self.p2x = self.p1x + 100
		# self.p2y = self.p1y + random.randint(100,300)
		self.p2y = self.p1y + 100
		self.sx = random.randint(0, 3)
		self.sy = random.randint(0, 3)
		self.moveRight = (random.randint(0, 1) == 1)
		self.moveDown = (random.randint(0, 1) == 1)


class ShapeFactory:

	def __init__(self, width, height):

		self.width = width
		self.height = height
		self.frame = np.zeros((height, width, 3), np.uint8)
		self.frameCounter = 0
		self.speed = 1
		self.objects = OrderedDict()
		self.nextObject = 0

	def createRandomObject(self):

		self.objects[self.nextObject] = RandomRect(self.width, self.height)
		self.nextObject += 1

	def update(self):
		self.frame = np.zeros((self.height, self.width, 3), np.uint8)

		for n, obj in self.objects.items():
			self.updateRect(obj)
			cv2.rectangle(self.frame, (obj.p1x, obj.p1y), (obj.p2x, obj.p2y), (255, 255, 255), 3)

		self.frameCounter += 1
		return self.frame

	def updateRect(self, rect):

		if rect.moveRight is True:
			rect.p1x = rect.p1x + rect.sx*self.speed
			rect.p2x = rect.p2x + rect.sx*self.speed

			if rect.p2x >= self.width:
				rect.moveRight = False

		else:
			rect.p1x = rect.p1x - rect.sx*self.speed
			rect.p2x = rect.p2x - rect.sx*self.speed

			if rect.p1x <= 0:
				rect.moveRight = True

		if rect.moveDown is True:
			rect.p1y = rect.p1y + rect.sy*self.speed
			rect.p2y = rect.p2y + rect.sy*self.speed

			if rect.p2y >= self.height:
				rect.moveDown = False

		else:
			rect.p1y = rect.p1y - rect.sy*self.speed
			rect.p2y = rect.p2y - rect.sy*self.speed

			if rect.p1y <= 0:
				rect.moveDown = True
