from time import time
import numpy as np
from utilsDVS128 import OpenModel, DisplayDVS128, predictObject, DVS128 
from openAEDAT import matrix_active
import tensorflow as tf
from itertools import groupby
import cv2
import matplotlib.pyplot as plt


if tf.__version__ == '2.0.0':
	physical_devices = tf.config.experimental.list_physical_devices('GPU')
	tf.config.experimental.set_memory_growth(physical_devices[0], True)
elif tf.__version__ == '1.14.0':
	config = tf.ConfigProto()
	config.gpu_options.allow_growth = True
	session = tf.Session(config=config)


device = DVS128()

device.start_data_stream()

clip_value = 3
m = 4

model = OpenModel('/home/user/GitHub/Classification_DVS128/model.json', '/home/user/GitHub/Classification_DVS128/model.h5')

def main():
	t = time()
	stop = False
	while not stop:
		try:
			(pol_events, num_pol_event, special_events, num_special_event) = device.get_event("events_hist")
			if num_pol_event != 0:
				img = pol_events[..., 1]-pol_events[..., 0]
				img = np.clip(img, -clip_value, clip_value)
				img = img+clip_value
				img = img.reshape((128,128)).astype('float32')
				img = cv2.resize(img, dsize=(128*m, 128*m))
				cv2.imshow("image", img/float(clip_value*2))
				if cv2.waitKey(1) & 0xFF == ord('q'):
					break
					
		except KeyboardInterrupt:
			device.shutdown()
			stop = True	
		       

if __name__ == "__main__":
	main()
	
	
	
	
	
	
	
	
	
	

