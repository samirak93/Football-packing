# -*- coding: utf-8 -*-
"""
* Find packing for real-time metrica data

* Owner: Samira Kumar
* Version: V1.0
* Last Updated: May-14-2020
"""
import os
import sys

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy.spatial import distance
from collections import defaultdict

import itertools
import random

# Import custom packages

from football_packing import packing
from football_packing import plot_packing

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


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
                'x', 'y', 'player']].dropna().set_index('player', drop=False)
        else:
            passing_team_xy = random_play_end_df[(random_play_end_df['team'] == 'home') &
                                                 (random_play_end_df['player']
                                                  != random_sender)
                                                 & (random_play_end_df['player'] != random_receiver)][[
                                                     'x', 'y', 'player']].dropna()
            defending_team_xy = random_play_end_df[random_play_end_df['team'] == 'away'][[
                'x', 'y', 'player']].dropna().set_index('player', drop=False)

        defending_team_xy = defending_team_xy.rename(
            columns={'player': 'player_id'})

        self.get_defend_side(defending_team_xy, passing_team_xy)

        pack = packing(sender_xy, receiver_xy,
                       defending_team_xy, col_label_x='x', col_label_y='y', defend_side=self.defend_side)
        self.packing_df, self.packing_rate, self.pass_pressure = pack.get_packing()

        plot = plot_packing(passer_team_df=passing_team_xy, packing_df=self.packing_df,
                            col_label_x='x', col_label_y='y',
                            packing_rate=self.packing_rate,  pass_pressure=self.pass_pressure,
                            sender_xy=sender_xy, receiver_xy=receiver_xy,
                            x_range=[0, 1], y_range=[1, 0], path_to_save=dir_path+'/',
                            pass_frame=random_end_frame, file_name='metrica',
                            bcg_img='/images/pitch/pitch.jpg')

        plot.plot()


if __name__ == '__main__':

    dir_path = os.path.dirname(os.path.realpath(__file__))

    """
    Path to the game level data -
    Use this Tidy data - https://drive.google.com/drive/folders/1BGLHbe7DB_NGZxitjJAQxu2-N-B4Zk3s
    Credit - Eliot McKinley
    """
    path_game_df = sys.argv[1]
    # Path to the event level data
    path_events_df = sys.argv[2]

    game_id = '1'
    metric = metrica(path_game_df, path_events_df, game_id)
    metric.process_data()
