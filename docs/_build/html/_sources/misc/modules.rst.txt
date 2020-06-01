********************
Modules
********************
|

.. _link-target-module:

Calculate Packing
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
defending players is within that space. A bounding box (:ref:`green box here<Scenario 2:>`) 
is created between the sender and receiver and the defending players inside the box 
(and certain distance threshold outside the box) are marked as 1.

:code:`Method 2` looks at the distance between the defender and line of pass. If the defender is 
within a certain distance (`method2_radius`), they are marked as 1. This helps to consider defenders
who are only within the range of the pass.

:code:`Method 3` looks at the angle between the sender & receiver to the defender. In order to consider 
the lines of the defender, instead of just making a vertical line, based on the direction of pass angles
are calculated. This is seen with an example :ref:`here.<Scenario 1:>`

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

.. _link-target3:

Visualize Packing
============================================
|

.. automodule:: plot_packing
    :members: plot_packing