import itertools
import sys
import os
import pandas as pd
import numpy as np
import bokeh.plotting as bk
from bokeh.models import Span
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.plotting import figure, output_file, show
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource
from bokeh.models.tools import HoverTool
from bokeh.palettes import Category20_20  # suppress unresolved import
from bokeh.transform import linear_cmap
from datetime import datetime

from common.plotting_common import plot_image, create_table


# TODO move finalized code to common.plotting_common.
#  Only code that is specific to post_processing log files for
#  subteam analysis should live here

# instructions and explanations be found here https://programminghistorian.org/en/lessons/visualizing-with-bokeh
# https://bokeh.pydata.org/en/latest/docs/user_guide.html
# https://pandas.pydata.org/pandas-docs/stable/index.html

def rc_data_parse(logfile):
    # TODO this is final output - iterable
    # output_file('{}_{}.html'.format(logfile[:-4], datetime.now().strftime('%Y-%m-%d_%H-%M-%S')))
    # TODO use this one during testing
    # output_file('{}_{}.html'.format(logfile[:-4], 'test'))

    data = pd.read_csv('..\{}'.format(logfile))
    data = data.fillna(method='ffill')

    # data = data.dropna()
    return data


# TODO split so that each subteams data can be pulled by calling this function with seperate args
def plot_rcprodata(df, filename):
    susp_source = ColumnDataSource(df)
    temp_source = ColumnDataSource(df)
    accel_source = ColumnDataSource(df)

    susp = figure(sizing_mode='scale_both', width=700, height=300, title='Suspension_{}'.format(filename),
                  x_axis_label='Time')
    powertrain = figure(sizing_mode='scale_both', width=700, height=300, title='Powertrain_{}'.format(filename),
                        x_axis_label='Time')
    accel = figure(sizing_mode='scale_both', width=700, height=300, title='Accel_{}'.format(filename),
                   x_axis_label='X', y_axis_label='Y')
    traction = figure(sizing_mode='scale_both', width=700, height=300, title='Traction Circle{}'.format(filename),
                      x_axis_label='X', y_axis_label='Y')

    # TODO figure out color palletes https://bokeh.pydata.org/en/latest/docs/reference/palettes.html
    # create a color iterator
    colors = itertools.cycle(Category20_20)

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
    # print(susp_source.column_names)
    time = 'Interval|"ms"|0|0|1'
    for data_series, color in zip(SUSPENSION, colors):
        susp.line(x=time, y=data_series,
                  line_width=2,
                  line_color=color,
                  source=susp_source,
                  legend=data_series.split('|')[0],
                  name=data_series.split('|')[0])
    for data_series, color in zip(POWERTRAIN, colors):
        powertrain.line(x=time, y=data_series,
                        line_width=2,
                        line_color=color,
                        source=temp_source,
                        legend=data_series.split('|')[0],
                        name=data_series.split('|')[0])
    for data_series, color in zip(ACCELERATION, colors):
        accel.line(x=time, y=data_series,
                   line_width=1,
                   line_color=color,
                   source=accel_source,
                   legend=data_series.split('|')[0],
                   name=data_series.split('|')[0])
    traction.circle(x='AccelX|"G"|-3.0|3.0|25', y='AccelY|"G"|-3.0|3.0|25', source=accel_source, size=3,
                    color='firebrick')
    hover = HoverTool()
    susp_hover = HoverTool()
    powertrain_hower = HoverTool()

    susp_hover.tooltips = [
        ('Data', '$name'),
        ('Time (MS)', '$x{0.}'),
        ('Volts', '$y{0.000}')
    ]

    powertrain_hower.tooltips = [
        ('Data', '$name'),
        ('Time (MS)', '$x{0.}'),
        ('Pressure/Temp', '$y{0.000}')
    ]
    #
    # hover.tooltips = [
    #     ('x', '$x{0.}'),
    #     ('y', '$y{0.000}')
    # ]

    susp.sizing_mode = 'scale_width'
    powertrain.sizing_mode = 'scale_width'
    susp.add_tools(susp_hover)
    powertrain.add_tools(powertrain_hower)
    susp.legend.click_policy = 'hide'
    powertrain.legend.click_policy = 'hide'

    # TODO decide if we want this behaviour
    # show(column(susp, powertrain))
    return susp, powertrain, traction, accel


def plot_coords(df, filename):
    lat = 'Latitude|"Degrees"|-180.0|180.0|10'
    long = 'Longitude|"Degrees"|-180.0|180.0|10'
    speed = 'Speed|"mph"|0.0|150.0|10'
    df.loc[df[lat] == 0, lat] = np.nan
    df.loc[df[long] == 0, long] = np.nan
    coord_source = ColumnDataSource(df)
    coord_source.add(df['Interval|"ms"|0|0|1'], name='Time')

    coord = figure(sizing_mode='scale_both', width=700, height=600, title='GPS Data_{}'.format(filename))

    # TODO figure out why this is broken
    # mapper = linear_cmap(field_name='Speed"|"mph"|0.0|150.0|10', palette=Spectral6, low=min(speed), high=max(speed))

    coord.circle(x=lat, y=long, source=coord_source, size=3, color='darkcyan')

    # TODO figure out how to make the points be connected
    # coord.line(x=lat, y=long, source=coord_source, line_width=2, color='red')

    # Tools
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
    for file in os.listdir(r'..\\'):
        if file.endswith('.log'):
            logfile = file
            data = rc_data_parse(logfile)
            susp_plot, pt_plot, traction_plot, accel_plot = plot_rcprodata(data, filename=logfile)
            coord_plot = plot_coords(data, filename=logfile)
            data_table = create_table(data, filename=logfile)
            # sr_logo = plot_image('..\Schulich Racing.png')

            # TODO decide if we want this behaviour
            show(column(row(column(traction_plot, accel_plot, pt_plot), column(coord_plot, susp_plot)), data_table))
            print('Finished processing')


# TODO see if scatter plot can be represented with a smoothed connected line - look into averaging techniques for
#  track mapping

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
