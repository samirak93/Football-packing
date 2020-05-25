********************
Usage & Examples
********************

Usage
====================

Get packing rate
--------------------------------------------

The entire documentation can be found :ref:`under modules.<Calculate packing>`

.. code-block:: python

    import football_packing as fp

    pack = fp.packing(sender_xy, receiver_xy, def_team_xy_df,
                    col_label_x='defender_team_x', col_label_y='defender_team_y', 
                    defend_side=self.defend_side)
    packing_df, packing_rate, pass_pressure = pack.get_packing()

Plot packing
--------------------------------------------

The entire documentation can be found :ref:`under modules.<Visualize Packing>`

.. code-block:: python

    import football_packing as fp

    plot = fp.plot_packing(passer_team_df=passing_team_xy, packing_df=self.packing_df, col_label_x='defender_team_x',
                            col_label_y='defender_team_y', packing_rate=self.packing_rate, pass_pressure=self.pass_pressure,
                            sender_xy=sender_xy, receiver_xy=receiver_xy, x_range=[-5250, 5250], y_range=[3400, -3400],
                            path_to_save=dir_path+'/', pass_frame=self.play_id, file_name='belgium', plot_hint='on')
    plot.plot()


|

Examples
==========================

There are 2 examples present in Packing/Examples folder.

|

Belgium.py 
----------------------------------------------------------------------------------------------------

(Data Source: `GitHub <https://github.com/JanVanHaaren/mlsa18-pass-prediction>`__)

Run the :code:`belgium.py` from the examples folder under main football_packing folder. A html file, 
:code:`belgium.html`, with the plot will be created in the same folder.


