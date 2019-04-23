import os
import sys
from datetime import datetime
from glob import glob

import jinja2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from bokeh.embed import autoload_static, components
from bokeh.io import export_png, export_svgs
from bokeh.layouts import column, gridplot, row
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.palettes import Spectral8
from bokeh.plotting import figure, output_file, show
from bokeh.resources import CDN
from bokeh.transform import linear_cmap
from fitparse import FitFile
from flask import Flask, Markup, render_template

COLORS = {'text': '#222222', 'bg': '#FFFFFF', 'special': '#FFFF00',
          '10k': '#2A4BD3', '4k': '#63B0C4', '1k': Spectral8[0]}
NCOLS = 7
SIZE = 150
BORDER = 10
app = Flask(__name__)


def fig(fn):
    fitfile = FitFile(fn)
    total = []
    for record in fitfile.get_messages('record'):
        values = record.get_values()
        total.append(values)

    df = pd.DataFrame(total)

    try:
        df['lat'] = df.position_lat.map(lambda x: x * 180 / (2 << 30))
        df['long'] = df.position_long.map(lambda x: x * 180 / (2 << 30))
    except AttributeError as e:
        print(fn)
        print(e)
        return None

    # print(df.iloc[-1])
    # msg = f"{df.iloc[-1]['timestamp']}  {df.iloc[-1]['distance']}"
    msg = f"{df.iloc[-1]['distance']/1000}"
    # print(df.long)
    # df.plot(kind='line', x='long', y='lat', c='distance', colormap='viridis')
    # plt.scatter(df['long'], df['lat'], c=df['distance'], s=1)
    # plt.plot(df['long'], df['lat'], c='c')
    # plt.show()

    source = ColumnDataSource(df)
    p = figure(plot_width=SIZE, plot_height=SIZE,
               toolbar_location=None, tools="", title=msg)
    # p.circle(df['long'], df['lat'], size=1)
    # p.circle("long", "lat", size=5, source=source)
    p.line('long', 'lat',  line_width=3, source=source)
    # p.line('long', 'lat', color=COLORS['1k'], line_width=3, source=source)
    # p.background_fill_color = COLORS['bg']
    # p.outline_line_color = COLORS['bg']
    p.min_border_left = BORDER
    p.min_border_right = BORDER
    p.min_border_top = BORDER
    p.min_border_bottom = BORDER
    p.grid.grid_line_color = None
    p.axis.visible = False

    export_png(p, filename=f'img/{fn[4:-4]}.png')
    # p.output_backend = "svg"
    # export_svgs(p, filename=f'img/{fn[4:-4]}.svg')
    return p


def main():
    d = 'FIT/'
    figs = []
    for p in sorted(os.listdir(d)):
        fn = f'{d}{p}'
        print(fn)
        r = fig(fn)
        if r:
            figs.append(r)

    p = gridplot(figs, ncols=NCOLS, toolbar_location=None)
    # output_file('run.html')
    # show(p)

    script, div = components(p)

    template = "templates.html"
    render_vars = {
        "script": script,
        "div": div
    }

    env = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))
    output = env.get_template(template).render(render_vars)

    # print(output)
    with open('index.html', 'w')as f:
        f.write(output)


if __name__ == "__main__":
    main()
