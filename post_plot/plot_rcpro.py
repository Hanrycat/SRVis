import sys
import os
import pandas as pd
from bokeh.plotting import figure, output_file, show
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource
from bokeh.palettes import Spectral6
from bokeh.transform import linear_cmap
from datetime import datetime

from bokeh.models.tools import HoverTool


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

    susp = figure(width=1000, plot_height=300, title='Suspension')
    powertrain = figure(width=1000, plot_height=300, title='Powertrain')

    # TODO modularize column names
    # Ideally we want this to be
    # for data_series in subteam
    #   subteam.line(x=time, y=data_series_header, etc) with automatic color generation

    # TODO figure out color palletes https://bokeh.pydata.org/en/latest/docs/reference/palettes.html
    susp.line(x='Interval|"ms"|0|0|1', y='RearRight|""|0.0|5.0|50',
              line_width=2,
              line_color="red",
              source=susp_source,
              legend='RearRight')
    susp.line(x='Interval|"ms"|0|0|1', y='RearLeft|""|0.0|5.0|50',
              line_width=2,
              line_color="orange",
              source=susp_source,
              legend='RearLeft')
    susp.line(x='Interval|"ms"|0|0|1', y='FrontLeft|""|0.0|5.0|50',
              line_width=2,
              line_color="yellow",
              source=susp_source,
              legend='FrontLeft')
    susp.line(x='Interval|"ms"|0|0|1', y='FrontRight|""|0.0|5.0|50',
              line_width=2,
              line_color="blue",
              source=susp_source,
              legend='FrontRight')
    powertrain.line(x='Interval|"ms"|0|0|1', y='EngineTemp|"C"|0|200|1',
                    line_width=2,
                    line_color="navy",
                    source=temp_source,
                    legend='EngineTemp')
    powertrain.line(x='Interval|"ms"|0|0|1', y='OilPressure|"psi"|0.0|200.0|50',
                    line_width=2,
                    line_color="firebrick",
                    source=temp_source,
                    legend='OilPressure')
    powertrain.line(x='Interval|"ms"|0|0|1', y='OilTemp|"F"|0|300|1',
                    line_width=2,
                    line_color="aqua",
                    source=temp_source,
                    legend='OilTemp')
    powertrain.line(x='Interval|"ms"|0|0|1', y='FuelTemp|"C"|0|1024|1',
                    line_width=2,
                    line_color="green",
                    source=temp_source,
                    legend='FuelTemp')

    hover = HoverTool()
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

    coord = figure(width=1000, plot_height=600, title='GPS Data')
    lat = 'Latitude|"Degrees"|-180.0|180.0|10'
    long = 'Longitude|"Degrees"|-180.0|180.0|10'
    speed = 'Speed"|"mph"|0.0|150.0|10'
    # TODO figure out why this is broken
    # mapper = linear_cmap(field_name='Speed"|"mph"|0.0|150.0|10', palette=Spectral6, low=min(speed), high=max(speed))
    coord.circle(x=lat, y=long, source=coord_source, size=2, color='purple')

    hover = HoverTool()
    hover.tooltips = [
        ('x', '$x{0.}'),
        ('y', '$y{0.000}')
    ]

    coord.add_tools(hover)
    return coord


def plot_all(args):
    for file in os.listdir(r'..\\'):
        if file.endswith('.log'):
            logfile = file
            data = rc_data_parse(logfile)
            susp_plot, pt_plot = plot_rcprodata(data)
            coord_plot = plot_coords(data)
            # TODO decide if we want this behaviour
            show(row(column(susp_plot, pt_plot), coord_plot))



# TODO see if scatter plot can be represented with a smoothed connected line - look into averaging techniques for track mapping
# TODO get streaming working https://www.youtube.com/watch?v=NUrhOj3DzYs
# TODO start to look into generating laptimes - user interactivity
# TODO add highlighted column that shows data values on left graphs when hovering on point in scatter plot


# https://programminghistorian.org/en/lessons/visualizing-with-bokeh

if __name__ == "__main__":
    plot_all(sys.argv)
