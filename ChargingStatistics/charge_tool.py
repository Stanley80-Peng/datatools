import sys
import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from Charging_ui import *
from DataSeparate import *
from DataTogether import *


class ToolWindow(Ui_Form):
    def init_ui(self, form):
        self.setupUi(form)
        self.connect_buttons()
        self.lineEdit_path.setText('/home/airobot/log/planner')

    def connect_buttons(self):
        self.button_browse.clicked.connect(self.browse)
        self.button_get.clicked.connect(self.get)

    def browse(self):  # 以工作者目录为起始目录浏览所需文件夹的位置
        dir_choose = QFileDialog.getExistingDirectory(None, "Choose planner DIR", os.path.expanduser('~'))
        if dir_choose == "":
            return
        self.lineEdit_path.setText(dir_choose)

    def get(self):
        DataSeparate(self.lineEdit_path.text())
        DataTogether()


def show_ToolWindow():  # 此函数为生成 QWidget 的标准函数，非必要时请尽量不要修改
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QWidget()
    ui = ToolWindow()
    ui.init_ui(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    show_ToolWindow()
