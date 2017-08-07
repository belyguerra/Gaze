import TI_settings as settings #use PM_settings for matrices
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

# infers AOI based on the gaze coordinates. AOIs defined in settings
def add_aoi(row):
    x = float(row['Gaze(x)'])
    y = float(row['Gaze(y)'])
    condition = row['Condition']
    row['AOI'] = 'N' #nowhere
    if x == settings.default_value or y == settings.default_value:
        return
    aoi_list = settings.AOIs[condition]
    for aoi_data in aoi_list:
        if x >= aoi_data[0] and x <= aoi_data[1] and y >= aoi_data[2] and y <= aoi_data[3]:
            row['AOI'] = aoi_data[4]
            return

def get_next_window(x, y, t):
    xwindow = x[0:1]
    ywindow = y[0:1]
    twindow = t[0:1]

    MAX_TIME_IN_WINDOW = 150
    index = 1
    start_time = twindow[0]
    while (
        # if want to enforce max num of pts in window
        # len(xwindow) < max_pts_in_window
        index < len(x)
        and t[index] - start_time <= MAX_TIME_IN_WINDOW
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
    while len(x) > 0:
        xwindow, ywindow, twindow = get_next_window(x, y, t)
        num_points_skipped = 0
        if (
            len(xwindow) >= MIN_PTS_IN_WINDOW
            and twindow[-1] - twindow[0] >= MIN_MS_WINDOW
            and abs(float(max(xwindow)) - float(min(xwindow))) <= DIST_PIX
            and abs(float(max(ywindow)) - float(min(ywindow))) <= DIST_PIX
        ):
            i = len(xwindow)
            # length of window will always be > 1
            prev_time = twindow[i-2]
            undo_end_fixation = True
            while undo_end_fixation:
                while (
                    abs(float(max(xwindow)) - float(min(xwindow))) <= DIST_PIX
                    and abs(float(max(ywindow)) - float(min(ywindow))) <= DIST_PIX
                    and twindow[i-1] - prev_time <= MAX_MS_BETWEEN_PTS_IN_FIXATION
                    and i < len(x)
                ):
                    xwindow.append(x[i])
                    ywindow.append(y[i])
                    twindow.append(t[i])
                    prev_time = twindow[i-1]
                    i += 1

                # check if next point is in fixation
                n = 1
                undo_end_fixation = False
                while (
                    n <= MAX_OUTLIER_PTS
                    and i + n < len(x)
                    and not undo_end_fixation
                ):
                    plus_n_xwindow = xwindow + [x[i+n]]
                    plus_n_ywindow = ywindow + [y[i+n]]
                    plus_n_twindow = twindow + [t[i+n]]
                    plus_n_prev_time = plus_n_twindow[i + n - 1]

                    if (abs(float(max(plus_n_xwindow)) - float(min(plus_n_xwindow))) <= DIST_PIX
                        and abs(float(max(plus_n_ywindow)) - float(min(plus_n_ywindow))) <= DIST_PIX
                        and plus_n_twindow[i+n] - prev_time <= MAX_MS_BETWEEN_PTS_IN_FIXATION

                        abs(float(max(plus_n_xwindow)) - float(min(plus_n_xwindow))) <= DIST_PIX
                        and abs(float(max(plus_n_ywindow)) - float(min(plus_n_ywindow))) <= DIST_PIX
                        #and plus_n_twindow[i + n] - prev_time <= MAX_MS_BETWEEN_PTS_IN_FIXATION
                        and plus_n_twindow - prev_time <= MAX_MS_BETWEEN_PTS_IN_FIXATION):

                        undo_end_fixation = True
                        break

                    n += 1

                if undo_end_fixation:
                    xwindow = plus_n_xwindow
                    ywindow = plus_n_ywindow
                    twindow = plus_n_twindow
                    i += n
                    prev_time = twindow[-2]


            counter += 1
            fixs += [counter]  * (len(xwindow)-1)
            x = x[len(xwindow)-1:]
            y = y[len(ywindow)-1:]
            t = t[len(twindow)-1:]
        else:
            x = x[1:]
            y = y[1:]
            t = t[1:]
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
    for trial_num, data in trial_to_data.iteritems():

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

    for trial, list_transitions in trial_to_transitions.iteritems():
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
                'TotalFixations_R1': 0,
                'TotalFixations_R2': 0,
                'TotalFixations_I1': 0,
                'TotalFixations_I2': 0,
                'TotalFixations_Q': 0,
                'TotalFixTime': 0,
                'TotalFixTime_N': 0,
                'TotalFixTime_R1': 0,
                'TotalFixTime_R2': 0,
                'TotalFixTime_I1': 0,
                'TotalFixTime_I2': 0,
                'TotalFixTime_Q': 0,
                'Time_toFirst_Fix_R1': settings.default_value,
                'Time_toFirst_Fix_R2': settings.default_value,
                'Time_toFirst_Fix_I1': settings.default_value,
                'Time_toFirst_Fix_I2': settings.default_value,
                'Time_toFirst_Fix_Q': settings.default_value,
                'Time_toFirst_Fix_N': settings.default_value,
                'VisualSearch_R' : settings.default_value,
                'SearchTime_R': settings.default_value,
                'VisualSearch_I' : settings.default_value,
                'SearchTime_I': settings.default_value,
                'VisualSearch_Itrans': settings.default_value,
                'SearchTime_Itrans': settings.default_value
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

    for trial, aois_times in trial_to_aois.iteritems():
        trial_to_data[trial]['VisualSearch_R'],trial_to_data[trial]['SearchTime_R']  = get_visual_search(aois_times)
        trial_to_data[trial]['VisualSearch_I'],trial_to_data[trial]['SearchTime_I']  = get_last_I(aois_times)
        trial_to_data[trial]['VisualSearch_I_trans'],trial_to_data[trial]['SearchTime_I_trans']  = get_last_Itrans(aois_times)

    return trial_to_data

def get_visual_search(aois_times):
    visual_search = settings.default_value
    search_time = settings.default_value

    start = -1
    index = -1
    match_count = 0
    for aoi, time in aois_times:
        index += 1

        if aoi == 'N' or aoi == 'Q':
            continue
        elif aoi[0] != 'R':
            match_count = 0
            start = -1
        else:
            match_count += 1
            if start == -1:
                start = index
                #time_start = time

            if match_count == 3:
                visual_search = start
                search_time = time
                break

    return visual_search, search_time

def get_last_I(aois_times):
    search_last_I = settings.default_value
    time_last_I = settings.default_value

    index = -1

    for aoi, time in aois_times:
        index += 1

        if aoi[0] == 'I':
            search_last_I = index
            time_last_I = time

    return search_last_I, time_last_I

def get_last_Itrans(aois_times):
    search_last_Itrans = settings.default_value
    time_last_Itrans = settings.default_value

    start = -1
    index = -1
    match_count = 0
    for aoi, time in aois_times:
        index += 1

        if aoi == 'N' or aoi == 'Q':
            continue
        elif aoi[0] != 'I':
            match_count = 0
            start = -1
        else:
            match_count += 1
            if start == -1:
                start = index
                #time_start = time

            if match_count == 2:
                search_last_Itrans = start
                time_last_Itrans = time
                break

        return search_last_Itrans, time_last_Itrans
