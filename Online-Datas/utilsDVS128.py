import numpy as np
import math 
from scipy import signal
import pygame
from random import randint
from time import time

class BoundingBox(object):
    
    def __init__(self, screen, x, y, M):
        self.x = x
        self.y = y
        self.screen = screen
        self.coord = np.array(list(zip(x, y)))
        self.partic = []
        self.M = M
    
    def checkNeighborhood(self, pos):
        cond = False
        l = 5
        while not cond:            
            p = pos[(-l <= pos[:,0]) & (pos[:,0] <= l) & (-l <= pos[:,1]) & (pos[:,1] <= l)]
            if len(p) < (((2*l+1)**2)*0.1):
                cond = True
                return p
            else:
                l += 2                
        
    def createParticles(self):
        xy = np.array(list(zip(self.x, self.y)))
        while len(xy) > 0:     
            auxXY = xy - xy[0]
            auxXY = self.checkNeighborhood(auxXY) + xy[0]
            xy = np.array(list(set(list(map(tuple, xy))) - set(list(map(tuple, auxXY)))))
            if len(auxXY) > 30:
                self.partic.append(auxXY)                  
              
    def createParticles2(self):
        xy = np.array(list(zip(self.x, self.y)))
        i, j = len(xy),  int(len(xy)*0.1)
        while len(xy) > 0 and i > 0:     
            auxXY = xy - xy[0]
            auxXY = self.checkNeighborhood(auxXY) + xy[0]
            i -= j
            xy = np.array(list(set(list(map(tuple, xy))) - set(list(map(tuple, auxXY)))))
            if len(auxXY) > 5:
                self.partic.append(auxXY)
        
    
    def plotParticles(self):
        self.createParticles2()   
        for p in self.partic:            
            Pxmin = int((127 - np.amin(np.array(p[:,0]))) * self.M) 
            Pymin = int(np.amin(np.array(p[:,1])) * self.M)
            Pxmax = int((127 - np.amax(np.array(p[:,0]))) * self.M - Pxmin)
            Pymax = int(np.amax(np.array(p[:,1])) * self.M - Pymin)
            pygame.draw.rect(self.screen, (255, 0, 0), [Pxmin, Pymin, Pxmax, Pymax], 4)
            
            
    

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


