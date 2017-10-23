import M_settings as settings #use PM_settings for matrices
import os
import numpy as np
from collections import Counter


# converts gaze coordinates to ogama's system
# for simplicity we will use the same coordinate in all processing
def ogama_coordiates(row):
    x = float(row['Gaze(x)'])
    y = float(row['Gaze(y)'])
    row['Gaze(x)_ogama'] = settings.default_value
    row['Gaze(y)_ogama'] = settings.default_value
    if x == -1 or y == -1:
        return
    row['Gaze(x)_ogama'] = x + 640
    row['Gaze(y)_ogama'] = (y*-1) + 512

def add_aoi(row):
    x = float(row['Gaze(x)'])
    y = float(row['Gaze(y)'])
    row['AOI'] = 'N' #nowhere
    if x == settings.default_value or y == settings.default_value:
        return
    aoi_list = settings.AOIs
    for aoi_data in aoi_list:
        if x >= aoi_data[0] and x <= aoi_data[1] and y >= aoi_data[2] and y <= aoi_data[3]:
            row['AOI'] = aoi_data[4]
            return

def add_rules_violated(row, dic_rules):
    aoi_to_rules = df_utils_m.map_picture_aoi(row, dic_rules)
    aoi = row['AOI']
    if aoi not in aoi_to_rules:
        row['RulesViolated'] = row['AOI']
    else:
        row['RulesViolated'] = aoi_to_rules[aoi][1]


def get_next_window(x, y, t, trials):
    xwindow = x[0:1]
    ywindow = y[0:1]
    twindow = t[0:1]
    current_trial = trials[0]

    MAX_TIME_IN_WINDOW = 125
    index = 1
    start_time = twindow[0]
    while (
        # if want to enforce max num of pts in window
        #len(xwindow) < max_pts_in_window
        index < len(x)
        and t[index] - start_time <= MAX_TIME_IN_WINDOW
        and trials[index] == current_trial
    ):
        xwindow.append(x[index])
        ywindow.append(y[index])
        twindow.append(t[index])
        index += 1

    return xwindow, ywindow, twindow

# IDs fixations - must be run before describe_fixations function
# gaze data grouped as one fixation if within 100ms the dispertation <= 35px
# make function to get the next x&y within time_limit, xwindow and ywindo take the result of that func
# change this to keep track of time (t) similar to how i keep track of x&y, need to check if t is within time window
def identify_fixations(rows):
    fixs = []
    counter = 0
    MAX_MS_BETWEEN_PTS_IN_FIXATION = 40
    MIN_PTS_IN_WINDOW = 6
    MIN_MS_WINDOW = 100
    DIST_PIX = 35
    MAX_OUTLIER_PTS = 1
    x = [float(row['Gaze(x)']) for row in rows]
    y = [float(row['Gaze(y)']) for row in rows]
    t = [int(row['Time']) for row in rows]
    trials = [row['Trial'] for row in rows]
    while len(x) > 0:
        xwindow, ywindow, twindow = get_next_window(x, y, t, trials)
        current_trial = trials[0]
        num_points_skipped = 0
        if (
            len(xwindow) >= MIN_PTS_IN_WINDOW
            and abs(float(max(xwindow)) - float(min(xwindow))) <= DIST_PIX
            and abs(float(max(ywindow)) - float(min(ywindow))) <= DIST_PIX
            and twindow[-1] - twindow[0] >= MIN_MS_WINDOW
        ):
            i = len(xwindow)
            undo_end_fixation = True
            while undo_end_fixation:
                while i < len(x):
                    if abs(float(max(xwindow + [x[i]])) - float(min(xwindow + [x[i]]))) > DIST_PIX:
                        break
                    elif abs(float(max(ywindow + [y[i]])) - float(min(ywindow + [y[i]]))) > DIST_PIX:
                        break
                    if t[i] - t[i-1] > MAX_MS_BETWEEN_PTS_IN_FIXATION:
                        break
                    if trials[i] != current_trial:
                        break

                    xwindow.append(x[i])
                    ywindow.append(y[i])
                    twindow.append(t[i])
                    i += 1

                undo_end_fixation = False
                # if reached the end, don't undo end fixation
                if i >= len(x):
                    break
                # if trial changed, don't undo end fixation
                if trials[i] != current_trial:
                    break
                # if next point is too far in future, don't undo end fixation
                if t[i] - t[i-1] > MAX_MS_BETWEEN_PTS_IN_FIXATION:
                    break

                # add point i to window
                plus_n_xwindow = xwindow + [x[i]]
                plus_n_ywindow = ywindow + [y[i]]
                plus_n_twindow = twindow + [t[i]]
                i += 1
                n = 0
                while i + n < len(x):
                    if n >= MAX_OUTLIER_PTS:
                        break
                    if t[i + n] - t[i + n - 1] > MAX_MS_BETWEEN_PTS_IN_FIXATION:
                        break
                    if trials[i + n] != current_trial:
                        break
                    if (
                        abs(float(max(plus_n_xwindow + [x[n+i]])) - float(min(plus_n_xwindow + [x[n+i]]))) <= DIST_PIX
                        and abs(float(max(plus_n_ywindow + [y[n+i]])) - float(min(plus_n_ywindow + [y[n+i]]))) <= DIST_PIX
                    ):
                        undo_end_fixation = True
                        break
                    else:
                        plus_n_xwindow += [x[n+i]]
                        plus_n_ywindow += [y[n+i]]
                        plus_n_twindow += [t[n+i]]
                    n += 1

                if undo_end_fixation:
                    xwindow = plus_n_xwindow
                    ywindow = plus_n_ywindow
                    twindow = plus_n_twindow
                    i += n + 1

            counter += 1
            fixs += [counter] * len(xwindow)
            x = x[len(xwindow):]
            y = y[len(ywindow):]
            t = t[len(twindow):]
            trials = trials[len(twindow):]
        else:
            x = x[1:]
            y = y[1:]
            t = t[1:]
            trials = trials[1:]
            fixs += [-1]

    if len(fixs) != len(rows):
        raise Exception('number of fixations is not the same as number of rows')
    for i, row in enumerate(rows):
        row['Fixation'] = fixs[i]

# trial -> transition_cnt_dictionary
def get_transitions(rows):
    trial_to_data = {}
    trial_to_transitions = {}

    for row in rows:
        aoi = row['AOI']
        fixation = int(row['Fixation'])
        trial_num = int(row['Trial'])

        if fixation == settings.default_value or fixation == -1:
            continue

        if trial_num not in trial_to_data:
            trial_to_data[trial_num] = {}

        if fixation not in trial_to_data[trial_num]:
            trial_to_data[trial_num][fixation] = []

        trial_to_data[trial_num][fixation].append(aoi)

    # iterate data and add transitions to dictionary
    for trial_num, data in trial_to_data.items():

        if trial_num not in trial_to_transitions:
            trial_to_transitions[trial_num] = []

        sorted_fixations = sorted(data.keys())
        if len(sorted_fixations) > 1:
            prev_aoi = Counter(data[sorted_fixations[0]]).most_common()[0][0]
            for i in range(1, len(sorted_fixations)):
                next_aoi = Counter(data[sorted_fixations[i]]).most_common()[0][0]
                trial_to_transitions[trial_num].append((prev_aoi, next_aoi))
                prev_aoi = next_aoi

    trial_to_transition_cnts = {}

    for trial, list_transitions in trial_to_transitions.items():
        trial_to_transition_cnts[trial] = {t[2]:0 for t in settings.transitions}
        for transition in list_transitions:
            key = transition[0] + '-' + transition[1]
            trial_to_transition_cnts[trial][key] += 1

    return trial_to_transition_cnts

# calculates start and duration of fixations on each AOI
# creates an output file that can be used for plotting heatmaps
def describe_fixations(rows):

    output_fixation_data = []
    trial_to_fixation_data = {}
    trial_times = {}

    for row in rows:
        aoi = row['AOI']
        fixation = int(row['Fixation'])
        trial_num = int(row['Trial'])
        time = float(row['Time'])
        subject = int(row['PID'])
        block = row['Block']
        condition = row['Condition']

        if fixation == settings.default_value or fixation == -1:
            continue

        if trial_num not in trial_times:
            trial_times[trial_num] = []
        trial_times[trial_num].append(time)

        if trial_num not in trial_to_fixation_data:
            trial_to_fixation_data[trial_num] = {}

        if fixation not in trial_to_fixation_data[trial_num]:
            trial_to_fixation_data[trial_num][fixation] = {
                'aois' : [],
                'times' : []
            }

        trial_to_fixation_data[trial_num][fixation]['aois'].append(aoi)
        trial_to_fixation_data[trial_num][fixation]['times'].append(time)

    trial_nums_sorted = sorted(trial_to_fixation_data.keys())
    for trial_num in trial_nums_sorted:
        fixations_sorted = sorted(trial_to_fixation_data[trial_num].keys())
        for fixation in fixations_sorted:
            aoi = Counter(trial_to_fixation_data[trial_num][fixation]['aois']).most_common()[0][0]
            max_time = max(trial_to_fixation_data[trial_num][fixation]['times'])
            min_time = min(trial_to_fixation_data[trial_num][fixation]['times'])
            duration = max_time - min_time
            time_start_fixation = min_time - min(trial_times[trial_num])

            data = {
                'PID' : subject,
                'Block' : block,
                'Trial' : trial_num,
                'Condition' : condition,
                'Fixation' : fixation,
                'AOI' : aoi,
                'Fixation_Dur' : duration,
                'Fixation_Start' : time_start_fixation
            }
            output_fixation_data.append(data)

    return output_fixation_data


def summary_gaze_data(rows):
    trial_to_data = {}
    trial_to_aois = {}
    trial_to_default_vals = {}
    for row in rows:
        trial = int(row['Trial'])
        if trial not in trial_to_data:
            trial_to_data[trial]= {
                'TotalFixations': 0,
                'TotalFixations_N': 0,
                'TotalFixations_P1': 0,
                'TotalFixations_P2': 0,
                'TotalFixations_P3': 0,
                'TotalFixations_P4': 0,
                'TotalFixations_P5': 0,
                'TotalFixations_P6': 0,
                'TotalFixations_P7': 0,
                'TotalFixations_P8': 0,
                'TotalFixations_PQ': 0,
                'TotalFixations_A_rv_0': 0,
                'TotalFixations_A_rv_1': 0,
                'TotalFixations_A_rv_1': 0,
                'TotalFixations_A_rv_2': 0,
                'TotalFixations_A_rv_3': 0,
                'TotalFixTime': 0,
                'TotalFixTime_N': 0,
                'TotalFixTime_P1': 0,
                'TotalFixTime_P2': 0,
                'TotalFixTime_P3': 0,
                'TotalFixTime_P4': 0,
                'TotalFixTime_P5': 0,
                'TotalFixTime_P6': 0,
                'TotalFixTime_P7': 0,
                'TotalFixTime_P8': 0,
                'TotalFixTime_PQ': 0,
                'TotalFixTime_A_rv_0': 0,
                'TotalFixTime_A_rv_1': 0,
                'TotalFixTime_A_rv_2': 0,
                'TotalFixTime_A_rv_3': 0,
                'Time_toFirst_Fix_P1': settings.default_value,
                'Time_toFirst_Fix_P2': settings.default_value,
                'Time_toFirst_Fix_P3': settings.default_value,
                'Time_toFirst_Fix_P4': settings.default_value,
                'Time_toFirst_Fix_P5': settings.default_value,
                'Time_toFirst_Fix_P6': settings.default_value,
                'Time_toFirst_Fix_P7': settings.default_value,
                'Time_toFirst_Fix_P8': settings.default_value,
                'Time_toFirst_Fix_PQ': settings.default_value,
                'Time_toFirst_Fix_N': settings.default_value,
                'Time_toFirst_Fix_A_rv_0': settings.default_value,
                'Time_toFirst_Fix_A_rv_1': settings.default_value,
                'Time_toFirst_Fix_A_rv_2': settings.default_value,
                'Time_toFirst_Fix_A_rv_3': settings.default_value,
            }
            trial_to_default_vals[trial] = {}


        if trial not in trial_to_aois:
            trial_to_aois[trial] = []

        trial_to_data[trial]['TotalFixations'] += 1
        aoi = row['AOI']
        key = 'TotalFixations_' + aoi
        trial_to_data[trial][key] += 1
        start_time = row['Fixation_Start']

        trial_to_aois[trial].append((aoi, start_time))

        duration = row['Fixation_Dur']
        trial_to_data[trial]['TotalFixTime'] += duration
        key = 'TotalFixTime_' + aoi
        trial_to_data[trial][key] += duration

        key = 'Time_toFirst_Fix_'+ aoi
        if key not in trial_to_default_vals[trial]:
            trial_to_default_vals[trial][key] = True
            trial_to_data[trial][key] = start_time

    return trial_to_data
