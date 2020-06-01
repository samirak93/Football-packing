Football Packing

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-red.svg)](https://www.python.org/downloads/release/python-370/)

This is a python package to calculate packing rate for a given [pass](<https://en.wikipedia.org/wiki/Passing_(association_football)>)
in soccer.
This is a variation of the metric created by [Impect](https://www.impect.com/).

One of the main variation of this metric from other traditional ones is that only the defending players
who are in the scope of the pass are considered for packing and not all the defenders on the pitch.
The other difference would be the fact that for defenders, their lines on the pitch are considered with respect to the pass direction. Sample Scenarios section on the doc has more details
about these differences.

If a defender's line is cut by a pass, they're considered to be packed (+1 for that defender)
even if the defender is not near the line of pass (pass is on one
side of the pitch and defender is far away).So if an attacking player makes a long pass beyond the entire defense,
then all the defenders would be considered as packed (+1), but in truth only few of the players would be near the
line of pass and could have an impact on the outcome of the pass/play.

Also for different types of passes (forward, back & side) packing is still calculated but a constant is
multiplied with the packing value based on the type of pass.

- For a back pass, multiplying factor is `-1`.
- For a side pass, multiplying factor is `0.5`.
- For a forward pass, multiplying factor is `1`.

**Disclaimer**

The concept of packing belongs to [Impect](https://www.impect.com/) and I do not take credit for the metric.

This is an attempt to create an open source variation of it, with few modifications on how the metrics are calculated. The logic behind the metric calculations are explained in `How packing is calculated` section in the docs.

For any questions/feedback, reach out to me on twitter [@SamiraK93](https://twitter.com/Samirak93).

If you'd like to file any issues/updates, submit a PR on GitHub.
