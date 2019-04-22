import os
import sys
from datetime import datetime
from math import pow

import numpy as np
from bokeh.io import export_svgs, export_png
from bokeh.layouts import column, gridplot, row
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.palettes import Spectral6
from bokeh.plotting import figure, output_file, show
from bokeh.transform import linear_cmap
from fitparse import FitFile

import matplotlib.pyplot as plt
import pandas as pd


def fig(fn):
    fitfile = FitFile(fn)
    total = []
    for record in fitfile.get_messages('record'):
        values = record.get_values()
        total.append(values)

    df = pd.DataFrame(total)

    df['lat'] = df.position_lat.map(lambda x: x * (180 / pow(2, 31)))
    df['long'] = df.position_long.map(lambda x: x * (180 / pow(2, 31)))
    # df['colors'] = ["#%02x%02x%02x" % (int(r), int(g), 23) for r, g in zip(df.distance, df.speed)]
    # df['colors'] = ["#%02x%02x%02x" %
    #                 (int(r), 100, 10) for r in df.heart_rate * 5]
    # mapper = linear_cmap(field_name=df.distance,
    #                      palette=Spectral6, low=min(df.distance), high=max(df.distance))
    # print(mapper)

    # print(df.iloc[-1])
    # print(df.long)
    # df.plot(kind='line', x='long', y='lat', c='distance', colormap='viridis')
    # plt.scatter(df['long'], df['lat'], c=df['distance'], s=1)
    # plt.plot(df['long'], df['lat'], c='c')
    # plt.show()

    p = figure(plot_width=100, plot_height=100, toolbar_location=None)
    source = ColumnDataSource(df)
    # p.circle(df['long'], df['lat'], size=1)
    # p.circle("long", "lat", size=5, source=source)
    p.line('long', 'lat', line_width=3, source=source)
    p.grid.grid_line_color = None
    p.axis.visible = False

    # output_file("run.html")
    # show(p)
    return p


if __name__ == "__main__":
    d = 'FIT/'
    figs = []
    for p in os.listdir(d):
        fn = f'{d}{p}'
        print(fn)
        figs.append(fig(fn))

    output_file("run.html")
    p = gridplot(figs, ncols=4, toolbar_location=None)
    # show(p)
    # export_svgs(p, filename="oneKrun.svg")
    export_png(p, filename="oneKrun.png")
