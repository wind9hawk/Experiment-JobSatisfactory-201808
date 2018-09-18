# coding:utf-8
# 本脚本主要工作是：
# 通过分析CERT5.2场景二的攻击用户列表
# 以及通过分析CERT5.2中所有用户的离职用户关系统计数据（原始counts）
# 分别绘制同一团队内、同一部门不同团队内、同一职能下不同部门内三个层次的单个以及2-3列和的分布图

import os
import sys
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

print '开始绘制CERT5.2中所有用户离职人员关系图...\n'
# G:\GitHub\Essay-Experiments\Experiment-JobSatisfactory-201808\r5.2-2
Insiders_2 = [] # CERT5.2中场景二攻击者列表
DirPath = os.path.dirname(sys.path[0]) + '\\' + 'r5.2-2'
for user in os.listdir(DirPath):
    # r5.2-2-ZIE0741.csv
    Insiders_2.append(user[7:-4])
print 'CERT5.2场景二攻击者列表为： ', len(Insiders_2), Insiders_2[:10], '\n'




# 读取原始CERT5.2 2000个用户的离职人员关系数据
f = open('CERT5.2-LaidOff-Relationship.csv', 'r')
f_lst = f.readlines()
f.close()
LaidOff_Relationship = [] # CERT5.2所有用户的五个层次的离职人员统计次数以及前2前3个的和
for line in f_lst:
    line_lst = line.strip('\n').strip(',').split(',')
    if len(line_lst) < 2:
        continue
    LaidOff_Re = []
    # MMK1532,No,0,11,21,87,119
    LaidOff_Re.append(line_lst[0])
    LaidOff_Re.append(float(line_lst[2]))
    LaidOff_Re.append(float(line_lst[3]))
    LaidOff_Re.append(float(line_lst[4]))
    LaidOff_Re.append(float(line_lst[5]))
    LaidOff_Re.append(float(line_lst[6]))
    LaidOff_Re.append(float(line_lst[2]) + float(line_lst[3]))
    LaidOff_Re.append(float(line_lst[2]) + float(line_lst[3]) + float(line_lst[4]))
    LaidOff_Relationship.append(LaidOff_Re)
print '离职人员统计读入完成...\n'
for i in range(10):
    print LaidOff_Relationship[i], '\n'




sys.exit()

