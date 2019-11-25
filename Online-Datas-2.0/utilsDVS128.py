from __future__ import print_function, absolute_import
import abc
import cv2
import numpy as np
from pyaer import libcaer, utils
from builtins import range
from pyaer.filters import DVSNoise
import math 
import pygame
from random import randint
from time import time
from keras.models import model_from_json


class DisplayDVS128:
    pygame.display.set_caption('Neuromorphic Camera - DVS128')

    def __init__(self, width, height, m=7):
        self.m = m
        self.width = width * self.m
        self.height = height * self.m
        self.background = (128, 128, 128)
        self.colorPos = (255, 255, 255)
        self.colorNeg = (0, 0, 0)
        self.gameDisplay = pygame.display.set_mode((self.width, self.height))
        self.gameDisplay.fill(self.background)        
        
    def printFPS(self, fps):
        font = pygame.font.SysFont('Segoe UI', 20)
        txtFPS = font.render('FPS: {0:.2f}'.format(fps), True, (0, 0, 0))
        self.gameDisplay.blit(txtFPS,(0,0))
		
    def plotEvents(self, pol, x, y, ts):
        i = 0
        while i < len(pol):
            if pol[i] == 0:
                self.gameDisplay.fill(self.colorPos, ((127 - x[i]) * self.m, y[i] * self.m, self.m, self.m))
                i += 1
            else:
                self.gameDisplay.fill(self.colorNeg, ((127 - x[i]) * self.m, y[i] * self.m, self.m, self.m))
                i += 1	



#########################################################################################################################################################################################################################################
#########################################################################################################################################################################################################################################
#########################################################################################################################################################################################################################################



def OpenModel(model_JSON_file, model_WEIGHTS_file):
	'''
	imgC = UploadModel.OpenModel('/home/user/GitHub/Classification_DVS128/model.json', '/home/user/GitHub/Classification_DVS128/model.h5')
	'''	
	# load model from JSON file
	with open(model_JSON_file, "r") as json_file:
		loadedModel_JSON = json_file.read()
		loadedModel = model_from_json(loadedModel_JSON)

	# load weights into the new model
	loadedModel.load_weights(model_WEIGHTS_file)
	loadedModel._make_predict_function()
	
	return loadedModel


#########################################################################################################################################################################################################################################


def predictObject(img, model, flag='N'):

	# flag = input("Would you like to change the default object set? ")  
	if flag == "Sim" or flag == "sim" or flag == "S" or flag == "s":
		objectSet = input("New object set: ").split(", ")
	else:
		objectSet = [[0, 'Caneca'],
					 [1, 'Nada'],
					 [2, 'Calculadora'],
					 [3, 'Chave'],
					 [4, 'Tesoura']]
					 
	preds = model.predict(img)
	return objectSet[np.argmax(preds)][0], objectSet


#########################################################################################################################################################################################################################################
#########################################################################################################################################################################################################################################
#########################################################################################################################################################################################################################################





#########################################################################################################################################################################################################################################
#########################################################################################################################################################################################################################################
#########################################################################################################################################################################################################################################




class DVS128():
    def __init__(self, device_id=1, bus_number_restrict=0, dev_address_restrict=0, serial_number="", noise_filter=False):
    
        self.handle = None
        self.get_event_number_funcs = {
            libcaer.POLARITY_EVENT:
                libcaer.caerEventPacketHeaderGetEventNumber,
            libcaer.SPECIAL_EVENT:
                libcaer.caerEventPacketHeaderGetEventNumber,
            libcaer.IMU6_EVENT:
                libcaer.caerEventPacketHeaderGetEventNumber,
            libcaer.IMU9_EVENT:
                libcaer.caerEventPacketHeaderGetEventNumber,
            libcaer.SPIKE_EVENT:
                libcaer.caerEventPacketHeaderGetEventNumber
            }
        self.get_event_packet_funcs = {
            libcaer.POLARITY_EVENT:
                libcaer.caerPolarityEventPacketFromPacketHeader,
            libcaer.SPECIAL_EVENT:
                libcaer.caerSpecialEventPacketFromPacketHeader,
            libcaer.FRAME_EVENT:
                libcaer.caerFrameEventPacketFromPacketHeader,
            libcaer.IMU6_EVENT:
                libcaer.caerIMU6EventPacketFromPacketHeader,
            libcaer.IMU9_EVENT:
                libcaer.caerIMU9EventPacketFromPacketHeader,
            libcaer.SPIKE_EVENT:
                libcaer.caerSpikeEventPacketFromPacketHeader
            }
            
        self.open(libcaer.CAER_DEVICE_DVS128, device_id, bus_number_restrict, dev_address_restrict, serial_number)
        self.obtain_device_info(self.handle)
        self.filter_noise = noise_filter
        if noise_filter is True:
            self.noise_filter = DVSNoise(self.dvs_size_X, self.dvs_size_Y)
        else:
            self.noise_filter = None


    @abc.abstractmethod
    def obtain_device_info(self, handle):
        return


    def open(self, device_type, device_id=1, bus_number_restrict=0, dev_address_restrict=0, serial_number=""):
        self.handle = libcaer.caerDeviceOpen(device_id, device_type, bus_number_restrict, dev_address_restrict, serial_number)
        if self.handle is None:
            raise ValueError("The device is failed to open.")         
            
            
    def close(self):
        if self.handle is not None:
            libcaer.caerDeviceClose(self.handle)


    def shutdown(self):
        self.data_stop()
        self.close()


    def data_start(self):
        if self.handle is not None:
            data_start_success = libcaer.caerDeviceDataStart(self.handle, None, None, None, None, None)
            return data_start_success
        else:
            return False


    def data_stop(self):
        libcaer.caerDeviceDataStop(self.handle)


    def send_default_config(self):
        if self.handle is not None:
            send_success = libcaer.caerDeviceSendDefaultConfig(self.handle)
            return send_success
        else:
            return False


    def set_data_exchange_blocking(self, exchange_blocking=True):
        return self.set_config(libcaer.CAER_HOST_CONFIG_DATAEXCHANGE, libcaer.CAER_HOST_CONFIG_DATAEXCHANGE_BLOCKING, exchange_blocking)


    def set_config(self, mod_addr, param_addr, param):
        if self.handle is not None:
            set_success = libcaer.caerDeviceConfigSet(self.handle, mod_addr, param_addr, param)
            return set_success
        else:
            return False


    def get_packet_container(self):
        packet_container = libcaer.caerDeviceDataGet(self.handle)
        if packet_container is not None:
            packet_number = libcaer.caerEventPacketContainerGetEventPacketsNumber(packet_container)
            return packet_container, packet_number
        else:
            return None, None


    def get_packet_header(self, packet_container, idx):
        packet_header = libcaer.caerEventPacketContainerGetEventPacket(packet_container, idx)
        if packet_header is None:
            return (None, None)
        else:
            packet_type = libcaer.caerEventPacketHeaderGetEventType(packet_header)
            return packet_header, packet_type


    def get_event_packet(self, packet_header, packet_type):
        num_events = self.get_event_number_funcs[packet_type](packet_header) if packet_type in self.get_event_number_funcs else None
        event_packet = self.get_event_packet_funcs[packet_type](packet_header) if packet_type in self.get_event_packet_funcs else None
        return num_events, event_packet


    def get_special_event(self, packet_header):
        num_events, special = self.get_event_packet(packet_header, libcaer.SPECIAL_EVENT)
        events = libcaer.get_special_event(special, num_events*2).reshape(num_events, 2)
        return events, num_events



    def start_data_stream(self, send_default_config=True):
        if send_default_config is True:
            self.send_default_config()
        self.data_start()
        self.set_data_exchange_blocking()



    def get_polarity_event(self, packet_header, noise_filter=False):
        num_events, polarity = self.get_event_packet(packet_header, libcaer.POLARITY_EVENT)
        if noise_filter is True:
            polarity = self.noise_filter.apply(polarity)
            events = libcaer.get_filtered_polarity_event(polarity, num_events*5).reshape(num_events, 5)
        else:
            events = libcaer.get_polarity_event(polarity, num_events*4).reshape(num_events, 4)
        return events, num_events
        


    def get_polarity_hist(self, packet_header, device_type=None):
    
        num_events, polarity = self.get_event_packet(packet_header, libcaer.POLARITY_EVENT)
        if device_type == "DVS128":
            hist = libcaer.get_polarity_event_histogram_128(polarity, num_events)
        else:
            return None, 0
        return hist, num_events
        
        
                
    def get_event(self, mode="events"):
        packet_container, packet_number = self.get_packet_container()
        if packet_container is not None:
            num_pol_event = 0
            num_special_event = 0
            pol_events = None
            special_events = None
            for packet_id in range(packet_number):
                packet_header, packet_type = self.get_packet_header(packet_container, packet_id)
                if packet_type == libcaer.POLARITY_EVENT:
                    if mode == "events":
                        events, num_events = self.get_polarity_event(packet_header, self.filter_noise)
                        pol_events = np.hstack((pol_events, events)) if pol_events is not None else events
                    elif mode == "events_hist":
                        hist, num_events = self.get_polarity_hist(packet_header, device_type="DVS128")
                        pol_events = hist if pol_events is None else pol_events+hist
                    num_pol_event += num_events
                    
                elif packet_type == libcaer.SPECIAL_EVENT:
                    events, num_events = self.get_special_event(packet_header)
                    special_events = np.hstack((special_events, events)) if special_events is not None else events
                    num_special_event += num_events
            libcaer.caerEventPacketContainerFree(packet_container)

            return (pol_events, num_pol_event, special_events, num_special_event)
        else:
            return None
            

            
            
            
            
           
