'''
Biomedical Engineering Lab (BioLab)- Federal University of Uberlandia (UFU)
Eber Lawrence Souza - email: eberlawrence@hotmail.com

This script it receive and visualize the event flow of DVS128 camera
using UDP socket (c to python) and pygame.
To connect through the UDP socket, run the c file dvs128.c in the folder ''/openDVS/Online'

Moreover, it can classify in real time some objects and send the result to an arduino code.


TO DO:

'''

import socket
import pygame
from time import time
import numpy as np
import utilsDVS128
import tensorflow as tf
import serial
import sys
sys.path.append('/home/user/GitHub/HandStuff/Detection')

from segmentationUtils import segmentationUtils


if tf.__version__ == '2.0.0':
	physical_devices = tf.config.experimental.list_physical_devices('GPU')
	tf.config.experimental.set_memory_growth(physical_devices[0], True)
elif tf.__version__ == '1.14.0':
	config = tf.ConfigProto()
	config.gpu_options.allow_growth = True
	session = tf.Session(config=config)

HOST = ''
PORT = 8000
clock = pygame.time.Clock()

model = utilsDVS128.openModel('model/model7.json', 'model/model7.h5')

ard = serial.Serial('/dev/ttyUSB0', 115200)

def main():

	stop = False
	pygame.init()
	displayEvents = utilsDVS128.DisplayDVS128(128, 128)
	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	udp.bind((HOST, PORT))
	pol, x, y, ts_LSB, ts_MSB = [], [], [], [], []
	countShape, countAngle = [], []
	var = []

	while True:
		if str(ard.readline())[2] == '1':
			while not stop:
				t = time()
				for e in pygame.event.get():
					if e.type == pygame.QUIT:
						stop = True

				vet = []
				msg, cliente = udp.recvfrom(30000)
				for a in msg:
					vet.append(a)

				size = int(len(vet) / 5)
				pol.extend(vet[ : size])
				x.extend(vet[size : 2 * size])
				y.extend(vet[2 * size : 3 * size])
				ts_LSB.extend(vet[3 * size : 4 * size])
				ts_MSB.extend(vet[4 * size : ])
				ts = list(map(lambda LSB, MSB: LSB + (MSB << 8), ts_LSB, ts_MSB))

				if np.sum(ts) >= 30000: # acumulate events during that time
					displayEvents.plotEventsF(pol, x, y)
					img = displayEvents.frame
					watershedImage, mask, detection, opening, sure_fg, sure_bg, markers = segmentationUtils.watershed(img, '--neuromorphic', minimumSizeBox=0.5, smallBBFilter=True, centroidDistanceFilter = True, mergeOverlapingDetectionsFilter = True, flagCloserToCenter=True)
					utilsDVS128.plotBoundingBox(displayEvents.gameDisplay, detection, displayEvents.m)
					imgROI, interpROI = segmentationUtils.getROI(detection, img)
					ang = utilsDVS128.getOrientationROI(displayEvents.gameDisplay, imgROI, detection, 6)
					interpROI = interpROI.reshape(1, 64, 64, 1)
					resp, objectSet = utilsDVS128.predictShape(interpROI, model)

					countShape.append(resp)
					countAngle.append(ang)

					if len(countShape) == 100:
						countShape = np.bincount(countShape) # array with the number of times that each number repeats.
						countAngleAux = round(np.median(countAngle),1)
						countAngle = round((1 / 2) * np.median(countAngle))
						print(objectSet[np.argmax(countShape)][1] + ": " + str([np.argmax(countShape)]))
						print(str(countAngleAux) + " Degrees: " + str([int(countAngle + 45)]))
						ard.write(bytes([np.argmax(countShape)]))
						ard.write(bytes([int(countAngle + 45)]))
						countShape, countAngle = [], []
						stop = True

					t2 = time() - t
					displayEvents.printFPS(1 / t2)
					pygame.display.update()

					pol, x, y, ts_LSB, ts_MSB = [], [], [], [], [] # reset the lists
			stop = False

	pygame.quit()
	udp.close()

if __name__ == "__main__":
	main()
