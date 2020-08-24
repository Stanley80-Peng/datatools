import os
import re
import sys
import time
import multiprocessing as mp
from multiprocessing import Pool

temp_path = 'ChargeTemp'


def clear_dir():
    if not os.path.exists(temp_path):
        os.mkdir(temp_path)
    else:
        files = os.listdir(temp_path)
        for file in files:
            os.remove(temp_path + '/' + file)


class DataSeparate(object):
    def __init__(self, path):
        self.path = path
        clear_dir()
        self.process_dir()

    def process_dir(self):
        files = sorted(os.listdir(self.path))
        p = Pool(mp.cpu_count())
        print(mp.cpu_count())
        for file in files:
            if re.search('planner', file) and re.search('log', file) and re.search('INFO', file):
                print('Accept file: ' + file)
                p.apply_async(process_file, args=(self.path + '/' + file, file.split('.')[-2],))
        p.close()
        p.join()


def process_file(f_name, name):
    f = open(f_name, 'r', encoding='UTF-8')
    date = -1
    begin = 0
    over = 0
    success = 0
    fail = 0
    retry = 0
    time_list = []
    reason_list = []
    phase_list = []
    try_list = []

    def output_day_data():
        out_file = open('ChargeTemp/' + name + '.csv', 'w', encoding='UTF-8')
        # out_file.write('date,begin,over,success,fail,retry\n')
        out_file.write('%d,%d,%d,%d,%d,%d\n' % (int(date), begin, over, success,
                                                fail, retry))
        if fail:
            for j in range(len(time_list)):
                out_file.write(',%d,%s,%s,%s,%s\n' % (j, time_list[j], reason_list[j],
                                                      phase_list[j], try_list[j]))
        out_file.write('\n')
        out_file.close()

    lines = f.readlines()
    for i in range(len(lines)):
        if not lines[i][1:5].isdigit():
            continue
        if date == -1:
            date = int(lines[i][1:5])
        if int(lines[i][1:5]) != date:
            output_day_data()
            begin = 0
            over = 0
            success = 0
            fail = 0
            retry = 0
            time_list.clear()
            reason_list.clear()
            phase_list.clear()
            try_list.clear()
            date = int(lines[i][1:5])
        if re.search('adjust', lines[i]):
            retry += 1
        if not re.search('<Charge>', lines[i]):
            continue
        if re.search('BEGIN', lines[i]):
            begin += 1
        elif re.search('OVER', lines[i]):
            over += 1
        elif re.search('SUCCESS', lines[i]):
            success += 1
        elif re.search('FAIL', lines[i]):
            fail += 1
            time_list.append(lines[i][6:14])
            phase_list.append(lines[i].split(']')[-2].split(':')[-1])
            try_list.append(lines[i + 1].split(']')[-3].split(':')[-1])
            reason_list.append(lines[i + 1].split(']')[-2].strip('['))
    if begin:
        output_day_data()
