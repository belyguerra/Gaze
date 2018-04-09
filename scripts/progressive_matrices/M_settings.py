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
print(blinkcols)
behavcols = ['Trial', 'CorrectAnswer', 'ResponseClicked','SubjectResponse', 'RT_Solving',
             'RT_SolvingUnc', 'RT_Response', 'RT_ResponseUnc', 'ListAOIs']

#headers for the file that is used for plotting the grid with fixation patterns.
fixation_headers = ['PID', 'Block', 'Trial', 'Condition', 'Fixation', 'AOI', 'Fixation_Dur', 'Fixation_Start']

#headers for the summary file that has aggregate data from all subjects
summary_headers = [
    'PID', 'Block', 'Trial', 'Condition', 'ACC', 'RT',
    'TotalFixations', 'TotalFixations_N', 'TotalFixation_P', 'TotalFixations_A',
    'TotalFixTime', 'TotalFixTime_N', 'TotalFixTime_P', 'TotalFixTime_A',
    'Time_toFirst_Fix_P', 'Time_toFirst_Fix_A'
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
dic_dir = '/home/bunge/bguerra/Desktop/git/eyetracking/gaze/scripts/progressive_matrices'
filepath_dic_cond_A = os.path.join(dic_dir, 'setA_list_condition_m.txt')
filepath_dic_cond_B = os.path.join(dic_dir, 'setB_list_condition_m.txt')
filepath_dic_pic_A = os.path.join(dic_dir, 'setA_list_image_m.txt')
filepath_dic_pic_B = os.path.join(dic_dir, 'setB_list_image_m.txt')
filepath_dic_rules = os.path.join(dic_dir, 'answer_rules_violation.txt')


###################################################################################

default_value = np.nan

#(xmin, xmax, ymin, ymax)
#old p = (306, 970, 48, 558, 'P')
#old a = (209, 1064, 625, 970, 'A')
#newer but unused for now
#(-335, 335, -50, 480, 'P')
#(-430, 430, -464, -110, 'A'),
#aois were 90 pixels, but allowing a little white space around them
#because I am getting too many fixations on N
AOIs = [
    (-260, -120, 363, 503, 'P1'), #P1 -235, -145, 388, 478
    (-70, 70, 363, 503, 'P2'),
    (120, 260, 363, 503, 'P3'),
    (-260, -120, 187, 327, 'P4'),
    (-70, 70, 187, 327, 'P5'),
    (120, 260, 187, 327, 'P6'), #(145, 235, 193, 283, 'P6')
    (-260, -120, 11, 151, 'P7'),
    (-70, 70, 11, 151, 'P8'),
    (120, 260, 11, 151, 'PQ'),
    (-355, -215, -311, -171, 'A1'), #(-330, -240,-286, -196, 'A1'),
    (-165, -25, -311, -171, 'A2'),
    (25, 165, -311, -171, 'A3'),
    (215, 355, -311, -171, 'A4'), #(240, 330, -286, -196, 'A4'),
    (-355, -215, -487, -347, 'A5'),
    (-165, -25, -487, -347, 'A6'),
    (25, 165, -487, -347, 'A7'),
    (215, 355, -487, -347, 'A8') #(240, 330, -462, -372, 'A8')
]


combined_AOIs = [
(-335, 335, -50, 480, 'P'),
(-430, 430, -464, -110, 'A')
]

transitions = {
    #('N', 'N', 'N-N'),
    #('N', 'A', 'N-A'),
    #('N', 'P', 'N-P'),

    #('P', 'N', 'P-N'),
    #('P', 'P', 'P-P'),
    #('P', 'A', 'P-A'),

    #('A', 'N', 'A-N'),
    #('A', 'P', 'A-P'),
    #('A', 'A', 'A-A'),

    #direct horizontal
    ('P1', 'P2', 'P12'),
    ('P2', 'P3', 'P23'),
    ('P4', 'P5', 'P45'),
    ('P5', 'P6', 'P56'),
    ('P7', 'P8', 'P78'),
    ('P8', 'PQ', 'P8Q'),

    #direct vertical
    ('P1', 'P4', 'P14'),
    ('P2', 'P5', 'P25'),
    ('P3', 'P6', 'P36'),
    ('P4', 'P7', 'P47'),
    ('P5', 'P8', 'P58'),
    ('P6' , 'PQ', 'P6Q')
}
