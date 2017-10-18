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

# infers AOI based on the gaze coordinates. AOIs defined in settings
def add_aoi(row):
    x = float(row['Gaze(x)_ogama'])
    y = float(row['Gaze(y)_ogama'])
    condition = row['Condition']
    row['AOI'] = 'N' #nowhere
    if x == settings.default_value or y == settings.default_value:
        return
    aoi_list = settings.AOIs[condition]
    for aoi_data in aoi_list:
        if x >= aoi_data[0] and x <= aoi_data[1] and y >= aoi_data[2] and y <= aoi_data[3]:
            row['AOI'] = aoi_data[4]
            return

# IDs fixations - must be run before describe_fixations function
# gaze data grouped as one fixation if within 100ms the dispertation <= 35px
def identify_fixations(rows):
    fixs = []
    counter = 0
    x = [float(row['Gaze(x)_ogama']) for row in rows]
    y = [float(row['Gaze(y)_ogama']) for row in rows]
    while len(x) > 1:
        xwindow = x[0:12]
        ywindow = y[0:12]
        if (abs(float(max(xwindow)) - float(min(xwindow))) <= 35) and (abs(float(max(ywindow)) - float(min(ywindow))) <= 35):
            i = 12
            while (abs(float(max(xwindow)) - float(min(xwindow))) <= 35) and (abs(float(max(ywindow)) - float(min(ywindow)))) <= 35 and i < len(x):
                xwindow.append(x[i])
                ywindow.append(y[i])
                i += 1
            counter += 1
            fixs += [counter] * (len(xwindow)-1)
            x = x[len(xwindow)-1:]
            y = y[len(ywindow)-1:]
        else:
            x = x[1:]
            y = y[1:]
            fixs += [-1]

    #classify last point
    if len(x) != 0:
        xwindow.append(x[0])
        ywindow.append(y[0])
        if (abs(float(max(xwindow)) - float(min(xwindow))) <= 35) and (abs(float(max(ywindow)) - float(min(ywindow))) <= 35):
            fixs += [counter]
        else:
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
                'TotalFixations_P': 0,
                'TotalFixations_A': 0,
                'TotalFixTime': 0,
                'TotalFixTime_N': 0,
                'TotalFixTime_P': 0,
                'TotalFixTime_A': 0,
                'Time_toFirst_Fix_P': settings.default_value,
                'Time_toFirst_Fix_A': settings.default_value,
                'Time_toFirst_Fix_N': settings.default_value,
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
                visual_search = start
                search_time = time
                break

    return visual_search, search_time
