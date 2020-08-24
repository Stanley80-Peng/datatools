from PyQt5.QtWidgets import QFileDialog, QMessageBox
from windowContents_for_linux import *
from multiprocessing import Process, Queue
from AnimatePlanner import *
from AnimateShadow import *
from DataShadow import *
from DataPlanner import *
import os
import sys
import datetime as dt


class ToolWindow(Ui_Form):

    def init_ui(self, form):
        self.setupUi(form)
        self.declare_globals()
        self.set_config()
        self.connect_buttons()

    def declare_globals(self):
        self.map_path = ''
        self.mes = Queue()
        self.map_id = ''
        self.is_running = False
        self.file_path = ''

    def set_config(self):
        if not os.path.exists('config.txt'):
            QMessageBox.information(None, 'ERROR', 'Failed to open config file!\nPlease clone again!')
            exit(1)

        if not self.check_essentials():
            QMessageBox.information(None, 'ERROR',
                                    'Log paths are not all correct\nSome functions might not work well')

        f = open('config.txt', 'r', encoding='UTF-8')
        lines = f.readlines()

        self.lineEdit_filepath.setText(str(lines[0].split('\'')[1]))
        self.map_path = str(lines[1].split('\'')[1])
        self.lineEdit_mapid.setText(str(lines[8].split('\'')[1]))
        show_mode = str(lines[9].split('\'')[1])
        if show_mode == 'planner':
            self.radio_planner.setChecked(True)
        elif show_mode == 'shadow':
            self.radio_shadow.setChecked(True)
        self.lineEdit_auto.setText(str(lines[10].split('\'')[1]))
        f.close()

        if not os.path.exists(self.map_path):
            QMessageBox.information(None, 'ERROR', 'Please set the correct map path in \'config.txt\'!')
            #exit(1)

        default_time = str(dt.datetime.now()).split('-')
        self.lineEdit_date.setText(default_time[1] + default_time[2][0:2])

    def connect_buttons(self):
        self.button_browse.clicked.connect(self.browse)
        self.button_init.clicked.connect(self.init)
        self.button_start.clicked.connect(self.start)
        self.button_pause.clicked.connect(lambda: self.mes.put('pause'))
        self.slider_speed.valueChanged.connect(self.speed_change)
        self.button_forw30.clicked.connect(lambda: self.jump(30))
        self.button_forw15.clicked.connect(lambda: self.jump(900))
        self.button_forw1h.clicked.connect(lambda: self.jump(3600))
        self.button_back20.clicked.connect(lambda: self.jump(-20))
        self.button_back6.clicked.connect(lambda: self.jump(-360))
        self.button_back30.clicked.connect(lambda: self.jump(-1800))
        self.button_skip.clicked.connect(lambda: self.mes.put('skip'))
        self.button_clear_path.clicked.connect(lambda: self.mes.put('clear_path'))
        self.button_hide_path.clicked.connect(lambda: self.mes.put('hide_path'))
        self.button_clear_load.clicked.connect(lambda: self.mes.put('clear_loads'))
        self.button_save.clicked.connect(lambda: self.mes.put('save_fig'))
        self.button_jump.clicked.connect(self.customize_jump)
        self.button_set.clicked.connect(self.set_auto_clear)
        self.button_stamp.clicked.connect(lambda: self.mes.put('stamp'))
        self.button_planner.clicked.connect(lambda: self.mes.put('planner'))
        self.button_robotcom.clicked.connect(lambda: self.mes.put('robot_com'))
        self.button_slam.clicked.connect(lambda: self.mes.put('slam'))
        self.button_middle_end.clicked.connect(lambda: self.mes.put('middle_end'))
        self.button_view_all.clicked.connect(lambda: self.mes.put('view_all'))

    def browse(self):  # 以工作者目录为起始目录浏览所需文件夹的位置
        dir_choose = QFileDialog.getExistingDirectory(None, "选取文件夹", os.path.expanduser('~'))
        if dir_choose == "":
            return
        self.lineEdit_filepath.setText(dir_choose)

    def init(self):
        self.map_id = self.lineEdit_mapid.text()
        self.file_path = self.lineEdit_filepath.text()

        if not os.path.exists(self.map_path + '/' + str(self.map_id) + '.png'):
            QMessageBox.information(None, 'ERROR', 'No available map in the \"maps\" folder!')
            return

        if not os.path.exists(self.file_path):
            QMessageBox.information(None, 'ERROR', 'Path does not exist!')
            return

        if not os.path.isdir(self.file_path):
            QMessageBox.information(None, 'ERROR', 'Please select a folder!')
            return

        if self.radio_planner.isChecked():
            if not DataPlanner(self.file_path).valid_file_count:
                QMessageBox.information(None, 'ERROR', 'No valid data in selected folder!')
                return
        elif self.radio_shadow.isChecked():
            DataShadow(self.file_path)
        else:
            QMessageBox.information(None, '', 'Please select replay mode!')

    def start(self):
        if not self.mes.empty():
            self.is_running = False
            while not self.mes.empty():
                self.mes.get()

        if self.is_running:  # 为防止将start误认为resume按下而新建模拟窗口，特设此检查
            QMessageBox.information(None, '', 'Animation is already running')
            return

        self.slider_speed.setValue(3)  # 设置默认起始速度为4x
        self.mes.put('speed')
        self.mes.put('4')

        self.map_id = self.lineEdit_mapid.text()
        if not os.path.exists(self.map_path + '/' + str(self.map_id) + '.png'):
            QMessageBox.information(None, 'ERROR', 'No available map in the \"maps\" folder!\n')
            return

        if self.radio_planner.isChecked():

            if not os.path.exists('./positions/planner'):
                QMessageBox.information(None, 'ERROR', 'Please init before replaying!')
                return

            if not len(os.listdir('./positions/planner')):
                QMessageBox.information(None, 'ERROR', 'No valid data!\nPlease init again!')
                return

            show = AnimatePlanner(self.lineEdit_date.text())

            if show.plan_get() == 0:
                QMessageBox.information(None, 'ERROR', 'No data of entered date!')
                return

            self.is_running = True
            plan = Process(target=show.start, args=(self.mes, self.map_id))
            plan.start()

        elif self.radio_shadow.isChecked():

            QMessageBox.information(None, 'Note',
                                    'Shadow mode is currently under maintenance!\nPlease wait for the next version!')

            '''if not os.path.exists('./positions/shadow'):
                QMessageBox.information(None, 'ERROR', 'Please check the infos above and init!')
                return
            delete_existed_files()
            show = AnimateShadow()
            show.shad_get(self.map_id)
            self.is_running = True
            shad = Process(target=show.start, args=(self.mes, self.map_id,))
            shad.start()'''

            return

    @staticmethod
    def check_essentials():
        good_flag = True
        f = open('config.txt', 'r', encoding='UTF-8')
        lines = f.readlines()
        if not os.path.isdir(lines[3].split('\'')[1]):
            good_flag = False
        if not os.path.isdir(lines[4].split('\'')[1]):
            good_flag = False
        if not os.path.isdir(lines[5].split('\'')[1]):
            good_flag = False
        if not os.path.isdir(lines[6].split('\'')[1]):
            good_flag = False
        return good_flag

    def speed_change(self):
        expo = self.slider_speed.value()
        speed = int(pow(2, expo - 1))
        self.mes.put('speed')
        self.mes.put(str(speed))
    
    def jump(self, sec):
        self.mes.put('jump')
        self.mes.put(sec)
        
    def customize_jump(self):
        self.jump(self.lineEdit_jump.text())
        
    def set_auto_clear(self):
        self.mes.put('auto')
        self.mes.put(self.lineEdit_auto.text())
    

def show_ToolWindow():  # 此函数为生成 QWidget 的标准函数，非必要时请尽量不要修改
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QWidget()
    ui = ToolWindow()
    ui.init_ui(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    show_ToolWindow()
