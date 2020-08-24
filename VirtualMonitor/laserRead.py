import os
import struct
import numpy as np


class laserRead(object):
    def __init__(self, laser_path):
        self.file = open(laser_path, 'rb')
        dir_name_tup = (laser_path.split('/')[-1]).split('-')
        self.date = dir_name_tup[1] + dir_name_tup[2]
        self.start_hour = int(dir_name_tup[3])
        self.start_min = int(dir_name_tup[4])
        self.start_sec = int(dir_name_tup[5])
        self.first_flag = True
        self.always_minus = -1

    def read_line(self):
        _time = self.file.read(2*4)
        if not _time:
            return None, None, None,
        time_tup = struct.unpack('II', _time)
        if self.first_flag:
            self.always_minus = int(time_tup[0])
            self.first_flag = False
        sub_sec = int(str(time_tup[1])[0:2])
        sub_sec -= sub_sec % 3
        time_stamp = str(time_tup[0]) + '.' + str(sub_sec)

        exp_time = self.get_exp_time(time_tup[0])
        data = self.get_data()
        return time_stamp, exp_time, data,

    def get_exp_time(self, time_tup):
        cor_time = time_tup[0] - self.always_minus
        cor_time += self.start_hour * 3600 + self.start_min * 60 + self.start_sec
        hour = int(cor_time / 3600)
        if hour > 23:
            hour -= 24
        min = int((cor_time % 3600 - cor_time % 60) / 60)
        if min > 59:
            min -= 60
        sec = int(cor_time % 60)
        if sec > 59:
            sec -= 60
        return '%02d:%02d:%02d,' % (hour, min, sec)

    def get_data(self):
        self.file.read(38)
        range_length = struct.unpack('I', self.file.read(4))
        data = struct.unpack('I'*range_length, self.file.read(4*range_length))
        return data


if __name__ == '__main__':
    print('This is not the correct entrance!\nPlease exec main!')