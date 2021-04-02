
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
path = '/home/biolab-07/Documentos/Mestrado/Eduardo/HandStuff/Datasource/AEDAT_files/standardized data/Pencil.aedat'

t, x, y, p = aedatUtils.loadaerdat(path)

tI=50000 #50 ms

totalImages = []
totalImages = aedatUtils.getFramesTimeBased(t,p,x,y,tI,True)

plotMask = False

if plotMask:
    fig, axarr = plt.subplots(1,2)
    axarr[0].set_title('neuromorphic image')
    axarr[1].set_title('watershed mask')
else:
    fig,axarr = plt.subplots(1)
    handle = None

rects = []
detection = []

for f in totalImages:
    
    # for s in range(len(rects)):
    #     rects[s].set_visible(False)

    # f = filterUtils.avg(f)
    # f = filterUtils.median(f)
    
    #watershedImage, mask, detection = segmentationUtils.watershed(f,'--neuromorphic')
    # watershedImage = watershedImage.astype(np.uint8)
    #watershedImage = f
    watershedImage = f.astype(np.uint8)
    if plotMask:
        axarr[0].imshow(np.dstack([watershedImage,watershedImage,watershedImage]))
        axarr[1].imshow(mask)
    else:
        if handle is None:
            handle = plt.imshow(np.dstack([watershedImage,watershedImage,watershedImage]))
        else:
            handle.set_data(np.dstack([watershedImage,watershedImage,watershedImage]))


    for j in range(len(detection)):
        # Create a Rectangle patch
        rect = patches.Rectangle((detection[j][1],detection[j][0]),detection[j][3],detection[j][2],linewidth=1,edgecolor='r',facecolor='none')
        rects.append(rect)
        # Add the patch to the Axes
        plt.gca().add_patch(rect)


    plt.pause(tI/1000000)
    plt.draw()


