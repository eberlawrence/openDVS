import numpy as np
import math 
import pygame
from random import randint
from time import time
from keras.models import model_from_json

class DisplayDVS128:
    pygame.display.set_caption('Neuromorphic Camera - DVS128')

    def __init__(self, width, height, m=7):
        self.m = m
        self.width = width * self.m
        self.height = height * self.m
        self.background = (128, 128, 128)
        self.colorPos = (255, 255, 255)
        self.colorNeg = (0, 0, 0)
        self.gameDisplay = pygame.display.set_mode((self.width, self.height))
        self.gameDisplay.fill(self.background)        
        
    def printFPS(self, fps):
        font = pygame.font.SysFont('Segoe UI', 20)
        txtFPS = font.render('FPS: {0:.2f}'.format(fps), True, (0, 0, 0))
        self.gameDisplay.blit(txtFPS,(0,0))
		
    def plotEvents(self, pol, x, y, ts):
        i = 0
        while i < len(pol):
            if pol[i] == 0:
                self.gameDisplay.fill(self.colorPos, ((127 - x[i]) * self.m, y[i] * self.m, self.m, self.m))
                i += 1
            else:
                self.gameDisplay.fill(self.colorNeg, ((127 - x[i]) * self.m, y[i] * self.m, self.m, self.m))
                i += 1	

		
		
class BoundingBox(object):
    
    def __init__(self, screen, x, y, M=7):
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
            if len(p) < (((2*l+1)**2)*0.4):
                cond = True
                return p
            else:
                l += 2                
                                
    def particlesFromEvents(self):
        xy = np.array(list(zip(self.x, self.y)))
        i, j = len(xy),  int(len(xy)*0.02)
        while len(xy) > 0 and i > 0:     
            auxXY = xy - xy[0]
            auxXY = self.checkNeighborhood(auxXY) + xy[0]
            i -= j
            xy = np.array(list(set(list(map(tuple, xy))) - set(list(map(tuple, auxXY)))))
            if len(auxXY) > 4:
                self.partic.append(auxXY)
                        
        for p in self.partic:            
            Pxmin = int((127 - np.amin(np.array(p[:,0]))) * self.M) 
            Pymin = int(np.amin(np.array(p[:,1])) * self.M)
            Pxmax = int((127 - np.amax(np.array(p[:,0]))) * self.M - Pxmin)
            Pymax = int(np.amax(np.array(p[:,1])) * self.M - Pymin)
            pygame.draw.rect(self.screen, (255, 0, 0), [Pxmin, Pymin, Pxmax, Pymax], 4)                

    def particlesFromFrames(self):      
        matrix = np.zeros([128, 128])
        for i in range(len(self.x)):
            matrix[self.x[i],self. y[i]] = 1
        p = []
        c = 2
        
        while c < 128:
            l = 2
            while l < 128:
                m = np.sum([matrix[l - 2 : l + 3, c - 2 : c + 3]])
                if m >= 5:
                    p.append((l, c))  
                    self.screen.fill((0, 255, 0), (l * self.M, c * self.M, self.M, self.M))              
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
            pygame.draw.circle(self.screen, (0, 255, 0), (127 - medianX * self.M, medianY * self.M), self.M * 10, 3)



def OpenModel(model_JSON_file, model_WEIGHTS_file):
	'''
	imgC = UploadModel.OpenModel('/home/user/GitHub/Classification_DVS128/model.json', '/home/user/GitHub/Classification_DVS128/model.h5')
	'''	
	# load model from JSON file
	with open(model_JSON_file, "r") as json_file:
		loadedModel_JSON = json_file.read()
		loadedModel = model_from_json(loadedModel_JSON)

	# load weights into the new model
	loadedModel.load_weights(model_WEIGHTS_file)
	loadedModel._make_predict_function()
	
	return loadedModel


def predictObject(img, model, flag='N'):

	# flag = input("Would you like to change the default object set? ")  
	if flag == "Sim" or flag == "sim" or flag == "S" or flag == "s":
		objectSet = input("New object set: ").split(", ")
	else:
		objectSet = [[0, 'Caneca'],
					 [1, 'Nada'],
					 [2, 'Calculadora'],
					 [3, 'Chave'],
					 [4, 'Tesoura']]
					 
	preds = model.predict(img)
	return objectSet[np.argmax(preds)][0], objectSet

	

