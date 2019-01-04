"""

    https://bokeh.pydata.org/en/latest/docs/user_guide/server.html

    https://bokeh.pydata.org/en/latest/docs/gallery.html

    https://demo.bokehplots.com/apps/stocks
    https://github.com/bokeh/bokeh/tree/master/examples/app/stocks

    https://demo.bokehplots.com/apps/selection_histogram
    https://github.com/bokeh/bokeh/blob/master/examples/app/selection_histogram.py
"""
import itertools
import os

import pandas as pd
import numpy as np
from bokeh.layouts import column, row
from bokeh.models import Button, GlyphRenderer
from bokeh.palettes import Category20_8
from bokeh.plotting import figure, curdoc

SUSPENSION = [
    'RearRight|""|0.0|5.0|50',
    'RearLeft|""|0.0|5.0|50',
    'FrontLeft|""|0.0|5.0|50',
    'FrontRight|""|0.0|5.0|50'
]
POWERTRAIN = [
    'EngineTemp|"C"|0|200|1',
    'OilPressure|"psi"|0.0|200.0|50',
    'OilTemp|"F"|0|300|1',
    'FuelTemp|"C"|0|1024|1',
]
POSITIONING = [
    'Latitude|"Degrees"|-180.0|180.0|10',
    'Longitude|"Degrees"|-180.0|180.0|10',
    'Speed|"mph"|0.0|150.0|10',
    'Interval|"ms"|0|0|1'
]
lat = 'Latitude|"Degrees"|-180.0|180.0|10'
long = 'Longitude|"Degrees"|-180.0|180.0|10'
time = 'Interval|"ms"|0|0|1'


def rc_data_parse(logfile):
    data = pd.read_csv('{}'.format(logfile))
    data = data.fillna(method='ffill')
    data['filename'] = logfile
    return data


def build_dict(parsed_data):
    new_dict = {}
    for dict_data_series in SUSPENSION:
        new_dict[dict_data_series.split('|')[0]] = parsed_data[dict_data_series]
    for dict_data_series in POWERTRAIN:
        new_dict[dict_data_series.split('|')[0]] = parsed_data[dict_data_series]
    for dict_data_series in POSITIONING:
        new_dict[dict_data_series.split('|')[0]] = parsed_data[dict_data_series]
    return new_dict


def collect_logs():
    logfiles = []
    for file in os.listdir(os.getcwd()):
        if file.endswith('.log'):
            logfiles.append(file)
    return logfiles


i = 0


def callback():
    print('UPDATE')
    global i
    logfiles = collect_logs()
    parsed_data = rc_data_parse(logfiles[i])
    current_filename = 'GPS Data_{}'.format(logfiles[i])
    parsed_data.loc[parsed_data[lat] == 0, lat] = np.nan
    parsed_data.loc[parsed_data[long] == 0, long] = np.nan
    ds.data = build_dict(parsed_data)

    i = i + 1
    if i >= logfiles.__len__():
        i = 0


global ds
global current_filename
default_filename = collect_logs()[0]
default_source = build_dict(rc_data_parse(collect_logs()[0]))

susp = figure(sizing_mode='scale_both', width=700, height=300, title='Suspension',
              x_axis_label='Time')
powertrain = figure(sizing_mode='scale_both', width=700, height=300, title='Powertrain',
                    x_axis_label='Time')
coord = figure(sizing_mode='scale_both', width=700, height=600, title='GPS Data')
colors = itertools.cycle(Category20_8)
# TODO figure out how to get the lines to update
for data_series, color in zip(SUSPENSION, colors):
    l = susp.line(x='Interval', y=data_series.split('|')[0],
              line_width=2,
              line_color=color,
              source=default_source,
              legend=data_series.split('|')[0])
    ds = l.data_source

for data_series, color in zip(POWERTRAIN, colors):
    l = powertrain.line(x='Interval', y=data_series.split('|')[0],
                    line_width=2,
                    line_color=color,
                    source=default_source,
                    legend=data_series.split('|')[0])
    ds = l.data_source

c = coord.circle(x='Latitude', y='Longitude', source=default_source, size=3, color='darkcyan')
ds = c.data_source
ds = l.data_source
current_filename = coord.title
# TODO Add datatable
# TODO Add box selection/highlighting
# add a button widget and configure with the call back
button = Button(label="Switch logs")
button.on_click(callback)

# put the button and plot in a layout and add to the document
curdoc().add_root(column(row(column(susp, powertrain), coord), button))
callback()
