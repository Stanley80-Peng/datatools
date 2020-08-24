#====@Stanley Peng====
#Language: Python 3.8
#Expiration Date: 2020/12/31

#All the files that need to be visualized should be put in--
#--the "BatteryInfo" folder in the parent directory

#This program uses a key word "batteryVoltage" to search if the line--
#--contains the information of battery, thus is irresponsible for--
#--any error if an irrelevant log in the directory contains the key word

#This program limits the voltage scope between 15 and 35 while limits--
#--the current scope between -6 and 8, so don't forget to change the limits if needed

#All the output images are in the "OutputIMG" directory in the parent directory


import os
import re
import matplotlib.pyplot as plt
from IPython.core.pylabtools import figsize


MAXVOT = 35
MINVOT = 15
MAXCUR = 8
MINCUR = -6
timlist = []
votlist = []
curlist = []
day = -1

def proc():
    while True:
        temp = f.readline()
        if not temp:
            break
        res = re.search("batteryVoltage", temp)
        if res:
            appe(re.findall(r'\d+', temp), len(re.findall(r'[-]\d+', temp)))
            # function len() is used to decide if the "CURRENT" statistic is below 0
        else:
            continue

def appe(tup, sta):
    global day
    nowday = int(tup[0])
    if day == -1:
        day = nowday
    elif nowday != day:
        draw()
        timlist.clear()
        votlist.clear()
        curlist.clear()
        day = nowday
        # this elif is helpful in managing memory
    hour = int(tup[1])
    min = int(tup[2])
    sec = float(tup[3] + '.' + tup[4])
    vot = float(tup[11] + '.' + tup[12])
    cur = float(tup[13] + '.' + tup[14])
    if sta:
        cur = -cur
    if vot > MAXVOT or vot < MINVOT:
        return
    if cur > MAXCUR or cur < MINCUR:
        return
    #All the statistics that don't meet the limit requirements are passed
    timlist.append(hour+min/60+sec/3600)
    votlist.append(vot)
    curlist.append(cur)
    return

def draw():
    figsize(16, 4)
    fig, ax1 = plt.subplots()
    ax1.plot(timlist, votlist, linewidth=0.4, color='b')
    ax1.set_ylabel('Votage(Blue)') #Change the color if you like :D
    ax1.tick_params(labelsize=10)
    ax2 = ax1.twinx()
    ax2.plot(timlist, curlist, linewidth=0.4, color='r')
    ax2.set_ylabel('Current(Red)') #Change the color if you like :D
    ax2.tick_params(labelsize=10)

    ax1.set_xlim(left=0, right=24)
    ax1.set_ylim(bottom=15, top=35)
    ax2.set_ylim(bottom=-6, top=8)
    ax1.xaxis.set_major_locator(plt.MultipleLocator(2))
    plt.title('BatteryInfo of 2020-'+str(day),y=-0.15)
    plt.rcParams['savefig.dpi'] = 120
    if not os.path.exists('./OutputIMG'):
        os.mkdir('./OutputIMG')
    plt.savefig('./OutputIMG/BatteryInfo-2020-'+str(day)+'.jpg')
    plt.close()
    return


print('Please wait...')
DIR = os.listdir('./BatteryInfo')
fileList = []
for file in DIR:
    fileList.append(file)
fileList.sort()
for file in fileList:
    if file.find('.DS')+1 and file.find('robotcomm')+1 and file.find('log')+1 and file.find('INFO')+1:
        with open('./BatteryInfo/'+file) as f:
            proc()
draw()
