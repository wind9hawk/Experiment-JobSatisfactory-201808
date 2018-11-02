# coding:utf-8
# 本模块则主要验证我们从人格特征和OS入手研究关系的方法；
# 结合每个用户的离职数据匹配，计算个数作为JS_Risk
# 中间要生成对应的聚类，并保存这些成员列表

import os, sys
import numpy as np
import KMeans_Module
from sklearn.preprocessing import MinMaxScaler

print '....<<<<确定数据源>>>>....\n\n'
f_Big5_LDAP_Feats = open('CERT5.2_Big5_LDAP_Part1_Feats.csv', 'r')
# f_Big5_LDAP_Feats = open('CERT5.2_Big5_LDAP_Part1_Feats.csv', 'r')
f_Big5_LDAP_Feats_lst =  f_Big5_LDAP_Feats.readlines()
f_Big5_LDAP_Feats.close()

f_Leave = open('CERT5.2-Leave-Relationship.csv', 'r')
f_Leave_lst = f_Leave.readlines()
f_Leave.close()

f_Big5_LDAP = open('CERT5.2_LDAP_ID.csv', 'r')
f_Big5_LDAP_lst = f_Big5_LDAP.readlines()
K_range = len(f_Big5_LDAP_lst)
f_Big5_LDAP.close()




print '....<<<<开始对Big5_LDAP特征进行聚类，形成关系>>>>....\n\n'
# 定义一个全局用户列表
CERT52_Users = []
# 定义一个全局Feats列表，用于与原始顺序、CERT52_Users对应
CERT52_Big5_LDAP_Feats = []
for line in f_Big5_LDAP_Feats_lst:
    # MMK1532,17.0,17.0,16.0,22.0,28.0,2.0,5.0,20.0,40.0,
    line_lst = line.strip('\n').strip(',').split(',')
    CERT52_Users.append(line_lst[0])
    tmp_0 = []
    for feat in line_lst[1:6]:
        tmp_0.append(float(feat))
    #tmp_0.remove(tmp_0[0])
    #tmp_0.remove(tmp_0[2])
    CERT52_Big5_LDAP_Feats.append(tmp_0)
# 这里默认的KMeans的最大取值范围为组织内部的所有最小团队数量
# K_range = 2
Count_Part1 = 0
Count_Part2 = 0
for line in f_Big5_LDAP_lst:
    # 1 - Executive: : : ,NJC0003,PTH0005,1,0,0,0,
    line_lst = line.strip('\n').strip(',').split(',')[0].split(':')
    if line_lst[0] == '1 - Executive':
        Count_Part1 += 1
    if line_lst[0] == '2 - Executive':
        Count_Part2 += 1
K_range = Count_Part1
print 'K均值上限为最小组织单位数量： ', K_range, '\n\n'
K_Best, SC_Value, Y_Pred = KMeans_Module.Auto_K_Choice(CERT52_Big5_LDAP_Feats, K_range)
print '....<<<<对于KMeans而言，最佳K聚类为： >>>>....\n\n'
print K_Best, '\t', SC_Value, '\n\n'



print '....<<<<将聚类结果映射到用户，并保存>>>>....\n\n'
Clusters = [[] for i in range(K_Best)]
i = 0
while i < len(CERT52_Users):
    Clusters[Y_Pred[i]].append(CERT52_Users[i])
    i += 1
f_Clusters = open('CERT5.2_Big5_LDAP_Part1_Clusters.csv-0.3', 'w')

print '..<<保存聚类结果>>..\n\n'
j = 0
while j < len(Clusters):
    f_Clusters.write('Cluster_' + str(j))
    f_Clusters.write('\n')
    for usr in Clusters[j]:
        f_Clusters.write(usr)
        f_Clusters.write(',')
    f_Clusters.write('\n')
    j += 1
print '..<<用户聚类结果保存完毕>>..\n\n'


