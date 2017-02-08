import os

############################# file headers ########################################
trialcols = ['trial_number', 'trial_index']
timecols = ['time', 'uncertainty']

gazecols = trialcols + ['gaze(x)', 'gaze(y)'] + timecols
#gazecols += ['matrix_pos','matrix_pic_num','solution_pos','solution_pic_num']

pupilcols = trialcols + ['pupil(x)', 'pupil(y)'] + timecols + ['empty']
blinkcols = trialcols + ['blink(x)', 'blink(y)'] + timecols
behavcols = ['Trial', 'Infer', 'CorrectAnswer', 'Response', 'ProbRel', 'RT', 'RT_Unc']
###################################################################################

############################# file directory ########################################
# directory that contains all the data files
root_dir = '/home/bunge/bguerra/EyeTracking'
# raw data files directory
rawfiles_dir = os.path.join(root_dir, 'Raw_Data/Transinf_data/LSAT_T1')
# output directory
outputfiles_dir = os.path.join(root_dir, 'OgamaProcessing/LSAT_T1/matrices_v2')

# directory to dictionaries
dic_dir = '/home/bunge/bguerra/EyeTracking'
filepath_dic_cond_A = os.path.join(dic_dir, 'setA_list_condition.txt')
filepath_dic_cond_B = os.path.join(dic_dir, 'setB_lis_conditiont.txt')
filepath_dic_pic_A = os.path.join(dic_dir, 'setA_list_image.txt')
filepath_dic_pic_B = os.path.join(dic_dir, 'setB_lis_image.txt')
###################################################################################

default_value = -1

#(xmin, xmax, ymin, ymax)
AOIs = {

	'1': [
		(400, 792, 625, 875, 'Q'), 
		(348, 601, 178, 472, 'R1'),
		(631, 884, 178, 472, 'R2'),
		(65, 318, 178, 472, 'I1'),
		(914, 1167, 178, 472, 'I2'),
	],

	'2': [
		(400, 792, 625, 875, 'Q'),
		(65, 318, 178, 472, 'R1'),
		(631, 884, 178, 472, 'R2'),
		(348, 601, 178, 472, 'I1'),
		(914, 1167, 178, 472, 'I2')
	],

	'3': [
		(400, 792, 625, 875, 'Q'),
		(65, 318, 178, 472, 'R1'),
		(914, 1167, 178, 472, 'R2'),
		(348, 601, 178, 472, 'I1'),
		(631, 884, 178, 472, 'I2')
	],

	'4': [
		(400, 792, 625, 875, 'Q'),
		(631, 884, 178, 472, 'R1'),
		(914, 1167, 178, 472, 'R2'),
		(65, 318, 178, 472, 'I1'),
		(348, 601, 178, 472, 'I2')
	],

	'5': [
		(400, 792, 625, 875, 'Q'),
		(348, 601, 178, 472, 'R1'),
		(914, 1167, 178, 472, 'R2'),
		(65, 318, 178, 472, 'I1'),
		(631, 884, 178, 472, 'I2')
	],

	'6': [
		(400, 792, 625, 875, 'Q'),
		(65, 318, 178, 472, 'R1'),
		(914, 1167, 178, 472, 'R2'),
		(348, 601, 178, 472, 'I1'),
		(631, 884, 178, 472, 'I2')
	 ]
}

transitions = {
('N', 'N', 'N-N'), #nowhere not up there :/
('N', 'Q', 'N-Q'),
('N', 'R1', 'N-R1'),
('N', 'R2', 'N-R2'),
('N', 'I1', 'N-I1'),
('N', 'I2', 'N-I2'),

('Q', 'N', 'N-N'),
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