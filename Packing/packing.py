# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

from scipy.spatial import distance

import math
from sklearn import preprocessing


class calculate_packing:

    def __init__(self):
        self.packing_rate = 0

    def get_pass_direction(self, sender, receiver, goal):
        """
        Get Pass Direction

        Returns: 
            Forward/Back/Side
        """
        # Distance of 3 sides sender-receiver-goal triangle
        d_sg = np.round(np.linalg.norm(sender-goal), 3)
        d_rg = np.round(np.linalg.norm(
            receiver-goal), 3)

        if (d_rg < d_sg) and (np.abs(d_rg-d_sg) > 0.02):
            return 'Forward'
        elif (d_rg > d_sg) and (np.abs(d_rg-d_sg) > 0.02):
            return 'Back'
        else:
            return 'Side'

    def method_1(self, a, b, c, d, df_m1, col_label_x, col_label_y, rect_thresh=0.1):
        """
        Method 1 - Create a rectangle box between sender and receiver to see if any player 
        is within the bounding box. A rect_thresh pf 0.1 is kept to consider players on the
        edge of the box.

        Parameters
        ----------
        a : ndarray
            ['sender_x', 'sender_y']
        b : ndarray
            ['sender_x', 'receiver_y']
        c : ndarray
            ['receiver_x', 'receiver_y']
        d : ndarray
            ['receiver_x', 'sender_y']
        df_m1 : DataFrame 
            A copy of defending_team_xy dataframe
        col_label_x : String
            The column label for defending team's X coordinate in defending_team_xy
        col_label_y : String
            The column label for defending team's Y coordinate in defending_team_xy
        rect_thresh : Float
            A threshold to check if any player is outside/on the edge of the box within
            the threshold distance

        Returns
        ----------
        df_m1 -- Dataframe with 1/0 for Method 1, bounding rectangle length and width

        """
        def area_triangle(s1, s2, s3):

            s = (s1 + s2 + s3) / 2.0
            area = (s*(s-s1)*(s-s2)*(s-s3)) ** 0.5

            if area == np.nan:
                return 0
            else:
                return np.round(area, 3)

        def checkCollision(df):
            method_1 = 0
            point_def = df[[col_label_x, col_label_y]].values.tolist()

            p_a = np.linalg.norm(point_def-a)
            p_b = np.linalg.norm(point_def-b)
            p_c = np.linalg.norm(point_def-c)
            p_d = np.linalg.norm(point_def-d)

            area_rect = np.round(ab*bc, 3)
            area_ab = area_triangle(p_a, p_b, ab)
            area_bc = area_triangle(p_b, p_c, bc)
            area_cd = area_triangle(p_c, p_d, cd)
            area_da = area_triangle(p_d, p_a, da)

            # Point lies inside the bounding box
            # rect_thresh = 0.1 is for normalized data

            if (area_ab + area_bc + area_cd + area_da) - area_rect < rect_thresh:
                method_1 = 1
            else:
                method_1 = 0

            return pd.to_numeric(pd.Series({'triangle_area': (area_ab + area_bc + area_cd + area_da),
                                            'rect_length': ab, 'rect_width': bc, 'method_1': method_1}),
                                 downcast='integer')

        # rectangle edges
        ab = np.linalg.norm(a-b)
        bc = np.linalg.norm(b-c)
        cd = np.linalg.norm(c-d)
        da = np.linalg.norm(d-a)

        df_m1[['triangle_area', 'rect_length', 'rect_width', 'method_1']
              ] = df_m1.apply(checkCollision, axis=1)

        return df_m1

    def method_2(self, p_s, p_r, df_m2, col_label_x, col_label_y, method2_radius=0.150):
        """
        Method 2 - If player is within a certain distance to line of pass so that 
        pass can potentially be intersected ignoring the speed of the pass

        Parameters
        ----------
        p_s : ndarray 
            ['sender_x', 'sender_y'] values
        p_r : ndarray 
            ['receiver_x', 'receiver_y'] values 
        df_m2 : DataFrame 
            Updated dataframe from Method 1
        radius : Float, default 0.150
            search radius for find if player can potentially intersect the pass
            by being within a given distance

        Returns
        ----------
        df_m2 : DataFrame
            Dataframe with 1/0 for Method 2
        """

        def check_intersection(df):
            method_2 = 0
            center = df[[col_label_x, col_label_y]].values

            line = np.linalg.norm(p_r - p_s)

            dist = np.round(np.abs(np.cross(p_r-p_s, p_r-center)) /
                            np.linalg.norm(p_r-p_s), 3)

            if (dist <= method2_radius):
                method_2 = 1
            else:
                method_2 = 0

            return pd.to_numeric(pd.Series({'method2_dist': dist,
                                            'method_2': method_2}),
                                 downcast='integer')

        df_m2[['method2_dist', 'method_2']] = df_m2.apply(
            check_intersection, axis=1)

        return df_m2

    def method_3(self, p_s, p_r, df_m3, col_label_x, col_label_y):
        """
        Method 3 - Check if pass is breaking the defending players lines (angles)

        Parameters
        ----------
        p_s : ndarray 
            ['sender_x', 'sender_y']
        p_r : ndarray 
            ['receiver_x', 'receiver_y'] 
        df_m3 : DataFrame 
            Updated dataframe from Method 2

        Returns
        ----------
        df_m3 : DataFrame 
            Dataframe with 1/0 for Method 3
        """
        def check_lines(df):
            method_3 = 0
            center = df[[col_label_x, col_label_y]].values

            d_sr = np.linalg.norm(p_s-p_r)
            d_sd = np.linalg.norm(p_s-center)
            d_rd = np.linalg.norm(p_r-center)

            angle_s = np.round(math.degrees(
                math.acos((d_sr**2 + d_sd**2 - d_rd**2)/(2.0 * d_sr * d_sd))))
            angle_r = np.round(math.degrees(
                math.acos((d_sr**2 + d_rd**2 - d_sd**2)/(2.0 * d_sr * d_rd))))

            if (angle_s <= 90.0) & (angle_r <= 90.0):
                method_3 = 1
            else:
                method_3 = 0
            return pd.to_numeric(pd.Series({'method2_angle_s': angle_s,
                                            'method2_angle_r': angle_r,
                                            'method_3': method_3}),
                                 downcast='integer')

        df_m3[['method2_angle_s', 'method2_angle_r', 'method_3']
              ] = df_m3.apply(check_lines, axis=1)

        return df_m3

    def update_method_1(self, df_update):
        """
        Method 1 Update - Check if bounding box is almost a line i.e: either width/length <= 0.07 units
        Then update the method_1 value to 1 if both method_2 and method_3 are 1

        Parameters
        ----------
        df_update : DataFrame
            Final dataframe after method 1,2 & 3

        Returns
        ----------
        df_update : DataFrame
            Final Dataframe with updated 1/0 for Method 1
        """
        rect_length = df_update['rect_length'].unique()[0]
        rect_width = df_update['rect_width'].unique()[0]

        if (rect_length <= 0.07) and (rect_width <= 0.07):
            df_update.loc[:, 'method_1'] = np.where(((df_update['method_1'] == 0) &
                                                     (df_update['method_2'] == 1) &
                                                     (df_update['method_3'] == 1)), 1, df_update['method_1'])

        return df_update

    def get_pass_pressure(self, sender_xy, receiver_xy, defending_team_xy, col_label_x, col_label_y,
                          ):
        """
        For defender who are not in the packing rate, if they are close (<=0.05 units) to the 
        sender/receiver, they're considered to be an influence on the pass, increasing the 
        pressure of the pass

        Parameters
        ----------
        sender_xy : ndarray 
            Sender XY coordinates as numpy array
        receiver_xy : ndarray
            Receiver XY coordinates as numpy array    
        defending_team_xy {[type]} -- [description]
            col_label_x {[type]} -- [description]
            col_label_y {[type]} -- [description]

        Returns
        ----------
            Total count of defenders putting pressure on pass
        """
        defend_xy = defending_team_xy[defending_team_xy['packing'] == 0][[
            col_label_x, col_label_y]].values
        sender_def_cdist = distance.cdist(sender_xy, defend_xy)
        receiver_def_cdist = distance.cdist(receiver_xy, defend_xy)

        sender_ids = np.array(
            np.where(sender_def_cdist[0] <= 0.05)).tolist()[0]
        receiver_ids = np.array(
            np.where(receiver_def_cdist[0] <= 0.05)).tolist()[0]

        pass_pressure_players = list(set(sender_ids) - set(receiver_ids))
        return len(pass_pressure_players)


class packing:
    """
    Find the packing for a given pass

    Parameters
    ----------
    sender_xy : ndarray
        Sender XY coordinates as numpy array
    receiver_xy : ndarray
        Receiver XY coordinates as numpy array
    defending_team_xy : DataFrame
        DataFrame with the defending team coordinates
    col_label_x : String
        The column label for defending team's X coordinate in defending_team_xy
    col_label_y : String
        The column label for defending team's Y coordinate in defending_team_xy
    defend_side : String
        The side of the defending team on the football pitch. Left/Right
    goal_center : Dict
        Center of goal, based on defend_side
        {'left': [-5250, 0], 'right': [5250, 0]} - Rescaled later

    Returns
    ----------
    packing_df : DataFrame
        Returns a dataframe with the following columns 
        ['triangle_area', 'rect_length', 'rect_width', 'method_1', 'method2_dist', 
        'method_2', 'method2_angle_s', 'method2_angle_r', 'method_3', 'packing', 
        col_label_x, col_label_y]
    packing_rate : Float
        Packing rate for that given pass scenario
        Packing rate will be multiplied by a factor based on the pass type:
        1.0 : Forward Pass
        -1.0 : Back Pass
        0.5 : Side pass
    pass_pressure : Integer
        Defending players who are closer to sender/receiver but not involved in 
        packing. Indicator to see if players take high risk pass. 
        For eg: packing rate could be lower but pass pressure can be higher if pass
        sender/receiver are heavily marked. 

    """

    def __init__(
        self,
        sender_xy: np.array,
        receiver_xy: np.array,
        defending_team_xy: pd.DataFrame,
        col_label_x: str,
        col_label_y: str,
        defend_side: str,
    ):
        self.sender_xy = np.array(sender_xy)
        self.receiver_xy = np.array(receiver_xy)
        self.defending_team_xy = defending_team_xy.copy()
        self.col_label_x = col_label_x
        self.col_label_y = col_label_y
        self.defend_side = defend_side
        self.goal_center = {'left': [-5250, 0], 'right': [5250, 0]}
        self.pass_pressure = None

    def get_packing(self):

        if self.sender_xy.size == 0:
            raise RuntimeError(
                "Sender coordinates are empty. A valid array with [x, y] should be provided")

        if self.receiver_xy.size == 0:
            raise RuntimeError(
                "Receiver coordinates are empty. A valid array with [x, y] should be provided")

        if self.defending_team_xy.size == 0:
            raise RuntimeError(
                "Defending team coordinates are empty. A valid dataframe with [x, y] should be provided for at least 1 player")

        if not isinstance(self.defending_team_xy, pd.DataFrame):
            raise RuntimeError(
                "Defending team coordinates should be a dataframe with x and y values.")

        defend_xy_cols = self.defending_team_xy.columns.tolist()
        if self.col_label_x not in defend_xy_cols or self.col_label_x not in defend_xy_cols:
            raise RuntimeError(
                f"Either {self.col_label_x} or {self.col_label_y} is not a column in defending_team_xy. Please provide valid column names")

        min_max_scaler = preprocessing.MinMaxScaler()
        defending_team_xy_scaled = min_max_scaler.fit_transform(
            self.defending_team_xy[[self.col_label_x, self.col_label_y]].values)
        self.defending_team_xy.drop(
            [self.col_label_x, self.col_label_y], axis=1, inplace=True)
        self.defending_team_xy[self.col_label_x], self.defending_team_xy[
            self.col_label_y] = defending_team_xy_scaled[:, 0], defending_team_xy_scaled[:, 1]

        self.sender_xy = min_max_scaler.transform(
            self.sender_xy.reshape(1, 2))[0]
        self.receiver_xy = min_max_scaler.transform(
            self.receiver_xy.reshape(1, 2))[0]

        box_a = np.array(self.sender_xy)  # sender
        box_b = np.array([self.sender_xy[0], self.receiver_xy[1]])
        box_c = np.array(list(self.receiver_xy))  # receiver
        box_d = np.array([self.receiver_xy[0], self.sender_xy[1]])

        self.goal_xy = min_max_scaler.transform(
            np.array(self.goal_center[self.defend_side]).reshape(1, 2))[0]

        cp = calculate_packing()

        self.pass_direction = cp.get_pass_direction(
            self.sender_xy, self.receiver_xy, self.goal_xy)

        self.packing_df = cp.method_1(
            box_a, box_b, box_c, box_d, self.defending_team_xy.copy(), col_label_x=self.col_label_x, col_label_y=self.col_label_y)

        self.packing_df = cp.method_2(
            box_a, box_c, self.packing_df, col_label_x=self.col_label_x, col_label_y=self.col_label_y)

        self.packing_df = cp.method_3(
            box_a, box_c, self.packing_df, col_label_x=self.col_label_x, col_label_y=self.col_label_y)

        self.packing_df = cp.update_method_1(self.packing_df)

        self.packing_df['packing'] = np.where(
            self.packing_df[["method_1", "method_2", "method_3"]].sum(axis=1) == 3, 1, 0)

        # If back pass, multiple packing by -1
        if self.pass_direction == 'Back':
            self.packing_df.loc[:,
                                'packing'] = self.packing_df.loc[:, 'packing']*-1.0
        elif self.pass_direction == 'Side':
            self.packing_df.loc[:,
                                'packing'] = self.packing_df.loc[:, 'packing']*0.5

        self.packing_rate = self.packing_df['packing'].sum()

        self.pass_pressure = cp.get_pass_pressure(self.sender_xy.reshape(1, -1), self.receiver_xy.reshape(1, -1),
                                                  self.packing_df, self.col_label_x,
                                                  self.col_label_y,)

        defending_team_xy_unscaled = min_max_scaler.inverse_transform(
            self.packing_df[[self.col_label_x, self.col_label_y]].values)
        self.packing_df.drop(
            [self.col_label_x, self.col_label_y], axis=1, inplace=True)
        self.packing_df[self.col_label_x], self.packing_df[
            self.col_label_y] = defending_team_xy_unscaled[:, 0], defending_team_xy_unscaled[:, 1]

        return self.packing_df, self.packing_rate, self.pass_pressure
