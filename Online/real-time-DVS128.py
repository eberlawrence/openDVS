'''
Biomedical Engineering Lab (BioLab)- Federal University of Uberlandia (UFU)
Eber Lawrence Souza - email: eberlawrence@hotmail.com

This script it receive and visualize the event flow of DVS128 camera
using UDP socket (c to python) and pygame.
To connect through the UDP socket, run the c file dvs128.c in the folder ''/openDVS/Online'


TO DO:

'''

import socket
import pygame
from time import time
import utilsDVS128


m = 2
frameTime = 10000
HOST = ''
PORT = 8000
clock = pygame.time.Clock()

def main():

	stop = False
	pygame.init()
	displayEvents = utilsDVS128.DisplayDVS128(128, 128, m)
	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	udp.bind((HOST, PORT))
	pol, x, y, ts_LSB, ts_MSB = [], [], [], [], []
	count = []
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

		if sum(ts) >= frameTime:
			displayEvents.plotEventsF(pol, x, y)
			t2 = time() - t
			displayEvents.printFPS(1/t2)
			pygame.display.update()
			pol, x, y, ts_LSB, ts_MSB = [], [], [], [], []

	pygame.quit()
	udp.close()

if __name__ == "__main__":
	main()
