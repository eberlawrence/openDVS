import sys
sys.path.append('../Online')
import numpy as np
import neo
import quantities as pq
import elephant as elep
import matplotlib.pyplot as plt
from multiprocessing import Pool
import time

import openAEDAT

t, x, y, p = openAEDAT.loadaerdat('Nada3.aedat')

t, x, y, p = t[:int(len(t)*0.2)], x[:int(len(x)*0.2)], y[:int(len(y)*0.2)], p[:int(len(p)*0.2)]
def roiToSpikes(x, y, i=0, s=128):
    final = []
    for a in range(i,s):
        for b in range(i,s):
            final.append(list(t[(x == a) & (y == b)]))
    return np.array(final)

f = roiToSpikes(x, y)

st = [neo.SpikeTrain(i, units='microsecond', t_stop=t[-1]) for i in f]

#victor purpura distance
vpd_dist = elep.spike_train_dissimilarity.victor_purpura_dist(st,sort=False,q=20*pq.Hz)
#van rossum distance
vrs_dist = elep.spike_train_dissimilarity.van_rossum_dist(st,tau=0.2*pq.second,sort=False)

#rescale the spike vector to time
ts = [st[i].rescale(pq.us) for i in range(len(f))]
#plot the rastergram
plt.figure()

for i in range(len(f)):
    plt.plot(st[i],i*np.ones_like(st[i]),'k.',markersize=2)


plt.axis('tight')
plt.show()


#plot vpd distance
plt.figure()
plt.matshow(vpd_dist,fignum=False)
plt.colorbar()
plt.title('Victor Purpura Distance')

#plot van rossum distance
plt.figure()
plt.matshow(vrs_dist,fignum=False)
plt.colorbar()
plt.title('Van Rossum Distance')

plt.show()











# def get_spikes(idx):
#     t0 = time.time()
#     print('started ' + str(idx))
#     global x,y
#     idxX = int(idx/128)
#     idxY = y % 128
#     tf = time.time()
#     print('finished! ' + str(idx) + ' ' + str(tf-t0))
#     return np.where((x==idxX) & (y==idxY))[0]
#
# #run parallel stuff
# p = Pool(processes=4)
# resultSpikes = p.map(get_spikes,np.arange(0,128*128))
# p.join()
# p.close()
