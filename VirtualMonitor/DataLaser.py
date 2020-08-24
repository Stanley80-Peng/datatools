import time
from math import *
import struct
from multiprocessing import Process, Pool


class DataLaser(object):
    def __init__(self, path):
        self.path = path
        self.start_hour = 0
        self.start_min = 0
        self.start_sec = 0
        self.res_path()
        self.always_minus = 0
        self.always_add = self.start_hour * 3600 + self.start_min * 60 + self.start_sec
        self.frame_id_length = 0
        self.ranges_length = 0
        self.intensities_length = 0

        p = Pool(2)
        for i in range(2):
            p.apply_async(self.proc_laser, args=(path, i,))
        # self.proc_laser(path, 1, )
        p.close()
        p.join()

    def res_path(self):
        date_time = (str(self.path).split('/')[-1]).split('-')
        self.start_hour = int(date_time[3])
        self.start_min = int(date_time[4])
        self.start_sec = int(date_time[5])

    def proc_laser(self, path, num):
        f = open(path + '/laser' + str(num + 1) + 'Record.bin', 'rb')
        out_file = open('positions/shadow/' + str(path).split('/')[-1] + '-laser' + str(num + 1) + '.csv', 'w')
        frame_id_length, ranges_length, intensities_length = self.first_line(f)
        data_count = 0
        while True:
            data_count += 1
            temp = f.read(8)
            if not temp:
                break
            time1, time2 = struct.unpack('II', temp)
            time2 = int(time2 * 0.0000001)
            time2 -= time2 % 2
            time2 = time2 * 0.01
            out_file.write('%.02f,' % float(time1 + time2))
            time1 -= self.always_minus
            time1 += self.always_add
            hour = int(time1 / 3600)
            if hour > 23:
                hour -= 24
            min = int((time1 % 3600 - time1 % 60) / 60)
            if min > 59:
                min -= 60
            sec = int(time1 % 60)
            if sec > 59:
                sec -= 60
            out_file.write('%02d:%02d:%02d,' % (hour, min, sec))  # time1
            f.read(36 + frame_id_length)
            # f.read(32 + frame_id_length)
            # test = struct.unpack('I', f.read(4))[0]
            distances = struct.unpack('f'*ranges_length, f.read(4*ranges_length))
            for i in range(ranges_length):
                out_file.write('%.4f,' % distances[i])
            out_file.write('\n')
            f.read(4 + 4 * intensities_length)
        f.close()

    def first_line(self, source_file):
        time1, time2 = struct.unpack('II', source_file.read(8))
        self.always_minus = int(time1)
        frame_id_length = struct.unpack('I', source_file.read(4))[0]
        source_file.read(frame_id_length + 28)
        ranges_length = struct.unpack('I', source_file.read(4))[0]
        source_file.read(4 * ranges_length)
        intensities_length = struct.unpack('I', source_file.read(4))[0]
        source_file.read(4 * intensities_length)
        return frame_id_length, ranges_length, intensities_length


if __name__ == '__main__':
    print('This is not the correct entrance!\nPlease exec main!')