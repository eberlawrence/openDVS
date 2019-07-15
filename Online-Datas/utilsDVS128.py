import numpy as np
import math 
from scipy import signal
import pygame

class BoundingBox(object):
    
    def __init__(self, screen, x, y, M):
        self.x = x
        self.y = y
        self.screen = screen
        self.coord = np.array(list(zip(x, y)))
        self.partic = []
        self.M = M
    
    def checkNeighborhood(self, pos, l=3):        
        return pos[(-l <= pos[:,0]) & (pos[:,0] <= l) & (-l <= pos[:,1]) & (pos[:,1] <= l)]
        
    def createParticles(self):
        xy = np.array(list(zip(self.x, self.y)))
        while len(xy) > 0:            
            auxXY = xy - xy[0]
            auxXY = self.checkNeighborhood(auxXY) + xy[0]
            self.partic.append(auxXY)
            
            break
            var1 = list(map(tuple, xy))        
            var2 = list(map(tuple, auxXY))           
            xy = np.array(list(set(var1) - set(var2)))       
    
    def plotParticles(self):
        self.createParticles()
        print("\n", self.partic[0])   
        for p in self.partic:            
            if len(p) > 3:
                Px = int(np.mean(np.array(p[:,0])))
                Py = int(np.mean(np.array(p[:,1])))
                pygame.draw.circle(self.screen, (255, 0, 0), (Px * self.M, Py * self.M), self.M * 10, 2)
            
            
    

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


