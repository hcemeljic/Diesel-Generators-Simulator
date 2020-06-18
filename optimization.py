import pandas as pd
import sqlite3
import numpy as np
from random import randint
import time
import matplotlib.pyplot as plt

timer = time.time()
con = sqlite3.connect('d:/temp/duplicates5.sqlite')
query2 = 'SELECT "TOTAL POWER" AS TOT_POW, "REQUIRED ENGINES" AS ENGINES, "Time", "DG1 POWER [%]" AS DG1, "DG2 POWER [%]" AS DG2, "DG3 POWER [%]" AS DG3,"DG4 POWER [%]" AS DG4,"DG5 POWER [%]" AS DG5 from Engine_Room_Database LIMIT 200 OFFSET 18050'   #LIMIT 2000 OFFSET 47000, limit 30770 offset 18050 za vidjeti start i stop, 200 18050 za start, 200 753100 za start, 25500 OFFSET 3055005 za 4,3,4,3,4
query5 = 'SELECT "TOTAL POWER" AS TOT_POW, "Time", "DG1 POWER [%]" AS DG1, "DG5 POWER [%]" AS DG5 from Engine_Room_Database LIMIT 200'   # JAK TRIPPING NA 1750000,  LIMIT 6000 OFFSET 1750000 za tripping, LIMIT 2250 OFFSET 1750000 za razvijati funkciju
df = pd.DataFrame(pd.read_sql_query(query2, con))
power_list = df[['TOT_POW', 'Time']].to_numpy()

start_limit = 91  # Given in [%]    def 85, comm: 80
start_time = 15  # Given in [s]     def 15, comm:  10
stop_limit = 69  # Given in [%]      def 71, comm: 70
stop_time = 650  # Given in [s]      def 1599, comm: 200
current_engines_online = 2  # At the beginning of the simulation two engines are running.
starting_in = 0  # Used to prevent starting more than one engine at the time.
stopping_in = 0  # Used to prevent stopping more than one engine at the time.
reset_start_limit = start_limit  # Reset of a local variable inside a function.
reset_start_time = start_time  # Reset of a local variable inside a function.
reset_stop_limit = stop_limit  # Reset of a local variable inside a function.
reset_stop_time = stop_time  # Reset of a local variable inside a function.
reset_ignore_time = starting_in  # Reset of a local variable inside a function.
ramping_up = 0  # Trigger for ramp up when an engine comes online.
ramp_up_plus_chunk = 0  # Chunks by which the engine is ramped up when it comes online.
ramp_up_minus_chunk = 0  # Chunks by which the running engines are ramped down when a new engine comes online.
ramp_down_plus_chunk = 0  # Chunks by which the engines are ramped up when an engine goes offline.
ramp_down_minus_chunk = 0  # Chunks by which the engine is ramped down when it goes offline.
offline_ramping = False  # Trigger for ramping when an engine goes offline.
change_no_engines = 0  # Counts how many times the number of online engines has changed.
running_hours = 0  # Total combined running hours.
consumed = 0  # Total fuel consumed by all of the engines.
bins = 16  # Used for histograms below.
high_load_detected = False
high_load_counter = 0
load_list = [0.1, 10, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 100]
consumption_per_h_gallons = [0, 21.9, 32.5, 38.0, 43.5, 49.25, 55.0, 60.95, 66.9, 72.95,
                             79.0,  84.75, 90.5, 96.4, 102.5, 108.2, 113.9, 124.6]


def engines_online(__self__):
    global current_engines_online
    online = current_engines_online
    return online


def estimate_load_per_engine(total_power_in_kw):
    return round(total_power_in_kw / current_engines_online / 1830 * 100, 2)


def count_to_start(load):
    global start_time, starting_in, current_engines_online, ramping_up
    if load > start_limit and starting_in == 0:
        start_time = start_time - 1
        if start_time < 0:
            start_time = reset_start_time
            starting_in = randint(40, 87)
            return 'ENGINE ' + str(current_engines_online+1)
        else:
            return start_time
    elif starting_in != 0:
        starting_in = starting_in - 1
        if starting_in == 0:
            current_engines_online = current_engines_online + 1
            ramping_up = 40
            return starting_in
        else:
            return 'ONLINE IN: ' + str(starting_in)
    else:
        start_time = reset_start_time
        return np.nan


def count_to_stop(engine_power):
    global stop_time, stopping_in, current_engines_online, offline_ramping
    if engine_power / (online_engines - 1) / 1830.0 * 100.0 <= stop_limit and stopping_in == 0:
        stop_time = stop_time - 1
        if stop_time < 0:
            stop_time = reset_stop_time
            stopping_in = 20
            return 'ENGINE ' + str(current_engines_online)
        else:
            return stop_time
    elif stopping_in != 0:
        stopping_in = stopping_in - 1
        if stopping_in == 0:
            current_engines_online = current_engines_online - 1
            return stopping_in
        else:
            offline_ramping = True
            return 'OFFLINE IN: ' + str(stopping_in)
    else:
        stop_time = reset_stop_time
        offline_ramping = False
        return np.nan


def each_engine_load(engines):
    engines_matrix = np.zeros((1, 5))
    engines_matrix[0][0] = round(mean_load_per_engine, 3)
    for j in range(1, engines):
        engines_matrix[0][j] = round(mean_load_per_engine, 3)
    return engines_matrix


def online_ramp_up(engines):
    global ramping_up, ramp_up_plus_chunk
    pct_per_sec = round(engines[0][current_engines_online - 1] / 20, 3)
    if ramping_up == 0:
        ramp_up_plus_chunk = 0
        pass
    else:
        ramp_up_plus_chunk = ramp_up_plus_chunk + pct_per_sec
        engines[0][current_engines_online - 1] = ramp_up_plus_chunk
        ramping_up = ramping_up - 1
        return round(ramp_up_plus_chunk, 3)


def online_ramp_down(engines):
    global ramping_up, ramp_up_minus_chunk
    if ramping_up == 0 or ramping_up == 39:
        ramp_up_minus_chunk = 0
        pass
    else:
        ramping_up = ramping_up - 1
        load_difference = ((mean_load_per_engine * current_engines_online) /
                           (current_engines_online - 1)) - engines[0][0]
        ramp_up_minus_chunk = ramp_up_minus_chunk + (load_difference/20)
        load_difference = round(load_difference - ramp_up_minus_chunk, 3)
        engines[0][0:current_engines_online - 1] = engines[0][0:current_engines_online - 1] + load_difference
        return load_difference


def offline_ramp_down(engines):
    global ramp_down_minus_chunk
    pct_per_sec = round(engines[0][current_engines_online - 1] / 20, 3)
    while offline_ramping is False or stop_time != reset_stop_time:
        ramp_down_minus_chunk = 0
        return offline_ramping
    else:
        ramp_down_minus_chunk = ramp_down_minus_chunk - pct_per_sec
        engines[0][current_engines_online - 1] = engines[0][current_engines_online - 1] + ramp_down_minus_chunk
        if simulate_running[-1][2] != current_engines_online:
            engines[0][current_engines_online - 1] = engines[0][current_engines_online - 2]
            engines[0][current_engines_online] = 0
            return round(ramp_down_minus_chunk, 3)


def offline_ramp_up(engines):
    global ramp_down_plus_chunk
    while offline_ramping is False or stop_time != reset_stop_time:
        ramp_down_plus_chunk = 0
        return offline_ramping
    else:
        load_difference = round(((mean_load_per_engine * current_engines_online) /
                                 (current_engines_online - 1)) - engines[0][0], 3)
        ramp_down_plus_chunk = ramp_down_plus_chunk + (load_difference / 20)
        engines[0][0:current_engines_online - 1] = engines[0][0:current_engines_online - 1] + ramp_down_plus_chunk
        if simulate_running[-1][2] != current_engines_online:
            engines[0][current_engines_online - 1] = engines[0][current_engines_online - 1] + ramp_down_plus_chunk
        return round(ramp_down_plus_chunk, 3)


def count_change_in_number_of_engines(online_engines):
    global change_no_engines
    if online_engines != current_engines_online:
        change_no_engines += 1
        return change_no_engines
    else:
        return change_no_engines


def count_running_hours(online):
    global running_hours
    running_hours = online + running_hours
    return round((running_hours / 3600), 2)


def get_closest_consumption(load_list, engine_load):
    pass
    #global consumed
    #for j in range(len(engine_load[0])):
    #    closest_load = min(load_list, key=lambda x: abs(x - engine_load[0, j]))
    #    closest_consumption = [j for j, x in enumerate(load_list) if x == closest_load][0]
    #    consumed = consumed + (consumption_per_h_gallons[closest_consumption] / 3600 * 3.78541)
    #return round(consumed, 2)


def detect_high_load(engines):
    global current_engines_online, starting_in, high_load_counter
    if engines[0][0] >= 100:
        current_time = current_engines_online * 1
        high_load_counter += current_time
        high_load_detected = True
        starting_in = randint(40, 87)
        return high_load_detected
    else:
        high_load_detected = False
        return high_load_detected


simulate_running = []

for i in power_list:
    power = i[0]
    online_engines = engines_online(power)
    mean_load_per_engine = estimate_load_per_engine(power)
    count_start = count_to_start(mean_load_per_engine)
    count_stop = count_to_stop(power)
    each_engine = each_engine_load(online_engines)
    ramp_up_engine = online_ramp_up(each_engine)
    ramp_down_engine = online_ramp_down(each_engine)
    offline_up = offline_ramp_up(each_engine)
    offline_down = offline_ramp_down(each_engine)
    count_change_engines = count_change_in_number_of_engines(online_engines)
    total_running_hours = count_running_hours(online_engines)
    consumption = get_closest_consumption(load_list, each_engine)
    high_load = detect_high_load(each_engine)
    """
    print(i[1], 'POWER:' + str(power), 'ONLINE:' + str(online_engines), 'CHANGE NO. ENGINES:' +
          str(count_change_engines), 'RUNNING HOURS:' + str(total_running_hours), 'MEAN LOAD/ENG:'
          + str(mean_load_per_engine), 'STARTING:' + str(count_start), 'STOPPING:' + str(count_stop),
          'STARTING IN:' + str(starting_in), 'STOPPING IN:' + str(stopping_in),
          'EACH ENGINE:' + str(each_engine), 'HIGH LOAD:' + str(high_load), 'RAMP DOWN:' +
          str(ramp_down_engine), 'RAMP UP:' + str(ramp_up_engine), 'OFFLINE UP:' +
          str(offline_up), 'OFFLINE DOWN:' + str(offline_down), 'CONSUMPTION:' + str(consumption))
    """
    values = [i[1], power, online_engines, each_engine, mean_load_per_engine, count_change_engines,
              total_running_hours, consumption, high_load_counter]
    simulate_running.append(values)

print(simulate_running[-1])


# MEASURED: LINE PLOT DG1, DG2, STOP TIMER, DG3
plt.subplot(4, 1, 1)
df['DG1'].plot()
plt.ylabel('Load [%]')
plt.title('DG1 LOAD, DG2 LOAD, STOP TIME COUNTER AND DG3 LOAD')
plt.subplot(4, 1, 2)
df['DG5'].plot()
plt.ylabel('Load [%]')
plt.subplot(4, 1, 3)
plt.plot([item[-1] for item in simulate_running])
plt.ylabel('Counter')
plt.subplot(4, 1, 4)
df['DG4'].plot()
plt.ylabel('Load [%]')
plt.show()




#  LINE PLOTS: MEASURED TOTAL POWER, ESTIMATED STOP TIME, ESTIMATED CHANGE IN NUMBER OF ENGINES
plt.subplot(3, 1, 1)
plt.plot(df['TOT_POW'])
plt.title('TOTAL POWER IN kW')
plt.subplot(3, 1, 2)
plt.plot([item[-1] for item in simulate_running])
plt.title('MODEL: STOP TIME')
plt.subplot(3, 1, 3)
plt.plot([item[2] for item in simulate_running])
plt.title('MODEL: CHANGE IN NUMBER OF ENGINES')
plt.show()




#  START TIME LINE PLOTS
plt.subplot(2, 1, 1)
plt.plot(df['ST'])
plt.title('MEASURED: START TIME')
plt.subplot(2, 1, 2)
plt.plot([item[-1] for item in simulate_running])
plt.title('MODEL: START TIME')
plt.show()




#  DG1 HISTOGRAM
data=[[item[3][0,0] for item in simulate_running]]
arr=plt.hist(data, bins=bins, log=True, range=[-1,150])
for i in range(bins):
    plt.text(arr[1][i],arr[0][i],str(arr[0][i]))
plt.title('MODEL: DG1 LOAD')
plt.show()




# LINE SUBPLOTS OF DG1 MEASURED AND DG1 ESTIMATED LOAD
plt.subplot(2, 1, 1)
plt.plot(df['DG1'])
plt.title('MEASURED: DG1 LOAD')
plt.subplot(2, 1, 2)
plt.plot([item[3][0,0] for item in simulate_running])
plt.title('MODEL: DG1 LOAD')
plt.show()




#  LINE SUBPLOTS OF MEASURED AND ESTIMATED CHANGE IN NUMBER OF ENGINES
plt.subplot(2, 1, 1)
plt.plot(df['ENGINES'])
plt.title('MEASURED: CALCULATION OF REQUIRED ENGINES')
plt.subplot(2, 1, 2)
plt.plot([item[2] for item in simulate_running])
plt.title('MODEL: CHANGE IN NUMBER OF ENGINES')
plt.show()




# HISTOGRAM DG1 MEASURED AND ESTIMATED
plt.subplot(2, 1, 1)
arr=plt.hist(df['DG1'], bins=bins, log=True, range=[-1,160])
for i in range(bins):
    plt.text(arr[1][i],arr[0][i],str(arr[0][i]))
plt.title('MEASURED: DG1 LOAD')
plt.subplot(2, 1, 2)
data=[[item[3][0,0] for item in simulate_running]]
arr=plt.hist(data, bins=bins, log=True, range=[-1,160])
for i in range(bins):
    plt.text(arr[1][i],arr[0][i],str(arr[0][i]))
plt.title('ESTIMATED: DG1 LOAD')
plt.show()




# MEAN LOAD PER ENGINE MEASURED AND ESTIMATED
plt.subplot(2, 1, 1)
df['MEAN POWER'] = df['TOT_POW'] / df['ENGINES'] / 1830 * 100
arr = plt.hist(df['MEAN POWER'], bins=bins, log=True, range=[-1, 160])
for i in range(bins):
    plt.text(arr[1][i], arr[0][i], str(arr[0][i]))
plt.title('MEASURED: MEAN LOAD PER ENGINE')
plt.subplot(2, 1, 2)
data = [[item[4] for item in simulate_running]]
arr = plt.hist(data, bins=bins, log=True, range=[-1, 160])
for i in range(bins):
    plt.text(arr[1][i], arr[0][i], str(arr[0][i]))
plt.title('ESTIMATED: MEAN LOAD PER ENGINE')
plt.show()




# HISTOGRAM 5X ENGINES ESTIMATED
for i in range(1, 6):
    plt.subplot(5, 1, i)
    data = [[item[3][0, i-1] for item in simulate_running]]
    arr=plt.hist(data, bins=bins, log=True, range=[-1,130])
    for i in range(bins):
        plt.text(arr[1][i], arr[0][i], str(arr[0][i]))
    plt.xlabel('Load [%]')
plt.title('MODEL: ALL DG HISTOGRAMS')
plt.show()



# MEASURED: LINE PLOT, ALL FIVE ENGINES
plt.subplot(3, 1, 1)
df['DG1'].plot()
plt.ylabel('Load [%]')
plt.title('MEASURED: DG1, DG2 AND DG3 LOAD')
plt.subplot(3, 1, 2)
df['DG5'].plot()
plt.ylabel('Load [%]')
plt.subplot(3, 1, 3)
df['DG4'].plot()
plt.ylabel('Load [%]')
plt.show()


print("--- %s seconds ---" % (time.time() - timer))