import os
import time
import datetime as dt


class Delete(object):
    def __init__(self, path, num):
        self.dir_path = path
        self.num = int(num)
        if self.num < 7:
            self.num = 7
        self.delete_files(self.dir_path)

    def delete_files(self, path):
        none_type_list = os.listdir(path)
        for dir_or_file in none_type_list:
            if os.path.isdir(path + '/' + dir_or_file):
                self.delete_files(path + '/' + dir_or_file)
            else:
                if not str(dir_or_file).split('.')[-1].isdigit():
                    continue
                mtime = os.path.getmtime(path + '/' + dir_or_file)
                m_date = time.strftime('%Y-%m-%d', time.localtime(mtime))
                now_time = dt.datetime.now().strftime('%Y-%m-%d')
                m_days = int(m_date.split('-')[1]) * 30 + int(m_date.split('-')[2])
                n_days = int(now_time.split('-')[1]) * 30 + int(now_time.split('-')[2])
                if n_days - m_days > self.num:
                    os.remove(path + '/' + dir_or_file)
