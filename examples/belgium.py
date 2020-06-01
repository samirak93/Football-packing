# -*- coding: utf-8 -*-
"""
Find packing for Belgian football data (https://github.com/JanVanHaaren/mlsa18-pass-prediction)

Owner: Samira Kumar
Version: V2.0
Last Updated: May-20-2020

"""
#import modules
import numpy as np
import pandas as pd

from football_packing import packing
from football_packing import plot_packing

import os
import math

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


class belgium:
    """
    Find the packing for a given play

    Arguments:
            df {string} -- source for the data
            play_id {string} -- Id for the given pass - taken from index of df
            defend_side {string} -- Side of the defending team
            pass_direction {string} -- Direction of pass - Forward, Back or Side
            pass_pressure {int} -- Total players that put pressure on sender & receiver (excluding players involved
                                    in packing)
            goal_center -- Center of goal, based on defend_side

    Returns:
            packing_rate {int} -- packing rate for that given pass option (Eg: player A --> B)
            plot (figure) -- matplotlib figure with player location and packing rate
    """

    def __init__(
        self,
        df,
        play_id
    ):
        self.df = df
        self.play_id = play_id
        self.defend_side = ""
        self.pass_direction = ""
        self.pass_pressure = 0
        self.packing_rate = 0
        self.goal_center = {'left': (-5250, 0), 'right': (5250, 0)}

    def get_pass_direction(self, sender: np.array, receiver: np.array, goal: np.array):
        """
        Get the direction of the pass.

        Arguments:
            sender {np.array} -- XY location of the sender
            receiver {np.array} -- XY location of the receiver
            goal {np.array} -- XY location of the goal

        Returns:
            direction -- Forward/Back/Side
        """

        # Distance of 3 sides sender-receiver-goal triangle

        d_sr = np.linalg.norm(sender-receiver)
        d_sg = np.linalg.norm(sender-goal)
        d_rg = np.linalg.norm(receiver-goal)

        angle_s = math.degrees(
            math.acos((d_sr**2 + d_sg**2 - d_rg**2)/(2.0 * d_sr * d_sg)))
        angle_g = math.degrees(
            math.acos((d_rg**2 + d_sg**2 - d_sr**2)/(2.0 * d_rg * d_sg)))
        angle_r = math.degrees(
            math.acos((d_sr**2 + d_rg**2 - d_sg**2)/(2.0 * d_sr * d_rg)))

        if (d_rg < d_sg) and ((angle_r >= 90) or (angle_r >= angle_g)):
            return "Forward"
        elif (d_rg > d_sg) and ((angle_s >= 90) or (angle_r >= angle_g)):
            return "Back"
        else:
            return "Side"

    def process_data(self):
        """
        Process the source data to get it in the necessary format
        """

        self.df.loc[:, 'home_away'] = self.df['sender_id'].apply(
            lambda x: 1 if x < 15 else 0)

        # Get pass sender and receiver location

        self.df.loc[:, 'sender_x'] = self.df.apply(
            lambda x: x.iloc[x['sender_id'].astype(int)+3], axis=1)
        self.df.loc[:, 'sender_y'] = self.df.apply(
            lambda x: x.iloc[x['sender_id'].astype(int)+31], axis=1)
        self.df.loc[:, 'receiver_x'] = self.df.apply(
            lambda x: x.iloc[x['receiver_id'].astype(int)+3], axis=1)
        self.df.loc[:, 'receiver_y'] = self.df.apply(
            lambda x: x.iloc[x['receiver_id'].astype(int)+31], axis=1)

        # Get passing and defender team location

        self.df.loc[:, 'passer_team_x'] = self.df.apply(lambda x: x.iloc[4:18].dropna(
        ).values.tolist() if x['home_away'] == 1 else x.iloc[18:32].dropna().values.tolist(), axis=1)
        self.df.loc[:, 'passer_team_y'] = self.df.apply(lambda x: x.iloc[32:46].dropna(
        ).values.tolist() if x['home_away'] == 1 else x.iloc[46:60].dropna().values.tolist(), axis=1)
        self.df.loc[:, 'defender_team_x'] = self.df.apply(lambda x: x.iloc[4:18].dropna(
        ).values.tolist() if x['home_away'] == 0 else x.iloc[18:32].dropna().values.tolist(), axis=1)
        self.df.loc[:, 'defender_team_y'] = self.df.apply(lambda x: x.iloc[32:46].dropna(
        ).values.tolist() if x['home_away'] == 0 else x.iloc[46:60].dropna().values.tolist(), axis=1)

        # Get passing and receiving team player ids
        passer_team_ids = self.df.apply(lambda x: x.iloc[4:18].dropna(
        ).index.tolist() if x['home_away'] == 1 else x.iloc[18:32].dropna().index.tolist(), axis=1).values.tolist()[0]
        self.df.loc[:, 'passer_team_id'] = pd.Series(
            [[int(i.replace('x_', '')) for i in passer_team_ids]])

        defend_team_ids = self.df.apply(lambda x: x.iloc[4:18].dropna(
        ).index.tolist() if x['home_away'] == 0 else x.iloc[18:32].dropna().index.tolist(), axis=1).values.tolist()[0]
        self.df.loc[:, 'defend_team_id'] = pd.Series(
            [[int(i.replace('x_', '')) for i in defend_team_ids]])

        team_x = {'defender_team_x': self.df['defender_team_x'].tolist()[0],
                  "passer_team_x": self.df['passer_team_x'].tolist()[0]}
        team_x_df = pd.DataFrame.from_dict(team_x, orient='index').fillna(0).T
        team_x_df['defender_pitch'] = np.where(
            team_x_df['defender_team_x'] <= 0, 'left', 'right')
        team_x_df['passer_pitch'] = np.where(
            team_x_df['passer_team_x'] <= 0, 'left', 'right')

        """
        Process to identify which side the defending team defends
        """

        total_defend_left = team_x_df[team_x_df['defender_team_x']
                                      <= -2000]['defender_team_x'].count()
        total_defend_right = team_x_df[team_x_df['defender_team_x']
                                       >= 2000]['defender_team_x'].count()
        total_passer_left = team_x_df[team_x_df['passer_team_x']
                                      <= -2100]['passer_team_x'].count()

        # 1. When only one end of pitch has a defender/gk

        if (((total_defend_left == 0) and (total_defend_right > 0)) or ((total_defend_left > 0) and (total_defend_right == 0))):

            if (total_defend_right > 0):
                self.defend_side = 'right'
            else:
                self.defend_side = 'left'

        # 2. When both end of pitch has a last man

        elif (total_defend_left > 0) and (total_defend_right > 0):

            # 2.1 When last man is on left and no attacking player near him
            if (total_defend_left > 0) and (total_passer_left == 0):
                self.defend_side = 'left'

            else:
                # 2.2
                self.defend_side = 'right'

        pass_sr = {'sender': list(zip(self.df['sender_x'], self.df['sender_y'])),
                   'receiver': list(zip(self.df['receiver_x'], self.df['receiver_y']))}

        # Get pass direction based on defending team side
        self.pass_direction = self.get_pass_direction(np.array(pass_sr['sender']), np.array(
            pass_sr['receiver']), np.array(self.goal_center[self.defend_side]))

        def_team_xy = {'defender_team_x': self.df['defender_team_x'].tolist()[0],
                       "defender_team_y": self.df['defender_team_y'].tolist()[0],
                       'passer_team_x': self.df['passer_team_x'].tolist()[0],
                       "passer_team_y": self.df['passer_team_y'].tolist()[0],
                       "defend_team_id":  self.df['defend_team_id'].tolist()[0]}

        self.def_team_xy_df = pd.DataFrame.from_dict(
            def_team_xy, orient='index').fillna(0).T.set_index('defend_team_id', drop=False)

        self.def_team_xy_df.loc[:, 'sender'] = np.where(((self.def_team_xy_df['passer_team_x'] == self.df['sender_x'].values[0])
                                                         & (self.def_team_xy_df['passer_team_y'] == self.df['sender_y'].values[0])), 1, 0)
        self.def_team_xy_df.loc[:, 'receiver'] = np.where(((self.def_team_xy_df['passer_team_x'] == self.df['receiver_x'].values[0])
                                                           & (self.def_team_xy_df['passer_team_y'] == self.df['receiver_y'].values[0])), 1, 0)
        # self.def_team_xy_df.set_index('defend_team_id')

    def packing_calculate(self):

        sender_xy = self.df[['sender_x', 'sender_y']].values[0]
        receiver_xy = self.df[['receiver_x', 'receiver_y']].values[0]

        pack = packing(sender_xy, receiver_xy, self.def_team_xy_df,
                       col_label_x='defender_team_x', col_label_y='defender_team_y',
                       defend_side=self.defend_side)
        self.packing_df, self.packing_rate, self.pass_pressure = pack.get_packing()

        passing_team_xy = pd.DataFrame({'passer_team_x': self.df['passer_team_x'].tolist()[0],
                                        'passer_team_y': self.df['passer_team_y'].tolist()[0],
                                        'passer_team_id': self.df['passer_team_id'].tolist()[0]})

        plot = plot_packing(passer_team_df=passing_team_xy, packing_df=self.packing_df,
                            col_label_x='defender_team_x', col_label_y='defender_team_y',
                            packing_rate=self.packing_rate, pass_pressure=self.pass_pressure,
                            sender_xy=sender_xy, receiver_xy=receiver_xy,
                            x_range=[-5250, 5250], y_range=[3400, -3400],
                            path_to_save=dir_path+'/', pass_frame=self.play_id, file_name='belgium',
                            bcg_img='/images/pitch/pitch.jpg')
        plot.plot()

    def execute_pack(self):
        # Looping functions
        steps = (
            self.process_data(),
            self.packing_calculate(),
        )

        for step in steps:
            step


if __name__ == '__main__':

    dir_path = os.path.dirname(os.path.realpath(__file__))
    df = pd.read_csv(dir_path+"/data/passes.csv")
    df.loc[:, 'pass_success'] = np.where(((df['sender_id'] <= 14) & (df['receiver_id'] <= 14))
                                         | ((df['sender_id'] > 14) & (df['receiver_id'] > 14)), 1, 0)

    df = df.loc[(df['pass_success'] == 1) & (df['sender_id'] !=
                                             df['receiver_id']), :].copy().reset_index(drop=True)
    df = df.sample(1).copy()
    play_id = str(df.index.values[0])
    df = df.reset_index(drop=True)
    pack_belgium = belgium(df, play_id)
    pack_belgium.execute_pack()
