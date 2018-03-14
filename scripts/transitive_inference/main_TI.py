import TI_settings as settings #use PM_settings for matrices
import fixation_utils #update settings in this file for Matrices
import df_utils #update settings in this file for Matrices
import os
import sys

#def main(Time='1'):
def main():
    #settings.isTime1 = Time == '1'
    failed=[]
    summary_rows = []
    fixation_rows = []
    dic_cond_A = df_utils.get_trial_dic(settings.filepath_dic_cond_A)
    dic_cond_B = df_utils.get_trial_dic(settings.filepath_dic_cond_B)
    dic_pic_A = df_utils.get_trial_dic(settings.filepath_dic_pic_A)
    dic_pic_B = df_utils.get_trial_dic(settings.filepath_dic_pic_B)

    default_row = {}
    for subjid in range(200,297):
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
                #print 'read %d rows' % len(blink)
                #we need to interpolate the blinks...
                #combined_data_dic = {}
                #df_utils.add_ocular_data_to_dataset(combined_data_dic, gaze)
                #df_utils.add_ocular_data_to_dataset(combined_data_dic, blink)
                #combined_rows = combined_data_dic.values()
                #combined_rows.sort(key=lambda r: (int(r['Trial']), int(r['Time'])))
                #print 'read %d rows' % len(combined_rows)

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

                fixation_utils.identify_fixations(gaze)
                output_gazefile = os.path.join(settings.output_gaze_processed_dir, str(subjid)+ '_' +block+'_processed_gaze.tsv')
                df_utils.output_rows(output_gazefile, gaze)

                fixation = fixation_utils.describe_fixations(gaze)
                fixation_rows += fixation
                summary_gaze_data = fixation_utils.summary_gaze_data(fixation)

                transition_data = fixation_utils.get_transitions(fixation)

                #process behavioral data and summary gaze file
                behav = df_utils.read_tsv(files[3], settings.behavcols)
                print('read %d rows' % len(behav))

                for row in behav:
                    row['Trial'] = int(row['Trial'])
                    trial = row['Trial']
                    trial_dic = dic_cond_A if block == 'A' else dic_cond_B
                    df_utils.map_conditions('Condition', row, trial_dic)
                    df_utils.subject_block(subjid,block,row)
                    df_utils.acc(row)

                    summary_data = get_default_summary_row(default_row)
                    summary_data['PID'] = subjid
                    summary_data['Block'] = block
                    summary_data['Trial'] = int(row['Trial'])
                    summary_data['Condition'] = row['Condition']
                    summary_data['ACC'] = int(row['ACC'])
                    summary_data['RT'] = float(row['RT'])

                    if trial not in summary_gaze_data:
                        print('Warning: missing fix/trans data for trial %d!' % trial)
                        for key in settings.gaze_headers:
                            summary_data[key] = settings.default_value

                    if trial in summary_gaze_data:
                        for key, val in summary_gaze_data[trial].items():
                            summary_data[key] = val

                        # combine gaze data for the main AOIs (e.g., rel vs. irrelevant scales)

                        summary_data['TotalFixations_R'] = df_utils.combine_vals(summary_data['TotalFixations_R1'], summary_data['TotalFixations_R2'])
                        summary_data['TotalFixations_I'] = df_utils.combine_vals(summary_data['TotalFixations_I1'], summary_data['TotalFixations_I2'])
                        summary_data['TotalFixTime_R'] = df_utils.combine_vals(summary_data['TotalFixTime_R1'], summary_data['TotalFixTime_R2'])
                        summary_data['TotalFixTime_I'] = df_utils.combine_vals(summary_data['TotalFixTime_I1'], summary_data['TotalFixTime_I2'])
                        summary_data['Time_toFirst_Fix_R'] = df_utils.min_vals(summary_data['Time_toFirst_Fix_R1'], summary_data['Time_toFirst_Fix_R2'])
                        summary_data['Time_toFirst_Fix_I'] = df_utils.min_vals(summary_data['Time_toFirst_Fix_I1'], summary_data['Time_toFirst_Fix_I2'])

                        summary_data['TotalFixations_R_vs'] = df_utils.combine_vals(summary_data['TotalFixations_R1_vs'], summary_data['TotalFixations_R2_vs'])
                        summary_data['TotalFixations_R_r'] = df_utils.combine_vals(summary_data['TotalFixations_R1_r'], summary_data['TotalFixations_R2_r'])
                        summary_data['TotalFixations_I_vs'] = df_utils.combine_vals(summary_data['TotalFixations_I1_vs'], summary_data['TotalFixations_I2_vs'])
                        summary_data['TotalFixations_I_r'] = df_utils.combine_vals(summary_data['TotalFixations_I1_r'], summary_data['TotalFixations_I2_r'])
                        summary_data['TotalFixTime_R_vs'] = df_utils.combine_vals(summary_data['TotalFixTime_R1_vs'], summary_data['TotalFixTime_R2_vs'])
                        summary_data['TotalFixTime_R_r'] = df_utils.combine_vals(summary_data['TotalFixTime_R1_r'], summary_data['TotalFixTime_R2_r'])
                        summary_data['TotalFixTime_I_vs'] = df_utils.combine_vals(summary_data['TotalFixTime_I1_vs'], summary_data['TotalFixTime_I2_vs'])
                        summary_data['TotalFixTime_I_r'] = df_utils.combine_vals(summary_data['TotalFixTime_I1_r'], summary_data['TotalFixTime_I2_r'])

                    if trial in transition_data:
                        for key, val in transition_data[trial].items():
                            summary_data[key] = val

                        summary_data['Q-R'] = df_utils.combine_vals(summary_data['Q-R1'], summary_data['R1-Q'])
                        summary_data['Q-R'] += df_utils.combine_vals(summary_data['Q-R2'], summary_data['R2-Q'])
                        summary_data['Q-I'] = df_utils.combine_vals(summary_data['Q-I1'], summary_data['I1-Q'])
                        summary_data['Q-I'] += df_utils.combine_vals(summary_data['Q-I2'], summary_data['I2-Q'])
                        summary_data['R-R_all'] = df_utils.combine_vals(summary_data['R1-R2'], summary_data['R2-R1'])
                        summary_data['R-R_all'] += df_utils.combine_vals(summary_data['R1-R1'], summary_data['R2-R2'])
                        summary_data['R-R'] = df_utils.combine_vals(summary_data['R1-R2'], summary_data['R2-R1'])
                        summary_data['R-I'] = df_utils.combine_vals(summary_data['R1-I1'], summary_data['I1-R1'])
                        summary_data['R-I'] += df_utils.combine_vals(summary_data['R1-I2'], summary_data['I2-R1'])
                        summary_data['R-I'] += df_utils.combine_vals(summary_data['R2-I1'], summary_data['R2-I1'])
                        summary_data['R-I'] += df_utils.combine_vals(summary_data['R2-I2'], summary_data['I2-R2'])
                        summary_data['I-I_all'] = df_utils.combine_vals(summary_data['I1-I2'], summary_data['I2-I1'])
                        summary_data['I-I_all'] += df_utils.combine_vals(summary_data['I1-I1'], summary_data['I2-I2'])
                        summary_data['I-I'] = df_utils.combine_vals(summary_data['I1-I2'], summary_data['I2-I1'])
                        summary_data['Q-N'] = df_utils.combine_vals(summary_data['Q-N'], summary_data['N-Q'])
                        summary_data['N-I'] = df_utils.combine_vals(summary_data['I1-N'], summary_data['I2-N'])
                        summary_data['N-I'] += df_utils.combine_vals(summary_data['N-I1'], summary_data['N-I2'])
                        summary_data['N-R'] = df_utils.combine_vals(summary_data['R1-N'], summary_data['R2-N'])
                        summary_data['N-R'] += df_utils.combine_vals(summary_data['N-R1'], summary_data['N-R2'])

                    summary_rows.append(summary_data)

                    # hack for default values
                    if len(default_row) == 0:
                        default_row = summary_data

        except Exception as e:
            failed.append((subjid,block))

            print( 'Failed for subject ' + str(subjid) + '_' + block)
            raise

    #output the fixation data for the grid plot
    output_fixationfile = os.path.join(settings.output_agg_dir, 'LSAT_TI_fixations.tsv')
    df_utils.output_rows(output_fixationfile, fixation_rows)

    # print the summary file
    output_summaryfile = os.path.join(settings.output_agg_dir, 'LSAT_TI_summary_gaze.tsv')
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
