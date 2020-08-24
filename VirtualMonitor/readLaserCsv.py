import time
import numpy as np

def readCSV():
    print(time.perf_counter())
    f = open('positions/shadow/2020-07-31-17-04-52-laser1.csv', 'r')

    print(time.perf_counter())
    time_list = []
    laser_list = np.zeros([107281, 1081], np.float32)
    linenum = 0
    while True:
        line = f.readline()
        if not line:
            break
        print(linenum)
        info = line.split(',')
        time_list.append(info[0] + info[1][2:])
        for i in range(1081):
            laser_list[linenum][i] = float(info[i + 2])
        linenum += 1
    print(time.perf_counter())

if __name__ == '__main__':
    print('This is not the correct entrance!\nPlease exec main!')