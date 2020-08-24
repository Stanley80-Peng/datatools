import os
import re
import matplotlib.pyplot as plt

class VotCurDraw(object):
    def __init__(self, params):
        self.robotcomm_path = params.robotcomm_path
        self.fig_width = int(params.fig_width)
        self.fig_height = int(params.fig_height)
        self.dpi = int(params.dpi)
        self.max_vol = int(params.max_vol)
        self.min_vol = int(params.min_vol)
        self.max_cur = int(params.max_cur)
        self.min_cur = int(params.min_cur)
        
        self.date = -1
        self.time_list = []
        self.vot_list = []
        self.cur_list = []

        self.process_dir()

    def process_dir(self):
        if not os.path.exists('OutputIMG'):
            os.mkdir('OutputIMG')
        else:
            files_to_delete = os.listdir('OutputIMG')
            for file in files_to_delete:
                os.remove('OutputIMG' + '/' + file)

        files = os.listdir(self.robotcomm_path)
        files.sort()
        for file in files:
            if re.search('robotcomm', file) and re.search('log', file) and re.search('INFO', file):
                with open(self.robotcomm_path + '/' + file, 'r', encoding='UTF-8') as f:
                    self.process_file(f)
        if len(self.time_list):
            self.draw_a_figure()

    def process_file(self, in_file):
        lines = in_file.readlines()
        for line in lines:
            if re.search("batteryVoltage", line):
                self.append_line(re.findall(r'\d+', line), len(re.findall(r'[-]\d+', line)))
                # function len() is used to decide if the "CURRENT" statistic is below 0

    def append_line(self, tup, if_minus):
        now_date = int(tup[0])
        if self.date == -1:
            self.date = now_date
        elif now_date != self.date:
            self.draw_a_figure()
            self.clear_lists()
            self.date = now_date
            
        hour = int(tup[1])
        minute = int(tup[2])
        second = float(tup[3] + '.' + tup[4])
        voltage = float(tup[11] + '.' + tup[12])
        current = float(tup[13] + '.' + tup[14])
        
        if if_minus:
            current = -current
        if voltage > self.max_vol or voltage < self.min_vol:
            return
        if current > self.max_cur or current < self.min_cur:
            return
        self.time_list.append(hour + minute / 60 + second / 3600)
        self.vot_list.append(voltage)
        self.cur_list.append(current)
    
    def draw_a_figure(self):
        fig, ax1 = plt.subplots(figsize=(self.fig_width, self.fig_height))
        ax1.plot(self.time_list, self.vot_list, linewidth=0.4, color='b')
        ax1.set_ylabel('Voltage (Blue)')
        ax1.set_xlabel('Time(hour)')
        ax1.tick_params(labelsize=10)
        
        ax2 = ax1.twinx()
        ax2.plot(self.time_list, self.cur_list, linewidth=0.4, color='r')
        ax2.set_ylabel('Current (Red)')
        ax2.tick_params(labelsize=10)
        
        ax1.set_xlim(left=0, right=24)
        ax1.set_ylim(bottom=self.min_vol, top=self.max_vol)
        ax1.xaxis.set_major_locator(plt.MultipleLocator(2))
        ax2.set_ylim(bottom=self.min_cur, top=self.max_cur)
        
        plt.title('Battery Info of %04d' % self.date)
        plt.rcParams['savefig.dpi'] = self.dpi

        plt.savefig('OutputIMG/Battery_Info_%04d' % self.date + '.png')
        plt.close()

    def clear_lists(self):
        self.time_list.clear()
        self.vot_list.clear()
        self.cur_list.clear()
