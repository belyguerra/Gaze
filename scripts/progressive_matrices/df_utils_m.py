import M_settings as settings #use PM_settings for matrices
import os


# collects the names of each subject's raw data files
def get_files(subjid, block):
    txtfiles = [os.path.join(settings.rawfiles_dir, f) for f in os.listdir(settings.rawfiles_dir)
        if os.path.isfile(os.path.join(settings.rawfiles_dir, f)) and '.txt' in f
        and block in f and str(subjid) in f]

    gazefile = None
    blinkfile = None
    pupilfile = None
    behavfile = None

    for txtfile in txtfiles:
        if 'gaze' in txtfile:
            gazefile = txtfile
        if 'blink' in txtfile:
            blinkfile = txtfile
        if 'pupil' in txtfile:
            pupilfile = txtfile
        if 'behav' in txtfile:
            behavfile = txtfile

    print("data for block: %s" %block)
    print(gazefile)
    print(blinkfile)
    print(pupilfile)
    print(behavfile)

    return [gazefile, blinkfile, pupilfile, behavfile]

 # Read each subject's raw data files. Headers are specified in settings
def read_tsv(filename, headers):
    rows = []

    with open(filename, 'r') as f:
        for line in f:
            data = line.rstrip().split('\t')

            row_data = {}
            column_cnt = 0
            for header in headers:
                row_data[header] = data[column_cnt]
                column_cnt += 1

            rows.append(row_data)

    return rows

# collects data from the raw data files ###check
def get_new_data_row():
    row = {}
    for val in settings.gazecols:
        row[val] = settings.default_value
    #for val in settings.behavcols:
        #row[val] = settings.default_value

    return row

# ogama needs trials starting at 1 so we modify all the trials for all processing
def trial_reindex(row):
    row['Trial'] = int( row['Trial']) + 1

# helps combine blink/pupil data with gaze file
def add_ocular_data_to_dataset(combined_data_set, rows):
    for r in rows:
        key = r['Trial'] + ':' + r['Time']
        if key not in combined_data_set:
            combined_data_set[key] = get_new_data_row()
        for col, value in r.items():
            combined_data_set[key][col] = value

## functions to assign a condition to each trial. conditions specified in settings.
# sets keys for trial number
def get_dic(filename):
    d = {}
    with open(filename, 'r') as d_list:
        for line in d_list:
            (key, val) = line.rstrip().split('\t')
            d[int(key)] = val
    return d
# maps the condition to the trial key
def map_conditions(new_column, row_data, trial_dic):
    if row_data['Trial'] not in trial_dic:
        raise Exception('trial not found %s' % row_data['Trial'])

    row_data[new_column] = trial_dic[row_data['Trial']]

# ogama can only read sbj ids that start with a letter
def ogama_subject(subjid, block, row):
    row['Subject_ogama'] = 'tp' + str(subjid) + block

# add subject and block information to the files
def subject_block(subjid, block, row):
    row['PID'] = subjid
    row['Block'] = block

# calculate accuracy based on behavioral info
def acc(row):
    #raise exception if behavioral information is missing?
    row['ACC'] = 1 if row['CorrectAnswer'] == row['SubjectResponse'] else 0

# helpful functions for calcuating summary measures
def combine_vals(val1, val2):
    if val1 == settings.default_value:
        return val2
    if val2 == settings.default_value:
        return val1

    return val1 + val2

def min_vals(val1, val2):
    if val1 == settings.default_value:
        return val2
    if val2 == settings.default_value:
        return val1

    return min(val1, val2)

# write out function to
def output_rows(filepath, rows):
    if len(rows) == 0:
        raise Exception('Nothing to write!')

    with open(filepath, 'w') as f:
        headers = list(rows[0].keys())
        f.write('\t'.join(headers))
        f.write('\n')

        for row in rows:
            values = [str(row[header]) for header in headers]
            line = '\t'.join(values)
            f.write(line)
            f.write('\n')

# map answer picture to position
def map_picture_aoi(row, rule_dict, listAOIs):
    pic_aoi_dict = {}
    picture_ids = listAOIs.split(',')
    aoi = 1
    for pic in picture_ids:
        pic_aoi_dict['A'+str(aoi)] = (pic, rule_dict[int(pic)])
        aoi += 1
    return pic_aoi_dict


def map_answer_rules(new_column, row, dic_rules):
    response = int(row['SubjectResponse'])
    if response not in dic_rules:
        raise Exception('rule associated with answer picture %s not found' % response)
    else:
        row[new_column] = dic_rules[response]
