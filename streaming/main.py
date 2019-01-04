import sys

from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, curdoc
from bokeh.driving import linear
import random
import datetime as dt
import pandas as pd

csv_data = pd.read_csv('laps.csv')
csv_data = csv_data.dropna()
csv_data = csv_data.reset_index(drop=False)
csv_x = csv_data['Lat']
csv_y = csv_data['Long']
csv_times = csv_data['Time']

source = ColumnDataSource(dict(
    x=[], y=[]
))

live_source = ColumnDataSource(dict(
    x=[], y=[]
))

p = figure(plot_width=800, plot_height=400)
r1 = p.circle(x='x', y='y', source=live_source, color='firebrick', radius=0.00002)
r2 = p.line(x='x', y='y', source=source, line_color='navy', line_width=2)

cur_time = 0
step = 1


def update():
    global cur_time, step, source
    ds1 = dict(x=[], y=[])
    ds2 = dict(x=[], y=[])

    ds1['x'].append(csv_x[cur_time])
    ds1['y'].append(csv_y[cur_time])

    ds2['x'].append(csv_x[cur_time])
    ds2['y'].append(csv_y[cur_time])
    cur_time += step
    source.stream(ds1)
    live_source.stream(ds2, 1)

    if cur_time >= csv_times.__len__():
        sys.exit()


curdoc().add_root(p)

# Add a periodic callback to be run every 500 milliseconds
curdoc().add_periodic_callback(update, 16)
print(cur_time)
if cur_time >= 10:
# if cur_time >= csv_times.size():
    sys.exit()
