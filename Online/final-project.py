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
from itertools import groupby
import serial


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

model = utilsDVS128.openModel('model/model2.json',
							  'model/model2.h5')

ard = serial.Serial('/dev/ttyUSB0', 9600)

def main():

	start, stop = False, False
	pygame.init()
	displayEvents = utilsDVS128.DisplayDVS128(128, 128)
	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	udp.bind((HOST, PORT))
	pol, x, y, ts_LSB, ts_MSB = [], [], [], [], []
	countShape, countAngle = [], []
	var = []

	while True:
		print(ard.in_waiting)
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


				size = int(len(vet)/5)
				pol.extend(vet[ : size])
				x.extend(vet[size : 2 * size])
				y.extend(vet[2 * size : 3 * size])
				ts_LSB.extend(vet[3 * size : 4 * size])
				ts_MSB.extend(vet[4 * size : ])
				ts = list(map(lambda LSB, MSB: LSB + (MSB << 8), ts_LSB, ts_MSB))


				if np.sum(ts) >= 10000: # acumulate events during that time
					displayEvents.plotEventsF(pol, x, y)

					img = displayEvents.frame
					img = img.reshape(1, 128, 128, 1)

					resp, objectSet = utilsDVS128.predictShape(img, model)
					ori = utilsDVS128.Orientation(displayEvents)
					ori.getOrientation()

					countShape.append(resp)
					countAngle.append(ori.ang)

					if len(countShape) == 100:
						countShape = np.bincount(countShape) # array with the number of times that each number repeats.
						countAngle = int((24/360) * np.median(countAngle))
						print(objectSet[np.argmax(countShape)][1])
						print(countAngle)
						ard.write(bytes([np.argmax(countShape)]))
						ard.write(bytes([countAngle]))
						countShape, countAngle = [], []
						stop = True

					t2 = time() - t
					displayEvents.printFPS(1/t2)
					pygame.display.update()

					pol, x, y, ts_LSB, ts_MSB = [], [], [], [], [] # reset the lists
			stop = False

	pygame.quit()
	udp.close()

if __name__ == "__main__":
	main()
