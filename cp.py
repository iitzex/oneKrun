import os
from shutil import copyfile


src_p = '/Volumes/GARMIN/GARMIN/ACTIVITY/'
dst_p = 'FIT/'


def main():
    src = set(os.listdir(src_p))
    dst = set(os.listdir(dst_p))

    for i in src.difference(dst):
        print(i)
        copyfile(f'{src_p}{i}', f'{dst_p}{i}')


if __name__ == "__main__":
    main()
