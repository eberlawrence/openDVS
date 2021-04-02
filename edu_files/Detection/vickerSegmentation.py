import copy
import math
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
from iou import iou
from classifierTools import classifierTools
from skimage.morphology import erosion, dilation, opening, closing, white_tophat,square,convex_hull_image
from segmentationUtils import segmentationUtils
import matplotlib.patches as patches
from filterUtils import filterUtils



rects = []
standardImage = cv.imread('/home/eduardo/Documentos/DVS/Eduardo work/Mestrado/Datasource/Standard files/HV5_FOTO 1.jpg')

watershedStandardImage, standardMask,detection, standardOpening, standardSure_fg, standardSure_bg,standardMarkers = segmentationUtils.watershed(standardImage)

f, axarr = plt.subplots(1,2)

axarr[1].set_title('image [original]')
axarr[1].imshow(np.dstack([standardOpening,standardOpening,standardOpening]))
axarr[0].set_title('mask')
axarr[0].imshow(np.dstack([standardMarkers,standardMarkers,standardMarkers]))

# for j in range(len(detection)):
#     if((detection[j][7] == 'closerToCenter')):
#         #patches receive (y,x), length and width
#         rect = patches.Rectangle((detection[j][1],detection[j][0]),detection[j][3],detection[j][2],linewidth=1,edgecolor='r',facecolor='none')
#         plt.gca().add_patch(rect)
#         #the append is necessary to make the predictions not visible after the refresh of the frame
#         rects.append(rect)
#         #detectionsClassified.append(detection[j])
plt.show()