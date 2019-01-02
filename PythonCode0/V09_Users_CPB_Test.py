# coding:utf-8
# 本模块简单地统计、分析CERT5.2中2000个用户的CPB倾向；
# 并分别依据CPB-I、CPB-O的高低顺序，输出三个Insiders类别中用户的排序位置以表明整体的倾向性；

# 由于程序结构简单，为了节省时间，采用面向过程实现

import os, sys

# 计算CPB的函数
def Cal_CPB(user_ocean):
    # 给定一个上述格式的6-format: user_id, o, c, e, a, n
    # 计算该用户的CPB-I与CPB-O分数
    # 这里使用的是CERT文献中的三元显著关联特征：
    # CPB-I = -0.34 * A_Score + 0.36 * A_Score * (-0.40)
    # CPB-O = -0.52 * C_Score + 0.36 * A_Score * (-0.41)
    CPB_I = user_ocean[4] * (-0.34) + user_ocean[4] * 0.36 * (-0.40)
    CPB_O = user_ocean[2] * (-0.52) + user_ocean[4] * 0.36 * (-0.41)
    return CPB_I, CPB_O
# 提取Insiders的函数
def Extract_Insiders():
    dst_dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.9'
    # Insiders-1_Leave.csv
    # data like: KEW0198,2010-07-29,
    insiders_1_lst = []
    insiders_2_lst = []
    insiders_3_lst = []
    for file in os.listdir(dst_dir):
        if 'Insiders-1_Leave' in file:
            f_1 = open(dst_dir + '\\' + file, 'r')
            for line_1 in f_1.readlines():
                line_lst = line_1.strip('\n').strip(',').split(',')
                insiders_1_lst.append(line_lst[0])
            f_1.close()
            print 'Insiders_1名单提取完毕..\n'
        if 'Insiders-2_Leave' in file:
            f_2 = open(dst_dir + '\\' + file, 'r')
            for line_2 in f_2.readlines():
                line_lst = line_2.strip('\n').strip(',').split(',')
                insiders_2_lst.append(line_lst[0])
            f_2.close()
            print 'Insiders_1名单提取完毕..\n'
        if 'Insiders-3_Leave' in file:
            f_3 = open(dst_dir + '\\' + file, 'r')
            for line_3 in f_3.readlines():
                line_lst = line_3.strip('\n').strip(',').split(',')
                insiders_3_lst.append(line_lst[0])
            f_3.close()
            print 'Insiders_1名单提取完毕..\n'
    return insiders_1_lst, insiders_2_lst, insiders_3_lst

import os, sys

print '初始化数据..\n'
Dst_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.9'
# psychometric-5.2.csv
f_psy = open(Dst_Dir + '\\' + 'psychometric-5.2.csv', 'r')
# data like:
# employee_name,user_id,O,C,E,A,N
# Maisie Maggy Kline,MMK1532,17,17,16,22,28
CERT52_Users_OCEAN = []
for line_psy in f_psy.readlines():
    line_lst = line_psy.strip('\n').strip(',').split(',')
    if line_lst[1] == 'user_id':
        continue
    tmp_psy = []
    tmp_psy.append(line_lst[1])
    for ele in line_lst[2:]:
        tmp_psy.append(float(ele))
    CERT52_Users_OCEAN.append(tmp_psy)
print 'CERT5.2 OCEAN分数提取完毕..\n'
Insiders_1, Insiders_2, Insiders_3 = Extract_Insiders()
print CERT52_Users_OCEAN[0], '\n', Insiders_1[2], '\n', Insiders_2[3], '\n', Insiders_3[4], '\n'

print '开始计算CPB分数..\n'
for user_ocean in CERT52_Users_OCEAN:
    cpb_i, cpb_o = Cal_CPB(user_ocean)
    user_ocean.append(cpb_i)
    user_ocean.append(cpb_o)
# 排序
CERT52_Users_OCEAN_CPBI = sorted(CERT52_Users_OCEAN, key=lambda t:t[6], reverse=True)
CERT52_Users_OCEAN_CPBO = sorted(CERT52_Users_OCEAN, key=lambda t:t[-1], reverse=True)

print 'Insiders_1 is :\n'
for user in Insiders_1:
    for line in CERT52_Users_OCEAN_CPBO:
        if line[0] == user:
            print line[0], user, line[-2:], CERT52_Users_OCEAN_CPBO.index(line)

print 'Insiders_2 is :\n'
for user in Insiders_2:
    for line in CERT52_Users_OCEAN_CPBO:
        if line[0] == user:
            print line[0], user, line[-2:], CERT52_Users_OCEAN_CPBO.index(line)

print 'Insiders_3 is :\n'
for user in Insiders_3:
    for line in CERT52_Users_OCEAN_CPBO:
        if line[0] == user:
            print line[0], user, line[-2:], CERT52_Users_OCEAN_CPBO.index(line)


