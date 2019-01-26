import itertools
import sys
import os
import pandas as pd
import numpy as np
import bokeh.plotting as bk
from bokeh.models import Span
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure, output_file, show, save
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource
from bokeh.models.tools import HoverTool
from bokeh.palettes import Category20_20
from bokeh.palettes import inferno
from bokeh.transform import linear_cmap
from datetime import datetime
from common.plotting_common import plot_image, create_table
from bokeh.layouts import widgetbox
from bokeh.models.widgets import CheckboxButtonGroup
from bokeh.models.widgets import RangeSlider

# hv.extension('bokeh')


# TODO move finalized code to common.plotting_common.
#  Only code that is specific to post_processing log files for
#  subteam analysis should live here

# instructions and explanations be found here https://programminghistorian.org/en/lessons/visualizing-with-bokeh
# https://bokeh.pydata.org/en/latest/docs/user_guide.html
# https://pandas.pydata.org/pandas-docs/stable/index.html

def rc_data_parse(logfile):

    data = pd.read_csv('..\{}'.format(logfile))
    data = data.fillna(method='ffill')
    return data


def plot_rcprodata(df, filename):
    # List of headers that correspond to each subteams data
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
    ACCELERATION = [
        'AccelX|"G"|-3.0|3.0|25',
        'AccelY|"G"|-3.0|3.0|25',
        'AccelZ|"G"|-3.0|3.0|25'
    ]

    lat = 'Latitude|"Degrees"|-180.0|180.0|10'
    long = 'Longitude|"Degrees"|-180.0|180.0|10'
    speed = ['Speed|"mph"|0.0|150.0|10']
    time = 'Interval|"ms"|0|0|1'

    susp = create_figure(filename, 'Suspension_{}')
    powertrain = create_figure(filename, 'Powertrain_{}')
    accel = create_figure(filename, 'Acceleration_{}')
    speed_p = create_figure(filename, 'Speed_{}')
    traction = create_figure(filename, 'Traction_{}')

    # TODO figure out color palletes https://bokeh.pydata.org/en/latest/docs/reference/palettes.html
    # create a color iterator
    colors = itertools.cycle(Category20_20)

    df.loc[df[lat] == 0, lat] = np.nan
    df.loc[df[long] == 0, long] = np.nan
    df[lat] = -df[lat]
    df[long] = -df[long]
    df = df.dropna()
    source = ColumnDataSource(df)
    source.add(df['Interval|"ms"|0|0|1'], name='Time')

    plot_data(susp, colors, source, time, SUSPENSION)
    plot_data(powertrain, colors, source, time, POWERTRAIN)
    plot_data(accel, colors, source, time, ACCELERATION)
    plot_data(speed_p, colors, source, time, speed)
    coord = plot_coords(df, source, filename, lat, long)
    traction.circle(x='AccelX|"G"|-3.0|3.0|25', y='AccelY|"G"|-3.0|3.0|25',
                    source=source, size=3, color='firebrick')

    susp_hover = HoverTool()
    powertrain_hover = HoverTool()
    accel_hover = HoverTool()
    traction_hover = HoverTool()
    speed_hover = HoverTool()

    susp_hover.tooltips = [
        ('Data', '$name'),
        ('Time (MS)', '$x{0.}'),
        ('Volts', '$y{0.000}')
    ]

    powertrain_hover.tooltips = [
        ('Data', '$name'),
        ('Time (MS)', '$x{0.}'),
        ('Pressure/Temp', '$y{0.000}')
    ]

    accel_hover.tooltips = [
        ('Data', '$name'),
        ('Time (MS)', '$x{0.}'),
        ('Accel (G)', '$y{0.000}')
    ]

    traction_hover.tooltips = [
        ('X Accel (G)', '$x{0.000}'),
        ('Y Accel (G)', '$y{0.000}')
    ]

    speed_hover.tooltips = [
        ('Speed (mph)', '$y{0.000}')
    ]

    susp.sizing_mode = 'scale_width'
    powertrain.sizing_mode = 'scale_width'
    susp.add_tools(susp_hover)
    powertrain.add_tools(powertrain_hover)
    accel.add_tools(accel_hover)
    traction.add_tools(traction_hover)
    speed_p.add_tools(speed_hover)
    susp.legend.click_policy = 'hide'
    powertrain.legend.click_policy = 'hide'

    return susp, powertrain, traction, accel, speed_p, coord


def create_figure(filename, title_string):

    TOOLS = 'pan,box_select,box_zoom,wheel_zoom,save,reset'
    if title_string == 'Traction':
        data_type = figure(output_backend="webgl", tools=TOOLS, sizing_mode='scale_both',
                           width=700, height=300, title=title_string.format(filename),
                           x_axis_label='X accel')
    else:
        data_type = figure(output_backend="webgl", tools=TOOLS, sizing_mode='scale_both',
                           width=700, height=300, title=title_string.format(filename),
                           x_axis_label='Time')

    return data_type


def plot_data(p, colors, source, time, header_list):

    for data_series, color in zip(header_list, colors):
        p.line(x=time, y=data_series,
            line_width=2,
            line_color=color,
            source=source,
            legend=data_series.split('|')[0],
            name=data_series.split('|')[0])


def plot_coords(df, source, filename, lat, long):

    TOOLS = 'pan,box_select,box_zoom,wheel_zoom,save,reset'
    speed = 'Speed|"mph"|0.0|150.0|10'

    coord = figure(output_backend="webgl", tools=TOOLS, sizing_mode='scale_both',
                   width=700, height=600, title='GPS Data_{}'.format(filename))

    mapper = linear_cmap(field_name='Speed|"mph"|0.0|150.0|10', palette=inferno(max(df[speed])-min(df[speed])),
                         # low_color='#ffffff', high_color='#ffffff',
                         low=min(df[speed] + 13), high=max(df[speed]) - 27)

    coord.circle(x=long, y=lat, source=source, size=3, color=mapper)

    hover = HoverTool()
    hover.tooltips = [
        ('Lat', '$x{0.000000}'),
        ('Long', '$y{0.000000}'),
        ('Time', '@Time')
    ]
    hover.point_policy = 'follow_mouse'
    coord.add_tools(hover)

    return coord

def widgets(df):

    lat = 'Latitude|"Degrees"|-180.0|180.0|10'
    long = 'Longitude|"Degrees"|-180.0|180.0|10'
    speed = ['Speed|"mph"|0.0|150.0|10']
    time = 'Interval|"ms"|0|0|1'

    df.loc[df[lat] == 0, lat] = np.nan
    df.loc[df[long] == 0, long] = np.nan
    df[lat] = -df[lat]
    df[long] = -df[long]
    df = df.dropna()
    source = ColumnDataSource(df)
    source.add(df['Interval|"ms"|0|0|1'], name='Time')

    time = 'Interval|"ms"|0|0|1'
    range_slider = RangeSlider(start=min(df[time]), end=max(df[time]),
                               value=(min(df[time]), max(df[time])),
                               step=1, title="Start - End")
    return range_slider

def plot_all(args):
    for file in os.listdir(r'..\\'):
        if file.endswith('.log'):
            logfile = file
            data = rc_data_parse(logfile)
            susp_plot, pt_plot, traction_plot, accel_plot, speed_plot, coord_plot = plot_rcprodata(data, filename=logfile)
            data_table = create_table(data, filename=logfile)

            # sr_logo = plot_image('..\Schulich Racing.png')

            susp_plot.x_range = pt_plot.x_range = accel_plot.x_range = speed_plot.x_range
            range_slider = widgets(data)

            save(column(row(column(traction_plot, accel_plot, pt_plot),
                 column(widgetbox(range_slider), coord_plot, speed_plot, susp_plot)), data_table),
                 filename='{}_{}.html'.format(logfile.split('.')[0], 'plot'))

            print('Finished processing')


# TODO get streaming working https://www.youtube.com/watch?v=NUrhOj3DzYs

# TODO start to look into generating laptimes - user interactivity
#  https://bokeh.pydata.org/en/latest/docs/user_guide/interaction/widgets.html BIG ONE
#  interactivity is most easily done via server code - simple examples found here
#  https://bokeh.pydata.org/en/latest/docs/gallery.html

# TODO return the x/y position of mousepos on left graphs - xpos corresponds to time interval, then highlight the
#  coordinate at that timestamp on coord graph. possibly use
#  https://bokeh.pydata.org/en/latest/docs/user_guide/annotations.html
#  will possibly also use https://bokeh.pydata.org/en/latest/docs/user_guide/tools.html#edit-tools
#  alternately add highlighted column that shows data values on left graphs when hovering on point in scatter
#  plot https://stackoverflow.com/questions/51775589/bokeh-linking-a-line-plot-and-a-scatter-plot
#  selector can use spans https://stackoverflow.com/questions/28797330/infinite-horizontal-line-in-bokeh


if __name__ == "__main__":
    plot_all(sys.argv)
