import os
import sys
from datetime import datetime
from glob import glob

import jinja2
import matplotlib.pyplot as plt
import pandas as pd
from bokeh.embed import components
from bokeh.io import export_png, export_svgs
from bokeh.layouts import column, gridplot
from bokeh.models import ColumnDataSource
from bokeh.palettes import all_palettes
from bokeh.plotting import figure, output_file, save, show
from fitparse import FitFile

palettes = all_palettes['Viridis'][5]
COLORS = {'text': '#222222', 'bg': '#FFFFFF', 'special': '#FFD700',
          '42k': palettes[4], '21k': palettes[3], '10k': palettes[2], '4k': palettes[1], '1k': palettes[0]}
NCOLS = 7
SIZE = 150
BORDER = 10
WWW = 'iitzex.github.io'


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


def get_data(fn):
    fitfile = FitFile(fn)
    table = []
    for record in fitfile.get_messages('record'):
        values = record.get_values()
        table.append(values)

    df = pd.DataFrame(table)
    return df


def track(fn):
    df = get_data(fn)

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

    if os.path.isfile(f'{WWW}/img/{fn[4:-4]}.svg'):
        return None, distance

    source = ColumnDataSource(df)
    trackmile = figure(plot_width=SIZE*4, plot_height=SIZE*4+10, title=f'{str(distance)}',
                       toolbar_location=None, tools="")
    trackmile.line('long', 'lat', color=color, line_width=3, source=source)

    hr = figure(plot_width=SIZE*6, plot_height=int(SIZE*1.3), title='HEART_RATE',
                toolbar_location=None, tools="")
    hr.line('distance', 'heart_rate', line_width=1, source=source)

    speed = figure(plot_width=SIZE*6, plot_height=int(SIZE*1.3), title='SPEED',
                   toolbar_location=None, tools="")
    speed.line('distance', 'speed', line_width=1, source=source)

    cadence = figure(plot_width=SIZE*6, plot_height=int(SIZE*1.3), title='CADENCE',
                     toolbar_location=None, tools="", )
    cadence.line('distance', 'cadence', line_width=1, source=source)

    altitude = figure(plot_width=SIZE*6, plot_height=int(SIZE*1.3), title='ALTITUDE',
                      toolbar_location=None, tools="", )
    altitude.line('distance', 'altitude', line_width=1, source=source)

    plot = column([trackmile, altitude, hr, speed, cadence])
    # export_png(plot, filename=f'WWW/track/{fn[4:-4]}.png')
    # save(plot, f'WWW/track/{fn[4:-4]}.html', title=timestamp.strftime('%Y/%m/%d'))
    script, div = components(plot)

    render_vars = {
        "root": '../',
        "title": timestamp.strftime('%Y/%m/%d'),
        "div": div,
        "script": f"<h4>{timestamp.strftime('%Y/%m/%d')}<br><br></h4>" + script,
        "ps": ''
    }
    render(render_vars, 'template.html', f'track/{fn[4:-4]}.html')

    preview = figure(plot_width=SIZE, plot_height=SIZE+10,
                     toolbar_location=None, tools="", title=str(distance))
    preview.line('long', 'lat', color=color, line_width=3, source=source)
    preview.outline_line_color = COLORS['bg']
    preview.min_border_left = BORDER
    preview.min_border_right = BORDER
    preview.min_border_top = BORDER
    preview.min_border_bottom = BORDER
    preview.grid.grid_line_color = None
    preview.axis.visible = False
    # export_png(preview, filename=f'{WWW}/img/{fn[4:-4]}.png')
    preview.output_backend = "svg"
    export_svgs(preview, filename=f'{WWW}/img/{fn[4:-4]}.svg')

    return preview, distance


def main():
    # figs = []
    total = 0
    img_html = ''

    d = 'FIT/'
    for num, f in enumerate(sorted(os.listdir(d))):
        img_name = f[:-4]
        path = f'{d}{f}'
        print(path)
        try:
            p, distance = track(path)
            # figs.append(p)
            total += distance
            img_html += f"<p><a href='track/{img_name}.html'><img src='img/{img_name}.svg' width='100%'/></a></p>\n"
        except TypeError:
            pass

    # plot = gridplot(figs, ncols=NCOLS, toolbar_location=None)
    # export_png(plot, filename=f'oneKrun.png')
    # output_file('run.html')
    # show(p)
    # script, div = components(plot)

    render_vars = {
        "title": '',
        "div": img_html,
        "script": '',
        "ps": f'{num} Runs\n<br>{total} K'
    }
    render(render_vars, 'template.html', 'index.html')


def render(render_vars, input_fn, output_fn):
    template = f"{WWW}/{input_fn}"
    env = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))
    html = env.get_template(template).render(render_vars)

    with open(f'{WWW}/{output_fn}', 'w')as f:
        f.write(html)


if __name__ == "__main__":
    main()
