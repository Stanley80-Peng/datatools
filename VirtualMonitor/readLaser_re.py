import os
import time
import struct


def readLaser(file_path):
    first_flag = True
    in_file = open(file_path, 'rb')
    out_file = open('./positions/shadow/2020-07-31-17-04-52-laser2.csv', 'w')
    inihour = 17
    inimin = 4
    inisec = 52
    always_minus = -1
    data_count = 0
    while True:
        data_count += 1
        temp = in_file.read(4)
        if not temp:
            break
        unpack = struct.unpack('I', temp)
        out_file.write('%d,' % unpack[0])
        unpack = struct.unpack('=I', in_file.read(4))
        data_float = float(unpack[0]) / pow(10, 9)
        out_file.write('0.%s,' % str(data_float)[2:7])  # time2
        frame_id_length = struct.unpack('I', in_file.read(4))[0]
        in_file.read(frame_id_length)
        in_file.read(4 * 7)
        ranges_length = struct.unpack('=I', in_file.read(4))[0]
        temp = struct.unpack('f' * ranges_length, in_file.read(4 * ranges_length))
        for i in range(ranges_length):
            out_file.write('%.4f,' % temp[i])
        out_file.write('\n')
        intensities_length = struct.unpack('=I', in_file.read(4))[0]
        in_file.read(4 * intensities_length)


if __name__ == '__main__':
    print('This is not the correct entrance!\nPlease exec main!')