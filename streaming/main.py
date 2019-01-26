import json
import pandas as pd
import redis
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, curdoc

host = "hilmi.ddns.net"
port = 20279
db = 0
password = "schulichracing14"
channel = "main-channel"
redis = redis.Redis(
    host=host,
    port=port,
    password=password)
ps = redis.pubsub()
ps.subscribe(channel)

LONGITUDE = 'Longitude|"Degrees"|-180.0|180.0|10'
LATITUDE = 'Latitude|"Degrees"|-180.0|180.0|10'
SPEED = 'Speed|"mph"|0.0|150.0|10'
INTERVAL = 'Interval|"ms"|0|0|1'
ACCEL_X = 'AccelX|"G"|-3.0|3.0|25'
ACCEL_Y = 'AccelY|"G"|-3.0|3.0|25'

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
    'FuelTemp|"C"|0|1024|1'
]
ACCELERATION = [
    'AccelX|"G"|-3.0|3.0|25',
    'AccelY|"G"|-3.0|3.0|25',
    'AccelZ|"G"|-3.0|3.0|25'
]

track_source = ColumnDataSource(dict(
    x=[], y=[], color=[]
))

car_source = ColumnDataSource(dict(
    x=[], y=[], color=[]
))

coords_f = figure(sizing_mode='scale_both', plot_width=700, plot_height=700)
r2 = coords_f.circle(x='x', y='y', source=track_source, color='color', radius=0.00002)
# r2 = coords_f.line(x='x', y='y', source=track_source, color='black', line_width=3)  # Line traced track
r1 = coords_f.circle(x='x', y='y', source=car_source, color='firebrick', radius=0.00002)

traction_f = figure(sizing_mode='scale_both', plot_width=700, plot_height=400)
traction_car = traction_f.circle(x='x', y='y', source=car_source, color='blue', radius=0.01)
traction_track = traction_f.circle(x='x', y='y', source=track_source, color='red', radius=0.02)

cur_time = 0
step = 1
top_speed = 0
previous_lat = 0
previous_long = 0
hypothetical_max_speed = 70


def update():
    global cur_time, step, previous_lat, previous_long, top_speed
    coords = dict(x=[], y=[], color=[])
    traction = dict(x=[], y=[], color=[])
    current_lat = 0
    current_long = 0
    current_speed = 0

    current_accel_x = 0
    current_accel_y = 0
    # current_accel_z = 0

    message = ps.get_message()  # Checks for message

    if not message or message['data'] == 1:
        print(r'Shit is fucked, yo! Message was: {}'.format(message))
        pass
    else:
        data = message['data'].decode('utf-8')
        data_string = json.loads(data)
        df = pd.DataFrame(data_string, index=[0])
        try:
            #coords
            current_long = float(df[LONGITUDE].values[0])
            current_lat = float(df[LATITUDE].values[0])
            current_speed = float(df[SPEED].values[0])

            #accels
            # current_accel_x = float(df[ACCEL_X].values[0])
            # current_accel_y = float(df[ACCEL_Y].values[0])
            # current_accel_z = float(df[ACCEL_Z].values[0])

        except (ValueError, TypeError):
            # print(message)
            pass  # failed to convert because values in were null

        if abs(current_long) > 1 and not current_long == previous_long and \
                abs(current_lat) > 1 and not current_lat == previous_lat:
            coords['x'].append(-1 * current_long)
            previous_long = current_long

            coords['y'].append(-1 * current_lat)
            previous_lat = current_lat

            current_color, new_max = get_color_from_speed(current_speed, top_speed)
            top_speed = new_max
            coords['color'].append(current_color)

        # traction['x'].append(current_accel_x)
        # traction['y'].append(current_accel_y)
        # traction['color'].append('red')

        track_source.stream(coords)
        car_source.stream(coords, 1)

        track_source.stream(traction)
        car_source.stream(traction, 1)

        cur_time += step


curdoc().add_root(coords_f)
# curdoc().add_root(traction_f)
curdoc().add_periodic_callback(update, 0)



def get_color_from_speed(speed, current_top_speed):
    if speed > hypothetical_max_speed:
        return 'ff0000', current_top_speed
    if speed > current_top_speed:
        current_top_speed = speed
    ratio = int(round(((2 * speed) / current_top_speed) * 255))

    if (2 * speed) < current_top_speed:
        r = 'ff'
        g = hex(ratio).split('x')[-1]
    elif 2 * speed > current_top_speed:
        r = hex(255 - ratio).split('x')[-1]
        g = 'ff'
    else:
        r = 'ff'
        g = 'ff'

        #yeet

    color_value = ''
    color_value += ('#' + r + g + '00')
    return color_value, current_top_speed
#
# within update():
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
#
# def is_left(x1, y1, x2, y2, x3, y3):
#     return (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
#
# def centroidnp(arr):
#     length = arr.shape[0]
#     sum = np.sum(arr[:])
#     return sum / length
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
