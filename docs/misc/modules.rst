********************
Modules
********************

Calculate packing
============================================

.. automodule:: Packing.packing
    :members:
   
.. _link-target:

How packing is calculated?
--------------------------------------------

A brief explanation of how packing rate is calcluated. There are 3 methods which
look at different aspects of the pass and defending player's relationship to the pass. 
Finally :code:`Method 1` gets a final update based on a specific condition.

Method 1
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autofunction:: Packing.packing.calculate_packing.method_1

Method 2
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autofunction:: Packing.packing.calculate_packing.method_2

Method 3
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autofunction:: Packing.packing.calculate_packing.method_3

Method 1 - Update
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autofunction:: Packing.packing.calculate_packing.update_method_1

Pass Pressure
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autofunction:: Packing.packing.calculate_packing.get_pass_pressure

Visualize Packing
============================================
.. automodule:: Packing.plot_packing
    :members: