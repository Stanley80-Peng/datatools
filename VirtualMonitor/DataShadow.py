import os
import time
import struct
from multiprocessing import Pool
import multiprocessing as mp


class DataShadow(object):
    def __init__(self, path):
        proc_dir(path)


def delete_existed_files():
    if not os.path.isdir('positions') and os.path.isdir('positions/shadow'):
        return
    files = os.listdir('positions/shadow')
    for file in files:
        os.remove('positions/shadow/' + str(file))


def proc_dir(path):
    files = os.listdir(path)
    for file in files:
        with open(path + '/' + file, 'rb') as f:
            if f.name.split('/')[-1].find('slam') + 1:
                proc_slam(f)


def proc_slam(in_file):
    if not os.path.exists('positions'):
        os.mkdir('positions')
        os.mkdir('positions/shadow')
    elif not os.path.exists('positions/shadow'):
        os.mkdir('positions/shadow')

    out_file = open('positions/shadow/slam1.csv', 'w', encoding='UTF-8')
    save_sec = 0
    while True:

        _time = in_file.read(2*4)
        if not _time:
            break

        unpack_time = struct.unpack('II', _time)
        now_sec = str(unpack_time[0]) + '0' * (9-len(str(unpack_time[1]))) + str(unpack_time[1])
        now_sec = int(int(now_sec) / pow(10, 7))
        now_sec = now_sec - now_sec % 2
        now_sec /= 100
        '''sub_sec = str(pow(10, -9) * float(unpack_time[1]))[2:4]
        sub_sec = sub_sec - sub_sec % 2
        now_sec = str(unpack_time[0]) + '.' + '%02d'.format(sub_sec)'''
        if now_sec == save_sec:
            in_file.read(4*7)
            continue
        save_sec = now_sec
        out_file.write('%.2f,' % now_sec)

        _float = in_file.read(4*7)
        unpack_float = struct.unpack('f'*7, _float)
        for i in range(6):
            out_file.write('%.4f,' % unpack_float[i])
        out_file.write('%.4f\n' % unpack_float[6])

    in_file.close()
    out_file.close()


if __name__ == '__main__':
    print('This is not the correct entrance!\nPlease exec main!')