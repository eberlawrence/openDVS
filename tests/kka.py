from __future__ import print_function
from __future__ import division
import cv2 as cv
import numpy as np
import argparse
from math import atan2, cos, sin, sqrt, pi
import openAEDAT as oa
import matplotlib.pyplot as plt

def drawAxis(img, p_, q_, colour, scale):
    p = list(p_)
    q = list(q_)
    angle = atan2(p[1] - q[1], p[0] - q[0]) # angle in radians
    hypotenuse = sqrt((p[1] - q[1]) * (p[1] - q[1]) + (p[0] - q[0]) * (p[0] - q[0]))
    # Here we lengthen the arrow by a factor of scale
    q[0] = p[0] - scale * hypotenuse * cos(angle)
    q[1] = p[1] - scale * hypotenuse * sin(angle)
    cv.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), colour, 1, cv.LINE_AA)
    # create the arrow hooks
    p[0] = q[0] + 9 * cos(angle + pi / 4)
    p[1] = q[1] + 9 * sin(angle + pi / 4)
    cv.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), colour, 1, cv.LINE_AA)
    p[0] = q[0] + 9 * cos(angle - pi / 4)
    p[1] = q[1] + 9 * sin(angle - pi / 4)
    cv.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), colour, 1, cv.LINE_AA)

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
    cv.circle(img, cntr, 3, (255, 0, 255), 2)
    p1 = (cntr[0] + 0.02 * eigenvectors[0,0] * eigenvalues[0,0], cntr[1] + 0.02 * eigenvectors[0,1] * eigenvalues[0,0])
    p2 = (cntr[0] - 0.02 * eigenvectors[1,0] * eigenvalues[1,0], cntr[1] - 0.02 * eigenvectors[1,1] * eigenvalues[1,0])
    drawAxis(img, cntr, p1, (0, 255, 0), 1)
    drawAxis(img, cntr, p2, (255, 255, 0), 5)
    angle = atan2(eigenvectors[0,1], eigenvectors[0,0]) # orientation in radians
    return angle

def getOrientation(pts, img):
    data_pts = pts.reshape(len(pts),2).astype('float64')
    # Perform PCA analysis
    mean, eigenvectors, eigenvalues = cv.PCACompute2(data_pts, np.array([]))
    # Store the center of the object
    cntr = (int(mean[0,0]), int(mean[0,1]))
    cv.circle(img, cntr, 3, (255, 0, 255), 2)
    p1 = (cntr[0] + 0.02 * eigenvectors[0,0] * eigenvalues[0,0], cntr[1] + 0.02 * eigenvectors[0,1] * eigenvalues[0,0])
    p2 = (cntr[0] - 0.02 * eigenvectors[1,0] * eigenvalues[1,0], cntr[1] - 0.02 * eigenvectors[1,1] * eigenvalues[1,0])
    drawAxis(img, cntr, p1, (0, 255, 0), 1)
    drawAxis(img, cntr, p2, (255, 255, 0), 5)
    angle = atan2(eigenvectors[0,1], eigenvectors[0,0]) # orientation in radians
    return angle


im, label = oa.main('Tesoura3', 100000)


def getOrientation(self, )

img = im[np.random.randint(int(len(im)*0.3),int(len(im)*0.8))].astype('uint8')
img[img == 0] = img.max()
img[img == 127] = 0
gray = cv.medianBlur(img, 3)

_, bw = cv.threshold(gray, 50, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)
contours, _ = cv.findContours(bw, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)

vet = []
for i, c in enumerate(contours):
    vet.append([len(c), i])

pts = contours[max(vet)[1]]
data_pts = pts.reshape(len(pts),2).astype('float64')
mean, eigenvectors, eigenvalues = cv.PCACompute2(data_pts, np.array([]))
cntr = (int(mean[0,0]), int(mean[0,1]))
p1 = (cntr[0] + 0.02 * eigenvectors[0,0] * eigenvalues[0,0], cntr[1] + 0.02 * eigenvectors[0,1] * eigenvalues[0,0])
p2 = (cntr[0] - 0.02 * eigenvectors[1,0] * eigenvalues[1,0], cntr[1] - 0.02 * eigenvectors[1,1] * eigenvalues[1,0])

cp1 = (p1[0] - cntr[0], p1[1] - cntr[1])
cp2 = (p2[0] - cntr[0], p2[1] - cntr[1])

m = np.zeros([128,128])
d = data_pts.astype('int')
for i in d:
    m[i[0], i[1]] = 1

plt.figure(1)
plt.imshow(m)
plt.arrow(cntr[1], cntr[0], cp1[1], cp1[0], length_includes_head=False, width=.5, head_width=2, head_length=2)
plt.arrow(cntr[1], cntr[0], cp2[1], cp2[0], length_includes_head=False, width=.5, head_width=2, head_length=2)
plt.plot(cntr[0], cntr[1], 'r')
plt.plot(p1[0], p1[1], 'y')
plt.plot(p2[0], p2[1], 'g')

plt.figure(2)
plt.imshow(gray)
plt.arrow(cntr[1], cntr[0], cp1[1], cp1[0], length_includes_head=False, width=.5, head_width=2, head_length=2)
plt.arrow(cntr[1], cntr[0], cp2[1], cp2[0], length_includes_head=False, width=.5, head_width=2, head_length=2)
plt.plot(cntr[0], cntr[1], 'r')
plt.plot(p1[0], p1[1], 'y')
plt.plot(p2[0], p2[1], 'g')
plt.show()



# parser = argparse.ArgumentParser(description='Code')
# parser.add_argument('--input', help='Path to input image.', default='1.png')
# args = parser.parse_args()
# src = cv.imread(cv.samples.findFile(args.input))
# # Convert image to grayscale
# gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
# #gray = cv.medianBlur(gray, 3)

# Convert image to binary
_, bw = cv.threshold(gray, 50, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)
contours, _ = cv.findContours(bw, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
for i, c in enumerate(contours):
    # Calculate the area of each contour
    area = cv.contourArea(c)
    # Ignore contours that are too small or too large
    if area < 1e2 or 1e5 < area:
        continue
    # Draw each contour only for visualisation purposes
    cv.drawContours(gray, contours, i, (0, 0, 255), 2)
    # Find the orientation of each shape
    getOrientation(c, gray)

cv.imshow('output', gray)
cv.waitKey()
cv2.destroyAllWindows()
