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
from bokeh.models import CustomJS, Slider, RadioButtonGroup, RangeSlider
# hv.extension('bokeh')

# List of headers, to access and read data.
TOOLS = 'pan,box_select,box_zoom,wheel_zoom,save,reset'
lat = 'Latitude|"Degrees"|-180.0|180.0|10'
long = 'Longitude|"Degrees"|-180.0|180.0|10'
speed = ['Speed|"mph"|0.0|150.0|10']
time = 'Interval|"ms"|0|0|1'

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


def create_source_df(df):
    df.loc[df[lat] == 0, lat] = np.nan
    df.loc[df[long] == 0, long] = np.nan
    df[lat] = -df[lat]
    df[long] = -df[long]
    df = df.dropna()
    source = ColumnDataSource(df)
    source.add(df['Interval|"ms"|0|0|1'], name='Time')
    print(source)
    print(df)
    return source, df


def create_filtered_source_df(df):
    df.loc[df[lat] == 0, lat] = np.nan
    df.loc[df[long] == 0, long] = np.nan
    df[lat] = -df[lat]
    df[long] = -df[long]
    df = df.dropna()


def plot_rcprodata(source, df, filename):
    global SUSPENSION, POWERTRAIN, ACCELERATION

    # Creating figures for all plots
    susp = figure(output_backend="webgl", tools=TOOLS, sizing_mode='scale_both',
                  width=700, height=300, title='Suspension',
                  x_axis_label='Time')

    powertrain = figure(output_backend="webgl", tools=TOOLS, sizing_mode='scale_both',
                        width=700, height=300, title='Powertrain',
                        x_axis_label='Time')

    accel = figure(output_backend="webgl", tools=TOOLS, sizing_mode='scale_both',
                   width=700, height=300, title='Acceleration',
                   x_axis_label='Time')

    speed_p = figure(output_backend="webgl", tools=TOOLS, sizing_mode='scale_both',
                     width=700, height=300, title='Speed',
                     x_axis_label='Time')

    traction = figure(output_backend="webgl", tools=TOOLS, sizing_mode='scale_both',
                      width=700, height=300, title='Traction',
                      x_axis_label='X accel')

    colors = itertools.cycle(Category20_20)

    # Plotting data to each figure
    plot_data(susp, colors, source, SUSPENSION)
    plot_data(powertrain, colors, source, POWERTRAIN)
    plot_data(accel, colors, source, ACCELERATION)
    plot_data(speed_p, colors, source, speed)
    coord = plot_coords(df, source, filename)
    traction.circle(x='AccelX|"G"|-3.0|3.0|25', y='AccelY|"G"|-3.0|3.0|25',
                    source=source, size=3, color='firebrick')

    # Creating hovertools to hover over specific points
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
    accel.legend.click_policy = 'mute'
    susp.legend.click_policy = 'mute'
    powertrain.legend.click_policy = 'mute'

    return susp, powertrain, traction, accel, speed_p, coord


def plot_data(p, colors, source, header_list):
    global time

    for data_series, color in zip(header_list, colors):
        p.line(x=time, y=data_series,
            line_width=2,
            line_color=color,
            source=source,
            legend=data_series.split('|')[0],
            name=data_series.split('|')[0])


def plot_coords(df, source, filename):
    global lat, long
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

def plot_all(args):
    global time, ACCELERATION, SUSPENSION, POWERTRAIN, long, lat

    for file in os.listdir(r'..\\'):
        if file.endswith('.log'):
            logfile = file
            data = rc_data_parse(logfile)
            source, df = create_source_df(data)
            susp_plot, pt_plot, traction_plot, accel_plot, speed_plot, coord_plot = plot_rcprodata(source, df,
                                                                                                   filename=logfile)
            data_table = create_table(data, filename=logfile)

            # TODO figure out how to do callback function
            callback = CustomJS(args=dict(source=source), code=""""
                            var f = slider.value;
                            console.log(f);
                        """)

            range_slider = RangeSlider(start=min(df[time]), end=max(df[time]), value=(min(df[time]), max(df[time])),
                                       step=40, title="Range Slider")

            slider = Slider(start=range_slider.value[0], end=range_slider.value[1], value=range_slider.value[0],
                            step=4, title="Car Slider", callback=callback)

            callback.args["slider"] = slider
            callback.args["ACCELERATION"] = ACCELERATION
            callback.args["time"] = time
            callback.args["lat"] = lat
            callback.args["long"] = long


            # sr_logo = plot_image('..\Schulich Racing.png')
            susp_plot.x_range = pt_plot.x_range = accel_plot.x_range = speed_plot.x_range

            save(column(row(column(traction_plot, accel_plot, pt_plot),
                 column(widgetbox(slider, range_slider),
                 coord_plot, speed_plot, susp_plot)), data_table),
                 filename='{}_{}.html'.format(logfile.split('.')[0], 'plot'))

            print('Finished processing')

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
