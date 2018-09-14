# coding:utf-8
# 本脚本主要用于初步分析CERT5.2数据集中，场景二跳槽行为的30个用户的大五人格特质分布特征；
# 根据CERT构造数据时参考的文献，N-A-C三种特质应与工作满意度有直接关联；
#
# 基本逻辑
# 1. 读入CERT5.2的psychometric-5.2.csv文件，得到全体用户列表以及对应的特质分数；
# 2. 依据读入的所有用户顺序，分别按列归一化；
# 3. 分别将第二场景的30个Insiders在图中以红色标记，查看其分布特征；

import os,sys
from sklearn.preprocessing import scale
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import matplotlib.pyplot as plt


print '本程序用于分析CERT5.2中用户的大五人格特质分布...\n'


# 读入CERT5.2数据中全部用户的ID以及OCEAN分数
# 输出当前文件路径
# print sys.path, '\n'
# print 'sys.argv[0] is: ', sys.argv[0], '\n'
# print 'sys.path[0] is : ', sys.path[0], '\n'
# sys.argv[0] is:  G:/GitHub/Essay-Experiments/Experiment-JobSatisfactory-201808/PythonCode0/UserBig5-Analyze.py
# sys.path[0] is :  G:\GitHub\Essay-Experiments\Experiment-JobSatisfactory-201808\PythonCode0
# 可以使用sys.path[0]获取当前所在目录路径
# 可以使用os.path.dirname(d)获取d的父级目录

filePath = os.path.dirname(sys.path[0]) + '\\' + 'psychometric-5.2.csv'
f_ocean = open(filePath, 'r')
f_ocean_lst = f_ocean.readlines()
f_ocean.close()
# employee_name,user_id,O,C,E,A,N
# Maisie Maggy Kline,MMK1532,17,17,16,22,28
Users = [] # 用于保存用户列表
Users_OCEAN = [] # 用于保存对应于Users列表的OCEAN分数
for line in f_ocean_lst:
    line_lst = line.strip('\n').split(',')
    if line_lst[1] == 'user_id':
        continue
    user_ocean_0 = []
    # [user_id, o, c, e, a, n]
    Users.append(line_lst[1])
    user_ocean_0.append(float(line_lst[2]))
    user_ocean_0.append(float(line_lst[3]))
    user_ocean_0.append(float(line_lst[4]))
    user_ocean_0.append(float(line_lst[5]))
    user_ocean_0.append(float(line_lst[6]))
    # print 'user_0 is ', user_0, '\n'
    Users_OCEAN.append(user_ocean_0)
print '用户user_id + OCEAN分数特征初始化完毕...\n'
print '第1个用户，第5个用户，第9个用户分别为： \n', Users[0], ' : ', Users_OCEAN[0], '\n', Users[4], ' : ', Users_OCEAN[4], '\n'


print '开始对用户的OCEAN分数按列归一化...\n'
# 基本数据读入完毕，开始准备对用户的OCEAN分别按列归一化
# 分别采用两种方法，建议采用MinMax归一化到0-1而非使用scale归一化到标准正态分布
Users_OCEAN_array = np.array(Users_OCEAN)
print '用户OCEAN分数转化为数组...\n'
print '数据示例： \n'
print Users_OCEAN_array[:2, :], '\n'
Users_OCEAN_MinMax = MinMaxScaler().fit_transform(Users_OCEAN_array)
Users_OCEAN_scale = scale(Users_OCEAN_array)
print 'Original: ', Users_OCEAN_array[:2, :], '\n'
print 'MinMax: ', Users_OCEAN_MinMax[:2, :], '\n'
print 'scale: ', Users_OCEAN_scale[:2, :], '\n'


print '数据归一化处理完毕，开始进行初始绘图...\n'
# 在此之前需要事先读取场景二的Insiders用户，然后再其中进行标记为红色;
Insiders_Dir = os.path.dirname(sys.path[0]) + '\\' + 'r5.2-2'
Insiders_lst = os.listdir(Insiders_Dir)
print 'r5.2-2 is ', len(Insiders_lst), Insiders_lst, '\n'
Insiders = []
for insider in Insiders_lst:
    Insiders.append(insider[7:-4])
print 'Insiders is ', Insiders, '\n'
# 需要将Insiders转换成全体用户Users中的坐标序号，从而绘制成红色
Index_insiders = [] # insiders在最初全体用户列表中的索引
for user in Insiders:
    Index_insiders.append(Users.index(user))
print 'Index_insiders is ', Index_insiders, '\n'


print '开始绘图...\n'
# 为了实现在一张图上不同x坐标的点的颜色不同，因此需要区分场景二insiders的坐标与其他坐标
# insiders的横坐标为Index_insiders，纵坐标为数组Insiders_Y
Insiders_Y = []
for x in Index_insiders:
    Insiders_Y.append(Users_OCEAN_MinMax[x][0])
Index_users = range(2000)
for x in Index_insiders:
    Index_users.remove(x)
Users_Y = []
for x in Index_users:
    #Users_Y.append(Users_OCEAN_MinMax[x][4])
    Users_Y.append(Users_OCEAN_scale[x][4])

plt.xlabel('User Index')
#plt.ylabel('N in MinMax')
plt.ylabel('N in scale')
print 'Insiders_X is ', len(Index_insiders), Index_insiders, '\n'
print 'Insiders_Y is ', len(Insiders_Y), Insiders_Y, '\n'

plt.plot(Index_insiders, Insiders_Y, 'rs', Index_users, Users_Y, 'b^')
plt.show()















sys.exc_clear()
