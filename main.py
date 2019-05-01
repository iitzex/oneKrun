import os
import sys
from datetime import datetime, timedelta
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


def TD(ts):
    h, m, s = ts.seconds//3600, (ts.seconds//60) % 60, ts.seconds % 60
    return f'{m}:{s}'


def get_km(df):
    df['km'] = df['distance'] / 1000
    key = 1
    msg = ''
    last_lapse = df.iloc[0]['timestamp']
    for i, j in enumerate(df['km']):
        if j - key > 0:
            now = df.iloc[i]['timestamp']
            diff = now - last_lapse
            last_lapse = now
            msg += f'#{key} [{TD(diff)}]\n'
            key += 1

    return msg


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
    distance = round(df.iloc[-1]['distance'] / 1000, 5)
    color = get_color(distance)
    begintime = df.iloc[0]['timestamp']
    endtime = df.iloc[-1]['timestamp']
    interval = endtime - begintime

    # if os.path.isfile(f'{WWW}/img/{fn[4:-4]}.svg'):
    #     return None, distance, interval
    print(fn)

    source = ColumnDataSource(df)
    trackmile = figure(plot_width=SIZE*4, plot_height=SIZE*4+10, title=f'{str(distance)}',
                       toolbar_location=None, tools="")
    trackmile.line('long', 'lat', color=color, line_width=3, source=source)
    # trackmile.axis.visible = False

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

    plot = column([trackmile, altitude, hr, speed])
    # export_png(plot, filename=f'WWW/track/{fn[4:-4]}.png')
    # save(plot, f'WWW/track/{fn[4:-4]}.html', title=timestamp.strftime('%Y/%m/%d'))
    script, div = components(plot)
    ps = f"{endtime.strftime('%Y/%m/%d')}"
    ps += '<br>' + f"{distance} K"
    ps += '<br>' + f"{interval}"

    ps += '<br><br>'
    ps += get_km(df).replace('\n', '<br>\n')
    # print(km)
    # ps += str(km)

    render_vars = {
        "root": '../',
        "title": endtime.strftime('%Y/%m/%d'),
        "div": div,
        "script": script,
        "ps": ps
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

    return preview, distance, interval


def main():
    # figs = []
    total_distance = 0
    total_time = timedelta()
    img_html = ''

    d = 'FIT/'
    for num, f in enumerate(sorted(os.listdir(d), reverse=True)):
        img_name = f[:-4]
        path = f'{d}{f}'
        try:
            p, distance, interval = track(path)
            # figs.append(p)
            total_distance += distance
            total_time += interval
            print(p, total_distance, total_time)

            img_html += f"<p><a href='track/{img_name}.html'><img src='img/{img_name}.svg' width='100%'/></a></p>\n"
        except TypeError as e:
            print(e)
            pass

    # plot = gridplot(figs, ncols=NCOLS, toolbar_location=None)
    # export_png(plot, filename=f'oneKrun.png')
    # output_file('run.html')
    # show(p)
    # script, div = components(plot)

    print(total_time)
    render_vars = {
        "title": '',
        "div": img_html,
        "script": '',
        "ps": f'{num+1} Runs\n<br>{round(total_distance, 5)} K\n<br>{total_time}'
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
