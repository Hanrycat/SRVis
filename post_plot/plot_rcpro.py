import itertools
import sys
import os
import pandas as pd
from bokeh.plotting import figure, output_file, show
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource
from bokeh.models.tools import HoverTool
from bokeh.palettes import Category20 #suppress unresolved import for now
from bokeh.transform import linear_cmap
from datetime import datetime

from common.plotting_common import plot_image


# TODO move finalized code to common.plotting_common.
#  Only code that is specific to post_processing log files for
#  subteam analysis should live here
# instructions and explanations be found here https://programminghistorian.org/en/lessons/visualizing-with-bokeh
def rc_data_parse(logfile):
    # TODO this is final output - iterable
    # output_file('{}_{}.html'.format(logfile[:-4], datetime.now().strftime('%Y-%m-%d_%H-%M-%S')))
    # TODO use this one during testing
    output_file('{}_{}.html'.format(logfile[:-4], 'test'))

    data = pd.read_csv('..\{}'.format(logfile))
    # data = data.dropna()
    return data


# TODO split so that each subteams data can be pulled by calling this function with seperate args
def plot_rcprodata(df):
    susp_source = ColumnDataSource(df)
    df_dna = df.dropna()
    temp_source = ColumnDataSource(df_dna)

    susp = figure(width=900, plot_height=300, title='Suspension')
    powertrain = figure(width=900, plot_height=300, title='Powertrain')

    # TODO modularize column names
    # Ideally we want this to be
    # for data_series in subteam
    #   subteam.line(x=time, y=data_series_header, etc) with automatic color generation

    # TODO figure out color palletes https://bokeh.pydata.org/en/latest/docs/reference/palettes.html
    # create a color iterator
    colors = itertools.cycle(Category20)

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
    # print(susp_source.column_names)
    time = 'Interval|"ms"|0|0|1'
    for data_series, color in zip(SUSPENSION, colors):
        susp.line(x=time, y=data_series,
                  line_width=2,
                  line_color=color,
                  source=susp_source,
                  legend=data_series.split('|')[0])
    for data_series, color in zip(POWERTRAIN, colors):
        powertrain.line(x=time, y=data_series,
                        line_width=2,
                        line_color=color,
                        source=temp_source,
                        legend=data_series.split('|')[0])

    hover = HoverTool()
    # TODO figure out how to get the tooltips to show like this
    # x=1323
    # rearleft=2.213
    # rearright=2.421
    # frontleft=4.211
    # frontright=4.653
    hover.tooltips = [
        ('x', '$x{0.}'),
        ('y', '$y{0.000}')
    ]

    susp.add_tools(hover)
    powertrain.add_tools(hover)
    susp.legend.click_policy = 'hide'
    powertrain.legend.click_policy = 'hide'

    # TODO decide if we want this behaviour
    # show(column(susp, powertrain))
    return susp, powertrain


def plot_coords(df):
    coord_source = ColumnDataSource(df)

    coord = figure(width=900, plot_height=600, title='GPS Data')
    lat = 'Latitude|"Degrees"|-180.0|180.0|10'
    long = 'Longitude|"Degrees"|-180.0|180.0|10'
    speed = 'Speed"|"mph"|0.0|150.0|10'
    # TODO figure out why this is broken
    # mapper = linear_cmap(field_name='Speed"|"mph"|0.0|150.0|10', palette=Spectral6, low=min(speed), high=max(speed))
    coord.circle(x=lat, y=long, source=coord_source, size=3, color='darkcyan')

    # TODO figure out how to make the points be connected
    # coord.line(x=lat, y=long, source=coord_source, line_width=2, color='red')

    coord_source.add(df['Interval|"ms"|0|0|1'], name='Time')
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
            susp_plot, pt_plot = plot_rcprodata(data)
            coord_plot = plot_coords(data)

            sr_logo = plot_image('..\Schulich Racing.png')

            # TODO decide if we want this behaviour
            show(row(column(susp_plot, pt_plot, sr_logo), coord_plot))


# TODO see if scatter plot can be represented with a smoothed connected line - look into averaging techniques for
#  track mapping
# TODO get streaming working https://www.youtube.com/watch?v=NUrhOj3DzYs
# TODO start to look into generating laptimes - user interactivity
#  interactivity is most easily done via server code - simple examples found here
#  https://bokeh.pydata.org/en/latest/docs/gallery.html
# TODO return the x/y position of mousepos on left graphs - xpos corresponds to time interval, then highlight the
#  coordinate at that timestamp on coord graph. possibly use
#  https://bokeh.pydata.org/en/latest/docs/user_guide/annotations.html
#  will possibly also use https://bokeh.pydata.org/en/latest/docs/user_guide/tools.html#edit-tools
#  alternately add highlighted column that shows data values on left graphs when hovering on point in scatter
#  plot https://stackoverflow.com/questions/51775589/bokeh-linking-a-line-plot-and-a-scatter-plot


if __name__ == "__main__":
    plot_all(sys.argv)
