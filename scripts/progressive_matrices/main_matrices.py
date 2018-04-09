import M_settings as settings #use PM_settings for matrices
import fixation_utils_m as fixation_utils #update settings in this file for Matrices
import df_utils_m as df_utils #update settings in this file for Matrices
import os
import sys
import numpy as np

#def main(Time='1'):
def main():
    #settings.isTime1 = Time == '1'
    failed=[]
    summary_rows = []
    fixation_rows = []
    dic_cond_A = df_utils.get_dic(settings.filepath_dic_cond_A)
    dic_cond_B = df_utils.get_dic(settings.filepath_dic_cond_B)
    dic_pic_A = df_utils.get_dic(settings.filepath_dic_pic_A)
    dic_pic_B = df_utils.get_dic(settings.filepath_dic_pic_B)
    dic_rules = df_utils.get_dic(settings.filepath_dic_rules)

    default_row = {}
    for subjid in range(100,197):
        print('\n processing subject %d' %subjid)
        try:
            for block in ['A', 'B']:

                files = df_utils.get_files(subjid, block)
                #if no gaze file continue
                if not files[0]:
                    continue

                #process ocular data
                gaze = df_utils.read_tsv(files[0], settings.gazecols)
                #blink = df_utils.read_tsv(files[1], settings.blinkcols)
                print('read %d rows' % len(gaze))

                #process behavioral data
                behav = df_utils.read_tsv(files[3], settings.behavcols)
                print('read %d rows' % len(behav))

                for row in gaze:
                    df_utils.trial_reindex(row)

                    df_utils.subject_block(subjid,block,row)

                    trial_dic = dic_cond_A if block == 'A' else dic_cond_B
                    df_utils.map_conditions('Condition', row, trial_dic)

                    trial_dic = dic_pic_A if block == 'A' else dic_pic_B
                    df_utils.map_conditions('Image_file', row, trial_dic)

                    fixation_utils.ogama_coordiates(row)
                    df_utils.ogama_subject(subjid, block, row)

                    fixation_utils.add_aoi(row)
                    listAOIs = behav[int(row['Trial'])-1]['ListAOIs']
                    fixation_utils.add_rules_violated(row, dic_rules, listAOIs)

                fixation_utils.identify_fixations(gaze)
                output_gazefile = os.path.join(settings.output_gaze_processed_dir, str(subjid)+ '_' +block+'_processed_gaze.tsv')
                df_utils.output_rows(output_gazefile, gaze)

                fixation = fixation_utils.describe_fixations(gaze)
                fixation_rows += fixation
                summary_gaze_data = fixation_utils.summary_gaze_data(fixation)

                transition_data = fixation_utils.get_transitions(fixation)



                for row in behav:
                    row['Trial'] = int(row['Trial'])
                    trial = row['Trial']
                    trial_dic = dic_cond_A if block == 'A' else dic_cond_B
                    df_utils.map_conditions('Condition', row, trial_dic)
                    df_utils.map_answer_rules('SubjectResponse_RulesViolated', row, dic_rules)
                    df_utils.subject_block(subjid,block,row)
                    df_utils.acc(row)

                    summary_data = get_default_summary_row(default_row)
                    summary_data['PID'] = subjid
                    summary_data['Block'] = block
                    summary_data['Trial'] = int(row['Trial'])
                    summary_data['Condition'] = row['Condition']
                    summary_data['ACC'] = int(row['ACC'])
                    summary_data['RT'] = float(row['RT_Solving'])
                    summary_data['SubjectResponse_RulesViolated'] = row['SubjectResponse_RulesViolated']

                    if trial not in summary_gaze_data:
                        print('Warning: missing fixation data for trial %d!' % trial)

                    if trial not in transition_data:
                        print('Warning: missing transitions for trial %d!' % trial)

                    if trial in summary_gaze_data:
                        for key, val in summary_gaze_data[trial].items():
                            summary_data[key] = val

                        # combine data from several small AOIs
                        summary_data['TotalFixations_A'] = np.nansum([
                            summary_data['TotalFixations_A_rv_0'],
                            summary_data['TotalFixations_A_rv_1'],
                            summary_data['TotalFixations_A_rv_2'],
                            summary_data['TotalFixations_A_rv_3']
                        ])

                        summary_data['TotalFixTime_A'] = np.nansum([
                            summary_data['TotalFixTime_A_rv_0'],
                            summary_data['TotalFixTime_A_rv_1'],
                            summary_data['TotalFixTime_A_rv_2'],
                            summary_data['TotalFixTime_A_rv_3']
                        ])

                        summary_data['Time_toFirst_Fix_A'] = np.nanmin([
                            summary_data['Time_toFirst_Fix_A_rv_0'],
                            summary_data['Time_toFirst_Fix_A_rv_1'],
                            summary_data['Time_toFirst_Fix_A_rv_2'],
                            summary_data['Time_toFirst_Fix_A_rv_3']
                        ])

                        summary_data['TotalFixations_P'] = np.nansum([
                            summary_data['TotalFixations_P1'],
                            summary_data['TotalFixations_P2'],
                            summary_data['TotalFixations_P3'],
                            summary_data['TotalFixations_P4'],
                            summary_data['TotalFixations_P5'],
                            summary_data['TotalFixations_P6'],
                            summary_data['TotalFixations_P7'],
                            summary_data['TotalFixations_P8'],
                            summary_data['TotalFixations_PQ']
                        ])

                        summary_data['TotalFixTime_P'] = np.nansum([
                            summary_data['TotalFixTime_P1'],
                            summary_data['TotalFixTime_P2'],
                            summary_data['TotalFixTime_P3'],
                            summary_data['TotalFixTime_P4'],
                            summary_data['TotalFixTime_P5'],
                            summary_data['TotalFixTime_P6'],
                            summary_data['TotalFixTime_P7'],
                            summary_data['TotalFixTime_P8'],
                            summary_data['TotalFixTime_PQ']
                        ])

                        summary_data['Time_toFirst_Fix_P'] = np.nanmin([
                            summary_data['Time_toFirst_Fix_P1'],
                            summary_data['Time_toFirst_Fix_P2'],
                            summary_data['Time_toFirst_Fix_P3'],
                            summary_data['Time_toFirst_Fix_P4'],
                            summary_data['Time_toFirst_Fix_P5'],
                            summary_data['Time_toFirst_Fix_P6'],
                            summary_data['Time_toFirst_Fix_P7'],
                            summary_data['Time_toFirst_Fix_P8'],
                            summary_data['Time_toFirst_Fix_PQ']
                        ])


                    if trial in transition_data:
                        for key, val in transition_data[trial].items():
                            summary_data[key] = val

                    summary_rows.append(summary_data)

                    # hack for default values
                    if len(default_row) == 0:
                        default_row = summary_data

        except Exception as e:
            failed.append((subjid,block))
            print('Failed for subject ' + str(subjid) + '_' + block)
            raise

    #output the fixation data for the grid plot
    output_fixationfile = os.path.join(settings.output_agg_dir, 'LSAT_M_fixations_v1.tsv')
    df_utils.output_rows(output_fixationfile, fixation_rows)

    # print the summary file
    output_summaryfile = os.path.join(settings.output_agg_dir, 'LSAT_M_summary_gaze_v1.tsv')
    df_utils.output_rows(output_summaryfile, summary_rows)


def get_default_summary_row(prototype):
    default_data = {}
    for key in prototype.keys():
        default_data[key] = settings.default_value

    return default_data

#if __name__ == '__main__':
#    if len(sys.argv)!=2:
#        print 'you forgot to specify the time (1 or 2)'
#        sys.exit(-1)
#    main(sys.argv[1])

if __name__ == '__main__':
    main()
