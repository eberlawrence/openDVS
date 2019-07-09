import socket
import pygame
from time import time

HOST = ''
PORT = 8000
clock = pygame.time.Clock()
m = 4

class DisplayDVS128:
    pygame.display.set_caption('Neuromorphic Camera - DVS128')

    def __init__(self, width, height):
        self.width = width * m
        self.height = width * m
        self.background = (255, 255, 255)
        self.colorPos = (255, 0, 0)
        self.colorNeg = (0, 0, 0)
        self.gameDisplay = pygame.display.set_mode((self.width, self.height))
        self.gameDisplay.fill(self.background)

    def plotEvents(self, pol, x, y, ts):
        i = 0
        while i < len(pol):
            if pol[i] == 0:
                self.gameDisplay.fill(self.colorPos, ((127 - x[i]) * m, (127 - y[i]) * m, m, m))
                i += 1
            else:
                self.gameDisplay.fill(self.colorNeg, ((127 - x[i]) * m, (127 - y[i]) * m, m, m))
                i += 1
		
		

def main():
    pygame.init()
    display = DisplayDVS128(128, 128)
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind((HOST, PORT))
    pol, x, y, ts = [], [], [], []
    while True:
        vet = []
        t = time()
        msg, cliente = udp.recvfrom(65535)
        for a in msg:
            vet.append(a)
        size = int(len(vet)/4)
        pol.extend(vet[ : size])
        x.extend(vet[size : 2 * size])
        y.extend(vet[2 * size : 3 * size])
        ts.extend(vet[3 * size : ])
        print(time()-t)
        if sum(ts) >= 16700: # 60 fps
            display.gameDisplay.fill(display.background)
            display.plotEvents(pol, x, y, ts)
            pol, x, y, ts = [], [], [], []        
        
        pygame.display.update()
    pygame.quit()
    udp.close()


if __name__ == "__main__":
	main()
