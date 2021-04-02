import copy
import math
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
from iou import iou
from classifierTools import classifierTools
from skimage.morphology import erosion, dilation, opening, closing, white_tophat,square,convex_hull_image
from filterUtils import filterUtils

class segmentationUtils:

    '''
    parameters:
        imagem - desired image
        minimumSizeBox - threshold for the size of the bounding box (in percentage)
        options - optional parameter who is a string with the desired options.
            avaiable options:
                '--neuromorphic' - is the declaration of neuromorphic image or else is a RGB image
    '''
    def watershed(imagem,options=None,minimumSizeBox = 2,smallBBFilter = True,centroidDistanceFilter=True,mergeOverlapingDetectionsFilter=True,flagCloserToCenter = False):

        opt = []
        flagNeuromorphic = False
        occurrences = 0
        global imageDimensions
        imageDimensions = imagem.shape
        if options != None:
            options = "".join(options.split())
            opt = options.split('--')

        if opt.__contains__('neuromorphic'):
            flagNeuromorphic = True
            img = imagem.astype(np.uint8)
            #img = filterUtils.median(img)
            #img = cv.medianBlur(img,3)
            img[img == 255] = 0
            #img = filterUtils.avg(img)
            occurrences = np.count_nonzero(img == 0)
            if len(img.shape) == 3:
                img = cv.cvtColor(img,cv.COLOR_RGB2GRAY)
        else:
            img = cv.cvtColor(imagem,cv.COLOR_RGB2GRAY)

        ret, thresh = cv.threshold(img,0,255,cv.THRESH_BINARY_INV+cv.THRESH_OTSU)
        # noise removal
        kernel = np.ones((2,2),np.uint8)
        ite_1 = 1
        ite_2 = 1
        if flagNeuromorphic and occurrences < 500:
            kernel = cv.getStructuringElement(shape=cv.MORPH_RECT, ksize=(3,3))
        elif flagNeuromorphic and occurrences >= 500:
            kernel = np.ones((1,1),np.uint8)
            ite_1 = 3
            ite_2 = 5
        
        opening = cv.morphologyEx(thresh,cv.MORPH_DILATE,kernel, iterations = ite_1)
        # sure background area
        sure_bg = cv.dilate(opening,kernel,iterations=ite_2)
        # Finding sure foreground area
        dist_transform = cv.distanceTransform(opening,cv.DIST_L2,0)
        ret, sure_fg = cv.threshold(dist_transform,0.05*dist_transform.max(),255,0)
        # Finding unknown region
        sure_fg = np.uint8(sure_fg)
        unknown = cv.subtract(sure_bg,sure_fg)
        # Marker labelling
        ret, markers = cv.connectedComponents(sure_fg)
        # Add one to all labels so that sure background is not 0, but 1
        markers = markers+1
        # Now, mark the region of unknown with zero
        markers[unknown==255] = 0
        img2 = cv.cvtColor(img, cv.COLOR_GRAY2RGB)
        markers = cv.watershed(img2,markers)
        img2[markers == -1] = [255,0,0]

        detections = segmentationUtils.makeRectDetection(markers,minimumSizeBox,smallBBFilter,centroidDistanceFilter,mergeOverlapingDetectionsFilter)
        detections = segmentationUtils.getOnlyCloseToCenter(flagCloserToCenter,detections)
        imagem = segmentationUtils.drawRect(imagem,detections)
        detections = segmentationUtils.getCoordinatesFromPoints(detections)
        return imagem, markers, detections, opening, sure_fg, sure_bg,markers

    def getOnlyCloseToCenter(flagCloserToCenter, detections):
        retorno = []
        if(flagCloserToCenter):
            for j in range(len(detections)):
                if (detections[j][7] == 'closerToCenter'):
                    retorno.append(detections[j])
        else:
            retorno = copy.deepcopy(detections)
        return retorno

    '''
    this method was make in order to receive a mask from multiple detection using the watershed method
    and make a rectangular bounding box ao redor of the detections.
    '''
    def makeRectDetection(mask,minimumSizeBox=2,smallBBFilter=True,centroidDistanceFilter=True,mergeOverlapingDetectionsFilter = True):
        #make sure that the edges of the image is not being marked
        mask[0,:] = 1
        mask[:,0] = 1
        mask[mask.shape[0]-1,:] = 1
        mask[:, mask.shape[1]-1] = 1
        unique = np.unique(mask)
        unique = unique[unique != -1]
        unique = unique[unique != 1]
        objects = []
        for i in range(len(unique)):
            positions = np.where(mask == unique[i])
            x = min(positions[0])
            y = min(positions[1])
            lastX = max(positions[0])
            lastY = max(positions[1])
            width = lastX - x
            height = lastY - y
            #if the area of the detection is bigger then 20% of the image size (128 * 128 = 16384)
            #so if the bb area is larger then 0.2*16384 the bb need to be keep. Otherwise I ignore then
            if ((smallBBFilter) and (width * height)>((minimumSizeBox/100.0)*(mask.shape[0]*mask.shape[1]))):
                objects.append([x, y, width, height])
            elif (not smallBBFilter):
                objects.append([x, y, width, height])

        # print(len(objects))

        objects = segmentationUtils.getCentroid(objects)
        objects = segmentationUtils.getPointsFromCoordinates(objects)
        objects = segmentationUtils.filterDetections(objects,centroidDistanceFilter,mergeOverlapingDetectionsFilter)
        objects = segmentationUtils.closerToCenter(objects)
        return objects

    '''
        INPUT -> coordinates =
                     [x, y, width, height, centroidx, centroidy, distanceToCenter]
        OUTPUT -> coordinates =
                     [x, y, width, height, centroidx, centroidy, distanceToCenter, infoAboutCloserToCenter]
    '''
    def closerToCenter(coordinates):
        if(len(coordinates) > 0):
            minOfEachColumn = np.amin(coordinates,axis=0)
            minOfEachColumnCoord = np.where(coordinates == np.amin(coordinates,axis=0))
            # print('coordenadas dos valores mínimos de cada coluna do array de coordenadas: ',minOfEachColumn)
            # print('array de coordenadas: ',coordinates)
            limitOfDistance = ((math.sqrt(((imageDimensions[0]-imageDimensions[0]/2)**2)+((imageDimensions[1]-imageDimensions[1]/2)**2)))*0.2)
        for i in range(len(coordinates)):
            if coordinates[i][6] == minOfEachColumn[6]:
                coordinates[i].append('closerToCenter')
            else:
                coordinates[i].append('notCloserToCenter')

        return coordinates





    '''
        INPUT ->
            coordinates =
                 [x, y, width, height]
        OUTPUT ->
            coordinates =
                [x, y, width, height, centroidx, centroidy, distanceToCenter]
    '''
    def getCentroid(coordinates):
        for i in range(len(coordinates)):
            distanceToCenter = 0
            Cxa = coordinates[i][0] + coordinates[i][2]/2
            Cya = coordinates[i][1] + coordinates[i][3]/2
            coordinates[i].append(Cxa)
            coordinates[i].append(Cya)
            if(imageDimensions and imageDimensions[0] != 0 and imageDimensions[1] != 0):
                distanceToCenter = math.sqrt(((coordinates[i][4]-imageDimensions[0]/2)**2)+((coordinates[i][5]-imageDimensions[1]/2)**2))
            coordinates[i].append(distanceToCenter)
        return coordinates

    def filterDetections(detections,centroidDistanceFilter=True,mergeOverlapingDetectionsFilter = True):
        flag = True
        retorno = detections[:]
        while(flag):
            flag, pos = segmentationUtils.checkIntersec(retorno,centroidDistanceFilter,mergeOverlapingDetectionsFilter)
            retorno = segmentationUtils.mergeDetections(retorno,pos)
        return retorno

    def checkIntersec(coordinates,centroidDistanceFilter=True,mergeOverlapingDetectionsFilter = True):
        count = len(coordinates)
        register = 0
        maxDistance = math.sqrt(imageDimensions[0]**2 + imageDimensions[1]**2)
        if (centroidDistanceFilter or mergeOverlapingDetectionsFilter):
            for i in range(len(coordinates)):
                for j in range(len(coordinates)):
                    if j > i:
                        area = iou.bb_intersection_over_union(coordinates[i],coordinates[j])
                        distance = segmentationUtils.getDistance(coordinates[i],coordinates[j])
                        if (area > 0.0 and area != 1.0 and mergeOverlapingDetectionsFilter) or (centroidDistanceFilter and distance < 0.35*maxDistance):
                            return True, [i,j]

        return False, None

    def getDistance(boxA, boxB):
        distance = math.sqrt(((boxA[4]-boxB[4])**2)+((boxA[5]-boxB[5])**2))
        # print('distance: '+ str(distance))
        return distance

    def drawRect(img, detections,lineWidth=None):
        bbColor = 8
        detections = segmentationUtils.getCoordinatesFromPoints(detections)
        if lineWidth == None:
            lineWidth = round(0.01*img.shape[0])
        if len(img.shape) == 3:
            bbColor = [255,0,0]
        for i in range(len(detections)):
            img[detections[i][0],detections[i][1]] = bbColor
            img[detections[i][0]:detections[i][0]+lineWidth,detections[i][1]:(detections[i][1]+detections[i][3])] = bbColor
            img[detections[i][0]:(detections[i][0]+detections[i][2]),detections[i][1]:detections[i][1]+lineWidth] = bbColor
            img[(detections[i][0]+detections[i][2]):(detections[i][0]+detections[i][2])+lineWidth,detections[i][1]:(detections[i][1]+detections[i][3])] = bbColor
            img[detections[i][0]:(detections[i][0]+detections[i][2]),(detections[i][1]+detections[i][3]):(detections[i][1]+detections[i][3])+lineWidth] = bbColor
        return img

    '''
        If one or more rectangular detections has a IOU the bounding boxes are merged and
    became just one
    '''
    def mergeDetections(detections,pos):
        retorno = detections
        if (pos != None):
            coordinates = copy.deepcopy(detections)
            retorno = []
            X1 = max(coordinates[pos[0]][0],coordinates[pos[0]][2],coordinates[pos[1]][0],coordinates[pos[1]][2])
            X2 = min(coordinates[pos[0]][0],coordinates[pos[0]][2],coordinates[pos[1]][0],coordinates[pos[1]][2])
            Y1 = max(coordinates[pos[0]][1],coordinates[pos[0]][3],coordinates[pos[1]][1],coordinates[pos[1]][3])
            Y2 = min(coordinates[pos[0]][1],coordinates[pos[0]][3],coordinates[pos[1]][1],coordinates[pos[1]][3])
            width = X1 - X2
            height = Y1 - Y2

            coordWithCentroid = segmentationUtils.getCentroid([[X2, Y2, width, height]])

            coordinates.remove(detections[pos[0]])
            coordinates.remove(detections[pos[1]])

            retorno = coordinates
            retorno.append([X2, Y2, X1, Y1, coordWithCentroid[0][4],coordWithCentroid[0][5],coordWithCentroid[0][6]])
        return retorno

    def getPointsFromCoordinates(detections):
        objects = []
        for i in range(len(detections)):
            x1 = detections[i][0]
            y1 = detections[i][1]
            x2 = detections[i][0] + detections[i][2]
            y2 = detections[i][1] + detections[i][3]
            objects.append([x1, y1, x2, y2, detections[i][4], detections[i][5],detections[i][6]])
        return objects
    def getCoordinatesFromPoints(detections):
        objects = []
        for i in range(len(detections)):
            if detections[i][2] - detections[i][0] > 1 and detections[i][3] - detections[i][1] > 1:
                x1 = detections[i][0]
                y1 = detections[i][1]
                width = detections[i][2] - x1
                lenght = detections[i][3] - y1
                objects.append([x1, y1, width, lenght, detections[i][4], detections[i][5],detections[i][6],detections[i][7]])
        return objects

    #this function get the original image and extract the ROI
    def getROI(d, image):
        _ = 0
        if len(d) > 0:
            dim = (128, 128)
            biggerEdge = max(d[0][2],d[0][3])
            smallerEdge = min(d[0][2],d[0][3])
            delta = int((biggerEdge - smallerEdge)/2)
            if(d[0].index(smallerEdge) == 2):
                d[0][0] = 0 if (d[0][0]-delta) < 0 else d[0][0]-delta
            else:
                d[0][1] = 0 if (d[0][1]-delta) < 0 else d[0][1]-delta
            d[0][d[0].index(smallerEdge)] = biggerEdge
            crop_img = image[(d[0][0] + 1) : d[0][0] + d[0][2], (d[0][1] + 1) : d[0][1] + d[0][3]]
            interp_img = cv.resize(crop_img, dim, interpolation = cv.INTER_NEAREST)
            # crop_img = crop_img.reshape(1, 128, 128, 1)
            return crop_img, interp_img
        else:
            return image, image

    '''
    this method run a demo for watershed segmentation technique.
    this will plot 4 images:
        - 1 standard image (original)
        - 1 standard image (watershed segmentation)
        - 1 neuromorphic image (original | probabily 100 ms event agroupation)
        - 1 neuromorphic image (watershed segmentation + filter of avg and median)
    '''
    def watershed_demo():
        font = {'family': 'serif',
                'color':  'red',
                'weight': 'normal',
                'size': 8,
        }
        off_set_text = 3

        dim = (128,128)

        neuromorphicImage = cv.imread('/home/eduardo/Documentos/DVS/Eduardo work/Mestrado/Detection/assets/testes/Mouse_22.png')
        nImage = copy.deepcopy(neuromorphicImage)
        standardImage = cv.imread('/home/eduardo/Documentos/DVS/Eduardo work/Mestrado/Datasource/Standard files/HV5_FOTO 1.jpg')

        watershedStandardImage, standardMask,standardDetection, standardOpening, standardSure_fg, standardSure_bg,standardMarkers = segmentationUtils.watershed(standardImage)

        neuromorphicImage = filterUtils.avg(neuromorphicImage)
        neuromorphicImage = filterUtils.median(neuromorphicImage)

        watershedNeuromorphicImage, neuromorphicMask,neuromorphicDetection, neurOpening, neuroSure_fg, neuroSure_bg,neuroMarkers = segmentationUtils.watershed(neuromorphicImage,'--neuromorphic')


        f, axarr = plt.subplots(2,3)
        axarr[0,0].set_title('neuromorphic image [original]')
        axarr[0,0].imshow(nImage)

        axarr[0,1].set_title('neuromorphic - mask')
        axarr[0,1].imshow(neuromorphicMask)

        crop_neuromorphic = nImage[neuromorphicDetection[0][0]+1:neuromorphicDetection[0][0]+neuromorphicDetection[0][2] , neuromorphicDetection[0][1]+1:neuromorphicDetection[0][1]+neuromorphicDetection[0][3]]

        axarr[0,2].set_title('croped bounding box')
        axarr[0,2].imshow(crop_neuromorphic)


        axarr[1,0].set_title('standard image [original]')
        axarr[1,0].imshow(standardImage)

        axarr[1,1].set_title('standard - mask')
        axarr[1,1].imshow(standardMask)

        crop_standard = standardImage[standardDetection[0][0]+(round(0.01*standardImage.shape[0])):standardDetection[0][0]+standardDetection[0][2] , standardDetection[0][1]+(round(0.01*standardImage.shape[0])):standardDetection[0][1]+standardDetection[0][3]]

        axarr[1,2].set_title('croped bounding box')
        axarr[1,2].imshow(crop_standard)


        model = classifierTools.openModel('model/model.json',
							              'model/model.h5')


        crop_img = cv.resize(crop_neuromorphic, dim, interpolation = cv.INTER_AREA)
        crop_img = cv.cvtColor(crop_img,cv.COLOR_RGB2GRAY)
        crop_img = crop_img.reshape(1, 128, 128, 1)
        resp, objectSet = classifierTools.predictObject(crop_img, model)
        predict = objectSet[resp][1]
        axarr[0,0].text(neuromorphicDetection[0][1], neuromorphicDetection[0][0]-off_set_text, predict, fontdict = font)

        plt.show()

if __name__ == "__main__":
	segmentationUtils.watershed_demo()
