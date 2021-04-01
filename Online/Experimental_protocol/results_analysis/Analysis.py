import numpy as np
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D


def radar_factory(num_vars, frame='circle'):
    """
    Create a radar chart with `num_vars` axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle', 'polygon'}
        Shape of frame surrounding axes.

    """
    # calculate evenly-spaced axis angles
    theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)

    class RadarAxes(PolarAxes):

        name = 'radar'
        # use 1 line segment to connect specified points
        RESOLUTION = 1

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # rotate plot such that the first axis is at the top
            self.set_theta_zero_location('N')

        def fill(self, *args, closed=True, **kwargs):
            """Override fill so that line is closed by default"""
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.append(x, x[0])
                y = np.append(y, y[0])
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            # The Axes patch must be centered at (0.5, 0.5) and of radius 0.5
            # in axes coordinates.
            if frame == 'circle':
                return Circle((0.5, 0.5), 0.5)
            elif frame == 'polygon':
                return RegularPolygon((0.5, 0.5), num_vars,
                                      radius=.5, edgecolor="k")
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

        def _gen_axes_spines(self):
            if frame == 'circle':
                return super()._gen_axes_spines()
            elif frame == 'polygon':
                # spine_type must be 'left'/'right'/'top'/'bottom'/'circle'.
                spine = Spine(axes=self,
                              spine_type='circle',
                              path=Path.unit_regular_polygon(num_vars))
                # unit_regular_polygon gives a polygon of radius 1 centered at
                # (0, 0) but we want a polygon of radius 0.5 centered at (0.5,
                # 0.5) in axes coordinates.
                spine.set_transform(Affine2D().scale(.5).translate(.5, .5)
                                    + self.transAxes)
                return {'polar': spine}
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

    register_projection(RadarAxes)
    return theta


import random

data1 = pd.DataFrame([[3, 48, 16, 80, 24, 0],
                     [0, 52, 18, 75, 16, 8],
                     [7, 36, 30, 75, 30, 0],
                     [0, 72, 32, 42, 52, 8],
                     [24, 26, 6, 54, 39, 0]],
                     columns=['Mental', 'Física', 'Temporal', 'Performance', 'Esforço', 'Frustração'])

# data1 = pd.DataFrame([[3, 48, 16, 80, 24, 0],
#                      [0, 52, 18, 75, 16, 8],
#                      [7, 36, 30, 75, 30, 0],
#                      [24, 26, 6, 54, 39, 0]],
#                      columns=['Mental', 'Física', 'Temporal', 'Performance', 'Esforço', 'Frustração'])


data2 = pd.DataFrame([[20, 12, 30, 45, 16, 20],
                     [32, 21, 3, 36, 6,	8],
                     [18, 56, 4, 18, 24, 12],
                     [24, 33, 15, 28, 22, 8],
                     [48, 10, 39, 51, 10, 9]],
                     columns=['Mental', 'Física', 'Temporal', 'Performance', 'Esforço', 'Frustração'])



aux = [3,4,1,2,0,5]

# random.shuffle(aux)

val = [data1.mean()[aux], data2.mean()[aux]]
std_val = [data1.std()[aux], data2.std()[aux]]
colors = np.array(["blue", "red"])

N = 6
theta = radar_factory(N, frame='polygon')

axis = data1.columns[aux]

fig, ax = plt.subplots(figsize=(9, 9),subplot_kw=dict(projection='radar'))


ax.set_rgrids([20, 40, 60, 80])
ax.set_ylim(0,100)

for y_est, y_err, color in zip(val, std_val, colors):
    print(y_est)
    print(y_err)
    print(color)
    ax.plot(theta, y_est, color=color, lw=4)
    ax.fill(theta,  y_est + y_err, facecolor=color, alpha=0.12)
    ax.fill(theta,  y_est - y_err, facecolor="white", alpha=1)

ax.set_varlabels(axis)

# add legend relative to top-left plot
labels = ('Média', 'Desvio padrão')
legend = ax.legend(labels, loc=(0.9, .95),
                          labelspacing=0.1, fontsize='small')


plt.show()



aux = [3,4,1,2,0,5]
colors = np.array(["blue", "red", "green", "yellow", "puple"])

# random.shuffle(aux)
val = [data1.iloc[0][aux], data1.iloc[1][aux], data1.iloc[2][aux], data1.iloc[3][aux], data1.iloc[4][aux]]

N = 6
theta = radar_factory(N, frame='polygon')

axis = data1.columns[aux]

fig, ax = plt.subplots(figsize=(9, 9),subplot_kw=dict(projection='radar'))


ax.set_rgrids([20, 40, 60, 80])
ax.set_ylim(0,100)

for y_est, color in zip(val, colors):
    ax.plot(theta, y_est, lw=2)
    ax.fill(theta, y_est, alpha=0.2)
ax.set_varlabels(axis)

# add legend relative to top-left plot
labels = ('V1 (M)', 'V2 (M)', 'V3 (M)', 'V4 (F)')
legend = ax.legend(labels, loc=(0.9, .95), labelspacing=0.1, fontsize='small')

plt.show()


aux = [3,4,1,2,0,5]

# random.shuffle(aux)
val = [data2.iloc[0][aux], data2.iloc[1][aux], data2.iloc[2][aux], data2.iloc[3][aux], data2.iloc[4][aux]]

N = 6
theta = radar_factory(N, frame='polygon')

axis = data2.columns[aux]

fig, ax = plt.subplots(figsize=(9, 9),subplot_kw=dict(projection='radar'))


ax.set_rgrids([20, 40, 60, 80])
ax.set_ylim(0,100)

for y_est, color in zip(val, colors):
    ax.plot(theta, y_est, lw=2)
    ax.fill(theta, y_est, alpha=0.2)
ax.set_varlabels(axis)

# add legend relative to top-left plot
labels = ('V1 (M)', 'V2 (M)', 'V3 (M)', 'V4 (F)')
legend = ax.legend(labels, loc=(0.9, .95), labelspacing=0.1, fontsize='small')

plt.show()
















step = "one"
vol = []
for i in range(4):
    vol.append(pd.read_csv("/home/user/GitHub/openDVS/Online/Experimental_protocol/DATA/vol" + str(i+1) + "_task_info_" + step + ".csv"))
    plt.plot(abs(vol[i].iloc[:,5] - vol[i].iloc[:,6]))


a = pd.DataFrame([abs(vol[0].iloc[:,5] - vol[0].iloc[:,6]),
                  abs(vol[1].iloc[:,5] - vol[1].iloc[:,6]),
                  abs(vol[2].iloc[:,5] - vol[2].iloc[:,6]),
                  abs(vol[3].iloc[:,5] - vol[3].iloc[:,6])])


plt.plot(abs(vol[0].iloc[:,5] - vol[0].iloc[:,6]))
plt.plot(abs(vol[1].iloc[:,5] - vol[1].iloc[:,6]))


plt.show()
