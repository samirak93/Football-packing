# Football Packing

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-red.svg)](https://www.python.org/downloads/release/python-370/)
[![PyPI Latest Release](https://img.shields.io/pypi/v/football-packing.svg)](https://pypi.org/project/football-packing/)

Docs: [https://samirak93.github.io/Football-packing/docs/html/index.html](https://samirak93.github.io/Football-packing/docs/html/index.html)

## What it does?

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

## Usage & Examples

### Usage

#### Get packing rate

The documentation can be found [here](https://samirak93.github.io/Football-packing/docs/html/misc/modules.html#calculate-packing)

```py
import football_packing as fp

pack = fp.packing(sender_xy, receiver_xy, def_team_xy_df,
                    col_label_x='defender_team_x', col_label_y='defender_team_y',
                    defend_side='left')
packing_df, packing_rate, pass_pressure = pack.get_packing()

```

#### Plot packing

The documentation can be found [here](https://samirak93.github.io/Football-packing/docs/html/misc/modules.html#visualize-packing)

```py
import football_packing as fp

plot = fp.plot_packing(passer_team_df=passing_team_xy, packing_df=packing_df,
                            col_label_x='defender_team_x', col_label_y='defender_team_y',
                            packing_rate=packing_rate, pass_pressure=pass_pressure,
                            sender_xy=sender_xy, receiver_xy=receiver_xy,
                            x_range=[-5250, 5250], y_range=[3400, -3400],
                            path_to_save=dir_path+'/', pass_frame=self.play_id, file_name='belgium',
                            bcg_img='/images/pitch/pitch.jpg')
plot.plot()

```

### Examples

There are 2 examples present in Examples folder under the main football_packing folder .

#### belgium.py

(Data Source: [GitHub](https://github.com/JanVanHaaren/mlsa18-pass-prediction))

Run the `belgium.py` from the examples folder. A html file, `belgium.html`,
with the plot will be saved in the same folder and plot will also open on browser.

#### metrica.py

(Data Source: [GitHub](https://github.com/metrica-sports/sample-data))

To run the `metrica.py` from the examples folder you would have to provide 2 arguments. First one is the path
to the game level data and the second argument is the path to the event level data.
Use this tidy data - [Credit - Eliot McKinley](https://drive.google.com/drive/folders/1BGLHbe7DB_NGZxitjJAQxu2-N-B4Zk3s)
for the game level data and the events data can be downloaded from the Metrica GitHub page.

The sample command to run the file would be like below:

```bash

python3 .../metrica.py .../metrica_tracking_tidy.csv .../Sample_Game_1_RawEventsData.csv

```

If you're using Conda, the python3 argument would be replaced with something like this
`/Users/{user_name}/opt/anaconda3/bin/python` on a mac.

**Note:**
This is still a work in progress as there are certain edge cases where packing rate could be incorrect.
Please leave a feedback/comment on Twitter/GitHub if you encounter any errors.

## Disclaimer

The concept of packing belongs to [Impect](https://www.impect.com/) and I do not take credit for the metric.

This is an attempt to create an open source variation of it, with few modifications on how the metrics are calculated. The logic behind the metric calculations are explained in `How packing is calculated` section in the docs.

For any questions/feedback, reach out to me on twitter [@SamiraK93](https://twitter.com/Samirak93).

If you'd like to file any issues or provide any updates, submit a PR on GitHub.
