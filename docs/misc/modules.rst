********************
Modules
********************
|

.. _link-target-module:

Calculate packing
============================================
|


.. automodule:: packing
    :members: packing
   
.. _link-target:

How packing is calculated?
--------------------------------------------
|

A brief explanation on how packing rate is calculated. There are 3 methods which
look at different aspects of the pass and defending player's relationship to the pass.

:code:`Method 1` looks at the space between the sender and receiver and checks if any
defending players is within that space.

:code:`Method 2` looks at the distance between the defender and line of pass.

:code:`Method 3` looks at the angle between the sender & receiver to the defender.

:code:`Method 1` gets a final update based on a specific condition as mentioned 
:ref:`in this section.<Method 1 - Update>`

|

Method 1
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
|

.. autofunction:: packing.calculate_packing.method_1

Method 2
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
|

.. autofunction:: packing.calculate_packing.method_2

Method 3
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
|

.. autofunction:: packing.calculate_packing.method_3

.. _link-target2:

Method 1 - Update
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
|

.. autofunction:: packing.calculate_packing.update_method_1

Pass Pressure
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
|

.. autofunction:: packing.calculate_packing.get_pass_pressure

Visualize Packing
============================================
|

.. automodule:: plot_packing
    :members: plot_packing