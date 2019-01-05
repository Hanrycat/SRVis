import sys

from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, curdoc
from bokeh.driving import linear
import random
import datetime as dt
import numpy as np
import pandas as pd

csv_data = pd.read_csv('laps.csv')
csv_data = csv_data.dropna()
csv_data = csv_data.reset_index(drop=False)
csv_x = csv_data['Long'] * -1
csv_y = csv_data['Lat'] * -1
csv_times = csv_data['Time']

source = ColumnDataSource(dict(
    x=[], y=[]
))

live_source = ColumnDataSource(dict(
    x=[], y=[]
))

centroid_source = ColumnDataSource(dict(
    x=[], y=[]
))

start_finish = ColumnDataSource(dict(
    x=[], y=[]
))

p = figure(plot_width=800, plot_height=700)
r1 = p.circle(x='x', y='y', source=live_source, color='firebrick', radius=0.00002)
r2 = p.line(x='x', y='y', source=source, line_color='navy', line_width=3)
r3 = p.circle(x='x', y='y', source=centroid_source, color='green', radius=0.00002)
r4 = p.circle(x='x', y='y', source=start_finish, color='white', alpha=0.5, line_color='black', radius=0.00003)
cur_time = 0
step = 1
prev_laps = 0
lap_length = 0
true_lap = -1
timeout = 0

def update():
    global cur_time, step, source, prev_laps, lap_length, true_lap, timeout
    ds1 = dict(x=[], y=[])
    ds2 = dict(x=[], y=[])
    ds3 = dict(x=[], y=[])
    ds4 = dict(x=[], y=[])

    ds1['x'].append(csv_x[cur_time])
    ds1['y'].append(csv_y[cur_time])

    ds2['x'].append(csv_x[cur_time])
    ds2['y'].append(csv_y[cur_time])
    cur_time += step
    if lap_length != 0:
        source.stream(ds1,lap_length)
    else:
        source.stream(ds1)
    live_source.stream(ds2, 1)

    ds3['x'].append(centroidnp(np.asarray(csv_x[:cur_time])))
    ds3['y'].append(centroidnp(np.asarray(csv_y[:cur_time])))
    centroid_source.stream(ds3, 1)


    if cur_time >= csv_times.__len__():
        sys.exit()
    laps, crossings = check_lapcounter(source,cur_time)
    if abs(laps-prev_laps) == 1 and timeout > 200: #TODO fix that it prints laps twice
        timeout=0
        if laps >0:
            true_lap = true_lap + 1
            print('Lap {}: {}'.format(true_lap, ((crossings[laps - 1][0]) - (crossings[laps - 2][0])) / 1000))
        lap_length=int(((crossings[laps - 1][0]) - (crossings[laps - 2][0]))/50)
    prev_laps = laps
    timeout += 1

    ds4['x'].append((crossings[laps - 1][1]))
    ds4['y'].append((crossings[laps - 1][2]))
    start_finish.stream(ds4,20)


curdoc().add_root(p)

# Add a periodic callback to be run every 500 milliseconds
curdoc().add_periodic_callback(update, 16)


def is_left(x1, y1, x2, y2, x3, y3):
    return ((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))


def centroidnp(arr):
    length = arr.shape[0]
    sum = np.sum(arr[:])
    return sum / length


def check_lapcounter(data, cur_time):
    x = data.data['x']
    y = data.data['y']
    # if cur_time < 620: #approx 10 seconds
    #     cx = x[0]
    #     cy = y[0]
    # else:
    #     cx = centroidnp(np.asarray(csv_x[:cur_time])) #TODO avoid hardcoding
    #     cy = centroidnp(np.asarray(csv_y[:cur_time]))
    cx = 96.769 #functional centroid
    cy = -40.8455
    # cx = 96.768 #trueish centroid
    # cy = -40.84575

    laps = -1
    crossings = [(csv_times[0], csv_x[0], csv_y[0])]
    for i in range(0, x.__len__() - 1):
        if y[i] <= cy:
            if (y[i + 1] > cy):
                if (is_left(x[i], y[i], x[i + 1], y[i + 1], cx, cy) > 0):
                    laps = laps + 1
                    crossings.append((csv_times[i], x[i], y[i]))

        else:
            if (y[i + 1] <= cy):
                if (is_left(x[i], y[i], x[i + 1], y[i + 1], cx, cy) < 0):
                    laps = laps - 1
                    crossings.append((csv_times[i], x[i], y[i]))
    return abs(laps), crossings
