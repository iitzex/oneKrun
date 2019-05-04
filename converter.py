import os

from pytz import timezone
import gpxpy
import pandas as pd
from fitparse import FitFile
from gpxpy import gpx


def gpxparser(fn):
    gpx_file = open(fn, 'r')
    gpx = gpxpy.parse(gpx_file)
    df = pd.DataFrame(columns=['timestamp', 'long',
                               'lat', 'altitude', 'heart_rate'])

    distance = 0
    speed = 0
    timestamp = 0
    for track in gpx.tracks:
        for segment in track.segments:
            for point_no, point in enumerate(segment.points):
                cst = timezone('Asia/Taipei')
                timestamp = ((point.time).astimezone(
                    cst)).strftime("%Y-%m-%d %H:%M:%S")
                if point_no > 0:
                    speed = point.speed_between(segment.points[point_no - 1])
                    distance += point.distance_2d(segment.points[point_no - 1])

                df = df.append({'timestamp': timestamp, 'long': point.longitude, 'lat': point.latitude,
                                'altitude': point.elevation, 'heart_rate': point.extensions[0].text,
                                'speed': speed, 'distance': distance}, ignore_index=True)

    t = (point.time).strftime('%m.%d.%Y')
    df.to_csv(f'CSV/{t}.csv')


def fitparser(fn):
    fitfile = FitFile(fn)
    table = []
    for record in fitfile.get_messages('record'):
        values = record.get_values()
        table.append(values)

    df = pd.DataFrame(table)
    df['lat'] = df.position_lat.map(lambda x: x * 180 / (2 << 30))
    df['long'] = df.position_long.map(lambda x: x * 180 / (2 << 30))
    t = (df.iloc[-1]['timestamp']).strftime('%m.%d.%Y')
    df.to_csv(f'CSV/{t}.csv')


if __name__ == "__main__":
    d = 'RAW/'
    for num, f in enumerate(sorted(os.listdir(d), reverse=True)):
        path = f'{d}{f}'
        print(path)
        if 'FIT' in f:
            fitparser(path)
        elif 'gpx' in f:
            gpxparser(path)
