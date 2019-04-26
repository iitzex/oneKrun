import os
import sys
from datetime import datetime
from glob import glob

import jinja2
import matplotlib.pyplot as plt
import pandas as pd
from bokeh.embed import components
from bokeh.io import export_png, export_svgs
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource
from bokeh.palettes import all_palettes
from bokeh.plotting import figure, output_file, show
from fitparse import FitFile

palettes = all_palettes['Viridis'][5]
COLORS = {'text': '#222222', 'bg': '#FFFFFF', 'special': '#FFFF00',
          '42k': palettes[4], '21k': palettes[3], '10k': palettes[2], '4k': palettes[1], '1k': palettes[0]}
NCOLS = 7
SIZE = 150
BORDER = 10


def get_color(distance):
    if distance < 4:
        return COLORS['1k']
    elif distance < 10:
        return COLORS['4k']
    elif distance < 21:
        return COLORS['10k']
    elif distance < 42:
        return COLORS['21k']
    else:
        return COLORS['42k']


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
    distance = df.iloc[-1]['distance'] / 1000
    color = get_color(distance)

    # print(df.long)
    # df.plot(kind='line', x='long', y='lat', c='distance', colormap='viridis')
    # plt.scatter(df['long'], df['lat'], c=df['distance'], s=1)
    # plt.plot(df['long'], df['lat'], c='c')
    # plt.show()

    source = ColumnDataSource(df)
    p = figure(plot_width=SIZE, plot_height=SIZE+10,
               toolbar_location=None, tools="", title=str(distance))
    # p.circle(df['long'], df['lat'], size=1)
    # p.circle("long", "lat", size=5, source=source)
    p.line('long', 'lat', color=color, line_width=3, source=source)
    # p.background_fill_color = COLORS['bg']
    # p.outline_line_color = COLORS['bg']
    p.min_border_left = BORDER
    p.min_border_right = BORDER
    p.min_border_top = BORDER
    p.min_border_bottom = BORDER
    p.grid.grid_line_color = None
    p.axis.visible = False

    # export_png(p, filename=f'img/{fn[4:-4]}.png')
    # p.output_backend = "svg"
    # export_svgs(p, filename=f'img/{fn[4:-4]}.svg')
    return p, distance


def main():
    figs = []
    total = 0

    d = 'FIT/'
    for num, f in enumerate(sorted(os.listdir(d))):
        fn = f'{d}{f}'
        print(fn)
        try:
            p, distance = fig(fn)
            figs.append(p)
            total += distance
        except TypeError:
            pass

    grid = gridplot(figs, ncols=NCOLS, toolbar_location=None)
    # export_png(grid, filename=f'oneKrun.png')
    # output_file('run.html')
    # show(p)

    script, div = components(grid)
    render_vars = {
        "script": script,
        "div": div,
        "number": num,
        "total": total
    }
    render(render_vars)


def render(render_vars):
    template = "dup/template.html"
    env = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))
    html = env.get_template(template).render(render_vars)

    with open('dup/out.html', 'w')as f:
        f.write(html)


if __name__ == "__main__":
    main()
