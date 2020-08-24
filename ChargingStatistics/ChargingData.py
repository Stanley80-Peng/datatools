import os
import re


class ChargingData(object):
    def __init__(self, path):
        self.path = path
        self.out_file = open('ChargeData.csv', 'w', encoding='UTF-8')
        self.date = -1
        self.begin = 0
        self.over = 0
        self.success = 0
        self.fail = 0
        self.retry = 0
        self.time_list = []
        self.reason_list = []
        self.phase_list = []
        self.try_list = []
        self.process_dir()
        self.out_file.close()

    def process_dir(self):
        files = sorted(os.listdir(self.path))
        for file in files:
            if re.search('planner', file) and re.search('log', file) and re.search('INFO', file):
                with open(self.path + '/' + file, 'r', encoding='UTF-8') as f:
                    print('Accept file: ' + f.name)
                    self.process_file(f)
        if self.begin or self.over or self.fail:
            self.output_day_data()

    def process_file(self, f):
        lines = f.readlines()
        for i in range(len(lines)):
            if not lines[i][1:5].isdigit():
                continue
            if self.date == -1:
                self.date = int(lines[i][1:5])
            if int(lines[i][1:5]) != self.date:
                self.output_day_data()
                self.clear()
                self.date = int(lines[i][1:5])
            if re.search('adjust', lines[i]):
                self.retry += 1
            if not re.search('<Charge>', lines[i]):
                continue
            if re.search('BEGIN', lines[i]):
                self.begin += 1
            elif re.search('OVER', lines[i]):
                self.over += 1
            elif re.search('SUCCESS', lines[i]):
                self.success += 1
            elif re.search('FAIL', lines[i]):
                self.fail += 1
                self.time_list.append(lines[i][6:14])
                self.phase_list.append(lines[i].split(']')[-2].split(':')[-1])
                self.try_list.append(lines[i+1].split(']')[-3].split(':')[-1])
                self.reason_list.append(lines[i+1].split(']')[-2].strip('['))

    def output_day_data(self):
        self.out_file.write('date,begin,over,success,fail,retry\n')
        self.out_file.write('%d,%d,%d,%d,%d,%d\n' % (int(self.date), self.begin, self.over, self.success,
                            self.fail, self.retry))
        if self.fail:
            self.out_file.write(',fail num,fail time,reason,stuck phase,try times\n')
            for i in range(len(self.time_list)):
                self.out_file.write(',%d,%s,%s,%s,%s\n' % (i, self.time_list[i], self.reason_list[i],
                                                        self.phase_list[i], self.try_list[i]))
        self.out_file.write('\n')

    def clear(self):
        self.begin = 0
        self.over = 0
        self.success = 0
        self.fail = 0
        self.retry = 0
        self.time_list.clear()
        self.reason_list.clear()
        self.phase_list.clear()
        self.try_list.clear()
