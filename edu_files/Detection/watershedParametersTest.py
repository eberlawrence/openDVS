
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
from openAEDAT import aedatUtils
import matplotlib.animation as animation
from segmentationUtils import segmentationUtils
import matplotlib.patches as patches

#path = '/home/eduardo/Documentos/DVS/Eduardo work/Mestrado/Datasource/AEDAT_files/standardized data/Mouse.aedat'
#path = '/home/eduardo/Documentos/DVS/Eduardo work/Mestrado/Datasource/AEDAT_files/random data/shorter records/two_objects.aedat'
#path = '/home/eduardo/Documentos/DVS/Eduardo work/Mestrado/Datasource/AEDAT_files/random data/shorter records/multi_objects_2.aedat'
#path = '/media/eduardo/9E1C99C51C99993B/Users/Samsung/Meus Documentos/Mestrado/HandStuff/Datasource/AEDAT_files/Celular.aedat'
path = '/home/eduardo/Documentos/DVS/Eduardo work/Mestrado/Datasource/AEDAT_files/standardized data/banana_1.aedat'
#path = '/home/eduardo/Documentos/DVS/Eduardo work/Mestrado/Datasource/AEDAT_files/standardized data/Phone.aedat'
#path = '/home/eduardo/Documentos/DVS/Eduardo work/Mestrado/Datasource/AEDAT_files/standardized data/Phone.aedat'
t, x, y, p = aedatUtils.loadaerdat(path)

tI=50000 #50 ms

totalImages = []
totalImages = aedatUtils.getFramesTimeBased(t,p,x,y,tI,False)

plotMask = True

if plotMask:
    fig, axarr = plt.subplots(1,6)
    axarr[0].set_title('neuromorphic image')
    axarr[1].set_title('opening')
    axarr[2].set_title('foreground')
    axarr[3].set_title('background')
    axarr[4].set_title('markers')
    axarr[5].set_title('tresh')
else:
    fig,axarr = plt.subplots(1)
    handle = None

rects = []
detection = []

for f in totalImages:

    watershedImage, mask, detection, opening, sure_fg, sure_bg, markers,tresh = segmentationUtils.watershed(f,'--neuromorphic')

    watershedImage = f.astype(np.uint8)
    if plotMask:
        axarr[0].imshow(np.dstack([watershedImage,watershedImage,watershedImage]))
        axarr[1].imshow(opening)
        axarr[2].imshow(sure_fg)
        axarr[3].imshow(sure_bg)
        axarr[4].imshow(markers)
        axarr[5].imshow(tresh)
    else:
        if handle is None:
            handle = plt.imshow(np.dstack([img,img,img]))
            # handle = plt.imshow(np.dstack([watershedImage,watershedImage,watershedImage]))
        else:
            handle.set_data(np.dstack([img,img,img]))
            # handle.set_data(np.dstack([watershedImage,watershedImage,watershedImage]))


    plt.pause(tI/1000000)
    plt.draw()


