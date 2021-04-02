
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
from openAEDAT import aedatUtils
import matplotlib.animation as animation
from segmentationUtils import segmentationUtils
from filterUtils import filterUtils
import matplotlib.patches as patches
import copy 

def main():
    nfVectorSave = [] 
    # path = '/home/eduardo/Documentos/DVS/Eduardo work/Mestrado/Datasource/Standard files/HV5_FOTO1.jpg'
    # path = '/home/eduardo/Documentos/DVS/Eduardo work/Mestrado/Datasource/Standard files/multi_objects.mp4'
    #path = '/home/eduardo/Documentos/DVS/Eduardo work/Mestrado/Datasource/Standard files/four_objects.mp4'
    
    # path = '/home/eduardo/Documentos/DVS/Eduardo work/CBEB - 2020/codigo/video_fn_2.mp4'
    path = '/home/eduardo/Documentos/DVS/Eduardo work/CBEB - 2020/codigo/walking_fn.mp4'
    # path = '/home/eduardo/Documentos/DVS/Eduardo work/CBEB - 2020/codigo/assets/video_piloto_1.mp4'


    video = cv.VideoCapture(path)

    plotMask = False

    if plotMask:
        fig, axarr = plt.subplots(1,2)
        axarr[0].set_title('standard image')
        axarr[1].set_title('watershed mask')
    else:
        fig,axarr = plt.subplots(1)
        handle = None

    off_set_text = 3
    rects = []
    texts = []
    while(video.isOpened()):
        ret, frame = video.read()
        if(ret == False):
            break
        if frame.shape != 0:
            #frame = cv.rotate(frame, cv.ROTATE_90_CLOCKWISE)
            imagem = copy.deepcopy(frame)
            # imagem = filterUtils.avg(imagem)
            # imagem = filterUtils.median(imagem)
            watershedImage, mask, detection,opening, sure_fg, sure_bg,markers = segmentationUtils.watershed(imagem,options="--neuromorphic",minimumSizeBox=0.0,smallBBFilter=True,centroidDistanceFilter = True, mergeOverlapingDetectionsFilter = True)

            # if plotMask:
            #     axarr[0].imshow(frame)
            #     axarr[1].imshow(mask)
            # else:
            #     if handle is None:
            #         handle = plt.imshow(frame)
            #     else:
            #         handle.set_data(frame)
            # cleanFigure(rects,texts)
            # for j in range(len(detection)):
            #     rect = patches.Rectangle((detection[j][1],detection[j][0]),detection[j][3],detection[j][2],linewidth=1,edgecolor='r',facecolor='none')
            #     plt.gca().add_patch(rect)
            #     #the append is necessary to make the predictions not visible after the refresh of the frame
            #     rects.append(rect)
            # plt.pause(0.01)
            # plt.draw()
            print(len(detection))
    
        
        nfVectorSave.append(watershedImage)

    video.release()
    cv.destroyAllWindows()
    filmaker(nfVectorSave)


def cleanFigure(rects,texts):
    for s in range(len(rects)):
        rects[s].set_visible(False)

    for s in range(len(texts)):
        texts[s].set_visible(False)

def filmaker(imageVector, name="walking_fn_tr.mp4"):
    #Cria um vídeo no formato .avi juntando todos os frames.
    video_name = name
    images = imageVector
    height, width, layers = (246,320,3)
    fourcc = cv.VideoWriter_fourcc(*'mpeg') 
    video = cv.VideoWriter(video_name, fourcc, 30, (width,height))
    for image in images:
       video.write(image)
    cv.destroyAllWindows()
    video.release()

if __name__ == "__main__":
	main()