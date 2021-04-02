import os
import cv2
import sys
import struct
import copy
import numpy as np
from scipy import  signal
import matplotlib.pyplot as plt



class filterUtils:

    def avg(img, kernel=(5,5)):
        return cv2.blur(img, kernel)
    
    def median(img,kernelSize=3):
         return cv2.medianBlur(img, kernelSize)

    def sobel(img, flagGaussianFilter=False):
        #edge detection using sobel operator
        # converting to gray scale
        #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # remove noise
        if flagGaussianFilter:
            img = filterUtils.gaussian(img)

        # convolute with proper kernels
        sobelx = cv2.Sobel(img,cv2.CV_64F,1,0,ksize=5)  # x
        sobely = cv2.Sobel(img,cv2.CV_64F,0,1,ksize=5)  # y
        return sobelx + sobely

    def laplacian(img, flagGaussianFilter=False):
        #edge detection using sobel operator
        # converting to gray scale
        #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # remove noise
        if flagGaussianFilter:
            img = filterUtils.gaussian(img)

        # convolute with proper kernels
        laplacian = cv2.Laplacian(img,cv2.CV_64F)
        return laplacian

    def gaussian(img):
        #edge detection using sobel operator
        # converting to gray scale
        #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # remove noise
        img = cv2.GaussianBlur(img,(3,3),0)
        return img
    
    def bitsoncount(i):
        retorno = 0
        for val in i:
            if val == 1:
                retorno = retorno + 1
            elif val == 0:
                retorno = retorno - 1

        if retorno < 0:
            retorno = 0
        return retorno


    def popCountDownSample(img,length=2):
        img = filterUtils.binarizeNeuromorphicImage(img)
        retorno_vertical = np.zeros((img.shape[0] - length,img.shape[1] - length))
        retorno_horizontal = np.zeros((img.shape[0] - length,img.shape[1] - length))
        if len(img.shape) == 3 and img.shape[2] == 3:
            img = img[:,:,1]
        for x in range(img.shape[0] - length):
            for y in range(img.shape[1] - length):
                retorno_vertical[x,y] = filterUtils.bitsoncount(img[x,y:(y+length)])
                retorno_horizontal[x,y] = filterUtils.bitsoncount(img[x:(x+length),y])
        
        filteredImage = retorno_vertical+retorno_horizontal
        filteredImage = (filteredImage/filteredImage.max())*255
        filteredImage = filteredImage.astype(np.uint8)
        filteredImage = cv2.resize(filteredImage, (img.shape[0],img.shape[1]), interpolation = cv2.INTER_AREA)
        return filteredImage


    def binarizeNeuromorphicImage(img):
        img[img == 0] = 1
        img[img == 255] = 1
        img[img == 128] = 0
        img[img == 127.5] = 0
        return img


    def main():
        #função para testar filtros nas imagens neuromórficas
        neuromorphicImage = cv2.imread('/home/biolab-07/Documentos/Mestrado/Eduardo/HandStuff/Datasource/assets/testes/pencil_1.png')
        
        deepCopy = copy.deepcopy(neuromorphicImage)
        
        #deepCopy = filterUtils.binarizeNeuromorphicImage(deepCopy)

        #filteredImage = filterUtils.popCountDownSample(deepCopy,3)
        filteredImage = filterUtils.sobel(deepCopy,False)
        filteredImage = filterUtils.laplacian(filteredImage,True)
        

        
        fig, axarr = plt.subplots(1,2)
        textPlot = plt.text(0,0,"")
        axarr[0].set_title('original')
        axarr[1].set_title('filtered')

        
        neuromorphicImage = neuromorphicImage/neuromorphicImage.max()
        neuromorphicImage = neuromorphicImage * 255
        neuromorphicImage = neuromorphicImage.astype(np.uint8)
        

        axarr[0].imshow(neuromorphicImage)
        if(filteredImage.shape[2] == 3):
            axarr[1].imshow(filteredImage)
        else:
            axarr[1].imshow(np.dstack([filteredImage,filteredImage,filteredImage]))

        plt.show()

if __name__ == "__main__":
    filterUtils.main()