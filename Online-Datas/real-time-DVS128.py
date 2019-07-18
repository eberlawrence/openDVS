import socket
import pygame
from time import time
import numpy as np
import utilsDVS128

HOST = ''
PORT = 8000
clock = pygame.time.Clock()

def main():
    t = time()
    stop = False
    pygame.init()
    displayEvents = utilsDVS128.DisplayDVS128(128, 128)
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind((HOST, PORT))
    pol, x, y, ts = [], [], [], []

    while not stop:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                stop = True
                
        vet = []
        msg, cliente = udp.recvfrom(10000)

        for a in msg:
            vet.append(a)

        size = int(len(vet)/4)
        pol.extend(vet[ : size])
        x.extend(vet[size : 2 * size])
        y.extend(vet[2 * size : 3 * size])
        ts.extend(vet[3 * size : ])
        if np.sum(ts) >= 10000: # 6 fps
            
            displayEvents.gameDisplay.fill(displayEvents.background)
            displayEvents.plotEvents(pol, x, y, ts)
            bB = utilsDVS128.BoundingBox(displayEvents.gameDisplay, x, y)
            bB.particlesFromFrames()
            t2 = time() - t               
            displayEvents.printFPS(1/t2)            
            pygame.display.update()
            t = time()
            pol, x, y, ts = [], [], [], [] 
       
    pygame.quit()
    udp.close()

if __name__ == "__main__":
	main()
