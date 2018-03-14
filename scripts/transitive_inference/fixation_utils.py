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

def get_next_window(x, y, t, trials):
    xwindow = x[0:1]
    ywindow = y[0:1]
    twindow = t[0:1]
    current_trial = trials[0]

    MIN_TIME_IN_WINDOW = 100
    index = 1
    start_time = twindow[0]
    while (
        # if want to enforce max num of pts in window
        #len(xwindow) < max_pts_in_window
        index < len(x)
        and trials[index] == current_trial
    ):
        xwindow.append(x[index])
        ywindow.append(y[index])
        twindow.append(t[index])
        if t[index] - start_time >= MIN_TIME_IN_WINDOW:
            break
        index += 1


    return xwindow, ywindow, twindow

# IDs fixations - must be run before describe_fixations function
# gaze data grouped as one fixation if within 100ms the dispertation <= 35px
# make function to get the next x&y within time_limit, xwindow and ywindo take the result of that func
# change this to keep track of time (t) similar to how i keep track of x&y, need to check if t is within time window
def identify_fixations(rows):
    fixs = []
    counter = 0
    MAX_MS_BETWEEN_PTS_IN_FIXATION = 75
    MIN_PTS_IN_WINDOW = 0
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
    trial_to_condition = {}
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

        if trial_num not in trial_to_condition:
            trial_to_condition[trial_num] = condition

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
        condition = trial_to_condition[trial_num]
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
                'TotalFixations_vs': 0,
                'TotalFixations_N_vs': 0,
                'TotalFixations_R1_vs': 0,
                'TotalFixations_R2_vs': 0,
                'TotalFixations_I1_vs': 0,
                'TotalFixations_I2_vs': 0,
                'TotalFixations_Q_vs': 0,
                'TotalFixations_r': 0,
                'TotalFixations_N_r': 0,
                'TotalFixations_R1_r': 0,
                'TotalFixations_R2_r': 0,
                'TotalFixations_I1_r': 0,
                'TotalFixations_I2_r': 0,
                'TotalFixations_Q_r': 0,
                'TotalFixTime': 0,
                'TotalFixTime_N': 0,
                'TotalFixTime_R1': 0,
                'TotalFixTime_R2': 0,
                'TotalFixTime_I1': 0,
                'TotalFixTime_I2': 0,
                'TotalFixTime_Q': 0,
                'TotalFixTime_vs': 0,
                'TotalFixTime_N_vs': 0,
                'TotalFixTime_R1_vs': 0,
                'TotalFixTime_R2_vs': 0,
                'TotalFixTime_I1_vs': 0,
                'TotalFixTime_I2_vs': 0,
                'TotalFixTime_Q_vs': 0,
                'TotalFixTime_r': 0,
                'TotalFixTime_N_r': 0,
                'TotalFixTime_R1_r': 0,
                'TotalFixTime_R2_r': 0,
                'TotalFixTime_I1_r': 0,
                'TotalFixTime_I2_r': 0,
                'TotalFixTime_Q_r': 0,
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
                'VisualSearch_I_onlyI': settings.default_value,
                'SearchTime_I_onlyI': settings.default_value,
                'Rel_Id': settings.default_value,
                'Trans_Int': settings.default_value
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

    for trial, aois_times in trial_to_aois.items():
        trial_to_data[trial]['Rel_Id'] = get_rel_id(aois_times)
        trial_to_data[trial]['Trans_Rel'] = get_trans_int(aois_times, trial_to_data[trial]['Rel_Id'])
        trial_to_data[trial]['Trans_Rel_Irel'] = get_trans_rel_irel(aois_times, trial_to_data[trial]['Rel_Id'])
        trial_to_data[trial]['Trans_Irel'] = get_trans_irel(aois_times, trial_to_data[trial]['Rel_Id'])
        trial_to_data[trial]['VisualSearch_R'],trial_to_data[trial]['SearchTime_R']  = get_visual_search(aois_times)
        trial_to_data[trial]['VisualSearch_I'],trial_to_data[trial]['SearchTime_I']  = get_last_I(aois_times)
        trial_to_data[trial]['VisualSearch_I_onlyI'],trial_to_data[trial]['SearchTime_I_onlyI']  = get_last_I_onlyI(aois_times)

    prev_trial = ''
    for row in rows:
        trial = int(row['Trial'])
        rel_id = trial_to_data[trial]['Rel_Id']
        if trial != prev_trial:
            fix_count = 1
            prev_trial = trial

        suffix = '_r'
        if rel_id == settings.default_value:
            suffix = '_vs'
        elif fix_count <= rel_id:
            suffix = '_vs'

        trial_to_data[trial]['TotalFixations' + suffix] += 1
        aoi = row['AOI']
        key = 'TotalFixations_' + aoi + suffix
        trial_to_data[trial][key] += 1
        duration = row['Fixation_Dur']
        trial_to_data[trial]['TotalFixTime' + suffix] += duration
        key = 'TotalFixTime_' + aoi + suffix
        trial_to_data[trial][key] += duration
        fix_count += 1

    return trial_to_data


def get_trans_int(aois_times, start):
    if start == settings.default_value:
        return 0

    filtered_aois = []
    tmp_aois = []
    # first change all QN to $
    # first change all NQ to $
    aois = [aoi.upper() for aoi, time in aois_times]
    aois = [(aoi, i+1) for i, aoi in enumerate(aois)] # index starts at 1
    for aoi in aois:
        if len(tmp_aois) > 0:
            prev = tmp_aois[-1][0]
        else:
            prev = ''
        if aoi[0] == 'N' and prev == 'Q':
            tmp_aois.pop()
            tmp_aois.append(('$', aoi[1]))
        elif aoi[0] == 'Q' and prev == 'N':
            tmp_aois.pop()
            tmp_aois.append(('$', aoi[1]))
        else:
            tmp_aois.append(aoi)

    prev_2 = ''
    prev = ''
    for aoi in tmp_aois:
        if prev == 'N' or prev == 'Q' or prev == '$':
            if prev_2.startswith('R') and aoi[0].startswith('R'):
                filtered_aois.pop()
        prev_2 = prev
        prev = aoi[0]
        filtered_aois.append(aoi)

    prev = None
    count = 0
    for i, aoi in enumerate(filtered_aois):
        if aoi[1] < start:
            continue
        if aoi[0] == 'R1' and prev == 'R2':
            count += 1
        elif aoi[0] == 'R2' and prev == 'R1':
            count += 1
        prev = aoi[0]

    return count

def get_trans_irel(aois_times, start):
    if start == settings.default_value:
        return 0

    filtered_aois = []
    tmp_aois = []
    # first change all QN to $
    # first change all NQ to $
    aois = [aoi.upper() for aoi, time in aois_times]
    aois = [(aoi, i+1) for i, aoi in enumerate(aois)] # index starts at 1
    for aoi in aois:
        if len(tmp_aois) > 0:
            prev = tmp_aois[-1][0]
        else:
            prev = ''
        if aoi[0] == 'N' and prev == 'Q':
            tmp_aois.pop()
            tmp_aois.append(('$', aoi[1]))
        elif aoi[0] == 'Q' and prev == 'N':
            tmp_aois.pop()
            tmp_aois.append(('$', aoi[1]))
        else:
            tmp_aois.append(aoi)

    prev_2 = ''
    prev = ''
    for aoi in tmp_aois:
        if prev == 'N' or prev == 'Q' or prev == '$':
            if prev_2.startswith('I') and aoi[0].startswith('I'):
                filtered_aois.pop()
        prev_2 = prev
        prev = aoi[0]
        filtered_aois.append(aoi)

    prev = None
    count = 0
    for i, aoi in enumerate(filtered_aois):
        if aoi[1] < start:
            continue
        if aoi[0] == 'I1' and prev == 'I2':
            count += 1
        elif aoi[0] == 'I2' and prev == 'I1':
            count += 1
        prev = aoi[0]

    return count

def get_trans_rel_irel(aois_times, start):
    if start == settings.default_value:
        return 0

    filtered_aois = []
    tmp_aois = []
    # first change all QN to $
    # first change all NQ to $
    aois = [aoi.upper() for aoi, time in aois_times]
    aois = [(aoi, i+1) for i, aoi in enumerate(aois)] # index starts at 1
    for aoi in aois:
        if len(tmp_aois) > 0:
            prev = tmp_aois[-1][0]
        else:
            prev = ''
        if aoi[0] == 'N' and prev == 'Q':
            tmp_aois.pop()
            tmp_aois.append(('$', aoi[1]))
        elif aoi[0] == 'Q' and prev == 'N':
            tmp_aois.pop()
            tmp_aois.append(('$', aoi[1]))
        else:
            tmp_aois.append(aoi)

    prev_2 = ''
    prev = ''
    for aoi in tmp_aois:
        if prev == 'N' or prev == 'Q' or prev == '$':
            if (prev_2.startswith('R') and aoi[0].startswith('I')) or \
            (prev_2.startswith('I') and aoi[0].startswith('R')):
                filtered_aois.pop()
        prev_2 = prev
        prev = aoi[0]
        filtered_aois.append(aoi)

    prev = None
    count = 0
    for i, aoi in enumerate(filtered_aois):
        if aoi[1] < start:
            continue
        if aoi[0] == 'R1' and prev == 'I1':
            count += 1
        elif aoi[0] == 'R2' and prev == 'I1':
            count += 1
        elif aoi[0] == 'R1' and prev == 'I2':
            count += 1
        elif aoi[0] == 'R2' and prev == 'I2':
            count += 1
        prev = aoi[0]

    return count

def get_rel_id(aois_times):
    if len(aois_times) == 0:
        return

    window = []
    window_length = int(round(len(aois_times) / 4))
    if window_length < 4:
        window_length = 4
    if window_length > 8:
        window_length = 8

    # first letter of aoi, and index in list, starting at 1
    vals_we_care_about = [(aoi[0][0].upper(), i+1) for i, aoi in enumerate(aois_times)]
    window = [v for v in vals_we_care_about[:window_length]]
    rest = [v for v in vals_we_care_about[window_length:]]
    found_rel_id = False
    while True:
        just_aois = [a[0] for a in window]
        c = Counter(just_aois)
        above_chance = False
        below_or_equal_chance = True
        chance = window_length / 4
        for val, count in c.items():
            if val == 'R' and count > chance:
                above_chance = True
            elif val != 'R' and count > chance:
                below_or_equal_chance = False
        if above_chance and below_or_equal_chance:
            found_rel_id = True
            break
        if len(rest) == 0:
            break

        # pop off first element
        window.pop(0)
        new = rest.pop(0)
        window.append(new)

    if found_rel_id:
        # get position of first R aoi
        for aoi, index in window:
            if aoi == 'R':
                return index

    return settings.default_value


#search fixations on any scale until Rel1-Rel2-Rel1 pattern
#search time until the return on Rel1-Rel2-Rel1 pattern (so @ onset of 2nd Rel1)
def get_visual_search(aois_times):
    visual_search = settings.default_value
    search_time = settings.default_value

    start = -1
    index = -1
    match_count = 0

    for aoi, time in aois_times:
        if aoi == 'N' or aoi == 'Q':
            continue
        index += 1
        if aoi[0] != 'R':
            match_count = 0
            start = -1
        else:
            match_count += 1
            if start == -1:
                start = index
                #time_start = time #search time to onset of 1st Rel1

            if match_count == 3:
                visual_search = start
                search_time = time
                #search_time = time_start #search time to onset of 1st Rel1
                break

    return visual_search, search_time

#search fixations on scales until last fixation on an irrelevant scale
#search time until onset of the last fixation on an irrelevant scale
def get_last_I(aois_times):
    search_last_I = settings.default_value
    time_last_I = settings.default_value

    index = -1

    for aoi, time in aois_times:
        if aoi == 'N' or aoi == 'Q':
            continue
        index += 1

        if aoi[0] == 'I':
            search_last_I = index
            time_last_I = time

    return search_last_I, time_last_I

#search fixations on irrel scales until last fixation on an irrelevant scale
#search time until onset of the last fixation on an irrelevant scale
def get_last_I_onlyI(aois_times):
    search_last_I = settings.default_value
    time_last_I = settings.default_value
    index = -1

    for aoi, time in aois_times:
        if aoi == 'N' or aoi == 'Q':
            continue
        if aoi[0] == 'I':
            index += 1
            search_last_I = index
            time_last_I = time

    return search_last_I, time_last_I
