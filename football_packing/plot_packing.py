# -*- coding: utf-8 -*-
from bokeh.plotting import figure, output_file, show, save
from bokeh.models import ColumnDataSource, Label, LabelSet, Range1d, Title
from bokeh.io import push_notebook, show, output_notebook
from bokeh.layouts import row, gridplot

from pathlib import Path

import os
from statistics import mean
output_notebook()


class plot_packing():
    """
    Plot the player location on the pitch and highlight the defending team players
    that might have been calculated in packing. Turning on/off plot_hint will show 
    how packing was calculated.

    Parameters
    ----------
    passer_team_df : DataFrame
        DataFrame with the passing team coordinates
    packing_df : DataFrame
        Resulting DataFrame from packing module (should not be altered)
    col_label_x : String
        The column label for defending team's X coordinate in defending_team_xy
    col_label_y : String
        The column label for defending team's Y coordinate in defending_team_xy
    packing_rate : Float
        Resulting output from packing module (should not be altered)
    pass_pressure : Int
        Defending players who are closer to sender/receiver but not involved in packing
    sender_xy : ndarray
        Sender XY coordinates as numpy array
    receiver_xy : ndarray
        Receiver XY coordinates as numpy array
    x_range : [start, end] list
        List of range of x-axis of the pitch, Eg: [0, 100] or [-5250, 5250]
    y_range : [start, end] list
        List of range of y-axis of the pitch, Eg: [0, 100] or [3400, -3400]
    pass_frame : String, Optional, default None
        Identifier to show pass event time
    bcg_img : String, default '/images/pitch/pitch.jpg'
        Path to background image
    plot_hint : String, default `off`
        To display the logic behind calculating packing
    file_name : String, default `packing`
        Filename to save the plot

    Returns
    ----------
    show() :
        Plot is shown on the browser. If module is run on jupyter notebook,
        plot will be visible within the notebook. 
    save() : 
        Plot saved locally to folder `plots`. If the folder does not exist, 
        folder is created. 
        Note: If `file_name` is not changed every time module is run, plots
        will be overwritten.
    """

    def __init__(
            self,
            passer_team_df,
            packing_df,
            col_label_x,
            col_label_y,
            packing_rate,
            pass_pressure,
            sender_xy,
            receiver_xy,
            x_range,
            y_range,
            pass_frame=None,
            bcg_img='/images/pitch/pitch.jpg',
            plot_hint='off',
            file_name='packing'
    ):
        self.passer_team_df = passer_team_df
        self.packing_df = packing_df
        self.col_label_x = col_label_x
        self.col_label_y = col_label_y
        self.packing_rate = packing_rate
        self.pass_pressure = pass_pressure
        self.sender_xy = sender_xy
        self.receiver_xy = receiver_xy
        self.bcg_img = bcg_img
        self.x_range = x_range
        self.y_range = y_range
        self.pass_frame = pass_frame
        self.plot_hint = plot_hint
        self.file_name = file_name
        self.path = os.path.dirname(os.path.realpath(__file__))
        Path(self.path+"/plots/").mkdir(parents=True, exist_ok=True)
        output_file(self.path+"/plots/"+self.file_name +
                    ".html", title=self.file_name + " plot")

    def save_plots(self, plot):
        """
        Save/Show the plots

        Parameters
        ----------
        plot : bokeh figure 

        Returns
        ----------
        show()
            plot is shown on browser, notebook(if module excuted there)
        save()
            plot save to the output_file path 
        """
        # show(plot)
        save(plot)
        print(
            f"Plot successfully saved at {self.path+'/plots/'+self.file_name+'.html'}")

    def plot(self):

        # Plot the visualization
        pass_team_cols = self.passer_team_df.columns.tolist()
        defend_team_cols = self.packing_df.columns.tolist()
        if len(pass_team_cols) < 3:
            raise ValueError(
                f"Expect minimum 3 columns in 'passer_team_df'. Please provide a valid dataframe with a column for x and y and player_id each.")

        pass_team_cols_x = [i for i in pass_team_cols if '_x' in i or 'x' == i]
        pass_team_cols_y = [i for i in pass_team_cols if '_y' in i or 'y' == i]
        pass_team_cols_id = [
            i for i in pass_team_cols if '_id' in i or 'id' == i or 'player' in i]

        defend_team_cols_id = [
            i for i in defend_team_cols if '_id' in i or 'id' == i or 'player' in i]

        if len(pass_team_cols_x) < 1:
            raise ValueError(
                f"The column name for passing team x does not contain 'x' or '_x'. Please provide a valid name with 'x' or '_x'")
        if len(pass_team_cols_y) < 1:
            raise ValueError(
                f"The column name for passing team y does not contain 'y' or '_y'. Please provide a valid name with 'y' or '_y'")
        if len(pass_team_cols_id) > 1:
            raise ValueError(
                f"There are multiple columns containing either 'id' or '_id' in passer_team_df dataframe. Please provide a single column with 'id' or '_id' as column name")
        if len(defend_team_cols_id) > 1:
            raise ValueError(
                f"There are multiple columns containing either 'id' or '_id' in packing_df dataframe. Please provide a single column with 'id' or '_id' as column name")

        fig_height, fig_width = 900, 550
        fig_title = "Packing rate: {} Pass pressure: {} \n".format(
            self.packing_rate, self.pass_pressure)

        plot = figure(name='base', plot_height=550, plot_width=850,
                      tools="save, wheel_zoom, reset, pan", toolbar_location="right",
                      x_range=self.x_range, y_range=self.y_range,)

        plot.add_layout(
            Title(text=f"Pass pressure: {self.pass_pressure}", text_font_size="10pt", align='center'), 'above')
        plot.add_layout(
            Title(text=f"Packing rate: {self.packing_rate}", text_font_size="10pt", align='center'), 'above')

        image_min_x, image_min_y, image_max_x, image_max_y = min(self.x_range), max(self.y_range), \
            (abs(self.x_range[0]) + abs(self.x_range[1])
             ), (abs(self.y_range[0]) + abs(self.y_range[1]))

        plot.image_url(url=[self.path+self.bcg_img], x=image_min_x, y=image_min_y,
                       w=image_max_x, h=image_max_y, anchor="bottom_left")

        plot.line([self.sender_xy[0], self.receiver_xy[0]], [self.sender_xy[1], self.receiver_xy[1]],
                  line_color="dodgerblue", line_alpha=0.5, line_width=4, line_dash='dashed',)

        source_pass_team = ColumnDataSource(self.passer_team_df)
        plot.scatter(x=pass_team_cols_x[0], y=pass_team_cols_y[0], source=source_pass_team,
                     size=17, fill_color='dodgerblue', fill_alpha=0.7)

        if pass_team_cols_id:
            labels_pass_team = LabelSet(x=pass_team_cols_x[0], y=pass_team_cols_y[0], text=pass_team_cols_id[0],
                                        x_offset=-4.5, y_offset=-6, source=source_pass_team, render_mode='canvas', text_font_size='8pt',
                                        text_color='white')
            plot.add_layout(labels_pass_team)

        source_sender = ColumnDataSource(
            data={'x': [self.sender_xy[0]], 'y': [self.sender_xy[1]], 'id': ['S']})
        plot.scatter('x', 'y', source=source_sender,
                     size=17, fill_color='dodgerblue', line_color='red', line_width=3)
        labels_sender = LabelSet(x='x', y='y', text='id',
                                 x_offset=-4.5, y_offset=5, source=source_sender, render_mode='canvas')
        plot.add_layout(labels_sender)

        source_receiver = ColumnDataSource(
            data={'x': [self.receiver_xy[0]], 'y': [self.receiver_xy[1]], 'id': ['R']})
        plot.scatter('x', 'y', source=source_receiver,
                     size=17, fill_color='dodgerblue', line_color='red', line_width=3)
        labels_receiver = LabelSet(x='x', y='y', text='id',
                                   x_offset=-4.5, y_offset=5, source=source_receiver, render_mode='canvas')
        plot.add_layout(labels_receiver)

        colors = {-1: 'green', 1: 'green', 0.5: 'green', 0: 'orangered'}
        alpha = {-1: 1, 1: 1, 0.5: 1, 0: 0.5}
        radius = {-1: 1000, 1: 1000, 0.5: 1000, 0: 0}

        for i in range(len(self.packing_df[self.col_label_x].tolist())):
            x = self.packing_df.iloc[i][self.col_label_x]
            y = self.packing_df.iloc[i][self.col_label_y]
            id = self.packing_df.iloc[i][defend_team_cols_id]
            edge_col = colors[self.packing_df.iloc[i]['packing']]
            fill_alpha = alpha[self.packing_df.iloc[i]['packing']]
            circle_radius = radius[self.packing_df.iloc[i]['packing']]

            source_def_team = ColumnDataSource(
                data={'x': [x], 'y': [y], 'id': [id], 'edge_col': [edge_col], 'fill_alpha': [fill_alpha], 'radius': [circle_radius]})

            if self.plot_hint == 'on':
                plot.circle(x='x', y='y', radius='radius',
                            color='navy', alpha=0.1, source=source_def_team)

            plot.scatter('x', 'y',
                         size=17, fill_color='orangered', line_color='edge_col', line_width=3, source=source_def_team,
                         fill_alpha='fill_alpha')

            if defend_team_cols_id:
                labels_pass_team = LabelSet(x='x', y='y', text='id',
                                            x_offset=-4.5, y_offset=-6, source=source_def_team, render_mode='canvas',
                                            text_font_size='8pt', text_color='white')
                plot.add_layout(labels_pass_team)

        if self.plot_hint == 'on':
            # plot rectangles

            plot.patches([[self.receiver_xy[0], self.receiver_xy[0], self.sender_xy[0], self.sender_xy[0]]],
                         [[self.sender_xy[1], self.receiver_xy[1],
                             self.receiver_xy[1], self.sender_xy[1]]],
                         color="#B3DE69", fill_alpha=0.3)

        plot.axis.visible = False
        plot.xgrid.grid_line_color = None
        plot.ygrid.grid_line_color = None
        plot.title.align = 'center'
        plot.toolbar.autohide = True
        plot.min_border = 40
        # plot.min_border_right = 30
        # plot.min_border_top = 30
        # plot.min_border_bottom = 30

        self.save_plots(plot)
