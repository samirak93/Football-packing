# -*- coding: utf-8 -*-
"""
* Find packing for real-time metrica data

* Owner: Samira Kumar
* Version: V1.0
* Last Updated: May-14-2020
"""
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy.spatial import distance
from collections import defaultdict

import itertools
import random

# Import custom packages

from packing import packing, calculate_packing
from plot_packing import plot_packing

pd.set_option('display.max_rows', 120)
pd.set_option('display.max_rows', None)


class metrica:
    def __init__(
        self,
        path_play_df: str,
        path_event_df: str,
        game_id: list
    ):
        self.path_play_df = path_play_df
        self.path_event_df = path_event_df
        self.game_id = game_id
        self.defend_side = ""
        self.goal_center = {'left': (0, 0.5), 'right': (1, 0.5)}

    def plot(self, passer_team_df, packing_df, r_x, r_y, packing_rate, sender_xy, receiver_xy,
             pass_start_frame, pass_pressure=None, def_defline=None):
        """
        Creating plot to visualize
        """

        font = {'family': 'serif', 'color':  'darkred',
                'weight': 'normal', 'size': 10, 'ha': 'center'}

        plt.figure(figsize=(8, 5))
        plt.title("Packing rate: {}\n Pass pressure: {}\n Defensive Line: {}".format(packing_rate, pass_pressure,
                                                                                     def_defline), fontdict=font)
        pitch = plt.imread('images/pitch/pitch.jpg')
        plt.imshow(pitch, extent=[0, 1, 1, 0])

        plt.scatter(passer_team_df['x'].tolist(),
                    passer_team_df['y'].tolist(), c='yellow', s=10)

        plt.scatter(sender_xy[0], sender_xy[1], c='red', s=30)
        plt.text(sender_xy[0], sender_xy[1], 'S', horizontalalignment='center',
                 verticalalignment='center', fontsize=12)

        plt.scatter(receiver_xy[0], receiver_xy[1], c='blue', s=30)
        plt.text(receiver_xy[0], receiver_xy[1], 'R',  horizontalalignment='center',
                 verticalalignment='center', fontsize=12)

        colors = {1: 'red', 0: 'green'}

        for i in range(len(packing_df['x'].tolist())):
            x = packing_df.iloc[i]['x']
            y = packing_df.iloc[i]['y']
            edge_col = colors[packing_df.iloc[i]['packing']]

            s = 10
            if packing_df.iloc[i]['packing'] == 1:
                s = 20

            plt.scatter(x, y, linewidths=2, c='green',
                        edgecolors=edge_col, s=s)
            plt.text(x-(x*0.04), y-(y*0.01), i, fontsize=8)

        self.box_a = np.array(sender_xy)
        self.box_b = np.array([sender_xy[0], receiver_xy[1]])
        self.box_c = np.array(list(receiver_xy))  # receiver
        self.box_d = np.array([receiver_xy[0], sender_xy[1]])

        plt.plot((self.box_a[0], self.box_b[0]),
                 (self.box_a[1], self.box_b[1]), linewidth=2, c='orange')
        plt.plot((self.box_b[0], self.box_c[0]),
                 (self.box_b[1], self.box_c[1]), linewidth=2, c='orange')
        plt.plot((self.box_c[0], self.box_d[0]),
                 (self.box_c[1], self.box_d[1]), linewidth=2, c='orange')
        plt.plot((self.box_d[0], self.box_a[0]),
                 (self.box_d[1], self.box_a[1]), linewidth=2, c='orange')

        plt.axis('off')

        plt.show()

    def write_files(self, df, file_name, overwrite=False):
        """
        * Save dataframes into csv

        * Arguments:
            df {dataframe} --  dataframe

        * Keyword Arguments:
            overwrite {bool} -- Either overwrite the file or not (give warning) (default: {True})

        """

        if len(df.index) == 0:
            print("No data to write...")
        else:
            if overwrite == True:
                df.to_csv('data/temp_'+file_name+'.csv', index=False)
                print(file_name+'.csv saved to data/temp...')
            else:
                print("File not saved as overwrite is set to False...")

    def get_defend_side(self, defending_team_xy, passing_team_xy):
        """
        * Process to identify which side the defending team defends
        """

        total_defend_left = defending_team_xy[defending_team_xy['x']
                                              <= 0.2]['x'].count()
        total_defend_right = defending_team_xy[defending_team_xy['x']
                                               >= 0.8]['x'].count()
        total_passer_left = passing_team_xy[passing_team_xy['x']
                                            <= 0.21]['x'].count()

        # 2. When only one end of pitch has a defender/gk

        if (((total_defend_left == 0) and (total_defend_right > 0)) or ((total_defend_left > 0) and (total_defend_right == 0))):

            if (total_defend_right > 0):
                self.defend_side = 'right'
            else:
                self.defend_side = 'left'

        # 1. When both end of pitch has a last man

        elif (total_defend_left > 0) and (total_defend_right > 0):

            # 1.1 When last man is on left and no attacking player near him
            if (total_defend_left > 0) and (total_passer_left == 0):
                self.defend_side = 'left'

            else:
                # 1.2
                self.defend_side = 'right'

    def get_pass_direction(self, sender, receiver, goal):
        """
        * Get Pass Direction

        * Returns: Forward/Back/Side

        """
        # distance of 3 sides sender-receiver-goal triangle

        d_sg = np.round(np.linalg.norm(sender-goal), 3)
        d_rg = np.round(np.linalg.norm(
            receiver-goal), 3)

        if (d_rg < d_sg) and (np.abs(d_rg-d_sg) > 0.02):
            return 'Forward'
        elif (d_rg > d_sg) and (np.abs(d_rg-d_sg) > 0.02):
            return 'Back'
        else:
            return 'Side'

    def process_data(self):

        game_events = pd.read_csv(self.path_event_df)
        play_df = pd.read_csv(self.path_play_df, dtype={
                              'frame': 'int', 'player': 'str', 'game_id': 'str'})

        play_df = play_df[play_df['game_id'] == self.game_id]
        event_type = ['PASS']

        game_events = game_events[game_events['Type'].isin(event_type)]

        game_events.loc[:, 'From'] = game_events['From'].str.replace(
            'Player', '')
        game_events.loc[:, 'To'] = game_events['To'].str.replace(
            'Player', '')

        random_index = random.choice(game_events.index.values)
        random_game_events = game_events[game_events.index == random_index]

        random_end_frame = random_game_events['End Frame'].values[0]
        random_sender = random_game_events['From'].values[0]
        random_receiver = random_game_events['To'].values[0]
        random_passing_team = random_game_events['Team'].values[0]

        random_play_end_df = play_df[play_df['frame']
                                     == random_end_frame].reset_index(drop=True)

        sender_xy = random_play_end_df[random_play_end_df['player'] == random_sender][[
            'x', 'y']].values[0]
        receiver_xy = random_play_end_df[random_play_end_df['player'] == random_receiver][[
            'x', 'y']].values[0]

        if random_passing_team == 'Away':
            passing_team_xy = random_play_end_df[(random_play_end_df['team'] == 'away') &
                                                 (random_play_end_df['player']
                                                  != random_sender)
                                                 & (random_play_end_df['player'] != random_receiver)][[
                                                     'x', 'y', 'player']].dropna()
            defending_team_xy = random_play_end_df[random_play_end_df['team'] == 'home'][[
                'x', 'y', 'player']].dropna()
        else:
            passing_team_xy = random_play_end_df[(random_play_end_df['team'] == 'home') &
                                                 (random_play_end_df['player']
                                                  != random_sender)
                                                 & (random_play_end_df['player'] != random_receiver)][[
                                                     'x', 'y', 'player']].dropna()
            defending_team_xy = random_play_end_df[random_play_end_df['team'] == 'away'][[
                'x', 'y', 'player']].dropna()

        self.get_defend_side(defending_team_xy, passing_team_xy)

        pack = packing(sender_xy, receiver_xy,
                       defending_team_xy, col_label_x='x', col_label_y='y', defend_side=self.defend_side)
        self.packing_df, self.packing_rate, self.pass_pressure = pack.get_packing()

        plot = plot_packing(passer_team_df=passing_team_xy, packing_df=self.packing_df, col_label_x='x', col_label_y='y',
                            packing_rate=self.packing_rate,  pass_pressure=self.pass_pressure,
                            sender_xy=sender_xy, receiver_xy=receiver_xy,
                            x_range=[0, 1], y_range=[1, 0], pass_frame=random_end_frame, file_name='metrica', plot_hint='off')

        plot.plot()


if __name__ == '__main__':

    prev_level_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../..'))

    metrica_path = os.path.join(prev_level_path, 'Metrica/sample-data/data/')
    path_play_df = metrica_path+'metrica_tracking_tidy.csv'
    path_event_df = metrica_path+'Sample_Game_1/Sample_Game_1_RawEventsData.csv'

    game_id = '1'
    metric = metrica(path_play_df, path_event_df, game_id)
    metric.process_data()
