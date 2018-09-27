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
from sklearn.decomposition import PCA


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


# 这里引入自动降维后查看自动聚类结果



# 开始构造pyplot的X轴与Y轴
# 现在的离职人员关系数据为：['CBN1983', 0.0, 8.0, 28.0, 82.0, 120.0, 8.0, 36.0]
Users_CERT52 = []
for line in LaidOff_Relationship:
        Users_CERT52.append(line[0])
# 如果直接用姓名作为X轴
#plt.xlabel('Users')
#plt.ylabel('test')
#plt.plot(Users_CERT52[:10], [1] * 10, 'ro')
#plt.show()
#plt.close()
# 上述代码说明了pyplot绘图时X轴可以是字符串列表
# 为了绘图方便，我们先转换为序号
Users_Index = range(len(Users_CERT52))
Insider_Index = []
for insider in Insiders_2:
    in_index = Users_CERT52.index(insider)
    Insider_Index.append(in_index)
    Users_Index.remove(in_index)
print 'Users_Index is like ', Users_Index[:10], '\n'
print 'Insider_Index is like ', Insider_Index[:10], '\n'


# 分别构造X轴与Y轴数组
# X轴数组就是Users_Index与Insider_Index
Users_Y = []
for ele in Users_Index:
    Users_Y.append(LaidOff_Relationship[ele][1:])
Insiders_Y = []
for ele in Insider_Index:
    Insiders_Y.append(LaidOff_Relationship[ele][1:])
print 'Users_Y is like ', Users_Y[:10], '\n'
print 'Insider_Y is like ', Insiders_Y[:10], '\n'

Users_Y_MinMax = MinMaxScaler().fit_transform(Users_Y)
Insiders_Y_MinMax = MinMaxScaler().fit_transform(Insiders_Y)
for i in range(len(Insiders_Y_MinMax)):
    print Insiders_2[i], Insiders_Y_MinMax[i], '\n'

print 'MinMax finished...\n'
print 'Users_Y_MinMax is like ', Users_Y_MinMax[:10], '\n'
print 'Insider_Y_MinMax is like ', Insiders_Y_MinMax[:10], '\n'

print 'Users_CERT52 is ', len(Users_CERT52), '\n'
print 'Users_Index is ', len(Users_Index), '\t', len(Users_Y_MinMax), '\n'
print 'Insiders_Index is ', len(Insider_Index), '\t', len(Insiders_Y_MinMax), '\n'
print '开始绘图...\n'
for i in range(7):
    plt.xlabel('Users in CERT5.2')
    plt.ylabel('LaidOff_Relationship_' + str(i))
    plt.plot(Users_Index, Users_Y_MinMax[:,i], 'bx', Insider_Index, Insiders_Y_MinMax[:,i], 'r^')
    plt.show()
    plt.close()
    i += 1
print 'Draw has finished...\n'




sys.exit()

