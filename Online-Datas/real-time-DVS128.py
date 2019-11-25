import socket
import pygame
from time import time
import numpy as np
import utilsDVS128
from openAEDAT import matrix_active
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

model = utilsDVS128.OpenModel('/home/user/GitHub/Classification_DVS128/model.json', '/home/user/GitHub/Classification_DVS128/model.h5')

#ard = serial.Serial('/dev/ttyUSB0', 9600)

def main():
    t = time()
    stop = False
    pygame.init()
    displayEvents = utilsDVS128.DisplayDVS128(128, 128)
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind((HOST, PORT))
    pol, x, y, ts_LSB, ts_MSB = [], [], [], [], []
    count = []
    while not stop:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                stop = True
                
        vet = []
        msg, cliente = udp.recvfrom(50000)

        for a in msg:
            vet.append(a)

        size = int(len(vet)/5)
        pol.extend(vet[ : size])
        x.extend(vet[size : 2 * size])
        y.extend(vet[2 * size : 3 * size])
        ts_LSB.extend(vet[3 * size : 4 * size])
        ts_MSB.extend(vet[4 * size : ])
        ts = list(map(lambda LSB, MSB: LSB + (MSB << 8), ts_LSB, ts_MSB))
            
		
        if np.sum(ts) >= 50000: # 6 fps            
            displayEvents.gameDisplay.fill(displayEvents.background)
            displayEvents.plotEvents(pol, x, y, ts)
            img = matrix_active(np.array(x), np.array(y), np.array(pol))
            img = img.reshape(1, 128, 128, 1)
            resp, objectSet = utilsDVS128.predictObject(img, model)
            count.append(resp)
            
            #print(resp)
            #print(percent)
            #print("\n")
            #bB = utilsDVS128.BoundingBox(displayEvents.gameDisplay, x, y)
            #bB.particlesFromEvents()
            t2 = time() - t               
            displayEvents.printFPS(1/t2)            
            pygame.display.update()
            t = time()
            pol, x, y, ts_LSB, ts_MSB = [], [], [], [], []
            if len(count) == 10:
            	count = np.bincount(count)
            	print(objectSet[np.argmax(count)][1])
            	#ard.write(bytes([np.argmax(count)]))
            	count = []
       
    pygame.quit()
    udp.close()

if __name__ == "__main__":
	main()
