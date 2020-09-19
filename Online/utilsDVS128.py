'''
Biomedical Engineering Lab (BioLab)- Federal University of Uberlandia (UFU)
Eber Lawrence Souza - email: eberlawrence@hotmail.com
'''

'''
Script:
    Useful classes and functions for working with a DVS128.

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
        - predictShape()
        - eventsToFrame()

TO DO:
- improve the segmentation methods.
- Finish comments.
'''

import math
import sys
import pygame
import cv2 as cv
import numpy as np
import openAEDAT as oA
from keras.models import model_from_json
import matplotlib.pyplot as plt

sys.path.append('/home/user/GitHub/HandStuff/Detection')

from segmentationUtils import segmentationUtils




class DisplayDVS128:
    '''
    Class created to display the event flow on a pygame screen.
    Pygame is very useful for creating and updating a screen in real time. So sounds
    good use it for printing events flow in real time.

    Parameters:
    (width, height) -> screen size, so (128, 128) for DVS128
    m -> multiplier of the screen size, for better visualization.

    '''

    def __init__(self, width, height, m=6):
        '''
        Constructor
        '''
        self.m = m # Screen multiplier
        self.width = width * self.m # Setting the axis X
        self.height = height * self.m # Setting the axis Y
        self.background = (128, 128, 128) # Background color (8-bits) -> GRAY
        self.colorPos = (255, 255, 255) # Positive events color (8-bits) -> WHITE
        self.colorNeg = (0, 0, 0) # Negative events color (8-bits) -> BLACK
        pygame.display.set_caption('Neuromorphic Camera - DVS128') # Screen title
        self.gameDisplay = pygame.display.set_mode((self.width, self.height))
        self.gameDisplay.fill(self.background)
        self.frame = np.array([]) # attribute to receive a frame of an events flow

    def printFPS(self, fps):
        '''
        Method to print the FPS on the pygame screen

        Parameters:
        fps -> FPS value.
        '''
        font = pygame.font.SysFont('Segoe UI', 20) # Setting the type of font
        txtFPS = font.render('FPS: {0:.2f}'.format(fps), True, (0, 0, 0)) # Setting the text to be printed
        self.gameDisplay.blit(txtFPS,(0,0)) # printing the FPS

    def plotEventsF(self, pol, x, y):
        '''
        Method to plot a frame made from an event flow on the screen.

        Parameters:
        pol, x, y -> arrays of event polarity (i.e. +1 or -1), X addr event (i.e. 0 to 128) and
        Y addr event (i.e. 0 to 128), respectively
        '''
        self.frame = eventsToFrame(pol, x, y) # it calls the eventsToFrame function and get the event frame
        #self.frame = cv.medianBlur(self.frame.astype('float32'), 3) # it calls the eventsToFrame function and get the event frame

        framePrinted = cv.resize(np.dstack([self.frame, self.frame, self.frame]).astype('float32'),
                                           (128 * self.m, 128 * self.m),
                                           interpolation=cv.INTER_AREA) # change the frame size according to the screen multiplier (m)
        pygame.surfarray.blit_array(self.gameDisplay, framePrinted) # print the frame on the pygame screen

    def plotEvents(self, pol, x, y):
        '''
        Method to plot an event flow on the seceen, like the method above, but rather to create a frame,
        this one just fill the screen with each event obtained.

        Parameters:
        pol, x, y -> arrays of event polarity (i.e. +1 or -1), X addr event (i.e. 0 to 128) and
        Y addr event (i.e. 0 to 128), respectively
        '''
        i = 0
        while i < len(pol):
            if pol[i] == 0:
                self.gameDisplay.fill(self.colorPos, ((127 - x[i]) * self.m, y[i] * self.m, self.m, self.m))
                i += 1
            else:
                self.gameDisplay.fill(self.colorNeg, ((127 - x[i]) * self.m, y[i] * self.m, self.m, self.m))
                i += 1


class BoundingBox:
    '''
    (it needs to improve!)
    Class to segment and create a bounding box for each object on the screen.

    Parameters:
    screen -> class DisplayDVS128, it is used to get the surface and the current frame
    m -> multiplier of the screen size, for better visualization.
    '''
    def __init__(self, screen, m=6):
        '''
        Constructor
        '''
        self.surf = screen.gameDisplay # getting pygame surface
        self.frame = screen.frame # getting the current frame
        self.m = m # screen multiplier
        self.partic = [] # array to be filled with particle dimentions
        self.rect = pygame.draw.rect(self.surf, (255, 0, 0), [0,0,0,0])

    def checkNeighborhood(self, pos):
        '''
        Method to check the event neighborhood with area = 4(l**2 + l), if the number of events
        is higher then a percentage (per), it will return an array of events in that area.

        Parameters:
        pos -> coordinate of an event.
        '''
        stop = False
        l = 3
        per = 40
        area = 4 * ((l * l) + l)
        while not stop:
            p = pos[(-l <= pos[:,0]) & (pos[:,0] <= l) & (-l <= pos[:,1]) & (pos[:,1] <= l)]

            if len(p) > area * (per / 100):
                l += 2
                area = 4 * ((l * l) + l)
            else:
                stop = True
                return p

    def createPartNew(self):
        l = 128
        flag = False
        m = 2 * ((self.frame - 127.5) / 255)
        while flag == False and l >= 10:
            pygame.display.update()
            min = int((len(m)/2) - (l + 1))
            max = int((len(m)/2) + (l + 1))
            aux = m[min : max, min : max]
            flag = True if np.sum(np.abs(aux)) >= len(aux.reshape(-1)) * 0.15 else False
            if flag == True:
                self.rect = pygame.draw.rect(self.surf,
                                             (255, 0, 0),
                                             [(min * self.m), (min * self.m), (max - min) * self.m, (max - min) * self.m],
                                             4) # drawing the bounding box for every particles
            l -= 4

    def particlesFromEvents(self, x, y):
        '''
        Method to create all particles in a array of events.

        Parameters:
        x, y -> X addr event (i.e. 0 to 128) and Y addr event (i.e. 0 to 128), respectively
        '''
        xy = np.array(list(zip(x, y))) # zip X and Y arrays
        i, j = len(xy), int(len(xy)*0.04)
        while len(xy) > 0 and i > 0:
            auxXY = xy - xy[0] # put an offset on the array, the current event at (0, 0) position
            auxXY = self.checkNeighborhood(auxXY) + xy[0] # receiving a new particle and then remove the offset
            i -= j # decreasing the 'i' counter with a step equal 'j'
            xy = np.array(list(set(map(tuple, xy)) - set(map(tuple, auxXY)))) # removing the events of the particle
            if len(auxXY) > 50:
                self.partic.append(auxXY) # placing the particles in an array
        for p in self.partic:
            Pxmin = int((np.amin(np.array(p[:,0]))) * self.m)
            Pymin = int(np.amin(np.array(p[:,1])) * self.m)
            Pxmax = int((np.amax(np.array(p[:,0]))) * self.m - Pxmin)
            Pymax = int(np.amax(np.array(p[:,1])) * self.m - Pymin)
            pygame.draw.rect(self.surf, (255, 0, 0), [Pxmin, Pymin, Pxmax, Pymax], 4) # drawing the bounding box for every particles

    def particlesFromFrames(self, x, y):
        '''
        todo
        '''
        matrix = np.zeros([128, 128])
        for i in range(len(x)):
            matrix[x[i],y[i]] = 1
        p = []
        c = 2

        while c < 128:
            l = 2
            while l < 128:
                m = np.sum([matrix[l - 2 : l + 3, c - 2 : c + 3]])
                if m >= 5:
                    p.append((l, c))
                    self.surf.fill((0, 255, 0), (l * self.m, c * self.m, self.m, self.m))
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
            pygame.draw.circle(self.surf,
                               (0, 255, 0),
                               (127 - medianX * self.m, medianY * self.m),
                               self.m * 10, 3)

    def boundingBoxEduGod(self, flag):
        var = []
        watershedImage, mask, detection = segmentationUtils.watershed(self.frame,
                                                                      '--neuromorphic',
                                                                      minimumSizeBox=0.5,
                                                                      smallBBFilter=True,
                                                                      centroidDistanceFilter = True,
                                                                      mergeOverlapingDetectionsFilter = True)
        for j in range(len(detection)):
            if (detection[j][7] == 'closerToCenter'):
                var = detection[j]
        if flag == True and len(var) != 0:
            self.rect = pygame.draw.rect(self.surf,
                                         (255, 0, 0),
                                         [var[0] * self.m,var[1] * self.m, var[2]* self.m, var[3]* self.m],
                                         4) # drawing the bounding box for every particles

        return var


class Orientation:

    def __init__(self, screen, m=3):
        self.surf = screen.gameDisplay # getting pygame surface
        self.frame = screen.frame # getting the current frame
        self.roi = roi
        self.m = m # screen multiplier
        self.ang = 0

    def get_cloud_point(self, frame):
        frame[frame == 0], frame[frame == 127.5] = frame.max(), 0
        frame = frame.astype('uint8')
        cloud_point, _ = cv.findContours(frame, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
        return cloud_point

    def get_orientation(self):
        pC = self.get_cloud_point(self.frame)
        vet = []

        for i, c in enumerate(pC):
            vet.append([len(c), i])
        pts = pC[max(vet)[1]]
        data_pts = pts.reshape(len(pts),2).astype('float64')
        mean, eivec, eival = cv.PCACompute2(data_pts, np.array([]))
        cntr = (int(mean[0,0]), int(mean[0,1]))
        p1 = (cntr[0] + 0.1 * eivec[0,0] * eival[0,0], cntr[1] + 0.1 * eivec[0,1] * eival[0,0])
        p2 = (cntr[0] - 0.1 * eivec[1,0] * eival[1,0], cntr[1] - 0.1 * eivec[1,1] * eival[1,0])
        pygame.draw.circle(self.surf, (255, 255, 0), (int(cntr[1] * self.m), int(cntr[0] * self.m)), 5)
        pygame.draw.circle(self.surf, (255, 0, 0), (int(p1[1] * self.m), int(p1[0] * self.m)), 5)
        pygame.draw.line(self.surf, (0, 0, 255), (cntr[1] * self.m, cntr[0] * self.m), (p1[1] * self.m, p1[0] * self.m), 7)
        pygame.draw.line(self.surf, (0, 255, 0), (cntr[1] * self.m, cntr[0] * self.m), (p2[1] * self.m, p2[0] * self.m), 7)
        cOpo = p1[1] - cntr[1]
        cAdj = p1[0] - cntr[0]
        ang = math.degrees(math.atan(abs(cOpo / cAdj)))

        if   p1[0] < cntr[0] and p1[1] < cntr[1] or p1[0] > cntr[0] and p1[1] > cntr[1]:
            self.ang = -ang

        elif p1[0] < cntr[0] and p1[1] > cntr[1] or p1[0] > cntr[0] and p1[1] < cntr[1]:
            self.ang = ang


def getOrientationROI(surf, roi, refXY, m):
    ang = 0
    roi[roi == 0], roi[roi == 127.5] = roi.max(), 0
    roi = roi.astype('uint8').T
    roi = cv.medianBlur(roi, 3)
    a, b = np.ogrid[(*map(slice, roi.shape),)]
    pointCloud = np.argwhere(roi > 0)
    if len(pointCloud > 0) and len(refXY) > 0:
        refX, refY = refXY[0][0], refXY[0][1]
        data = pointCloud.reshape(len(pointCloud), 2).astype('float64')
        mean, eivec, eival = cv.PCACompute2(data, np.array([]))

        cntr = (int(mean[0, 0]), int(mean[0, 1]))
        # print(refX, '\n', refY, '\n', cntr, '\n', eivec, '\n', eival, '\n\n\n')
        if len(eivec) == 2 or len(eival) == 2:
            p1 = (cntr[0] + 0.1 * eivec[0, 0] * eival[0, 0], cntr[1] + 0.1 * eivec[0, 1] * eival[0, 0])
            p2 = (cntr[0] - 0.1 * eivec[1, 0] * eival[1, 0], cntr[1] - 0.1 * eivec[1, 1] * eival[1, 0])

            cOpo = p1[1] - cntr[1]
            cAdj = p1[0] - cntr[0]
            ang = math.degrees(math.atan(abs(cOpo / cAdj)))

            if   p1[0] < cntr[0] and p1[1] < cntr[1] or p1[0] > cntr[0] and p1[1] > cntr[1]:
                ang = -ang

            elif p1[0] < cntr[0] and p1[1] > cntr[1] or p1[0] > cntr[0] and p1[1] < cntr[1]:
                ang = ang

            pygame.draw.line(surf, (0, 0, 255), ((cntr[1] + refX) * m, (cntr[0] + refY) * m), ((p1[1] + refX) * m, (p1[0] + refY) * m), 7)
            pygame.draw.line(surf, (0, 255, 0), ((cntr[1] + refX) * m, (cntr[0] + refY) * m), ((p2[1] + refX) * m, (p2[0] + refY) * m), 7)
            pygame.draw.circle(surf, (255, 0, 0), (int((p1[1] + refX) * m), int((p1[0] + refY) * m)), 5)
            pygame.draw.circle(surf, (0, 255, 255), (int((p2[1] + refX) * m), int((p2[0] + refY) * m)), 5)
            pygame.draw.circle(surf, (255, 255, 0), (int((cntr[1] + refX) * m), int((cntr[0] + refY) * m)), 5)
            # pygame.draw.circle(surf, (0, 0, 255), (int((p1[1] + refX) * m + (math.sin(ang)/math.tan(ang)) * 30), int((p1[0] + refY) * m + math.tan(ang)*math.cos(ang)*30)), 10)
            # pygame.draw.polygon(surf, (0, 0, 0), ((int((p1[1] + refX) * m) + (math.sin(ang)/math.tan(ang)) * 20, int((p1[0] + refY) * m) + math.tan(ang)*math(ang)*20), (100, 200), (150, 150)))


    return ang

# roi = img[0][62]
# watershedImage, mask, detection, opening, sure_fg, sure_bg, markers = segmentationUtils.watershed(roi,'--neuromorphic',minimumSizeBox=0.5,smallBBFilter=True,centroidDistanceFilter = True, mergeOverlapingDetectionsFilter = True,flagCloserToCenter=True)
# teste = segmentationUtils.getROI(detection, roi)
#
# roi[roi == 0], roi[roi == 127.5] = roi.max(), 0
# roi = roi.astype('uint8').T
# roi = cv.medianBlur(roi, 3)
# a, b = np.ogrid[(*map(slice, roi.shape),)]
# pointCloud = np.argwhere(roi > 0)
#
# refX, refY, refX2, refY2 = detection[0][0], detection[0][1], detection[0][2], detection[0][3]
# data = pointCloud.reshape(len(pointCloud), 2).astype('float64')
# mean, eivec, eival = cv.PCACompute2(data, np.array([]))
# p1 = (cntr[0] + 0.1 * eivec[0, 0] * eival[0, 0], cntr[1] + 0.1 * eivec[0, 1] * eival[0, 0])
# p2 = (cntr[0] - 0.1 * eivec[1, 0] * eival[1, 0], cntr[1] - 0.1 * eivec[1, 1] * eival[1, 0])
#

# plt.imshow(img[0][54].T, cmap='gray')
# plt.scatter(p1[0] + refX, p1[1] + refY, color='r')
# plt.scatter(p2[0] + refX, p2[1] + refY, color='g')
# plt.scatter(cntr[0] + refX, cntr[1] + refY, color='y')
# plt.show()


def createDataset(path='/home/user/GitHub/aedatFiles/dataset_cbeb_2020/',
                  objClass=[['spoon/spoon_1', 'spoon/spoon_2', 'spoon/spoon_3', 'spoon/spoon_4', 'spoon/spoon_5'], ['pencil/pencil_1', 'pencil/pencil_2', 'pencil/pencil_3', 'pencil/pencil_4', 'pencil/pencil_5'], ['apple/apple_1', 'apple/apple_2', 'apple/apple_3', 'apple/apple_4', 'apple/apple_5']],
                  setUp=True,
                  tI=30000):
    '''
    Function to create a dataset of frames from .aedat files

    Parameters:
                path       --> The file path.
                numClasses --> The number of classes to be divided.
                tI         --> The interval used for each frame (in milisseconds).

    return:
            totalImages --> all images obteined.
            labels      --> label corresponding to each frame.


    It is possible to join various files in a same class.

    If setUp=True, you will need to write manually the number of classes and the files for each class.
    You must write as bellow:
    Class 1 files:file1, file2, ..., fileN
    Class 2 files:file1, file2, ..., fileN
    ...              ...               ...
    Class N files:file1, file2, ..., fileN

    if setUp = False, you will need to add the file names to objClass.
    You must write as bellow:
    ---------------------------------------------------------------------------------------------------------
    |                     class 1                      class 2            ...            class N            |
    | objClass=[['file1', 'file2', 'file3'], ['file1', 'file2', 'file3'], ..., ['fileN', 'fileN', 'fileN']] |
    ---------------------------------------------------------------------------------------------------------
    '''

    if path == '':
        path = input('Write the file path: ')

    if setUp == True:
        objClass = []
        numClasses = int(input("Write the number of classes:"))
        for c in range(numClasses):
            objClass.append(input("Class " + str(c + 1) + " files:").split(", "))
    else:
        numClasses = len(objClass)

    print(numClasses)


    numSamples = []
    totalImages, labels = [], []
    finalDataset, finalLabels = [], []
    trainDataset, trainLabels = [], []
    testDataset, testLabels = [], []
    for j, fileName in enumerate(objClass): # for each class
        for v in fileName: # for each file in a class
            t, x, y, p = oA.loadAERDAT(path + str(v) + ".aedat") # load the file with that name
            i, aux = 0, 0
            images = []
            while (i + tI) < t[-1]:
                t2 = t[(i < t) & (t <= i + tI)]
                x2 = x[aux : aux + len(t2)]
                y2 = y[aux : aux + len(t2)]
                p2 = p[aux : aux + len(t2)]
                aux += len(t2)
                images.append(eventsToFrame(p2, x2, y2))
                #labels.append([j])
                i += tI
            totalImages.extend(images)
            labels.extend(np.zeros(len(images)) + j)
    totalImages, labels = np.array(totalImages), np.array(labels).astype('int')
    for i in range(numClasses):
        print("Number of samples in class " + str(i) + ": ", len(labels[labels == i]))

    resp = input("Would you like to reduce the dataset? (y/N) ")
    if resp == 'yes' or resp == 'y' or resp == 'Y':
        maxSamples = int(input("How many samples per class: "))
        trainTestSplit = input("Would you like to split the dataset? (y/N) ")
        per = float(input("Test samples percentage: "))
        for i in range(numClasses):
            if trainTestSplit == 'yes' or trainTestSplit == 'y' or trainTestSplit == 'Y':
                trainDataset.extend(totalImages[labels == i][:int(maxSamples * per)])
                trainLabels.extend(labels[labels == i][:int(maxSamples * per)])
                testDataset.extend(totalImages[labels == i][int(maxSamples * per):maxSamples])
                testLabels.extend(labels[labels == i][int(maxSamples * per):maxSamples])
            else:
                finalDataset.extend(totalImages[labels == i][:maxSamples])
                finalLabels.extend(labels[labels == i][:maxSamples])
    else:
        finalDataset, finalLabels = totalImages, labels

    if trainTestSplit == 'yes' or trainTestSplit == 'y' or trainTestSplit == 'Y':
        trainDataset, trainLabels, testDataset, testLabels = np.array(trainDataset), np.array(trainLabels), np.array(testDataset), np.array(testLabels)
        rand1, rand2 = np.arange(len(trainLabels)), np.arange(len(testLabels))
        np.random.shuffle(rand1)
        np.random.shuffle(rand2)
        trainDataset, trainLabels, testDataset, testLabels = trainDataset[rand1], trainLabels[rand1],  testDataset[rand2], testLabels[rand2]
        return (trainDataset, testDataset), (trainLabels, testLabels)

    else:
        finalDataset, finalLabels = np.array(finalDataset), np.array(finalLabels)
        randomize = np.arange(len(finalLabels))
        np.random.shuffle(randomize)
        finalDataset = finalDataset[randomize]
        finalLabels = finalLabels[randomize]
        return finalDataset, finalLabels


def openModel(model_JSON_file, model_WEIGHTS_file):
	'''
    Function to open a CNN model and its weights.

	imgC = UploadModel.OpenModel('/home/user/GitHub/Classification_DVS128/model.json',
                                 '/home/user/GitHub/Classification_DVS128/model.h5')
	'''
	# load model from JSON file
	with open(model_JSON_file, "r") as json_file:
		loadedModel_JSON = json_file.read()
		loadedModel = model_from_json(loadedModel_JSON)

	# load weights into the new model
	loadedModel.load_weights(model_WEIGHTS_file)
	loadedModel._make_predict_function()

	return loadedModel


def predictShape(img, model, flag='No'):

    #print(img.shape)
    # flag = input("Would you like to change the default object set? ")
    if flag == "Yes" or flag == "yes" or flag == "Y" or flag == "y":
        objectSet = input("New object set: ").split(", ")
    else:
        objectSet = [[0, 'Tripod'],
                    [1, 'Nothing'],
                    [2, 'Power']]

    preds = model.predict(img)
    aux = np.argmax(preds)
    selected_obj = objectSet[aux][0]

    #print(preds)
    return selected_obj, objectSet


def eventsToFrame(pol, x, y):
    matrix = np.zeros((128, 128)) # Cria uma matriz de zeros 128x128 onde serão inseridos os eventos
    pol = (np.array(pol) - 0.5) # Os eventos no array de Polaridade passam a ser -0.5 ou 0.5

    for i in range(len(x)):
            matrix[y[i], x[i]] = pol[i] # insere os eventos dentro da matriz de zeros
    matrix = (matrix)*255 + 127.5 # Normaliza a matriz para 8bits -> 0 - 255
    return matrix.T

#this function get the original image and extract the ROI
def getROI(detection,image):
    crop_img = image
    if(len(detection) != 0):
        dim = (128,128)
        crop_img = image[(detection[0]+1):detection[0]+detection[2],(detection[1]+1):detection[1]+detection[3]]
        crop_img = cv.resize(crop_img, dim, interpolation = cv.INTER_AREA)
    crop_img = crop_img.reshape(1, 128, 128, 1)
    return crop_img

def plotBoundingBox(surf, d, m):
    if len(d) > 0:
        pygame.draw.rect(surf, (255, 0, 0), [d[0][0] * m, d[0][1] * m, d[0][2] * m, d[0][3] * m], 4)
