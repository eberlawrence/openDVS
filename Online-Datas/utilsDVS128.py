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
        l = 10
        while not cond:            
            p = pos[(-l <= pos[:,0]) & (pos[:,0] <= l) & (-l <= pos[:,1]) & (pos[:,1] <= l)]
            if len(p) < (((2*l+1)**2)*0.2):
                cond = True
                return p
            else:
                l += 5                
        
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
        i = len(xy)
        j = 0
        while i > 0:     
            auxXY = xy - xy[j]
            auxXY = self.checkNeighborhood(auxXY) + xy[j]
            i -= 20
            j += 20
            if len(auxXY) > 20:
                self.partic.append(auxXY)
              
    def createParticles3(self):
        xy = np.array(list(zip(self.x, self.y)))
        i = len(xy)
        while len(xy) > 0 and i > 0:     
            auxXY = xy - xy[0]
            auxXY = self.checkNeighborhood(auxXY) + xy[0]
            i -= 20
            xy = np.array(list(set(list(map(tuple, xy))) - set(list(map(tuple, auxXY)))))
            if len(auxXY) > 10:
                self.partic.append(auxXY)
        
    def plotParticles(self):
        self.createParticles3()   
        for p in self.partic:            
            Pxmin = int(np.amin(np.array(p[:,0])) * self.M) 
            Pymin = int(np.amin(np.array(p[:,1])) * self.M)
            Pxmax = int(np.amax(np.array(p[:,0])) * self.M - Pxmin)
            Pymax = int(np.amax(np.array(p[:,1])) * self.M - Pymin)
            pygame.draw.rect(self.screen, (255, 0, 0), [Pxmin, Pymin, Pxmax, Pymax], 5)
            
            
    

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


