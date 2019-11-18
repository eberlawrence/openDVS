import pygame
from time import time
import numpy as np
import utilsDVS128
from openAEDAT import matrix_active
import tensorflow as tf
from itertools import groupby
from pyaer.dvs128 import DVS128

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

clock = pygame.time.Clock()

model = utilsDVS128.OpenModel('/home/user/GitHub/Classification_DVS128/model.json', '/home/user/GitHub/Classification_DVS128/model.h5')

def main():
	t = time()
	stop = False
	flag = True
	pygame.init()
	displayEvents = utilsDVS128.DisplayDVS128(128, 128, 4)
	pol, x, y, ts = [], [], [], []
	count = []
	while not stop:
		for e in pygame.event.get():
			if e.type == pygame.QUIT:
				stop = True
                
		pol_events, num_pol_event, special_events, num_special_event = device.get_event()
		if flag == True:
			first_ts = pol_events[0,0]
			flag = False
		
		ts.extend(pol_events[:,0] - first_ts)
		x.extend(pol_events[:,1])
		y.extend(pol_events[:,2])
		pol.extend(pol_events[:,3])
		
		if np.sum(ts) >= 50000: # 6 fps            
			displayEvents.gameDisplay.fill(displayEvents.background)
			displayEvents.plotEvents(pol, x, y, ts)
			img = matrix_active(np.array(x), np.array(y), np.array(pol))
			img = img.reshape(1, 128, 128, 1)
			resp, objectSet = utilsDVS128.predictObject(img, model)
			count.append(resp)

			t2 = time() - t               
			displayEvents.printFPS(1/t2)            
			pygame.display.update()
			t = time()
			pol, x, y, ts = [], [], [], []
			flag = True
			if len(count) == 10:
				count = np.bincount(count)
				print(objectSet[np.argmax(count)][1])       	
				count = []
       
	pygame.quit()

if __name__ == "__main__":
	main()
