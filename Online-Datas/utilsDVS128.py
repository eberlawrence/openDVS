import numpy as np
import math 
from scipy import signal
import pygame

def boundingBoxPart(screen, x, y, M):
    matrix = np.zeros([128, 128])
    for i in range(len(x)):
        matrix[x[i], y[i]] = 1
    p = []
    c = 2
    
    while c < 128:
        l = 2
        while l < 128:
            m = np.sum([matrix[l - 2 : l + 3, c - 2 : c + 3]])
            if m >= 5:
                p.append((l, c))  
                screen.fill((0, 255, 0), (l * M, c * M, M, M))              
            l += 5
        c += 5
    if len(p) > 2:
        particle = np.array(p)
        Px = int(np.sum(particle[:, 0])/len(particle))
        Py = int(np.sum(particle[:, 1])/len(particle))
        medianX = int(np.median(particle[:, 0]))
        medianY = int(np.median(particle[:, 1]))
        squareDiff = 0
        for i in particle[:, 0]:
            squareDiff += ((i - medianX)**2)
        
        d = math.sqrt(squareDiff/len(particle))
        pygame.draw.circle(screen, (0, 255, 0), (medianX * M, medianY * M), M * 10, 3)


