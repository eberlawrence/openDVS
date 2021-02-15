import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib import image as im

cap = cv2.VideoCapture(0)
frames = []
count = 464
while(True):
    count += 1
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frames.append(frame)
    im.imsave('images/mug/mug'+str(count)+'.png', frame)
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
