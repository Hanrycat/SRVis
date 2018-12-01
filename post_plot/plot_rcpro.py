import sys
import os
import pandas as pd
from bokeh.plotting import figure, output_file, show
from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from datetime import datetime

from bokeh.models.tools import HoverTool


def rc_data_parse(logfile):
    output_file('{}_{}.html'.format(logfile[:-4], datetime.now().strftime('%Y-%m-%d_%H-%M-%S')))

    data = pd.read_csv('..\{}'.format(logfile))
    # data = data.dropna()
    return data


def plot_rcprodata(df):
    susp_source = ColumnDataSource(df)
    df_dna = df.dropna()
    temp_source = ColumnDataSource(df_dna)

    susp = figure(width=1000, plot_height=300, title='Suspension')
    powertrain = figure(width=1000, plot_height=300, title='Powertrain')

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

    susp.legend.click_policy = 'hide'
    powertrain.legend.click_policy = 'hide'

    show(column(susp, powertrain))


def plot_all(args):
    for file in os.listdir(r'..\\'):
        if file.endswith('.log'):
            logfile = file
            data = rc_data_parse(logfile)
            plot_rcprodata(data)


if __name__ == "__main__":
    plot_all(sys.argv)
