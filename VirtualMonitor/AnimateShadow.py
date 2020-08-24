import os
import re
import time
import matplotlib.pyplot as plt
from math import *
from PIL import Image
from matplotlib.animation import FuncAnimation


class AnimateShadow(object):
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

        self.day_num = date
        self.data_count = 0
        self.now_time = ''

        self.time_list = []  # in csv col-2 [1]
        self.x_list = []  # in csv col-3 [2]
        self.y_list = []  # in csv col-4 [3]
        self.theta_list = []  # in csv col-5 [4]
        self.laser1_list = []
        self.laser2_list = []

        self.x_excursion = 0  # (only in shadow mode)
        self.y_excursion = 0  # (only in shadow mode)

        self.beg_index = 0
        self.end_index = 0

        self.img_height = 0
        self.img_width = 0

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
        self.len_robot = int(lines[19].split('\'')[1]) / 2
        self.wid_robot = int(lines[19].split('\'')[3]) / 2
        self.fig_width = int(lines[20].split('\'')[1])
        self.fig_height = int(lines[20].split('\'')[3])

        f.close()

    def shad_get(self, map_id):
        self.img_get(map_id)
        self.slam_get(map_id)

    def img_get(self, map_id):
        img = Image.open(self.map_path + '/' + map_id + '.png')
        self.img_height = img.height
        self.img_width = img.width

    def slam_get(self, map_id):
        DIR = os.listdir('./positions/shadow')
        DIR.sort()
        for file in DIR:
            with open('./positions/shadow/' + file, encoding='UTF-8') as f:
                self.proc_csv_slam(f, map_id)

    def proc_csv_slam(self, f, map_id):
        self.get_excursion(map_id)
        lines = f.readlines()
        for line in lines:
            line = line.strip('\n')
            info = line.split(',')
            self.time_list.append(info[0])
            self.x_list.append(int(float(info[1]) * 50 - self.x_excursion))
            self.y_list.append(int(self.img_height - (float(info[2]) * 50 - self.y_excursion * 50)))
            self.theta_list.append(float(-2 * atan2(float(info[6]), float(info[7]))))
            self.data_count += 1
        f.close()

    def get_excursion(self, map_id):
        map_json = open(self.map_path + '/' + str(map_id) + '.json')
        line = map_json.readline()
        self.x_excursion = float(line.split(':')[3][0:9])
        self.y_excursion = float(line.split(':')[4][0:9])

    def start(self, mes, map_id, file_path):
        laser1_data = open(file_path + 'laser1Record.bin', 'rb')
        laser2_data = open(file_path + 'laser2Record.bin', 'rb')

        fig, ax = plt.subplots(figsize=(10, 10))
        head, = ax.plot([], [], linewidth=1.6, color='#ff00e6')
        border, = ax.plot([], [], linewidth=1.6, color='#00b1fe')
        path, = ax.plot([], [], linewidth=1, color='#a771fd')
        text_detail = ax.text(30, 125, '  ', fontsize=8)
        laser1, = ax.plot([], [], 'o', markersize=2)
        laser2, = ax.plot([], [], 'o', markersize=2)
        im = plt.imread(self.map_path + '/' + map_id + '.png')
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
                self.beg_index = self.end_index

        def adjustFrame(spd):
            sec_aug = float(spd) * float(self.base_speed) * float(self.log_speed)
            self.sing_aug = ceil(sec_aug / float(self.max_fps))
            actual_rate = sec_aug / float(self.sing_aug)
            self.sleep_time = float(1000) / actual_rate - 27

        def speed():
            new_speed = mes.get()
            adjustFrame(new_speed)

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

        def stamp():
            print(self.time_list[self.end_index])

        def save_fig():
            print('Save figure at ' + self.time_list[self.end_index])
            if not os.path.exists('figures'):
                os.mkdir('figures')
            times = self.now_time
            plt.savefig('figures' + '/' + 'shadow-' +
                        times[0] + times[1] + times[2][0:3] + '.png', dpi=300)

        def find_line(log_path, identifier):
            files = os.listdir(log_path)
            date_time = str(self.day_num) + ' ' + self.time_list[self.end_index]
            for file in files:
                if re.search('INFO', str(file)) and re.search(identifier, str(file)) and re.search('log', str(file)):
                    mtime = str(os.path.getmtime(log_path + '/' + file)).split('-')
                    if not self.day_num > int(mtime[1] + mtime[2][0:2]):
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
            'stamp': stamp,
            'save_fig': save_fig,
            'planner': planner,
            'robot_com': robot_com,
            'slam': slam,
            'middle_end': middle_end,
            'view_all': view_all,
        }

        def check_mes():
            if not mes.empty():
                func = func_dict.get(mes.get())
                func()
            if not self.pause_flag:
                self.end_index += self.sing_aug
            if self.end_index >= self.data_count:
                self.end_index = self.data_count - 1

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
            theta_A = self.theta_list[self.end_index] - phi
            half_diag = sqrt(pow(self.len_robot, 2) + pow(self.wid_robot, 2)) / 2
            points_x[0] = points_x[4] = half_diag * cos(theta_A) + self.x_list[self.end_index]
            points_y[0] = points_y[4] = half_diag * sin(theta_A) + self.y_list[self.end_index]
            theta_B = self.theta_list[self.end_index] + pi + phi
            points_x[1] = half_diag * cos(theta_B) + self.x_list[self.end_index]
            points_y[1] = half_diag * sin(theta_B) + self.y_list[self.end_index]
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

        def get_laser1_data():
            return [], []

        def get_laser2_data():
            return [], []

        def update(no_use):
            check_mes()
            time.sleep(self.sleep_time / 1000)
            path.set_data(get_path())
            head.set_data(get_edges()[2:4])
            border.set_data(get_edges()[0:2])
            text_detail.set_text(get_detail())
            laser1.set_data(get_laser1_data())
            laser2.set_data(get_laser2_data())

            return path, head, border, text_detail, laser1, laser2,


        animation = FuncAnimation(fig, update, frames=[i for i in range(0, 1000)],
                                  interval=1, blit=True, repeat=True)
        plt.show()
        mes.put('over')

if __name__ == '__main__':
    print('This is not the correct entrance!\nPlease exec main!')