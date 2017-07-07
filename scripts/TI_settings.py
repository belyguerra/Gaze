import os
import numpy as np

############################# file headers ########################################
trialcols = ['wrong_counter', 'Trial']
timecols = ['Time', 'Uncertainty']

gazecols = trialcols + ['Gaze(x)', 'Gaze(y)'] + timecols
#gazecols += ['matrix_pos','matrix_pic_num','solution_pos','solution_pic_num']

pupilcols = trialcols + ['Pupil(x)', 'Pupil(y)'] + timecols + ['empty']
blinkcols = trialcols + ['Gaze(x)', 'Gaze(y)'] + timecols
print blinkcols
behavcols = ['Trial', 'Infer', 'CorrectAnswer', 'SubjectResponse', 'ProbRel', 'RT', 'RT_Unc']

#headers for the file that is used for plotting the grid with fixation patterns.
fixation_headers = ['PID', 'Block', 'Trial', 'Condition', 'Fixation', 'AOI', 'Fixation_Dur', 'Fixation_Start']

#headers for the summary file that has aggregate data from all subjects
summary_headers = [
    'PID', 'Block', 'Trial', 'Condition', 'ACC', 'RT', 
    'TotalFixations', 'TotalFixations_N', 'TotalFixation_R', 'TotalFixations_I', 'TotalFixations_Q',
    'TotalFixTime', 'TotalFixTime_N', 'TotalFixTime_R', 'TotalFixTime_I', 'TotalFixTime_Q',
    'Time_toFirst_Fix_R', 'Time_toFirst_Fix_I', 'Time_toFirst_Fix_Q', 'VisualSearch_R',
    'TotalTransitions', 'Q-R', 'Q-I', 'R-R', 'R-I', 'I-I'
]

###################################################################################

############################# file directory ########################################
#isTime1 = True
# directory that contains all the data files
root_dir = '/home/bunge/bguerra/EyeTracking'

# raw data files directory
#rawfiles_dir = os.path.join(root_dir, 'Raw_Data/Transinf_data/LSAT_T1') if isTime1==True else os.path.join(root_dir, 'Raw_Data/Transinf_data/LSAT_T2')


rawfiles_dir = os.path.join(root_dir, 'Raw_Data/Transinf_data/LSAT_T2')

# output directory for processed data
#output_gaze_processed_dir = os.path.join(root_dir, 'gaze_analysis/data/transif/preprocessed/T1') if isTime1==True else os.path.join(root_dir, 'gaze_analysis/data/transif/preprocessed/T2')
#output_agg_dir = os.path.join(root_dir, 'gaze_analysis/data/transif/results/T1') if isTime1==True else os.path.join(root_dir, 'gaze_analysis/data/transif/results/T2')

output_gaze_processed_dir = os.path.join(root_dir, 'gaze_analysis/data/transif/preprocessed/T2')

output_agg_dir = os.path.join(root_dir, 'gaze_analysis/data/transif/results/T2')

#for testing locally
#isTime1 = True
#root_dir = (u'C:\\Users\\belyguerra\\Desktop\\gaze')
#rawfiles_dir = os.path.join(root_dir, 'data\\T1') if isTime1==True else os.path.join(root_dir, 'data\\T2')
#output_gaze_processed_dir = os.path.join(root_dir, 'results\\T1') if isTime1==True else os.path.join(root_dir, 'results\\T2')
#output_agg_dir = os.path.join(root_dir, 'results\\T1') if isTime1==True else os.path.join(root_dir, 'results\\T2')
#dic_dir = root_dir

# directory to dictionaries
dic_dir = '/home/bunge/bguerra/EyeTracking/scripts/new'
filepath_dic_cond_A = os.path.join(dic_dir, 'setA_list_condition.txt')
filepath_dic_cond_B = os.path.join(dic_dir, 'setB_list_condition.txt')
filepath_dic_pic_A = os.path.join(dic_dir, 'setA_list_image.txt')
filepath_dic_pic_B = os.path.join(dic_dir, 'setB_list_image.txt')


###################################################################################

default_value = np.nan

#(xmin, xmax, ymin, ymax)
AOIs = {

    'IneqEq0': [
        (400, 792, 625, 875, 'Q'), 
        (348, 601, 178, 472, 'R1'),
        (631, 884, 178, 472, 'R2'),
        (65, 318, 178, 472, 'I1'),
        (914, 1167, 178, 472, 'I2'),
    ],

    'IneqEq1': [
        (400, 792, 625, 875, 'Q'),
        (65, 318, 178, 472, 'R1'),
        (631, 884, 178, 472, 'R2'),
        (348, 601, 178, 472, 'I1'),
        (914, 1167, 178, 472, 'I2')
    ],

    'IneqEq2': [
        (400, 792, 625, 875, 'Q'),
        (65, 318, 178, 472, 'R1'),
        (914, 1167, 178, 472, 'R2'),
        (348, 601, 178, 472, 'I1'),
        (631, 884, 178, 472, 'I2')
    ],

    'IneqIneq0': [
        (400, 792, 625, 875, 'Q'),
        (631, 884, 178, 472, 'R1'),
        (914, 1167, 178, 472, 'R2'),
        (65, 318, 178, 472, 'I1'),
        (348, 601, 178, 472, 'I2')
    ],

    'IneqIneq1': [
        (400, 792, 625, 875, 'Q'),
        (348, 601, 178, 472, 'R1'),
        (914, 1167, 178, 472, 'R2'),
        (65, 318, 178, 472, 'I1'),
        (631, 884, 178, 472, 'I2')
    ],

    'IneqIneq2': [
        (400, 792, 625, 875, 'Q'),
        (65, 318, 178, 472, 'R1'),
        (914, 1167, 178, 472, 'R2'),
        (348, 601, 178, 472, 'I1'),
        (631, 884, 178, 472, 'I2')
     ]
}

transitions = {
('N', 'N', 'N-N'),
('N', 'Q', 'N-Q'),
('N', 'R1', 'N-R1'),
('N', 'R2', 'N-R2'),
('N', 'I1', 'N-I1'),
('N', 'I2', 'N-I2'),

('Q', 'N', 'Q-N'),
('Q', 'Q', 'Q-Q'),
('Q', 'R1', 'Q-R1'),
('Q', 'R2', 'Q-R2'),
('Q', 'I1', 'Q-I1'),
('Q', 'I2', 'Q-I2'),

('R1', 'N', 'R1-N'),
('R1', 'Q', 'R1-Q'),
('R1', 'R1', 'R1-R1'),
('R1', 'R2', 'R1-R2'),
('R1', 'I1', 'R1-I1'),
('R1', 'I2', 'R1-I2'),

('R2', 'N', 'R2-N'),
('R2', 'Q', 'R2-Q'),
('R2', 'R1', 'R2-R1'),
('R2', 'R2', 'R2-R2'),
('R2', 'I1', 'R2-I1'),
('R2', 'I2', 'R2-I2'),

('I1', 'N', 'I1-N'),
('I1', 'Q', 'I1-Q'),
('I1', 'R1', 'I1-R1'),
('I1', 'R2', 'I1-R2'),
('I1', 'I1', 'I1-I1'),
('I1', 'I2', 'I1-I2'),

('I2', 'N', 'I2-N'),
('I2', 'Q', 'I2-Q'),
('I2', 'R1', 'I2-R1'),
('I2', 'R2', 'I2-R2'),
('I2', 'I1', 'I2-I1'),
('I2', 'I2', 'I2-I2'),

}