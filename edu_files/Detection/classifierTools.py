import os
import cv2
import sys
import struct
import numpy as np
from scipy import  signal
from sklearn.model_selection import train_test_split
from keras.models import model_from_json


class classifierTools:


    def predictObject(img, model, flag='No'):

        # flag = input("Would you like to change the default object set? ")
        if flag == "Yes" or flag == "yes" or flag == "Y" or flag == "y":
            objectSet = input("New object set: ").split(", ")
        else:
            objectSet = [[0, 'Mug'],
                        [1, 'Nothing'],
                        [2, 'Calculator'],
                        [3, 'Key'],
                        [4, 'Scissor']]

        preds = model.predict(img)
        return objectSet[np.argmax(preds)][0], objectSet





    def openModel(model_JSON_file, model_WEIGHTS_file):
        '''
        Function to open a CNN model and its weights.

        imgC = UploadModel.OpenModel('/home/user/GitHub/Classification_DVS128/model.json',
                                    '/home/user/GitHub/Classification_DVS128/model.h5')
        '''
        # load model from JSON file
        with open(model_JSON_file, "r") as json_file:
            loadedModel_JSON = json_file.read()
            loadedModel = model_from_json(loadedModel_JSON)

        # load weights into the new model
        loadedModel.load_weights(model_WEIGHTS_file)
        loadedModel._make_predict_function()

        return loadedModel
