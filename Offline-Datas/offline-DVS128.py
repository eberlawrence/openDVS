import pygame
from time import time
import numpy as np
import utilsDVS128
import openAEDAT

clock = pygame.time.Clock()

def main():
    t = time()
    stop = False
    pygame.init()
    displayEvents = utilsDVS128.DisplayDVS128(128, 128)

    

    while not stop:
        pol, x, y, ts = openAEDAT.loadaerdat('/home/user/GitHub/openDVS/TrackingCopo.aedat')
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                stop = True
                
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
            bB.particlesFromEvents()
            t2 = time() - t               
            displayEvents.printFPS(1/t2)            
            pygame.display.update()
            t = time()
            pol, x, y, ts = [], [], [], [] 
       
    pygame.quit()
    udp.close()

if __name__ == "__main__":
	main()
