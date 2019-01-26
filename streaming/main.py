import json
import pandas as pd
import redis
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row

host = "hilmi.ddns.net"
port = 20279
db = 0
password = "schulichracing14"
channel = "endurance-channel"
redis = redis.Redis(
    host=host,
    port=port,
    password=password)
ps = redis.pubsub()
ps.subscribe(channel)

LONGITUDE = 'Longitude'
LATITUDE = 'Latitude'
SPEED = 'Speed'
INTERVAL = 'Interval'
ACCEL_X = 'AccelX'
ACCEL_Y = 'AccelY'
TOOLS = 'pan,box_select,box_zoom,wheel_zoom,save,reset'

# List of headers that correspond to each subteams data
SUSPENSION = [
    'RearRight',
    'RearLeft',
    'FrontLeft',
    'FrontRight'
]
POWERTRAIN = [
    'EngineTemp',
    'OilPressure',
    'OilTemp',
    'FuelTemp'
]
ACCELERATION = [
    'AccelX',
    'AccelY',
    'AccelZ'
]

track_source = ColumnDataSource(dict(
    long=[], lat=[], color=[]
))

car_source = ColumnDataSource(dict(
    long=[], lat=[], color=[]
))

track_source2 = ColumnDataSource(dict(
    accel_x=[], accel_y=[]
))

car_source2 = ColumnDataSource(dict(
    accel_x=[], accel_y=[]
))

track_source3 = ColumnDataSource(dict(
    time=[], rr=[], rl=[], fl=[], fr=[]
))

track_source4 = ColumnDataSource(dict(
    time=[], mph=[]
))

coords_f = figure(output_backend="webgl", tools=TOOLS, sizing_mode='scale_both', plot_width=700, plot_height=700)
coords_track = coords_f.circle(x='long', y='lat', source=track_source, color='color',     radius=0.00002)
# r2 = coords_f.line(x='x', y='y', source=track_source, color='black', line_width=3)  # Line traced track
coords_car = coords_f.circle(  x='long', y='lat', source=car_source,   color='firebrick', radius=0.00002)

traction_f = figure(output_backend="webgl", tools=TOOLS, x_range=(-2, 2), y_range=(-1.5, 1.5), plot_width=700, plot_height=400)
traction_car = traction_f.circle(x='accel_x',   y='accel_y', source=car_source2,   color='blue', radius=0.05)
traction_track = traction_f.circle(x='accel_x', y='accel_y', source=track_source2, color='red',  radius=0.02)

susp_f = figure(output_backend="webgl", sizing_mode='scale_both', plot_width=700, plot_height=400)
susp_track_rr = susp_f.line(x='time', y='rr', source=track_source3, color='red',    line_width=1)
susp_track_rl = susp_f.line(x='time', y='rl', source=track_source3, color='green',  line_width=1)
susp_track_fl = susp_f.line(x='time', y='fl', source=track_source3, color='blue',   line_width=1)
susp_track_fr = susp_f.line(x='time', y='fr', source=track_source3, color='yellow', line_width=1)


speed_f = figure(output_backend="webgl", sizing_mode='scale_both', plot_width=700, plot_height=400)
speed_track = speed_f.line(x='time', y='mph', source=track_source4, color='black', line_width=3)

cur_time = 0
step = 1
top_speed = 1
previous_lat = 0
previous_long = 0
hypothetical_max_speed = 70


def update():
    global cur_time, step, previous_lat, previous_long, top_speed
    coords = dict(long=[], lat=[], color=[])
    traction = dict(accel_x=[], accel_y=[])
    susp = dict(time=[], rr=[], rl=[], fl=[], fr=[])
    speed = dict(time=[], mph=[])

    current_lat = 0
    current_long = 0
    current_speed = 0

    current_accel_x = 0
    current_accel_y = 0
    current_accel_z = 0

    current_rr_susp = 0
    current_rl_susp = 0
    current_fl_susp = 0
    current_fr_susp = 0

    message = ps.get_message()  # Checks for message

    if not message or message['data'] == 1:
        print(r'Shit is fucked, yo! Message was: {}'.format(message))
        pass
    else:
        data = message['data'].decode('utf-8')
        data_string = json.loads(data)
        df = pd.DataFrame(data_string, index=[0])
        try:
            #time
            current_interval = float(df[INTERVAL].values[0])

            #coords
            current_long = float(df[LONGITUDE].values[0])
            current_lat = float(df[LATITUDE].values[0])
            current_speed = float(df[SPEED].values[0])

            #accels
            current_accel_x = float(df[ACCELERATION[0]].values[0])
            current_accel_y = float(df[ACCELERATION[1]].values[0])
            current_accel_z = float(df[ACCELERATION[2]].values[0])

            #susps
            current_rr_susp = float(df[SUSPENSION[0]].values[0])
            current_rl_susp = float(df[SUSPENSION[1]].values[0])
            current_fl_susp = float(df[SUSPENSION[2]].values[0])
            current_fr_susp = float(df[SUSPENSION[3]].values[0])

            #speed
            current_speed = float(df[SPEED].values[0])

        except (ValueError, TypeError):
            # print(message)
            pass  # failed to convert because values in were null

        if abs(current_long) > 1 and not current_long == previous_long and \
                abs(current_lat) > 1 and not current_lat == previous_lat:
            coords['long'].append(-1 * current_long)
            previous_long = current_long

            coords['lat'].append(-1 * current_lat)
            previous_lat = current_lat

            current_color, new_max = get_color_from_speed(current_speed, top_speed)
            top_speed = new_max
            coords['color'].append(current_color)

        if (current_accel_y != 0) and (current_accel_x != 0):
            traction['accel_x'].append(current_accel_x)
            traction['accel_y'].append(current_accel_y)


        if current_rr_susp != 0:
            susp['rr'].append(current_rr_susp)
        if current_rl_susp != 0:
            susp['rl'].append(current_rl_susp)
        if current_fl_susp != 0:
            susp['fl'].append(current_fl_susp)
        if current_fr_susp != 0:
            susp['fr'].append(current_fr_susp)
        susp['time'].append(current_interval)

        if current_speed != 0:
            speed['mph'].append(current_speed)
            speed['time'].append(current_interval)

        track_source.stream(coords)
        car_source.stream(coords, 1)

        track_source2.stream(traction)
        car_source2.stream(traction, 1)

        track_source3.stream(susp)

        track_source4.stream(speed)

        cur_time += step
        val = track_source3
        print('val is {}'.format(val))


curdoc().add_root(column(row(column(traction_f, susp_f),
                  column(coords_f, speed_f))))
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
