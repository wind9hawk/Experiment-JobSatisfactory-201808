# coding:utf-8
# 本脚本用于基于CERT5.2-LaidOff-Relationship.csv的用户数据统计，重点是场景二的30个攻击用户

#CERT5.2 LaidOff Relationships for all Users
#MMK1532,No,0,11,21,87,119
#NTB0710,No,3,17,28,71,119
#MTD0971,2010-10,2,4,11,43,63

import sys
import os
from sklearn.preprocessing import MinMaxScaler
import numpy as np

print 'CERT5.2 laid-off users statistical analysis...\n'
f = open('CERT5.2-LaidOff-Relationship.csv', 'r')
f_lst = f.readlines()
f.close()

Users_CERT = []  # 用户列表
LaidOff_Users = [] # 离职人员数目
for line in f_lst:
    line_lst = line.strip('\n').strip(',').split(',')
    if len(line_lst) < 2:
        continue
    LaidOff_Users_tmp = []
    Users_CERT.append(line_lst[0])
    LaidOff_Users_tmp.append(float(line_lst[2]))
    LaidOff_Users_tmp.append(float(line_lst[3]))
    LaidOff_Users_tmp.append(float(line_lst[4]))
    LaidOff_Users_tmp.append(float(line_lst[5]))
    LaidOff_Users_tmp.append(float(line_lst[6]))
    LaidOff_Users.append(LaidOff_Users_tmp)
print 'LaidOff 用户数据统计完毕...\n'




# 使用MinMax统计
LaidOff_Users_array = np.array(LaidOff_Users)
LaidOff_Users_MinMax = MinMaxScaler().fit_transform(LaidOff_Users_array)

f = open('CERT5.2-LaidOff-Relationship-Statistical.csv', 'w')
for i in range(len(Users_CERT)):
    f.write(Users_CERT[i])
    f.write(',')
    for ele in LaidOff_Users_MinMax[i]:
        f.write(str(ele))
        f.write(',')
    f.write('\n')




print '离职用户统计分析完毕...\n'





print '重点分析CERT5.2场景二攻击用户的离职用户情况...\n'
# G:\GitHub\Essay-Experiments\Experiment-JobSatisfactory-201808\r5.2-2
Insiders = []
DirPath = os.path.dirname(sys.path[0]) + '\\' + 'r5.2-2'
for file in os.listdir(DirPath):
    # r5.2-2-ZIE0741.csv
    Insiders.append(file[7:-4])




for usr in Insiders:
    usr_index = Users_CERT.index(usr)
    print Users_CERT[usr_index], ':\t'
    for ele in LaidOff_Users_MinMax[usr_index]:
        print ele, ','
    print '\n'


sys.exit()