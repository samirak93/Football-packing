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


Examples
====================

There are 2 examples present in Packing/Examples folder.



