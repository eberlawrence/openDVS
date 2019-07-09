import socket
import struct
import pygame
import numpy as np

HOST = ''
PORT = 8080
clock = pygame.time.Clock()
m = 8

class DisplayDVS128:
    pygame.display.set_caption('Neuromorphic Camera - DVS128')

    def __init__(self, width, height):
        self.width = width * m
        self.height = width * m
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.gameDisplay = pygame.display.set_mode((self.width, self.height))
        self.gameDisplay.fill(self.black)

    def plotEvents(self, pol, x, y, ts):
        i = 0
        while i < len(pol):
            if pol[i] == 0:
                self.gameDisplay.fill(self.green, ((127 - x[i]) * m, (127 - y[i]) * m, m, m))
                i += 1
            else:
                self.gameDisplay.fill(self.red, ((127 - x[i]) * m, (127 - y[i]) * m, m, m))
                i += 1
		
		

def main():
    pygame.init()
    display = DisplayDVS128(128, 128)
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind((HOST, PORT))
    pol, x, y, ts = [], [], [], []
    while True:
        vet = []
        msg, cliente = udp.recvfrom(65535)
        for a in msg:
            vet.append(a)
        pol.append(vet[0])
        x.append(vet[1])
        y.append(vet[2])
        ts.append((vet[3] << 24) | (vet[4] << 16) | (vet[5] << 8) | (vet[6] << 0))
        if (ts[-1] - ts[0]) >= 33000:
            display.gameDisplay.fill(display.black)
            display.plotEvents(pol, x, y, ts)
            pol, x, y, ts = [], [], [], []        

        pygame.display.update()
        clock.tick()

    pygame.quit()
    udp.close()


if __name__ == "__main__":
	main()
