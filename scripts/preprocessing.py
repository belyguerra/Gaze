import transinf_settings
import os

def read_tsv(filename, headers):
    rows = []

    with open(filename, 'r') as f:
        f.next()
        for line in f:
            data = line.rstrip().split('\t')

            row_data = {}
            column_cnt = 0
            for header in headers:
                row_data[header] = data[column_cnt]
                column_cnt += 1

            rows.append(row_data)

    return rows

def get_trial_dic(filename):
    d = {}
    with open(filename, 'r') as d_list:
        for line in d_list:
            (key, val) = line.rstrip().split('\t')
            d[int(key)] = val
    return d


def map_conditions(new_column, row_data, trial_dic):
    if row_data['trial_index'] not in trial_dic:
        raise Exception('trial not found %s' % row_data['trial_index']) 

    row_data[new_column] = trial_dic[row_data['trial_index']]

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

    print "data for block: %s" %block
    print gazefile
    print blinkfile
    print pupilfile
    print behavfile

    return [gazefile, blinkfile, pupilfile, behavfile]

def get_new_data_row():
    row = {}
    for val in settings.gazecols:
        row[val] = settings.default_value
    for val in settings.blinkcols:
        row[val] = settings.default_value
    for val in settings.pupilcols:
        row[val] = settings.default_value
    for val in settings.behavcols:
        row[val] = settings.default_value

    return row

def add_data_to_dataset(combined_data_set, rows):
    for r in rows:
        #key = r['trial_index'] + ':' + r['time']
        key = r['trial_index']
        if key not in combined_data_set:
            combined_data_set = get_new_data_row()
        for col, value in r.iteritems():
            combined_data_set[key][col] = value

def add_aoi(row):
    x = int(row['gaze(x)'])
    y = int(row['gaze(y)'])
    condition = row['condition']
    row['AOI'] = 'N' #nowhere
    if x == -1 or y == -1:
        return
    aoi_list = settings.AOIs[condition]
    for aoi_data in aoi_list:
        if x >= aoi_data[0] and x <= aoi_data[1] and y >= aoi_data[2] and y <= aoi_data[3]:
            row['AOI'] = aoi_data[4]
            return

def ogama_coordiates(row):
    x = float(row['gaze(x)'])
    y = float(row['gaze(y)'])
    row['gaze(x)_ogama'] = -1
    row['gaze(y)_ogama'] = -1
    if x == -1 or y == -1:
        return
    row['gaze(x)_ogama'] = x + 640
    row['gaze(y)_ogama'] = (y*-1) + 512

def classify_fixations(rows):
    fixs = []
    counter = 0
    x = [float(row['gaze(x)']) for row in rows]
    y = [float(row['gaze(y)']) for row in rows]
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

    for row in rows:
        row[]


def trial_reindex(row):
    row['trial_index'] = int( row['trial_index']) + 1

def ogama_subject(subjid, block, row):
    row['subject'] = 'tp' + str(subjid) + block


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

def acc(row):
    row['ACC'] = 0
    if row['CorrectAnswer'] == row['SubjectResponse']:
        row['ACC'] = 1

def main_ogama():
    failed=[]
    dic_cond_A = get_trial_dic(settings.filepath_dic_cond_A)
    dic_cond_B = get_trial_dic(settings.filepath_dic_cond_A)
    dic_pic_A = get_trial_dic(settings.filepath_dic_pic_A)
    dic_pic_B = get_trial_dic(settings.filepath_dic_pic_B)

    for subjid in [102]:
        print '\n processing subject %d' %subjid
        try:
            for block in ['A', 'B']:
                files = get_files(subjid, block)
                gaze = read_tsv(files[0], settings.gazecols)
                #blink = read_df(files[1], settings.blinkcols) 
                #pupil = read_df(files[2], settings.pupilcols) 
                #behav = read_df(files[3], settings.behavcols) 

                #combined_data_dic = {}
                #add_data_to_dataset(combined_data_dic, gaze)
                #add_data_to_dataset(combined_data_dic, blink)
                #add_data_to_dataset(combined_data_dic, pupil)
                #add_data_to_dataset(combined_data_dic, behav)

                combined_rows = gaze
                #combined_rows.sort(key=lambda r: (int(r['trial_number']), int(r['time'])))
                combined_rows.sort(key=lambda r: (int(r['trial_number']), int(r['time'])))
                print 'read %d rows' % len(combined_rows)

                for row in combined_rows:
                    trial_reindex(row)
                    trial_dic = dic_cond_A if block == 'A' else dic_cond_B
                    map_conditions('condition', row, trial_dic)

                    trial_dic = dic_pic_A if block == 'A' else dic_pic_B
                    map_conditions('iamge_file', row, trial_dic)

                    ogama_coordiates(row)
                    ogama_subject(subjid, block, row)

                output_filepath = os.path.join(settings.outputfiles_dir, str(subjid)+ '_' +block+'_ogama.tsv')
                output_rows(output_filepath, combined_rows)
        
        except Exception as e:
            failed.append((subjid,block))
            print 'Failed for subject ' + str(subjid) + '_' + block
            raise



def main_summary():
    failed=[]
    dic_cond_A = get_trial_dic(settings.filepath_dic_cond_A)
    dic_cond_B = get_trial_dic(settings.filepath_dic_cond_A)
    dic_pic_A = get_trial_dic(settings.filepath_dic_pic_A)
    dic_pic_B = get_trial_dic(settings.filepath_dic_pic_B)

    for subjid in [102]:
        print '\n processing subject %d' %subjid
        try:
            for block in ['A', 'B']:
                files = get_files(subjid, block)
                gaze = read_tsv(files[0], settings.gazecols)
                #blink = read_df(files[1], settings.blinkcols) 
                #pupil = read_df(files[2], settings.pupilcols) 
                behav = read_df(files[3], settings.behavcols) 

                combined_data_dic = {}
                add_data_to_dataset(combined_data_dic, gaze)
                #add_data_to_dataset(combined_data_dic, blink)
                #add_data_to_dataset(combined_data_dic, pupil)
                add_data_to_dataset(combined_data_dic, behav)

                combined_rows = combined_data_dic.values()
                combined_rows.sort(key=lambda r: (int(r['trial_index']))
                print 'read %d rows' % len(combined_rows)

                for row in combined_rows:
                    trial_reindex(row)
                    trial_dic = dic_cond_A if block == 'A' else dic_cond_B
                    map_conditions('condition', row, trial_dic)

                    row['subject'] = str(subjid)
                    row['block'] = block
                    acc(row)



                output_filepath = os.path.join(settings.outputfiles_dir, str(subjid)+ '_' +block+'_ogama.tsv')
                output_rows(output_filepath, combined_rows)

        except Exception as e:
            failed.append((subjid,block))
            print 'Failed for subject ' + str(subjid) + '_' + block
            raise

if __name__ == '__main__':
    main_ogama()
    main_summary()