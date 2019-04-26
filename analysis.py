import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
from fitparse import FitFile
# plt.style.use('ggplot')


def fig(fn):
    fitfile = FitFile(fn)
    total = []
    for record in fitfile.get_messages('record'):
        values = record.get_values()
        total.append(values)

    df = pd.DataFrame(total)
    print(df.iloc[-1])

    try:
        df['lat'] = df.position_lat.map(lambda x: x * 180 / (2 << 30))
        df['long'] = df.position_long.map(lambda x: x * 180 / (2 << 30))
    except AttributeError as e:
        print(fn)
        print(e)
        return None

    print(df)
    # print(df.timestamp)

    fig, axes = plt.subplots(nrows=4, ncols=1)
    mpl.rcParams["figure.figsize"] = [240, 200]

    # df.plot(x='long', y='lat', ax=axes[0])
    df.plot(x='distance', y='speed', color='b', ax=axes[1])
    df.plot(x='distance', y='heart_rate', color='c', ax=axes[2])
    # df.plot.bar(x='timestamp', y=['heart_rate', 'cadence'], color=['b', 'c'])
    plt.tick_params(
        axis='x',
        which='both',
        bottom=False,
        top=False,
        labelbottom=False)
    plt.show()


if __name__ == "__main__":
    fn = 'FIT/94MG0247.FIT'
    fig(fn)
