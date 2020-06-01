********************
Football Packing
********************

This is a python package to calculate packing rate for a given `pass <https://en.wikipedia.org/wiki/Passing_(association_football)>`__
in soccer. This is a variation of the original metric created by `Impect <https://www.impect.com/>`__.

One of the main variation of this metric from other traditional ones is that only the defending players 
who are in the scope of the pass are considered for packing and not all the defenders on the pitch. 
The other difference would be the fact that for defenders, their lines on the pitch are considered with respect 
to the pass direction. :ref:`Refer to the examples<Sample Scenarios>` on more details
about these differences. 

If a defender's line is cut by a pass, they're considered to be packed (+1 for that defender) 
even if the defender is not near the line of pass (pass is on one 
side of the pitch and defender is far away).So if an attacking player makes a long pass beyond the entire defense, 
then all the defenders would be considered as packed (+1), but in truth only few of the players would be near the
line of pass and could have an impact on the outcome of the pass/play.

Also for different types of passes (forward, back & side) packing is still calculated but a constant is 
multiplied with the packing value based on the type of pass. 

- For a back pass, multiplying factor is :code:`-1`.
- For a side pass, multiplying factor is :code:`0.5`.
- For a forward pass, multiplying factor is :code:`1`.


.. toctree::
   :maxdepth: 2
   :caption: Table of Contents
   :name: mastertoc

   misc/install
   misc/modules
   misc/examples
   misc/license

|

.. note:: This is still a work in progress as there are certain edge cases where packing rate could be incorrect. 
         Please provide a feedback/comment on Twitter/GitHub if you encounter any errors.

|
