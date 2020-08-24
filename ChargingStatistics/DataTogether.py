import os


class DataTogether(object):
    def __init__(self):
        self.date = -1
        self.begin = 0
        self.over = 0
        self.success = 0
        self.fail = 0
        self.retry = 0
        self.fail_list = []
        self.temp_path = 'ChargeTemp'
        self.out_file = open('ChargeData.csv', 'w', encoding='UTF-8')
        self.get_together()

    def get_together(self):
        files = sorted(os.listdir(self.temp_path))
        for file in files:
            with open(self.temp_path + '/' + file, 'r', encoding='UTF-8') as f:
                self.proc_file(f)
        if self.begin or self.over:
            self.output_day_data()

    def proc_file(self, f):
        main_line = f.readline()
        main_line.strip('\n')
        infos = main_line.split(',')
        if self.date == -1:
            self.date = int(infos[0])
        elif self.date != int(infos[0]):
            self.output_day_data()
            self.clear()
            self.date = int(infos[0])
        self.begin += int(infos[1])
        self.over += int(infos[2])
        self.success += int(infos[3])
        self.fail += int(infos[4])
        self.retry += int(infos[5])
        for i in range(int(infos[4])):
            temp = f.readline()
            self.fail_list.append(temp)

    def output_day_data(self):
        self.out_file.write('date,begin,over,success,fail,retry\n')
        self.out_file.write('%d,%d,%d,%d,%d,%d\n' % (int(self.date), self.begin, self.over, self.success,
                                                     self.fail, self.retry))
        if self.fail:
            self.out_file.write(',fail num,fail time,reason,stuck phase,try times\n')
            for i in range(len(self.fail_list)):
                self.out_file.write(self.fail_list[i])
        self.out_file.write('\n')

    def clear(self):
        self.begin = 0
        self.over = 0
        self.success = 0
        self.fail = 0
        self.retry = 0
        self.fail_list.clear()



if __name__ == '__main__':
    DataTogether()


