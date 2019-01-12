import json

import pandas as pd
import redis
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, curdoc

host = "hilmi.ddns.net"
port = 20114
db = 0
password = "schulichracing14"
channel = "main-channel"
r = redis.Redis(
    host=host,
    port=port,
    password=password)
ps = r.pubsub()
ps.subscribe(channel)

LONGITUDE = 'Longitude|"Degrees"|-180.0|180.0|10'
LATITUDE = 'Latitude|"Degrees"|-180.0|180.0|10'
SPEED = 'Speed|"mph"|0.0|150.0|10'
INTERVAL = 'Interval|"ms"|0|0|1'

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

r2 = p.line(x='x', y='y', source=source, color='black', line_width=3)
r1 = p.circle(x='x', y='y', source=live_source, color='firebrick', radius=0.00002)

cur_time = 0
step = 1
prev_laps = 0
lap_length = 0
true_lap = -1
timeout = 0
previous_lat = 0
previous_long = 0


def update():
    global cur_time, step, source, prev_laps, lap_length, true_lap, timeout, previous_lat, previous_long
    coords = dict(x=[], y=[])
    current_lat = 0
    current_long = 0

    message = ps.get_message()  # Checks for message
    if not message or message['data'] == 1:
        print('shit went south')
        pass
    else:
        data = message['data'].decode('utf-8')
        data_string = json.loads(data)
        df = pd.DataFrame(data_string, index=[0])
        try:
            current_long = float(df[LONGITUDE].values[0])
            current_lat = float(df[LATITUDE].values[0])
        except ValueError:
            pass  # failed to convert because values in were null

        if abs(current_long) > 1 and not current_long == previous_long and \
                abs(current_lat) > 1 and not current_lat == previous_lat:
            coords['x'].append(-1 * current_long)
            previous_long = current_long

            coords['y'].append(-1 * current_lat)
            previous_lat = current_lat

        live_source.stream(coords, 1)
        source.stream(coords)

        cur_time += step


curdoc().add_root(p)

curdoc().add_periodic_callback(update, 0)
