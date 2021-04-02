from matplotlib.image import NonUniformImage
import matplotlib.pyplot as plt
import numpy as np

xedges = [0, 1, 3, 5]
yedges = [0, 2, 3, 4, 6]
x = np.random.normal(2, 1, 100)
y = np.random.normal(1, 1, 100)
H, xedges, yedges = np.histogram2d(x, y, bins=(xedges, yedges))
H = H.T  # Let each row list bins with common y range.
fig = plt.figure(figsize=(7, 3))
ax = fig.add_subplot(131, title='imshow: square bins')
plt.imshow(H, interpolation='nearest', origin='low',extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]])
ax = fig.add_subplot(132, title='pcolormesh: actual edges',aspect='equal')

X, Y = np.meshgrid(xedges, yedges)
ax.pcolormesh(X, Y, H)
ax = fig.add_subplot(133, title='NonUniformImage: interpolated',aspect='equal', xlim=xedges[[0, -1]], ylim=yedges[[0, -1]])

im = NonUniformImage(ax, interpolation='bilinear')

xcenters = (xedges[:-1] + xedges[1:]) / 2
ycenters = (yedges[:-1] + yedges[1:]) / 2

im.set_data(xcenters, ycenters, H)

ax.images.append(im)
plt.show()