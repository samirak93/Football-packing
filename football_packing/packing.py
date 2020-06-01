# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

from scipy.spatial import distance

import math
from sklearn import preprocessing


class calculate_packing:

    def __init__(self):
        self.packing_rate = 0

    def get_pass_direction(self, sender, receiver, goal, defend_side):
        """
        Get Pass Direction

        Returns:
            Forward/Back/Side
        """
        if defend_side == 'left':
            goal_sender = [0, sender[1]]
            goal_receiver = [0, receiver[1]]
        elif defend_side == 'right':
            goal_sender = [1, sender[1]]
            goal_receiver = [1, receiver[1]]

        # Distance of 3 sides sender-receiver-goal triangle
        d_sg = np.round(np.linalg.norm(sender-goal_sender), 5)
        d_rg = np.round(np.linalg.norm(
            receiver-goal_receiver), 5)

        if (d_rg < d_sg) and (np.abs(d_rg-d_sg) > 0.03):
            return 'Forward'
        elif (d_rg > d_sg) and (np.abs(d_rg-d_sg) > 0.03):
            return 'Back'
        else:
            return 'Side'

    def method_1(self, box_a, box_b, box_c, box_d, df_method1, col_label_x, col_label_y, rect_thresh=0.010):
        """
        Method 1 :
        Draw a rectangle box between sender and receiver to see if any player
        is inside the bounding box. A rect_thresh of 0.01 is used to consider players on the
        edge of the box.

        Parameters
        ----------
        box_a : ndarray
            A ndarray of ['sender_x', 'sender_y']
        box_b : ndarray
            A ndarray of ['sender_x', 'receiver_y']
        box_c : ndarray
            A ndarray of ['receiver_x', 'receiver_y']
        box_d : ndarray
            A ndarray of ['receiver_x', 'sender_y']
        df_method1 : DataFrame
            A copy of defending_team_xy dataframe
        col_label_x : String
            The column label for defending team's X coordinate in `defending_team_xy`
        col_label_y : String
            The column label for defending team's Y coordinate in `defending_team_xy`
        rect_thresh : Float, default 0.015
            A threshold to check if any player is outside/on the edge of the box within
            the threshold distance

        Returns
        ----------
        df_method1 : DataFrame
            A copy of original DataFrame with 1/0 for Method 1 and the following new columns :
            `triangle_area` : Float, `rect_length` : Float, `rect_width` : Float, `method_1` : Binary
        """
        def area_triangle(s1, s2, s3):

            s = (s1 + s2 + s3) / 2.0
            area = (s*(s-s1)*(s-s2)*(s-s3)) ** 0.5

            if area == np.nan:
                return 0
            else:
                return np.round(area, 5)

        def checkBoundary(df):
            method_1 = 0
            point_def = df[[col_label_x, col_label_y]].values.tolist()

            p_a = np.round(np.linalg.norm(point_def-box_a), 5)
            p_b = np.round(np.linalg.norm(point_def-box_b), 5)
            p_c = np.round(np.linalg.norm(point_def-box_c), 5)
            p_d = np.round(np.linalg.norm(point_def-box_d), 5)

            area_rect = np.round(ab*bc, 5)
            area_ab = area_triangle(p_a, p_b, ab)
            area_bc = area_triangle(p_b, p_c, bc)
            area_cd = area_triangle(p_c, p_d, cd)
            area_da = area_triangle(p_d, p_a, da)

            # Check if player xy lies inside the bounding box
            # rect_thresh = 0.010 is for normalized data

            if ((area_ab + area_bc + area_cd + area_da) - area_rect) <= rect_thresh:
                method_1 = 1
            else:
                method_1 = 0

            return pd.to_numeric(pd.Series({'triangle_area': (area_ab + area_bc + area_cd + area_da),
                                            'rect_length': ab, 'rect_width': bc,
                                            'area_diff': ((area_ab + area_bc + area_cd + area_da) - area_rect),
                                            'method_1': method_1}),
                                 downcast='integer')

        # rectangle edges
        ab = np.round(np.linalg.norm(box_a-box_b), 5)
        bc = np.round(np.linalg.norm(box_b-box_c), 5)
        cd = np.round(np.linalg.norm(box_c-box_d), 5)
        da = np.round(np.linalg.norm(box_d-box_a), 5)

        df_method1[['triangle_area', 'rect_length', 'rect_width', 'area_diff', 'method_1']
                   ] = df_method1.apply(checkBoundary, axis=1)

        return df_method1

    def method_2(self, sender_xy, receiver_xy, df_method2, col_label_x, col_label_y, method2_radius=0.12):
        """
        Method 2 :
        Check if player is within a certain distance to line of pass, so that
        the pass can potentially be intersected (assuming the speed of pass is not a factor).

        For a given defender, assume the defender xy to be center of circle. Find the perpendicular
        distance from player xy to the line of pass. If the distance is <= method2_radius, then method_2
        returns as 1, else 0.

        Parameters
        ----------
        sender_xy : ndarray
            A ndarray of ['sender_x', 'sender_y']
        receiver_xy : ndarray
            A ndarray of ['receiver_x', 'receiver_y']
        df_method2 : DataFrame
            A copy of defending_team_xy dataframe, updated from `Method 1`
        radius : Float, default 0.150
            search radius for find if player can potentially intersect the pass
            by being within a given distance

        Returns
        ----------
        df_method2 : DataFrame
            A copy of original DataFrame with 1/0 for Method 2 and the following new columns :
            `method2_dist` : Distance of player to line of pass,
            `method_2` : Binary, (1/0)
        """

        def check_intersection(df):
            """
            If rectangle from method_1 is big enough ((rect_length > 0.01) or (rect_width > 0.01)),
            take a diagonal (non player) side of the rectangle and find the perpendicular distance
            between it and the line of pass. If a defending player is within that distance to the
            line of pass, then method_2 = 1.

            If rectangle is small, then use method2_radius to check if a defending player
            is within that distance to the line of pass.
            """
            method_2 = 0

            # Defender point
            center = df[[col_label_x, col_label_y]].values
            dist_dl = np.round(np.abs(np.cross(receiver_xy-sender_xy, sender_xy-center)) /
                               np.linalg.norm(receiver_xy-sender_xy), 5)

            # Box diagonal
            box_diagonal = np.array([sender_xy[0], receiver_xy[1]])
            dist_box_line = np.round(np.abs(np.cross(receiver_xy-sender_xy, sender_xy-box_diagonal)) /
                                     np.linalg.norm(receiver_xy-sender_xy), 5)

            rect_length = df['rect_length']
            rect_width = df['rect_width']

            if (rect_length <= 0.07) or (rect_width <= 0.07):
                if (dist_dl <= method2_radius):
                    method_2 = 1
                else:
                    method_2 = 0
            elif dist_dl <= dist_box_line:
                method_2 = 1
            else:
                method_2 = 0

            return pd.to_numeric(pd.Series({'method2_dist': dist_dl,
                                            'method_2': method_2}),
                                 downcast='integer')

        df_method2[['method2_dist', 'method_2']] = df_method2.apply(
            check_intersection, axis=1)

        return df_method2

    def method_3(self, sender_xy, receiver_xy, df_method3, col_label_x, col_label_y):
        """
        Method 3 :
        Check defender angle with respect to sender & receiver.
        One of the draw back of `method_2` is that defender can be close to line to pass
        but still be beyond the sender or receiver (one of angle b/w defender & sender/receiver > 90).
        This method checks this condition.

        Parameters
        ----------
        sender_xy : ndarray
            A ndarray of ['sender_x', 'sender_y']
        receiver_xy : ndarray
            A ndarray of ['receiver_x', 'receiver_y']
        df_method3 : DataFrame
            A copy of defending_team_xy dataframe, updated from `Method 2`

        Returns
        ----------
        df_method3 : DataFrame
            A copy of original DataFrame with 1/0 for Method 3 and the following new columns :
            `method3_angle_s` : Angle between defender & sender,
            `method3_angle_r` : Angle between defender & receiver,
            `method_3` : Binary, (1/0)
        """
        def check_angles(df):
            method_3 = 0
            center = df[[col_label_x, col_label_y]].values

            # Distance between sender, receiver & defender combination
            d_sr = np.linalg.norm(sender_xy-receiver_xy)
            d_sd = np.linalg.norm(sender_xy-center)
            d_rd = np.linalg.norm(receiver_xy-center)

            angle_s = np.round(math.degrees(
                math.acos((d_sr**2 + d_sd**2 - d_rd**2)/(2.0 * d_sr * d_sd))))
            angle_r = np.round(math.degrees(
                math.acos((d_sr**2 + d_rd**2 - d_sd**2)/(2.0 * d_sr * d_rd))))

            if (angle_s <= 105) & (angle_r <= 105):
                method_3 = 1
            else:
                method_3 = 0

            return pd.to_numeric(pd.Series({'method3_angle_s': angle_s,
                                            'method3_angle_r': angle_r,
                                            'method_3': method_3}),
                                 downcast='integer')

        df_method3[['method3_angle_s', 'method3_angle_r', 'method_3']
                   ] = df_method3.apply(check_angles, axis=1)

        return df_method3

    def update_method_1(self, df_update):
        """
        Method 1 Update :
        For special cases where bounding box from `Method 1` is almost a line i.e: either width/length <= 0.07 units
        (both sender and receiver are in similar X or Y coordinate).
        In this case, update the value of method_1 value to 1 if both method_2 and method_3 are 1.

        Parameters
        ----------
        df_update : DataFrame
            The copy of DataFrame after Methods 1,2 & 3.

        Returns
        ----------
        df_update : DataFrame
            Final Dataframe with updated 1/0 for Method 1
        """
        rect_length = df_update['rect_length'].unique()[0]
        rect_width = df_update['rect_width'].unique()[0]

        if (rect_length <= 0.07) or (rect_width <= 0.07):
            df_update.loc[:, 'method_1_update'] = np.where(((df_update['method_1'] == 0) &
                                                            (df_update['method_2'] == 1) &
                                                            (df_update['method_3'] == 1)), 1, df_update['method_1'])
        else:
            df_update.loc[:, 'method_1_update'] = df_update['method_1']

        return df_update

    def get_pass_pressure(self, sender_xy, receiver_xy, defending_team_xy, col_label_x, col_label_y):
        """
        For defender who are not in the packing rate, if they are close (<=0.05 units) to the
        sender/receiver, they're considered to have an influence on the pass by increasing the
        pressure of the pass.

        Parameters
        ----------
        sender_xy : ndarray
            Sender XY coordinates as numpy array
        receiver_xy : ndarray
            Receiver XY coordinates as numpy array
        defending_team_xy : DataFrame
            DataFrame with the defending team coordinates
        col_label_x : String
            The column label for defending team's X coordinate in `defending_team_xy`
        col_label_y : String
            The column label for defending team's Y coordinate in `defending_team_xy`

        Returns
        ----------
        total_pressure : Int
            Total count of defenders applying pressure on the sender & receiver, but not involved in
            packing rate.
        """
        defend_xy = defending_team_xy[defending_team_xy['packing_rate'] == 0][[
            col_label_x, col_label_y]].values
        sender_def_cdist = distance.cdist(sender_xy, defend_xy)
        receiver_def_cdist = distance.cdist(receiver_xy, defend_xy)

        sender_ids = np.array(
            np.where(sender_def_cdist[0] <= 0.05)).tolist()[0]
        receiver_ids = np.array(
            np.where(receiver_def_cdist[0] <= 0.05)).tolist()[0]

        pass_pressure_players = list(
            set(sender_ids).symmetric_difference(set(receiver_ids)))
        total_pressure = len(pass_pressure_players)

        return total_pressure


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
        Do not include any passing team XY or other columns as it'll have an impact on 
        plotting function.
    col_label_x : String
        The column label for defending team's X coordinate in `defending_team_xy`
    col_label_y : String
        The column label for defending team's Y coordinate in `defending_team_xy`
    defend_side : String
        The side of the defending team on the football pitch. Left/Right, `not case sensitive`
    goal_center : Dict
        Center of goal selected based on defend_side
        {'left': [0, 0.5], 'right': [1, 0.5]}

    Returns
    ----------
    packing_df : DataFrame
        Returns a dataframe with the following new columns along with existing columns
        that was provided.
        New Columns :
        [`triangle_area`, `rect_length`, `rect_width`, `area_diff`, `method_1`, `method2_dist`,
        `method_2`, `method3_angle_s`, `method3_angle_r`, `method_3`, `method_1_update`,
        `packing_rate`, `col_label_x`, `col_label_y`]
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
        self.sender_xy = np.asarray(sender_xy)
        self.receiver_xy = np.asarray(receiver_xy)
        self.defending_team_xy = defending_team_xy.copy()
        self.col_label_x = col_label_x
        self.col_label_y = col_label_y
        self.defend_side = defend_side.lower()
        self.goal_center = {'left': [0, 0.5], 'right': [1, 0.5]}
        self.pass_pressure = None

    def get_packing(self):

        self.defending_team_xy_copy = self.defending_team_xy.copy()
        if self.sender_xy.size == 0:
            raise RuntimeError(
                "Sender coordinates are empty. A valid array with [x, y] should be provided")

        if self.receiver_xy.size == 0:
            raise RuntimeError(
                "Receiver coordinates are empty. A valid array with [x, y] should be provided")

        if self.defending_team_xy_copy.size == 0:
            raise RuntimeError(
                "Defending team coordinates are empty. A valid dataframe with [x, y] should be provided for at least 1 player")

        if not isinstance(self.defending_team_xy_copy, pd.DataFrame):
            raise RuntimeError(
                "Defending team coordinates should be a dataframe with x and y values.")

        defend_xy_cols = self.defending_team_xy_copy.columns.tolist()

        if self.col_label_x not in defend_xy_cols or self.col_label_x not in defend_xy_cols:
            raise RuntimeError(
                f"Either {self.col_label_x} or {self.col_label_y} is not a column in defending_team_xy. Please provide valid column names")

        self.goal_xy = self.goal_center[self.defend_side]

        if max(self.defending_team_xy_copy[[self.col_label_x]].values) > 1 or \
                max(self.defending_team_xy_copy[[self.col_label_y]].values) > 1:
            concat_location = np.concatenate([
                self.defending_team_xy_copy[[
                    self.col_label_x, self.col_label_y]].values,
                self.sender_xy.reshape(1, -1),
                self.receiver_xy.reshape(1, -1)
            ])
            min_max_scaler = preprocessing.MinMaxScaler()
            defending_team_xy_scaled = min_max_scaler.fit_transform(
                concat_location)
            self.defending_team_xy_copy.drop(
                [self.col_label_x, self.col_label_y], axis=1, inplace=True)
            self.defending_team_xy_copy[self.col_label_x], self.defending_team_xy_copy[
                self.col_label_y] = defending_team_xy_scaled[:-2, 0], defending_team_xy_scaled[:-2, 1]
            self.sender_xy = defending_team_xy_scaled[-2]
            self.receiver_xy = defending_team_xy_scaled[-1]

        box_a = np.asarray(self.sender_xy)  # sender
        box_b = np.asarray(
            [self.sender_xy[0], self.receiver_xy[1]])
        box_c = np.asarray(list(self.receiver_xy))  # receiver
        box_d = np.asarray(
            [self.receiver_xy[0], self.sender_xy[1]])

        cp = calculate_packing()

        self.pass_direction = cp.get_pass_direction(
            self.sender_xy, self.receiver_xy, self.goal_xy, self.defend_side)

        self.packing_df = cp.method_1(
            box_a, box_b, box_c, box_d, self.defending_team_xy_copy.copy(), col_label_x=self.col_label_x,
            col_label_y=self.col_label_y)

        self.packing_df = cp.method_2(
            self.sender_xy, self.receiver_xy, self.packing_df, col_label_x=self.col_label_x, col_label_y=self.col_label_y)

        self.packing_df = cp.method_3(
            self.sender_xy, self.receiver_xy, self.packing_df, col_label_x=self.col_label_x, col_label_y=self.col_label_y)

        self.packing_df = cp.update_method_1(self.packing_df)

        self.packing_df['packing_rate'] = np.where(
            self.packing_df[["method_1_update", "method_2", "method_3"]].sum(axis=1) == 3, 1, 0)

        # If back pass, multiple packing by -1
        if self.pass_direction == 'Back':
            self.packing_df.loc[:,
                                'packing_rate'] = self.packing_df.loc[:, 'packing_rate']*-1.0
        elif self.pass_direction == 'Side':
            self.packing_df.loc[:,
                                'packing_rate'] = self.packing_df.loc[:, 'packing_rate']*0.5

        self.packing_rate = self.packing_df['packing_rate'].sum()

        self.pass_pressure = cp.get_pass_pressure(self.sender_xy.reshape(1, -1), self.receiver_xy.reshape(1, -1),
                                                  self.packing_df, self.col_label_x,
                                                  self.col_label_y,)

        if max(self.defending_team_xy[[self.col_label_x]].values) > 1 or \
                max(self.defending_team_xy[[self.col_label_y]].values) > 1:

            defending_team_xy_unscaled = min_max_scaler.inverse_transform(
                self.packing_df[[self.col_label_x, self.col_label_y]].values)
            self.packing_df.drop(
                [self.col_label_x, self.col_label_y], axis=1, inplace=True)
            self.packing_df[self.col_label_x], self.packing_df[
                self.col_label_y] = defending_team_xy_unscaled[:, 0], defending_team_xy_unscaled[:, 1]

        return self.packing_df, self.packing_rate, self.pass_pressure
