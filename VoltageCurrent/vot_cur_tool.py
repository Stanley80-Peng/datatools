import os
import sys

from PyQt5.QtWidgets import QFileDialog, QMessageBox
from VotCurDraw import *
from Vot_Cur_ui import *


class ToolWindow(Ui_Form):
    def init_ui(self, form):
        self.setupUi(form)
        self.declare_globals()
        self.set_config()
        self.connect_buttons()

    def declare_globals(self):
        self.robotcomm_path = ''
        self.fig_width = 0
        self.fig_height = 0
        self.dpi = 0
        self.max_vol = 0
        self.min_vol = 0
        self.max_cur = 0
        self.min_cur = 0

    def set_config(self):
        if not os.path.exists('config.txt'):
            QMessageBox.information(None, 'ERROR', 'Failed to open config file!\nPlease clone again!')
            return
        config_file = open('config.txt', 'r', encoding='UTF-8')
        lines = config_file.readlines()
        self.robotcomm_path = lines[0].split('\'')[1]
        self.fig_width = lines[1].split('\'')[1]
        self.fig_height = lines[1].split('\'')[3]
        self.dpi = lines[2].split('\'')[1]
        self.max_vol = lines[3].split('\'')[1]
        self.min_vol = lines[4].split('\'')[1]
        self.max_cur = lines[5].split('\'')[1]
        self.min_cur = lines[6].split('\'')[1]

        self.lineEdit_path.setText(self.robotcomm_path)

    def connect_buttons(self):
        self.button_browse.clicked.connect(self.browse)
        self.button_draw.clicked.connect(self.draw)

    def browse(self):  # 以工作者目录为起始目录浏览所需文件夹的位置
        dir_choose = QFileDialog.getExistingDirectory(None, "Choose robotcomm DIR", os.path.expanduser('~'))
        if dir_choose == "":
            return
        self.lineEdit_path.setText(dir_choose)

    def draw(self):
        self.robotcomm_path = self.lineEdit_path.text()
        VotCurDraw(self)


def show_ToolWindow():  # 此函数为生成 QWidget 的标准函数，非必要时请尽量不要修改
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QWidget()
    ui = ToolWindow()
    ui.init_ui(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    show_ToolWindow()
