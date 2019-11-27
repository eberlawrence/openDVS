import pygame
import numpy as np
import utilsDVS128
import openAEDAT

clock = pygame.time.Clock()

def main():
    stop = False
    pygame.init()
    displayEvents = utilsDVS128.DisplayDVS128(128, 128)

    
    ts, x, y, pol = openAEDAT.loadaerdat('//home//user//GitHub//openDVS//recordings//velocidade_1_e_2_experimento_3.aedat')
    temp = 100000
    ini, fin = 0, temp
    ti = ts[0]
    ts -= ti
    
    while not stop:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                stop = True
                
        displayEvents.gameDisplay.fill(displayEvents.background)
        displayEvents.plotEvents(pol[(ini < ts) & (fin > ts)], x[(ini < ts) & (fin > ts)], y[(ini < ts) & (fin > ts)], ts[(ini < ts) & (fin > ts)])
        bB = utilsDVS128.BoundingBox(displayEvents.gameDisplay, x[(ini < ts) & (fin > ts)], y[(ini < ts) & (fin > ts)])
        bB.particlesFromEvents()
        pygame.display.update()                         
        ini += temp
        fin += temp
        #pygame.time.wait(int(temp/1000))
        if max(ts) <= fin:
            ini, fin = 0, temp
        
    pygame.quit()
    udp.close()

if __name__ == "__main__":
	main()
