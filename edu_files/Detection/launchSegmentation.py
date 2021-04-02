import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import copy 
import cv2 as cv
from openAEDAT import aedatUtils
from segmentationUtils import segmentationUtils


def main():
        
    #caso você queira que os retangulos sejam desenhados na tela:
    rectFlag = True


    #Caminho para o arquivo .aedat
    #path = '/home/eduardo/Documentos/DVS/Eduardo work/Mestrado/Datasource/AEDAT_files/standardized data/banana_1.aedat'
    path = '/home/eduardo/Documentos/DVS/Eduardo work/Mestrado/Datasource/AEDAT_files/standardized data/knife_1.aedat'
    #path = '/home/eduardo/Documentos/DVS/Eduardo work/Mestrado/Datasource/AEDAT_files/standardized data/Phone.aedat'
    #path = "/home/eduardo/Documentos/DVS/Eduardo work/Mestrado/Datasource/AEDAT_files/random data/longer records/Nada2.aedat"
    #carregando o arquivo aedat
    t, x, y, p = aedatUtils.loadaerdat(path)
    
    #determinando o intervalo de tempo para agrupamento dos eventos
    tI=50000 #50 ms

    #carregando todos os eventos agrupados em frames
    totalImages = []
    totalImages = aedatUtils.getFramesTimeBased(t,p,x,y,tI)

    #variável que armazena as bounding boxes
    detections = []

    fig,axarr = plt.subplots(1)
    textPlot = plt.text(0,0,"")
    handle = None
    rects = []

    teste = np.zeros_like(totalImages[0])
    imageVector = []
    for f in totalImages:
    
        f = f.astype(np.uint8)
        imagem = copy.deepcopy(f)
        
        watershedImage, mask, detection, opening, sure_fg, sure_bg, markers,_ = segmentationUtils.watershed(imagem,'--neuromorphic',minimumSizeBox=0.5,smallBBFilter=True,centroidDistanceFilter = True, mergeOverlapingDetectionsFilter = True,flagCloserToCenter=True)
        #detection contém todas as bounding box
        #cada bounding box tem o formato:
            # x -- detection[0]
            # y -- detection[1]
            # width -- detection[2]
            # length -- detection[3]
       
        cleanFigure(rects)
        if rectFlag: 
            for j in range(len(detection)):  
                #patches receive (y,x), length and width
                rect = patches.Rectangle((detection[j][1],detection[j][0]),detection[j][3],detection[j][2],linewidth=1,edgecolor='r',facecolor='none')
                plt.gca().add_patch(rect)
                #the append is necessary to make the predictions not visible after the refresh of the frame
                rects.append(rect)

        teste = segmentationUtils.getROI(detection,f)
        if handle is None:      
            handle = plt.imshow(np.dstack([f,f,f]))                
        else:
            handle.set_data(np.dstack([f,f,f]))
        imageVector.append(watershedImage)
        plt.pause(tI/1000000)
        plt.draw()
    #filmaker(imageVector,name="knife_modificado_50_2_07-08.avi")
    
        
def filmaker(imageVector, name="video.avi"):
    #Cria um vídeo no formato .avi juntando todos os frames.
    video_name = name
    images = imageVector
    height, width, layers = (128,128,3)
    fourcc = cv.VideoWriter_fourcc(*'DIVX') 
    video = cv.VideoWriter(video_name, fourcc, 10, (width,height))
    for image in images:
       video.write(np.dstack([image,image,image]))
    cv.destroyAllWindows()
    video.release()

def cleanFigure(rects = [],texts = []):
    for s in range(len(rects)):
        rects[s].set_visible(False)

    for s in range(len(texts)):
        texts[s].set_visible(False)



if __name__ == "__main__":
	main()