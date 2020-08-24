import os
import re
import time
import matplotlib.pyplot as plt
from math import *
from matplotlib.animation import FuncAnimation


class AnimatePlanner(object):
    def __init__(self, date):
        self.map_path = ''
        self.planner_path = ''
        self.planner_identifier = ''
        self.robot_com_path = ''
        self.robot_com_identifier = ''
        self.slam_path = ''
        self.slam_identifier = ''
        self.middle_end_path = ''
        self.middle_end_identifier = ''

        self.day_num = int(date)
        self.data_count = 0

        self.time_list = []  # in csv col-2 [1]
        self.x_list = []  # in csv col-3 [2]
        self.y_list = []  # in csv col-4 [3]
        self.theta_list = []  # in csv col-5 [4]
        self.v_list = []  # in csv col-6 [5] (only in planner mode)
        self.other_list = []  # in csv col-10 [9] (only in planner mode)

        self.loads_x = []  # (only in planner mode)
        self.loads_y = []  # (only in planner mode)

        self.img_height = 0  # used to adjust plot limits
        self.img_width = 0  # used to adjust plot limits

        self.beg_index = 0
        self.end_index = 0

        self.log_speed = 0
        self.base_speed = 0
        self.sing_aug = 0
        self.sleep_time = 0
        self.auto_del = 0
        self.max_fps = 0

        self.len_robot = 0
        self.wid_robot = 0

        self.pause_flag = False
        self.hide_path = False

        self.fig_width = 0
        self.fig_height = 0

        self.get_config()

    def get_config(self):
        f = open('config.txt', 'r', encoding='UTF-8')
        lines = f.readlines()

        self.map_path = lines[1].split('\'')[1]
        self.auto_del = int(lines[10].split('\'')[1])

        self.planner_path = lines[3].split('\'')[1]
        self.planner_identifier = lines[3].split('\'')[3]
        self.robot_com_path = lines[4].split('\'')[1]
        self.robot_com_identifier = lines[4].split('\'')[3]
        self.slam_path = lines[5].split('\'')[1]
        self.slam_identifier = lines[5].split('\'')[3]
        self.middle_end_path = lines[6].split('\'')[1]
        self.middle_end_identifier = lines[6].split('\'')[3]

        self.log_speed = int(lines[12].split('\'')[1])
        self.base_speed = float(lines[13].split('\'')[1])

        self.max_fps = int(lines[18].split('\'')[1])
        if self.max_fps > 64:
            self.max_fps = 64
        self.len_robot = int(lines[19].split('\'')[1]) / 2
        self.wid_robot = int(lines[19].split('\'')[3]) / 2
        self.fig_width = int(lines[20].split('\'')[1])
        self.fig_height = int(lines[20].split('\'')[3])

        f.close()

    def plan_get(self):
        _dir = os.listdir('./positions/planner')
        _dir.sort()
        for file in _dir:
            with open('./positions/planner/' + file, encoding='UTF-8') as f:
                self.proc_csv_plan(f)
        return self.data_count

    def proc_csv_plan(self, f):
        lines = f.readlines()
        for line in lines:
            if not int(line[0:4]) == self.day_num:
                continue
            line = line.strip('\n')
            info = line.split(',')
            self.time_list.append(str(info[1]))
            self.x_list.append(int(info[2]))
            self.y_list.append(int(info[3]))
            self.theta_list.append(float(info[4]))
            self.v_list.append(float(info[5]))
            self.other_list.append(info[6])
            self.data_count += 1

    def start(self, mes, map_id):

        fig, ax = plt.subplots(figsize=(self.fig_width, self.fig_height))
        head, = ax.plot([], [], linewidth=1.6, color='#ff00e6')
        border, = ax.plot([], [], linewidth=1.6, color='#00b1fe')
        path, = ax.plot([], [], linewidth=1, color='#a771fd')
        text_detail = ax.text(30, 125, '  ', fontsize=8)
        loads, = ax.plot([], [], 'o', markersize=4, color='orange')

        im = plt.imread(self.map_path + '/' + str(map_id) + '.png')
        plt.imshow(im, 'gray')
        plt.axis('off')

        def jump():
            sec = int(mes.get())
            self.end_index += sec * self.log_speed
            if self.end_index >= self.data_count:
                self.end_index = self.data_count - 1
            if self.end_index <= 1:
                self.end_index = 1
            if sec < 0:
                if self.end_index + sec < self.beg_index:
                    self.beg_index = self.end_index

        def adjust_frame(spd):
            sec_aug = float(spd) * float(self.base_speed) * float(self.log_speed)
            self.sing_aug = ceil(sec_aug / float(self.max_fps))
            actual_rate = sec_aug / float(self.sing_aug)
            self.sleep_time = float(1000) / actual_rate - 15.62

        def speed():
            new_speed = mes.get()
            adjust_frame(new_speed)

        def auto():
            sec = int(mes.get())
            self.auto_del = int(sec * self.log_speed)

        def pause():
            self.pause_flag = True if self.pause_flag is False else False

        def clear_path():
            self.beg_index = self.end_index
            self.auto_del = 0

        def hide_path():
            self.hide_path = True if self.hide_path is False else False

        def clear_loads():
            self.loads_x.clear()
            self.loads_y.clear()

        def skip():
            while True:
                if not self.v_list[self.end_index]:
                    self.end_index += 1
                else:
                    break

        def stamp():
            print(self.time_list[self.end_index])

        def save_fig():
            print('Save figure at ' + self.time_list[self.end_index])
            if not os.path.exists('figures'):
                os.mkdir('figures')
            times = str(self.time_list[self.end_index]).split(':')

            plt.savefig('figures' + '/' + 'planner-' + str(self.day_num) + '-' +
                        times[0] + times[1] + times[2][0:3] + '.png', dpi=300)

        def find_line(log_path, identifier):
            files = sorted(os.listdir(log_path))
            time_tup = str(self.time_list[self.end_index]).split(':')
            if identifier == 'planner' or identifier == 'slamNode' or identifier == 'robotcomm':
                date_time = str(self.day_num) + ' ' + time_tup[0] + ':' + time_tup[1]
            else:
                date_time = str(self.day_num) + ' ' + time_tup[0]
            # print(date_time)
            for file in files:
                if re.search('INFO', str(file)) and re.search(identifier, str(file)) and re.search('log', str(file)):
                    local = time.localtime(os.path.getmtime(log_path + '/' + file))
                    mtime = time.strftime('%Y-%m-%d-%H-%M-%S', local).split('-')
                    # print(int(mtime[1] + mtime[2]))
                    if not self.day_num - 1 > int(mtime[1] + mtime[2]):
                        # print('searching ' + file)
                        with open(log_path + '/' + str(file)) as f:
                            line_count = 0
                            lines = f.readlines()
                            for line in lines:
                                line_count += 1
                                if re.search(date_time, line):
                                    print(line)
                                    command = 'code --goto ' + log_path + '/' + \
                                              str(file) + ':' + str(line_count)
                                    os.system(command=command)
                                    return
            print('cannot find' + date_time + 'in selected folder')

        def planner():
            if not os.path.isdir(self.planner_path):
                print('Incorrect planner log path')
                return
            find_line(self.planner_path, self.planner_identifier)

        def robot_com():
            if not os.path.isdir(self.robot_com_path):
                print('Incorrect robot_com log path')
                return
            find_line(self.robot_com_path, self.robot_com_identifier)

        def slam():
            if not os.path.isdir(self.slam_path):
                print('Incorrect slam log path')
                return
            find_line(self.slam_path, self.slam_identifier)

        def middle_end():
            if not os.path.isdir(self.middle_end_path):
                print('Incorrect middle_end log path')
                return
            find_line(self.middle_end_path, self.middle_end_identifier)

        def view_all():
            planner()
            robot_com()
            slam()
            middle_end()

        func_dict = {
            'jump': jump,
            'speed': speed,
            'auto': auto,
            'pause': pause,
            'clear_path': clear_path,
            'hide_path': hide_path,
            'clear_loads': clear_loads,
            'skip': skip,
            'stamp': stamp,
            'save_fig': save_fig,
            'planner': planner,
            'robot_com': robot_com,
            'slam': slam,
            'middle_end': middle_end,
            'view_all': view_all,
        }

        def check_load():
            if self.other_list[self.end_index] == 'load':
                self.loads_x.append(self.x_list[self.end_index])
                self.loads_y.append(self.y_list[self.end_index])

        def check_mes():
            if not mes.empty():
                func = func_dict.get(mes.get())
                func()
            if not self.pause_flag:
                self.end_index += self.sing_aug
            if self.end_index >= self.data_count:
                self.end_index = self.data_count - 1
            check_load()

        def get_path():
            if not self.hide_path:
                if self.auto_del:
                    begin = self.beg_index if self.beg_index > self.end_index - self.log_speed * \
                                              self.auto_del else self.end_index - self.log_speed * self.auto_del
                    return self.x_list[begin:self.end_index], self.y_list[begin:self.end_index]
                else:
                    return self.x_list[self.beg_index:self.end_index], \
                           self.y_list[self.beg_index:self.end_index]
            else:
                return [], []

        def get_edges():
            points_x = [0, 0, 0, 0, 0]
            points_y = [0, 0, 0, 0, 0]
            phi = atan(self.wid_robot / self.len_robot)
            theta_a = self.theta_list[self.end_index] - phi
            half_diag = sqrt(pow(self.len_robot, 2) + pow(self.wid_robot, 2)) / 2
            points_x[0] = points_x[4] = half_diag * cos(theta_a) + self.x_list[self.end_index]
            points_y[0] = points_y[4] = half_diag * sin(theta_a) + self.y_list[self.end_index]
            theta_b = self.theta_list[self.end_index] + pi + phi
            points_x[1] = half_diag * cos(theta_b) + self.x_list[self.end_index]
            points_y[1] = half_diag * sin(theta_b) + self.y_list[self.end_index]
            points_x[2] = 2 * self.x_list[self.end_index] - points_x[0]
            points_y[2] = 2 * self.y_list[self.end_index] - points_y[0]
            points_x[3] = 2 * self.x_list[self.end_index] - points_x[1]
            points_y[3] = 2 * self.y_list[self.end_index] - points_y[1]
            return points_x[0:4], points_y[0:4], points_x[3:5], points_y[3:5]

        def get_detail():
            return 'time: %s   (x, y) = (%4d, %4d)   theta = %.04lf' % (str(self.time_list[self.end_index]),
                                                                        self.x_list[self.end_index],
                                                                        self.y_list[self.end_index],
                                                                        self.theta_list[self.end_index])

        def update(no_use):
            if not no_use + 1:
                return
            check_mes()
            time.sleep(self.sleep_time / 1000)
            path.set_data(get_path())
            head.set_data(get_edges()[2:4])
            border.set_data(get_edges()[0:2])
            text_detail.set_text(get_detail())
            loads.set_data(self.loads_x, self.loads_y)

            return path, head, border, text_detail, loads,

        animation = FuncAnimation(fig, update, frames=1000,
                                  interval=1, blit=True, repeat=True)
        plt.show()
        mes.put('over')

if __name__ == '__main__':
    print('This is not the correct entrance!\nPlease exec main!')
