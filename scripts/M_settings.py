import os
import numpy as np

############################# file headers ########################################
trialcols = ['wrong_counter', 'Trial']
timecols = ['Time', 'Uncertainty']
xtracols = ['M1', 'M2', 'M3', 'M4']

gazecols = trialcols + ['Gaze(x)', 'Gaze(y)'] + timecols + xtracols
#gazecols += ['matrix_pos','matrix_pic_num','solution_pos','solution_pic_num']

pupilcols = trialcols + ['Pupil(x)', 'Pupil(y)'] + timecols + ['empty']
blinkcols = trialcols + ['Gaze(x)', 'Gaze(y)'] + timecols
print blinkcols
behavcols = ['Trial', 'CorrectAnswer', 'ResponseClicked','SubjectResponse', 'RT_Solving', 
             'RT_SolvingUnc', 'RT_Response', 'RT_ResponseUnc', 'ListAOIs']

#headers for the file that is used for plotting the grid with fixation patterns.
fixation_headers = ['PID', 'Block', 'Trial', 'Condition', 'Fixation', 'AOI', 'Fixation_Dur', 'Fixation_Start']

#headers for the summary file that has aggregate data from all subjects
summary_headers = [
    'PID', 'Block', 'Trial', 'Condition', 'ACC', 'RT', 
    'TotalFixations', 'TotalFixations_N', 'TotalFixation_P', 'TotalFixations_A', 
    'TotalFixTime', 'TotalFixTime_N', 'TotalFixTime_P', 'TotalFixTime_A',
    'Time_toFirst_Fix_P', 'Time_toFirst_Fix_A',
    'TotalTransitions', 'P-P', 'P-A', 'A-P', 'A-A'
]

###################################################################################

############################# file directory ########################################
#isTime1 = True
# directory that contains all the data files
root_dir = '/home/bunge/bguerra/EyeTracking'

# raw data files directory
#rawfiles_dir = os.path.join(root_dir, 'Raw_Data/Transinf_data/LSAT_T1') if isTime1==True else os.path.join(root_dir, 'Raw_Data/Transinf_data/LSAT_T2')


rawfiles_dir = os.path.join(root_dir, 'Raw_Data/Matrices_data/LSAT_T2')

# output directory for processed data
#output_gaze_processed_dir = os.path.join(root_dir, 'gaze_analysis/data/transif/preprocessed/T1') if isTime1==True else os.path.join(root_dir, 'gaze_analysis/data/transif/preprocessed/T2')
#output_agg_dir = os.path.join(root_dir, 'gaze_analysis/data/transif/results/T1') if isTime1==True else os.path.join(root_dir, 'gaze_analysis/data/transif/results/T2')

output_gaze_processed_dir = os.path.join(root_dir, 'gaze_analysis/data/matrices/preprocessed/T2')

output_agg_dir = os.path.join(root_dir, 'gaze_analysis/data/matrices/results/T2')

#for testing locally
#isTime1 = True
#root_dir = (u'C:\\Users\\belyguerra\\Desktop\\gaze')
#rawfiles_dir = os.path.join(root_dir, 'data\\T1') if isTime1==True else os.path.join(root_dir, 'data\\T2')
#output_gaze_processed_dir = os.path.join(root_dir, 'results\\T1') if isTime1==True else os.path.join(root_dir, 'results\\T2')
#output_agg_dir = os.path.join(root_dir, 'results\\T1') if isTime1==True else os.path.join(root_dir, 'results\\T2')
#dic_dir = root_dir

# directory to dictionaries
dic_dir = '/home/bunge/bguerra/EyeTracking/scripts/new'
filepath_dic_cond_A = os.path.join(dic_dir, 'setA_list_condition_m.txt')
filepath_dic_cond_B = os.path.join(dic_dir, 'setB_list_conditiont_m.txt')
filepath_dic_pic_A = os.path.join(dic_dir, 'setA_list_image_m.txt')
filepath_dic_pic_B = os.path.join(dic_dir, 'setB_list_image_m.txt')


###################################################################################

default_value = np.nan

#(xmin, xmax, ymin, ymax)
AOIs = {

    '1_rule': [
        (209, 1064, 625, 970, 'A'), 
        (306, 970, 48, 558, 'P')
    ],
    
    '2_rule': [
        (209, 1064, 625, 970, 'A'), 
        (306, 970, 48, 558, 'P')
    ],

    '3_rule': [
        (209, 1064, 625, 970, 'A'), 
        (306, 970, 48, 558, 'P')
    ],

}

xtraAOIS = {    
    
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
('N', 'A', 'N-A'),
('N', 'P', 'N-P'),

('P', 'N', 'P-N'),
('P', 'P', 'P-P'),
('P', 'A', 'P-A'),

('A', 'N', 'A-N'),
('A', 'P', 'A-P'),
('A', 'A', 'A-A'),

}