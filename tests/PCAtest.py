from __future__ import print_function
from __future__ import division
import cv2 as cv
import numpy as np
import argparse
import matplotlib
from math import atan2, cos, sin, sqrt, pi
import matplotlib.pyplot as plt


def drawAxis(img, p_, q_, colour, scale):
    p = list(p_)
    q = list(q_)
    angle = atan2(p[1] - q[1], p[0] - q[0]) # angle in radians
    hypotenuse = sqrt((p[1] - q[1]) * (p[1] - q[1]) + (p[0] - q[0]) * (p[0] - q[0]))
    # Here we lengthen the arrow by a factor of scale
    q[0] = p[0] - scale * hypotenuse * cos(angle)
    q[1] = p[1] - scale * hypotenuse * sin(angle)
    cv.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), colour, 10, cv.LINE_AA)
    # create the arrow hooks
    p[0] = q[0] + 9 * cos(angle + pi / 4)
    p[1] = q[1] + 9 * sin(angle + pi / 4)
    cv.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), colour, 10, cv.LINE_AA)
    p[0] = q[0] + 9 * cos(angle - pi / 4)
    p[1] = q[1] + 9 * sin(angle - pi / 4)
    cv.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), colour, 10, cv.LINE_AA)


def getOrientation(pts, img):
    sz = len(pts)
    data_pts = np.empty((sz, 2), dtype=np.float64)
    for i in range(data_pts.shape[0]):
        data_pts[i,0] = pts[i,0,0]
        data_pts[i,1] = pts[i,0,1]
    # Perform PCA analysis
    mean = np.empty((0))
    mean, eigenvectors, eigenvalues = cv.PCACompute2(data_pts, mean)
    # Store the center of the object
    cntr = (int(mean[0,0]), int(mean[0,1]))
    cv.circle(img, cntr, 1, (255, 0, 255), 10)
    p1 = (cntr[0] + 0.02 * eigenvectors[0,0] * eigenvalues[0,0], cntr[1] + 0.02 * eigenvectors[0,1] * eigenvalues[0,0])
    p2 = (cntr[0] - 0.02 * eigenvectors[1,0] * eigenvalues[1,0], cntr[1] - 0.02 * eigenvectors[1,1] * eigenvalues[1,0])
    drawAxis(img, cntr, p1, (22, 183, 224), .44)
    drawAxis(img, cntr, p2, (40, 166, 18), 1.1)
    angle = atan2(eigenvectors[0,1], eigenvectors[0,0]) # orientation in radians
    return angle


# x->37-72 y->26-97
plt.imshow(np.dstack([np.zeros(2286144).reshape(1512,1512),np.zeros(2286144).reshape(1512,1512),np.zeros(2286144).reshape(1512,1512)]))

original = img[0][73].astype('uint8')

original[original == 0] = 255
original[original == 127] = 0

original = np.dstack([original,original,original])
original = cv.resize(original, (1512,1512), interpolation = cv.INTER_NEAREST)
matplotlib.image.imsave("testeee.jpeg", original)



src = cv.imread("testeee.jpeg")
# matplotlib.image.imsave("clock3_before.jpeg", src)

gray = cv.medianBlur(src, 17)

gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)

_, bw = cv.threshold(gray, 50, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)
# matplotlib.image.imsave("clock3_middle.jpeg", np.dstack([bw, bw, bw]))

lista = []
contours, _ = cv.findContours(bw, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)
for i, c in enumerate(contours):
    if  i != 156:
        area = cv.contourArea(c)
        if area < 10000 or 150000 < area:
            continue
        lista.append(i)
        # cv.drawContours(original, contours, i, (255, 0, 0), 3)
        getOrientation(c, original)


# original = cv.resize(original, (1512,1512), interpolation = cv.INTER_NEAREST)
plt.show()































matplotlib.image.imsave("clock3_after.jpeg", src)










src = img[0][113].astype('uint8')
src = cv.resize(src, (1512,1512), interpolation = cv.INTER_AREA)
matplotlib.image.imsave("dvs_before.jpeg", np.dstack([src,src,src]))





src = img[0][0].astype('uint8')

src[src == 255] = 0
src[src == 127] = 255


matplotlib.image.imsave("testeee.jpeg", np.dstack([src,src,src]))

src = cv.imread("testeee.jpeg")

# gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
src = cv.medianBlur(src, 3)
src = cv.resize(src, (1512,1512), interpolation = cv.INTER_AREA)

# Convert image to binary
# Find all the contours in the thresholded image
_, bw = cv.threshold(src, 50, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)

# lista = []
contours, _ = cv.findContours(bw, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)
for i, c in enumerate(contours):
    # if i != 393 and i != 435:
    # Calculate the area of each contour
    area = cv.contourArea(c)
    # Ignore contours that are too small or too large
    if area < 10000 or 100000 < area:
        continue
    # lista.append(i)
    # Draw each contour only for visualisation purposes
    cv.drawContours(src, contours, i, (255, 0, 0), 3)
    # Find the orientation of each shape
    getOrientation(c, src)



plt.imshow(src)
plt.show()



plt.imshow(gray)
plt.show()
