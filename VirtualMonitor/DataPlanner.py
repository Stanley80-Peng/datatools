import os
import re
import multiprocessing as mp
from multiprocessing import Pool


class DataPlanner(object):
    def __init__(self, path):
        self.delete_existed_files()
        self.valid_file_count = 0
        self.pool_files(path)

    @staticmethod
    def delete_existed_files():
        if not os.path.exists('positions') or not os.path.exists('positions/planner'):
            return
        files = os.listdir('positions/planner')
        for file in files:
            os.remove('positions/planner/' + str(file))

    def pool_files(self, path):
        p = Pool(mp.cpu_count())
        files = sorted(os.listdir(path))
        for file in files:
            if str(file).find('planner') + 1 and str(file).find('root') + 1 \
                    and str(file).find('INFO') + 1:
                self.valid_file_count += 1
                p.apply_async(proc_file, args=(path, str(file),))
        p.close()
        p.join()


def proc_file(path, filename):
    def append(data_line):
        pattern = re.compile(r'[(][^)]*[)]')
        find_list = pattern.findall(data_line)
        x_y_theta = find_list[1].split(',')
        v_omega = find_list[3].split(',')
        get_time = data_line.split(' ')
        after_ignore = get_time[1].split('.')
        day_list.append(data_line[1:5])
        time_list.append(after_ignore[0])
        x_list.append(x_y_theta[0][1:])
        y_list.append(x_y_theta[1][1:])
        theta_list.append(x_y_theta[2][1:-1])
        v_list.append(v_omega[0][1:])
        other_list.append('none')

    def append_load():
        if len(x_list):
            other_list[len(x_list) - 1] = 'load'

    def write_csv(name):  # 把有用的数据写到positions文件夹内的csv文件中
        if not os.path.exists('positions'):
            os.mkdir('positions')
        if not os.path.exists('positions/planner'):
            os.mkdir('positions/planner')
        out_file = open('positions/planner/' + name + '.csv', 'w', encoding='UTF-8')
        for i in range(len(x_list)):
            out_file.write(day_list[i] + ',')
            out_file.write(time_list[i] + ',')
            out_file.write(x_list[i] + ',')
            out_file.write(y_list[i] + ',')
            out_file.write(theta_list[i] + ',')
            out_file.write(v_list[i] + ',')
            out_file.write(str(other_list[i]) + '\n')
        out_file.close()

    day_list = []
    time_list = []
    x_list = []
    y_list = []
    theta_list = []
    v_list = []
    other_list = []
    f = open(path + '/' + filename)
    # print('open file ' + filename)  #
    while True:
        line = f.readline()
        if not line:
            break
        if re.search('(x, y, theta)', line):
            append(line)
        elif re.search('Forklift is down', line):
            append_load()
    f.close()
    write_csv(filename)


if __name__ == '__main__':
    print('This is not the correct entrance!\nPlease exec main!')
