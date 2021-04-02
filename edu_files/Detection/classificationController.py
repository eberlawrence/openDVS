
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
from openAEDAT import aedatUtils
from classifierTools import classifierTools
import matplotlib.animation as animation
from segmentationUtils import segmentationUtils
import matplotlib.patches as patches
import scipy as scipy
from filterUtils import filterUtils
import copy 
import os
def main():
        
    groupValue = 3 
    agroup = False
    predictFlag = False
    rectFlag = True
    filterPopCountFlag = False
    plotMask = False
    flagCloserToCenter = False

    #path = '/home/biolab-07/Documentos/Mestrado/Eduardo/HandStuff/Datasource/AEDAT_files/random data/shorter records/valocidade_1.aedat'
    #path = '/home/biolab-07/Documentos/Mestrado/Eduardo/HandStuff/Datasource/AEDAT_files/random data/shorter records/velocidade_1_e_2_experimento_3.aedat'
    #path = '/home/biolab-07/Documentos/Mestrado/Eduardo/HandStuff/Datasource/AEDAT_files/random data/shorter records/velocidade_3_experimento_2.aedat'
    #path = '/home/biolab-07/Documentos/Mestrado/Eduardo/HandStuff/Datasource/AEDAT_files/standardized data/Stiletto.aedat'
    #path = '/home/biolab-07/Documentos/Mestrado/Eduardo/HandStuff/Datasource/AEDAT_files/standardized data/Scissor.aedat'
    #path = '/home/biolab-07/Documentos/Mestrado/Eduardo/HandStuff/Datasource/AEDAT_files/standardized data/Phone.aedat'
    #path = '/home/biolab-07/Documentos/Mestrado/Eduardo/HandStuff/Datasource/AEDAT_files/standardized data/Pencil.aedat'
    #path = '/home/biolab-07/Documentos/Mestrado/Eduardo/HandStuff/Datasource/AEDAT_files/standardized data/Mouse.aedat'
    #path = '/home/biolab-07/Documentos/Mestrado/Eduardo/HandStuff/Datasource/AEDAT_files/standardized data/Mug.aedat'
    #path = '/home/biolab-07/Documentos/Mestrado/Eduardo/HandStuff/Datasource/AEDAT_files/standardized data/Box.aedat'
    #path = '/home/biolab-07/Documentos/Mestrado/Eduardo/HandStuff/Datasource/AEDAT_files/random data/shorter records/two_objects.aedat'
    #path = '/home/biolab-07/Documentos/Mestrado/Eduardo/HandStuff/Datasource/AEDAT_files/random data/shorter records/key.aedat'
    #path = '/home/biolab-07/Documentos/Mestrado/Eduardo/HandStuff/Datasource/AEDAT_files/random data/shorter records/four_objects_4.aedat'
    #path = '/home/biolab-07/Documentos/Mestrado/Eduardo/HandStuff/Datasource/AEDAT_files/random data/shorter records/four_objects_3.aedat'
    #path = '/home/biolab-07/Documentos/Mestrado/Eduardo/HandStuff/Datasource/AEDAT_files/random data/shorter records/one_object.aedat'
    #path = '/home/biolab-07/Documentos/Mestrado/Eduardo/HandStuff/Datasource/AEDAT_files/random data/shorter records/key_2.aedat'
    path = '/home/eduardo/Documentos/DVS/Eduardo work/Mestrado/Datasource/AEDAT_files/standardized data/banana_1.aedat'

    model = classifierTools.openModel('model/model.json',
                                        'model/model.h5')

    t, x, y, p = aedatUtils.loadaerdat(path)

    tI=10000 #10 ms

    totalImages = []
    totalImages = aedatUtils.getFramesTimeBased(t,p,x,y,tI,filtered=False)
    font = {'family': 'serif',
            'color':  'white',
            'weight': 'normal',
            'size': 8,
    }
    off_set_text = 3
    detections = []
    if plotMask:
        fig, axarr = plt.subplots(1,2)
        textPlot = plt.text(0,0,"")
        axarr[0].set_title('neuromorphic image')
        axarr[1].set_title('watershed mask')
    else:
        fig,axarr = plt.subplots(1)
        textPlot = plt.text(0,0,"")
        handle = None

    count = []
    rects = []
    texts = []
    framesCount = 0
    framesWithRectDrawned = []
    detectionsClassified = []
    g = 0
    for f in totalImages:
    
        detectionsClassified = []
        f = f.astype(np.uint8)
        imagem = copy.deepcopy(f)
        if filterPopCountFlag:
            imagem = filterUtils.popCountDownSample(imagem)
        else:
            imagem[imagem == 255] = 0
            imagem = filterUtils.avg(imagem)
            imagem = filterUtils.median(imagem)

        
        watershedImage, mask, detection, opening, sure_fg, sure_bg, markers = segmentationUtils.watershed(imagem,'--neuromorphic',minimumSizeBox=0.5,smallBBFilter=True,centroidDistanceFilter = True, mergeOverlapingDetectionsFilter = True)
        watershedImage = watershedImage.astype(np.uint8)


        if plotMask:
            axarr[1].imshow(np.dstack([f,f,f]))
            axarr[0].imshow(mask)
        else:
            if handle is None:
                #handle = plt.imshow(np.dstack([imagem,imagem,imagem]))                
                handle = plt.imshow(np.dstack([f,f,f]))                
            else:
                handle.set_data(np.dstack([f,f,f]))
                #handle.set_data(np.dstack([imagem,imagem,imagem]))

        if agroup:
            if detection:
                framesCount = framesCount + 1
                for s in range(len(detection)):
                    detections.append(detection[s])
            if framesCount >= groupValue and detections:
                cleanFigure(rects,texts)
                finalDetection = segmentationUtils.getPointsFromCoordinates(detections)
                finalDetection = segmentationUtils.filterDetections(finalDetection)
                finalDetection = segmentationUtils.getCoordinatesFromPoints(finalDetection)
                detection = finalDetection[:]
                #draw the bounding boxes and write the classification
                for j in range(len(detection)):
                    if predictFlag:
                        if flagCloserToCenter and (detection[j][7] == 'closerToCenter'):
                            imageRoi = getROI(detection[j],f)
                            predict = classify(imageRoi,model)
                            text = plt.gca().text(detection[j][1], detection[j][0]-off_set_text, predict, fontdict = font,bbox=dict(facecolor='red', alpha=1))
                            texts.append(text)
                        elif(not flagCloserToCenter):
                            imageRoi = getROI(detection[j],f)
                            predict = classify(imageRoi,model)
                            text = plt.gca().text(detection[j][1], detection[j][0]-off_set_text, predict, fontdict = font,bbox=dict(facecolor='red', alpha=1))
                            texts.append(text)
                    if rectFlag:
                        if flagCloserToCenter and (detection[j][7] == 'closerToCenter'):
                            #patches receive (y,x), length and width
                            rect = patches.Rectangle((detection[j][1],detection[j][0]),detection[j][3],detection[j][2],linewidth=1,edgecolor='r',facecolor='none')
                            plt.gca().add_patch(rect)
                            #the append is necessary to make the predictions not visible after the refresh of the frame
                            rects.append(rect)
                        elif(not flagCloserToCenter):
                            #patches receive (y,x), length and width
                            rect = patches.Rectangle((detection[j][1],detection[j][0]),detection[j][3],detection[j][2],linewidth=1,edgecolor='r',facecolor='none')
                            plt.gca().add_patch(rect)
                            #the append is necessary to make the predictions not visible after the refresh of the frame
                            rects.append(rect)
                framesCount = 0
                detections = []
        else:
            cleanFigure(rects,texts)
            for j in range(len(detection)):
                if predictFlag:
                    if flagCloserToCenter and (detection[j][7] == 'closerToCenter'):
                        imageRoi = getROI(detection[j],f)
                        predict = classify(imageRoi,model)
                        text = plt.gca().text(detection[j][1], detection[j][0]-off_set_text, predict, fontdict = font,bbox=dict(facecolor='red', alpha=1))
                        texts.append(text)
                    elif(not flagCloserToCenter):
                        imageRoi = getROI(detection[j],f)
                        predict = classify(imageRoi,model)
                        text = plt.gca().text(detection[j][1], detection[j][0]-off_set_text, predict, fontdict = font,bbox=dict(facecolor='red', alpha=1))
                        texts.append(text)
                if rectFlag:
                    if flagCloserToCenter and (detection[j][7] == 'closerToCenter'):
                        #patches receive (y,x), length and width
                        rect = patches.Rectangle((detection[j][1],detection[j][0]),detection[j][3],detection[j][2],linewidth=1,edgecolor='r',facecolor='none')
                        plt.gca().add_patch(rect)
                        #the append is necessary to make the predictions not visible after the refresh of the frame
                        rects.append(rect)
                        #detectionsClassified.append(detection[j])
                    elif(not flagCloserToCenter):
                        #patches receive (y,x), length and width
                        rect = patches.Rectangle((detection[j][1],detection[j][0]),detection[j][3],detection[j][2],linewidth=1,edgecolor='r',facecolor='none')
                        plt.gca().add_patch(rect)
                        #the append is necessary to make the predictions not visible after the refresh of the frame
                        rects.append(rect)
                        #detectionsClassified.append(detection[j])

    
        plt.pause(tI/1000000)
        plt.draw()
    
    
        


def cleanFigure(rects,texts):
    for s in range(len(rects)):
        rects[s].set_visible(False)

    for s in range(len(texts)):
        texts[s].set_visible(False)

#this function get the original image and extract the ROI
def getROI(detection,image):
    dim = (128,128)
    crop_img = image[(detection[0]+1):detection[0]+detection[2],(detection[1]+1):detection[1]+detection[3]]
    crop_img = cv.resize(crop_img, dim, interpolation = cv.INTER_AREA)
    crop_img = crop_img.reshape(1, 128, 128, 1)
    return crop_img

def classify(image,model):
    resp, objectSet = classifierTools.predictObject(image, model)
    predict = objectSet[resp][1]
    return predict

def filmaker(imageVector, name="video.avi"):
    #Cria um vídeo no formato .avi juntando todos os frames.
    video_name = name
    images = imageVector
    height, width, layers = (128,128,3)
    fourcc = cv.VideoWriter_fourcc(*'mpeg') 
    video = cv.VideoWriter(video_name, fourcc, 10, (width,height))
    for image in images:
       video.write(image)
    cv.destroyAllWindows()
    video.release()

if __name__ == "__main__":
	main()