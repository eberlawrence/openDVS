'''
Biomedical Lab (BioLab)- Federal University of Uberlandia (UFU)
By Eber Lawrence Souza

Script:
    Useful functions for working with a DVS128.

    The script consists of:

    -> Classes:
        - DisplayDVS128
            *Methods:
                - printFPS()
                - plotEventsF()
                - plotEvents()

        - BoundingBox
            *Methods:
                - checkNeighborhood()
                - particlesFromEvents()
                - particlesFromFrames()

    -> Functions:
        - openModel()
        - predictObject()
        - eventsToFrame()

'''


import cv2
import math
import pygame
import numpy as np
from keras.models import model_from_json

class DisplayDVS128:
    '''

    '''

    pygame.display.set_caption('Neuromorphic Camera - DVS128')

    def __init__(self, width, height, m=4):
        self.m = m
        self.width = width * self.m
        self.height = height * self.m
        self.background = (128, 128, 128)
        self.colorPos = (255, 255, 255)
        self.colorNeg = (0, 0, 0)
        self.gameDisplay = pygame.display.set_mode((self.width, self.height))
        self.gameDisplay.fill(self.background)
        self.surf = None

    def printFPS(self, fps):
        font = pygame.font.SysFont('Segoe UI', 20)
        txtFPS = font.render('FPS: {0:.2f}'.format(fps), True, (0, 0, 0))
        self.gameDisplay.blit(txtFPS,(0,0))

    def plotEventsF(self, pol, x, y):
        self.surf = eventsToFrame(pol, x, y)
        surfPrinted = cv2.resize(np.dstack([self.surf, self.surf, self.surf]).astype('float32'),
                                           (128 * self.m, 128 * self.m),
                                           interpolation=cv2.INTER_AREA)
        pygame.surfarray.blit_array(self.gameDisplay, surfPrinted)

    def plotEvents(self, pol, x, y):
        i = 0
        while i < len(pol):
            if pol[i] == 0:
                self.gameDisplay.fill(self.colorPos, ((127 - x[i]) * self.m, y[i] * self.m, self.m, self.m))
                i += 1
            else:
                self.gameDisplay.fill(self.colorNeg, ((127 - x[i]) * self.m, y[i] * self.m, self.m, self.m))
                i += 1


class BoundingBox:

    def __init__(self, screen, x, y, M=4):
        self.x = x
        self.y = y
        self.screen = screen
        self.partic = []
        self.M = M

    def checkNeighborhood(self, pos):
        stop = False
        l = 3
        per = 40
        area = (4 * (l * l)) + (4 * l) + 1
        while not stop:
            p = pos[(-l <= pos[:,0]) & (pos[:,0] <= l) & (-l <= pos[:,1]) & (pos[:,1] <= l)]

            if len(p) > area * (per / 100):
                l += 2
                area = (4 * (l * l)) + (4 * l) + 1
            else:
                stop = True
                return p


    def particlesFromEvents(self):
        xy = np.array(list(zip(self.x, self.y)))
        i, j = len(xy), int(len(xy)*0.04)
        while len(xy) > 0 and i > 0:
            auxXY = xy - xy[0]
            auxXY = self.checkNeighborhood(auxXY) + xy[0]
            i -= j
            xy = np.array(list(set(map(tuple, xy)) - set(map(tuple, auxXY))))
            if len(auxXY) > 50:
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
            Px = int(np.sum(particle[:, 0]) / len(particle))
            Py = int(np.sum(particle[:, 1]) / len(particle))
            medianX = int(np.median(particle[:, 0]))
            medianY = int(np.median(particle[:, 1]))
            squareDiff = 0
            for i in particle[:, 0]:
                squareDiff += ((i - medianX)**2)

            d = math.sqrt(squareDiff/len(particle))
            pygame.draw.circle(self.screen,
                               (0, 255, 0),
                               (127 - medianX * self.M, medianY * self.M),
                               self.M * 10, 3)




def openModel(model_JSON_file, model_WEIGHTS_file):
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


def eventsToFrame(pol, x, y):
    matrix = np.zeros((128, 128)) # Cria uma matriz de zeros 128x128 onde serão inseridos os eventos
    pol = (np.array(pol) - 0.5) # Os eventos no array de Polaridade passam a ser -0.5 ou 0.5

    for i in range(len(x)):
            matrix[y[i], x[i]] = pol[i] # insere os eventos dentro da matriz de zeros
    matrix = (matrix)*255 + 127.5 # Normaliza a matriz para 8bits -> 0 - 255
    return matrix.T
