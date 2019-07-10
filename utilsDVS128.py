import numpy as np
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
            if m >= 3:
                p.append((l, c))  
                pygame.draw.circle(screen, (255, 0, 0), (l * M, c * M), 2, 1)              
            l += 3
        c += 3




