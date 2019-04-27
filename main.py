import os
import sys
from datetime import datetime
from glob import glob

import jinja2
import matplotlib.pyplot as plt
import pandas as pd
from bokeh.embed import components
from bokeh.io import export_png, export_svgs
from bokeh.layouts import gridplot, column
from bokeh.models import ColumnDataSource
from bokeh.palettes import all_palettes
from bokeh.plotting import figure, output_file, show, save
from fitparse import FitFile

palettes = all_palettes['Viridis'][5]
COLORS = {'text': '#222222', 'bg': '#FFFFFF', 'special': '#FFD700',
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
    table = []
    for record in fitfile.get_messages('record'):
        values = record.get_values()
        table.append(values)

    df = pd.DataFrame(table)

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
    timestamp = df.iloc[-1]['timestamp']
    source = ColumnDataSource(df)

    track = figure(plot_width=SIZE, plot_height=SIZE+10,
                   toolbar_location=None, tools="", title=str(distance))
    track.line('long', 'lat', color=color, line_width=3, source=source)
    track.outline_line_color = COLORS['bg']
    track.min_border_left = BORDER
    track.min_border_right = BORDER
    track.min_border_top = BORDER
    track.min_border_bottom = BORDER
    track.grid.grid_line_color = None
    track.axis.visible = False
    export_png(track, filename=f'dup/img/{fn[4:-4]}.png')
    # p.output_backend = "svg"
    # export_svgs(p, filename=f'dup/img/{fn[4:-4]}.svg')

    single = figure(plot_width=SIZE*4, plot_height=SIZE*4+10, title=str(distance),
                    toolbar_location=None, tools="")
    single.line('long', 'lat', color=color, line_width=3, source=source)
    hr = figure(plot_width=SIZE*4, plot_height=int(SIZE*1.3), title='HEART_RATE',
                toolbar_location=None, tools="")
    hr.line('distance', 'heart_rate', line_width=3, source=source)
    speed = figure(plot_width=SIZE*4, plot_height=int(SIZE*1.3), title='SPEED',
                   toolbar_location=None, tools="")
    speed.line('distance', 'cadence', line_width=3, source=source)
    cadence = figure(plot_width=SIZE*4, plot_height=int(SIZE*1.3), title='CADENCE',
                     toolbar_location=None, tools="", )
    cadence.line('distance', 'cadence', line_width=3, source=source)
    plot = column([single, hr, speed, cadence])
    # export_png(plot, filename=f'dup/track/{fn[4:-4]}.png')
    save(plot, f'dup/track/{fn[4:-4]}.html',
         title=timestamp.strftime('%Y/%m/%d'))

    return track, distance


def main():
    figs = []
    total = 0
    img_html = ''

    d = 'FIT/'
    for num, f in enumerate(sorted(os.listdir(d))):
        img_name = f[:-4]
        path = f'{d}{f}'
        print(path)
        try:
            p, distance = fig(path)
            figs.append(p)
            total += distance
            img_html += f"<p><img src='img/{img_name}.png' width='100%'/></p>\n"
        except TypeError:
            pass

    plot = gridplot(figs, ncols=NCOLS, toolbar_location=None)
    export_png(plot, filename=f'oneKrun.png')
    # output_file('run.html')
    # show(p)
    # script, div = components(plot)

    script = img_html
    div = ''

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

    with open('dup/index.html', 'w')as f:
        f.write(html)


if __name__ == "__main__":
    main()
