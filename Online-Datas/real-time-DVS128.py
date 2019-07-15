import socket
import pygame
from time import time
import numpy as np
import utilsDVS128


HOST = ''
PORT = 8000
clock = pygame.time.Clock()
m = 4

class DisplayDVS128:
    pygame.display.set_caption('Neuromorphic Camera - DVS128')

    def __init__(self, width, height):
        self.width = width * m
        self.height = height * m
        self.background = (128, 128, 128)
        self.colorPos = (255, 255, 255)
        self.colorNeg = (0, 0, 0)
        self.gameDisplay = pygame.display.set_mode((self.width, self.height))
        self.gameDisplay.fill(self.background)

    def plotEvents(self, pol, x, y, ts):
        i = 0
        while i < len(pol):
            if pol[i] == 0:
                self.gameDisplay.fill(self.colorPos, (x[i] * m, y[i] * m, m, m))
                i += 1
            else:
                self.gameDisplay.fill(self.colorNeg, (x[i] * m, y[i] * m, m, m))
                i += 1
	
    def printFPS(self, fps):
        font = pygame.font.SysFont('Segoe UI', 20)
        txtFPS = font.render('FPS: {0:.2f}'.format(fps), True, (0, 0, 0))
        self.gameDisplay.blit(txtFPS,(0,0))
		

def main():
    t = time()
    pygame.init()
    displayEvents = DisplayDVS128(128, 128)
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind((HOST, PORT))
    pol, x, y, ts = [], [], [], []

    while True:
        vet = []
        msg, cliente = udp.recvfrom(10000)

        for a in msg:
            vet.append(a)

        size = int(len(vet)/4)
        pol.extend(vet[ : size])
        x.extend(vet[size : 2 * size])
        y.extend(vet[2 * size : 3 * size])
        ts.extend(vet[3 * size : ])
        #print(np.sum(ts))
        if np.sum(ts) >= 10000: # 6 fps
            
            displayEvents.gameDisplay.fill(displayEvents.background)
            displayEvents.plotEvents(pol, x, y, ts)
            bB = utilsDVS128.BoundingBox(displayEvents.gameDisplay, x, y, m)
            bB.plotParticles()
            t2 = time() - t               
            displayEvents.printFPS(1/t2)            
            pygame.display.update()
            #print(t2)
            t = time()
            pol, x, y, ts = [], [], [], [] 
       
    pygame.quit()
    udp.close()


if __name__ == "__main__":
	main()
