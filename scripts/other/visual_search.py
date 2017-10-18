FILE_FIXATION_DATA = r'/home/bunge/bguerra/EyeTracking/gaze_analysis/data/preprocessing/Transinf/LSAT_T2/Data_with_AOIs/new_run_v2/test/LSAT_T2transinf_fixations_v2.csv'
FILE_MASTER_DATASET = r'/home/bunge/bguerra/EyeTracking/gaze_analysis/data/preprocessing/Transinf/LSAT_T2/Data_with_AOIs/new_run_v2/test/LSAT_T2transinf_behav_gaze_trans.csv'
FILE_OUT = r'/home/bunge/bguerra/EyeTracking/gaze_analysis/data/preprocessing/Transinf/LSAT_T2/Data_with_AOIs/new_run_v2/test/LSAT_T2transinf_behav_gaze_trans_search_ABA_v2.csv'

class FixationData:
    not_found = '0'
    fixation_key = {
        'nowhere' : '1',
        'rel1' : '2',
        'rel2' : '3',
        'q' : '4',
        'irrel1' : '5',
        'irrel2' : '6'
    }

    def __init__(self, PID, trial, block):
        self.PID = PID
        self.trial = trial
        self.block = block
        self.fixations = ''
        self.start_times = []

    def add_fix(self, fix_text, start_time):
        if fix_text.lower() in FixationData.fixation_key:
            self.fixations += FixationData.fixation_key[fix_text.lower()]
        else:
            self.fixations += FixationData.not_found
            print 'WARNING: ENCOUNTERED NOT FOUND %s %s' % (self.PID, self.trial)
        
        self.start_times.append(start_time)

    def get_search(self):
        index1 = self.fixations.find('232')
        index2 = self.fixations.find('323')

        if index1 < 0 and index2 < 0:
            return -1

        if index1 < 0:
            return index2
        if index2 < 0:
            return index1

        if index1 < index2:
            return index1

        return index2

    def get_search_any(self):
        fix_any = self.fixations.replace('3', '2')

        return fix_any.find('222')

    def get_search_noq_any(self):
        index = -1
        prev = 'WOOF'
        message_cnt = 0
        found = False
        start_index = -1
        for ch in self.fixations:
            index += 1
            if ch == FixationData.fixation_key['q'] or ch == FixationData.fixation_key['nowhere']:
                continue

            if ch != FixationData.fixation_key['rel1'] and ch != FixationData.fixation_key['rel2']:
                message_cnt = 0
                start_index = -1
            else:
                if start_index < 0:
                    start_index = index
                message_cnt += 1
                if message_cnt == 3:
                    found = True
                    break

            prev = ch

        if not found:
            return -1

        return start_index # length of word is 3        

    def get_search_noq(self):

        index = -1
        prev = 'WOOF'
        message_cnt = 0
        found = False
        start_index = -1
        for ch in self.fixations:
            index += 1
            if ch == FixationData.fixation_key['q'] or ch == FixationData.fixation_key['nowhere']:
                continue

            if ch != FixationData.fixation_key['rel1'] and ch != FixationData.fixation_key['rel2']:
                start_index = -1
                message_cnt = 0
            elif ch != prev:
                if start_index < 0:
                    start_index = index

                message_cnt += 1
                if message_cnt == 3:
                    found = True
                    break
            else:
                message_cnt = 1
                start_index = index

            prev = ch

        if not found:
            return -1

        return start_index


if __name__ == '__main__':

    print 'Collecting fixation data...'
    fix_data = {}
    f = open(FILE_FIXATION_DATA, 'r')
    f.next()
    for line in f:
        data = line.strip().split(',')
        if len(data) < 6:
            print 'WARNING, invalid line in fix data!'

        pid = data[0]
        block = data[1]
        trial = data[2]
        fix = data[4]
        start_time = data[6]

        key = pid + ':' + block + ':' + trial
        if key not in fix_data:
            fix_data[key] = FixationData(pid, trial, block)
        fix_data[key].add_fix(fix, start_time)

    f.close()
    print 'Done collection fixation data!'

    # read in master data file and print new coloumns
    print 'Calculating output data...'
    output_lines = []
    f = open(FILE_MASTER_DATASET, 'r')
    first = True
    for line in f:
        # hack to deal with commas in data
        data_temp = line.strip().split('"')
        data = []
        add = True
        for d in data_temp:
            if add:
                add = False
                data += d.strip(',').split(',')
            else:
                data += ['DUMMY DATA']
                add = True

        if first:
            first = False

            output_lines.append(line.strip() + ',search,search_t,search_any,search_any_t,search_noQ,search_noQ_t,search_noQ_any,search_noQ_any_t')
            continue

        pid = data[1]
        block = data[3]
        trial = data[4]

        block = block.replace('set', '')

        key = pid + ':' + block + ':' + trial
        result = ['', '-1', '-1', '-1', '-1','-1', '-1', '-1', '-1']
        if key in fix_data:
            search = fix_data[key].get_search()
            search_t = fix_data[key].start_times[search] if search >= 0 else -1
            search_any = fix_data[key].get_search_any()
            search_any_t = fix_data[key].start_times[search_any] if search_any >= 0 else -1
            search_noQ = fix_data[key].get_search_noq()
            search_noQ_t = fix_data[key].start_times[search_noQ] if search_noQ >= 0 else -1
            search_noQ_any = fix_data[key].get_search_noq_any()
            search_noQ_any_t = fix_data[key].start_times[search_noQ_any] if search_noQ_any >= 0 else -1

            result = ['', str(search), str(search_t), str(search_any), str(search_any_t), str(search_noQ), str(search_noQ_t), str(search_noQ_any), str(search_noQ_any_t)]

        else:
            print 'WARNING: %s not found!' % key 

        output_lines.append(line.strip() + ','.join(result))

    f.close()
    print 'Done calculating output data!'

    print 'Writing data to file...'
    f = open(FILE_OUT, 'w')
    for line in output_lines:
        f.write(line + '\n')
    f.close()
    print 'Done writing data to file!'