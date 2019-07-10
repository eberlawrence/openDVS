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
            if m >= 5:
                p.append((l, c))  
                pygame.draw.circle(screen, (255, 0, 0), (l * M, c * M), 2, 1)              
            l += 3
        c += 3
    if len(p) > 10:
        particle = np.array(p)
        Px = int(np.sum(particle[:, 0])/len(particle))
        Py = int(np.sum(particle[:, 1])/len(particle))
        if np.std(particle[:, 0]) > np.std(particle[:, 1]):
            pygame.draw.circle(screen, (255, 0, 0), (Px * M, Py * M), 2*int(np.std(particle[:, 0])), 3)
        else:
            pygame.draw.circle(screen, (255, 0, 0), (Px * M, Py * M), 2*int(np.std(particle[:, 1])), 3)


