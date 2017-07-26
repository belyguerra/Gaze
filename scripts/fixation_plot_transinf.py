import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pylab
import os

### Creates fixation plot for transinf, with each aoi colored separately
#for some reason the plots don't' get saved :(

# modified from Mike's script

# file with fixation info
df = pd.read_table('/home/bunge/bguerra/EyeTracking/gaze_analysis/data/transif/results/T1/LSAT_TI_fixations_1.tsv')
subjects = pd.Series(df['PID'].values.ravel()).unique()
#test = [101, 102]
# can also replace subjects with a list of PIDs if only some plots needed
for subj in subjects:
    for block in ['A', 'B']:
        df_copy = df[(df['PID'] == subj) & (df['Block']==block)]
        plot_name = str(subj)+ '_' + block+ '.png'
        plot_file = os.path.join('/home/bunge/bguerra/EyeTracking/gaze_analysis/data/transif/results/T1/fixation_plots/', plot_name)

        # Create dictionary with trial number as key and fixation AOI and duration in a tuple as value
        myDict = {}
        for row, item in df_copy.iterrows():
            if df_copy['Trial'][row] not in myDict:
                myDict[df_copy['Trial'][row]] = []
                myDict[df_copy['Trial'][row]].append((df_copy['AOI'][row], df_copy['Fixation_Dur'][row]))
            elif df_copy['Trial'][row] in myDict:
                myDict[df_copy['Trial'][row]].append((df_copy['AOI'][row], df_copy['Fixation_Dur'][row]))

        print str(subj)+block

        # Calculate the total trial duration
        trials = pd.Series(df_copy['Trial'].values.ravel()).unique()
        trial_durs = []

        for i, trial in enumerate(trials):
            duration = []
            for row,item in enumerate(myDict[trial]):
                duration.append(myDict[trial][row][1])
                trial_durs.append(sum(duration))

        trial_durs = np.array(trial_durs)

            # Create the plot
        fig, ax = plt.subplots()

        for i, trial in enumerate(trials):
            point = 0
            for row, item in enumerate(myDict[trial]):
                if myDict[trial][row][0] == 'Q':
                    ax.broken_barh([(point, myDict[trial][row][1])], ((i+1)*10, 9), facecolors='black')
                    point += myDict[trial][row][1]
                elif myDict[trial][row][0] == 'R1':
                    ax.broken_barh([(point, myDict[trial][row][1])], ((i+1)*10, 9), facecolors='green')
                    point += myDict[trial][row][1]
                elif myDict[trial][row][0] == 'R2':
                    ax.broken_barh([(point, myDict[trial][row][1])], ((i+1)*10, 9), facecolors='blue')
                    point += myDict[trial][row][1]
                elif myDict[trial][row][0] == 'I1':
                    ax.broken_barh([(point, myDict[trial][row][1])], ((i+1)*10, 9), facecolors='red')
                    point += myDict[trial][row][1]
                elif myDict[trial][row][0] == 'I2':
                    ax.broken_barh([(point, myDict[trial][row][1])], ((i+1)*10, 9), facecolors='magenta')
                    point += myDict[trial][row][1]
                else:
                    ax.broken_barh([(point, myDict[trial][row][1])], ((i+1)*10, 9), facecolors='gray')
                    point += myDict[trial][row][1]

        print 'hello'

        index = 0
        ticks = []

        for x in range(0, len(trials)+1):
                tick = (index + 1) * 10 + 5
                ticks.append(tick)
                index += 1

        ax.set_title(str(subj)+ block+': Fixations in AOIs')
        ax.set_ylim(5, len(trials))
        ax.set_xlim(0, trial_durs.max()+1000)
        ax.set_xlabel('milliseconds since start')
        ax.set_ylabel('Trial')
        ax.set_yticks(ticks)
        ax.set_yticklabels(trials)
        ax.grid(False)
        print "hi"
        # Format the legend, define labels
        Q = mpatches.Patch(color='yellow', label='Q')
        R1 = mpatches.Patch(color='green', label='R1')
        R2 = mpatches.Patch(color='blue', label='R2')
        I1 = mpatches.Patch(color='red', label='I1')
        I2 = mpatches.Patch(color='magenta', label='I2')
        N = mpatches.Patch(color='gray', label='N')
        lgd = plt.legend(handles=[Q, R1, R2, I1, I2, N], bbox_to_anchor=(1, 1), loc=2, ncol=1, borderaxespad=0)

        plt.savefig(plot_file, bbox_inches='tight')