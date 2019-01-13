import json

import pandas as pd
import redis
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, curdoc
from bokeh.driving import linear
import random
import datetime as dt
import numpy as np
import pandas as pd


csv_data = pd.read_csv('Endurance Luke Driving June 23 18.csv')
csv_data = csv_data.dropna()

csv_data = csv_data.reset_index(drop=False)

csv_x = csv_data['Longitude|"Degrees"|-180.0|180.0|10'] * -1
# csv_x.loc[pd['Longitude|"Degrees"|-180.0|180.0|10'] == 0, 'Longitude|"Degrees"|-180.0|180.0|10'] = np.nan
csv_y = csv_data['Latitude|"Degrees"|-180.0|180.0|10'] * -1
# csv_y.loc[pd['Latitude|"Degrees"|-180.0|180.0|10'] == 0, 'Latitude|"Degrees"|-180.0|180.0|10'] = np.nan
csv_times = csv_data['Interval|"ms"|0|0|1']
csv_speed = csv_data['Speed|"mph"|0.0|150.0|10']

source = ColumnDataSource(dict(
    x=[], y=[], color=[]
))


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

track_source = ColumnDataSource(dict(
    x=[], y=[]
))

car_source = ColumnDataSource(dict(
    x=[], y=[]
))

p = figure(sizing_mode='scale_both', plot_width=800, plot_height=700)

r2 = p.circle(x='x', y='y', source=source, color='color', radius=0.00002)
# r3 = p.circle(x='x', y='y', source=centroid_source, color='navy', radius=0.00002)
# r4 = p.circle(x='x', y='y', source=start_finish, color='green', alpha=0.5, line_color='black', radius=0.00002)
r1 = p.circle(x='x', y='y', source=live_source, color='firebrick', radius=0.00002)

r2 = p.line(x='x', y='y', source=track_source, color='black', line_width=3)
r1 = p.circle(x='x', y='y', source=car_source, color='firebrick', radius=0.00002)

cur_time = 0
step = 1
prev_laps = 0
lap_length = 0
true_lap = -1
timeout = 0
top_speed = 1


def update():
    global cur_time, step, source, prev_laps, lap_length, true_lap, timeout, top_speed
    ds1 = dict(x=[], y=[], color=[])
    ds2 = dict(x=[], y=[])
    ds3 = dict(x=[], y=[])
    ds4 = dict(x=[], y=[])

    ds1['x'].append(csv_x[cur_time])
    ds1['y'].append(csv_y[cur_time])

    a, b = get_color_from_speed(csv_speed[cur_time], top_speed)
    top_speed = b
    ds1['color'].append(a)

    ds2['x'].append(csv_x[cur_time])
    ds2['y'].append(csv_y[cur_time])
    cur_time += step
    # if lap_length != 0:
    #     source.stream(ds1,lap_length)
    # else:
    source.stream(ds1)
    live_source.stream(ds2, 1)

    # ds3['x'].append(centroidnp(np.asarray(csv_x[:cur_time])))
    # ds3['y'].append(centroidnp(np.asarray(csv_y[:cur_time])))
    # centroid_source.stream(ds3, 1)

    if cur_time >= csv_times.__len__():
        sys.exit()
    # laps, crossings = check_lapcounter(source, cur_time)
    # if abs(laps - prev_laps) == 1 and timeout > 200:
    #     timeout = 0
    #     if laps > 0:
    #         true_lap = true_lap + 1
    #         print('Lap {}: {}'.format(true_lap, ((crossings[laps - 1][0]) - (crossings[laps - 2][0])) / 1000))
    #         lap_length = int(((crossings[laps - 1][0]) - (crossings[laps - 2][0])) / 50)
    # prev_laps = laps
    # timeout += 1

    # ds4['x'].append((crossings[laps - 1][1]))
    # ds4['y'].append((crossings[laps - 1][2]))
    # start_finish.stream(ds4, 20)
previous_lat = 0
previous_long = 0


def update():
    global cur_time, step, previous_lat, previous_long
    coords = dict(x=[], y=[])
    current_lat = 0
    current_long = 0

    message = ps.get_message()  # Checks for message
    if not message or message['data'] == 1:
        print(r'Shit\'s fucked, yo! Message was: {}'.format(message))
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

        track_source.stream(coords)
        car_source.stream(coords, 1)

        cur_time += step


curdoc().add_root(p)

# Add a periodic callback to be run every 500 milliseconds
curdoc().add_periodic_callback(update, 80)


def is_left(x1, y1, x2, y2, x3, y3):
    return ((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))


def get_color_from_speed(speed, top_speed):

    if speed > 70:
        return 'ff0000', top_speed
    if speed > top_speed:
        top_speed = speed
    ratio = int(round(((2 * speed) / top_speed) * 255))

    if (2 * speed) < top_speed:
        r = 'ff'
        g = hex(ratio).split('x')[-1]
    elif 2 * speed > top_speed:
        r = hex(255 - ratio).split('x')[-1]
        g = 'ff'
    else:
        r = 'ff'
        g = 'ff'

    color_value = ''
    color_value += ('#' + r + g + '00')
    print(color_value)
    return color_value, top_speed
#
# def centroidnp(arr):
#     length = arr.shape[0]
#     sum = np.sum(arr[:])
#     return sum / length
#
#
# def check_lapcounter(data, cur_time):
#     x = data.data['x']
#     y = data.data['y']
#     # if cur_time < 620: #approx 10 seconds
#     #     cx = x[0]
#     #     cy = y[0]
#     # else:
#     #     cx = centroidnp(np.asarray(csv_x[:cur_time])) #TODO avoid hardcoding
#     #     cy = centroidnp(np.asarray(csv_y[:cur_time]))
#     cx = 96.769  # functional centroid
#     cy = -40.8455
#     # cx = 96.768 #trueish centroid
#     # cy = -40.84575
#
#     laps = -1
#     crossings = [(csv_times[0], csv_x[0], csv_y[0])]
#     for i in range(0, x.__len__() - 1):
#         if y[i] <= cy:
#             if (y[i + 1] > cy):
#                 if (is_left(x[i], y[i], x[i + 1], y[i + 1], cx, cy) > 0):
#                     laps = laps + 1
#                     crossings.append((csv_times[i], x[i], y[i]))
#
#         else:
#             if (y[i + 1] <= cy):
#                 if (is_left(x[i], y[i], x[i + 1], y[i + 1], cx, cy) < 0):
#                     laps = laps - 1
#                     crossings.append((csv_times[i], x[i], y[i]))
#     return abs(laps), crossings
=======
curdoc().add_periodic_callback(update, 0)

