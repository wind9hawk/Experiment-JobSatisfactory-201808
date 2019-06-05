# coding:utf-8
# 本模块主要工作是选取CPB_FeatsLM均值特征与三类攻击场景各一个用户CPB特征
# 组成6元分组CPB特征，然后分别绘图

# 取得MinMax后的ATF特征
# 取得三类攻击场景用户名单
# 输出三个Insiders即可

# 不考虑通用性，先完成本次工作
import os,sys
import sklearn.preprocessing as skp
import copy
import math

print '开始..\n\n'
# 获取数据
Dst_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.9' + '\\' + 'KMeans_OCSVM_Insiders_Predictor'
# CERT5.2_Leave_Static_CPB_ATF-02.csv
ATF_lst = []
ATF_Users = []
f_ATF = open(Dst_Dir + '\\' + 'CERT5.2_Leave_Static_CPB_ATF-02.csv', 'r')
for line in f_ATF.readlines():
    line_lst = line.strip('\n').strip(',').split(',')
    if line_lst[0] == 'user_id':
        continue
    else:
        tmp = []
        ATF_Users.append(line_lst[0])
        for ele in line_lst[1:]:
            tmp.append(float(ele))
        ATF_lst.append(tmp)
print len(ATF_Users), len(ATF_lst), ATF_lst[0], '\n'
f_ATF.close()

Insiders_1 = []
Insiders_2 = []
Insiders_3 = []
for file in os.listdir(sys.path[0] + '\\' + 'JS-Risks_Analyze-0.9'):
    # Insiders-1_Leave.csv
    if 'Insiders-1' in file:
        f_1 = open(sys.path[0] + '\\' + 'JS-Risks_Analyze-0.9' + '\\' + file, 'r')
        for line in f_1.readlines():
            line_lst = line.strip('\n').strip(',').split(',')
            if line_lst[0] not in Insiders_1:
                Insiders_1.append(line_lst[0])
    if 'Insiders-2' in file:
        f_2 = open(sys.path[0] + '\\' + 'JS-Risks_Analyze-0.9' + '\\' + file, 'r')
        for line in f_2.readlines():
            line_lst = line.strip('\n').strip(',').split(',')
            if line_lst[0] not in Insiders_2:
                Insiders_2.append(line_lst[0])
    if 'Insiders-3' in file:
        f_3 = open(sys.path[0] + '\\' + 'JS-Risks_Analyze-0.9' + '\\' + file, 'r')
        for line in f_3.readlines():
            line_lst = line.strip('\n').strip(',').split(',')
            if line_lst[0] not in Insiders_3:
                Insiders_3.append(line_lst[0])
    else:
        continue
print len(Insiders_1), len(Insiders_2), len(Insiders_3), '\n'

Normal_Mean = [0.48910005, 0.51125164, 0.50229733, 0.17806591, 0.20199699, 0.5781269,
 0.46776428, 0.55608838, 0.59100597, 0.25762216, 0.18817143, 0.53839514,
 0.44814785, 0.27897101, 0.49302197, 0.19853182, 0.10848115, 0.51437663,
 0.13276488, 0.12528375, 0.23784272, 0.24771765, 0.11956776, 0.142736,
 0.25928251, 0.27493893, 0.31256463, 0.22452337, 0.38475448, 0.0574136]

ATF_lst = skp.MinMaxScaler().fit_transform(ATF_lst)

insider1_cpb = ATF_lst[ATF_Users.index(Insiders_1[0])]
insider2_cpb = ATF_lst[ATF_Users.index(Insiders_2[1])]
insider3_cpb = ATF_lst[ATF_Users.index(Insiders_3[2])]
print insider1_cpb, '\n', insider2_cpb, '\n', insider3_cpb, '\n'

def Cal_Group_CPB(line):
    tmp = []
    tmp.extend(line[:3])
    tmp.append(sum(line[3:13]))
    tmp.append(sum(line[13:26]))
    tmp.append(sum(line[26:28]))
    return tmp

Normal_Mean_Group = Cal_Group_CPB(Normal_Mean)
Insiders_1_Group = Cal_Group_CPB(insider1_cpb)
Insiders_2_Group = Cal_Group_CPB(insider2_cpb)
Insiders_3_Group = Cal_Group_CPB(insider3_cpb)

print Normal_Mean_Group, '\n'
print Insiders_1_Group, '\n'
print Insiders_2_Group, '\n'
print Insiders_3_Group, '\n'
