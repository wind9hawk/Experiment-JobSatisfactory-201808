# coding:utf-8
# 实验0.1与0.2发现了从邮件通讯刻画用户relationship存在的问题，重新回到论文构造数据说明的逻辑关系图，确定从OCEAN与组织架构（OS）两方面
# 刻画用户的人际关系；
# Step-1. 对CERT5.2中LDAP的组织层级结构进行标号：
# 1.1 按层顺序统计标记；
# 1.2 默认数字0表示空，即该层次模块无标记
# 1.3 生成所有组织模块独特的四维度标识，保存文件到CERT5.2_LDAP_ID.csv
# 1.4 结合用户的OCEAN数据与LDAP信息，生成其独特的人际关系特征数据CERT5.2_Big5_LDAP_Feats
# Step-2. 聚类发现relationship
# 对于得到的Big5_LDAP_Feats文件进行聚类，发现聚类，存储到相应的聚类文件中CER%5.2_Big5_LDAP_Clusters.csv

import os, sys
import numpy as np

print '....<<<<本模块主要根据CERT5.2用户的Big5分数与组织结构数据生成其独特的7维度特征>>>>....'
# Big5特征需要单独考虑N-A-C与同时考虑OCEAN
# OS结构数据（Organizational Structure）需要分别考虑全体2000个用户以及单独分事业部的用户特征
print '..<<首先需要确定基本的数据源，建立在原有数据分析基础上>>..\n\n'
# OCEAN(Big5)分数
f_big5 = open(os.path.dirname(sys.path[0]) + '\\' + 'psychometric-5.2.csv', 'r')
f_big5_lst = f_big5.readlines()
f_big5.close()
# Big5数据的基本数据格式
# employee_name,user_id,O,C,E,A,N
# Maisie Maggy Kline,MMK1532,17,17,16,22,28
# 组织结构数据LDAP
f_LDAP = open(r'CERT5.2-LDAPUsers.csv', 'r')
f_LDAP_lst = f_LDAP.readlines()
f_LDAP.close()
# 注意！！
# LDAP数据格式并不规范第一个组织位置字段为包含','的列表，后期需要处理为‘：’
# 原始LDAP数据的格式为：
# CERT5.2 LDAP Users
# 143
# ['', '', '', ''],ETW0002,
# ['1 - Executive', '', '', ''],NJC0003,PTH0005,
# ['1 - Executive', '1 - Adminstration', '', ''],BBB0012,CWC0006,
print '..<<将LDAP数据处理成规范数据格式>>..\n'
print '..<<OS序列, 成员1，成员2，...成员N>>..\n\n'
# 采用拼接的方法，重新处理LDAP序列
# 先定位到]位置，将其中的','替换为':'，然后再与后一部分分片拼接
# 定义一个全新的规范过的LDAP列表
CERT52_LDAP_NOM = []
for line in f_LDAP_lst[:]:
    line_lst = line.strip('\n').strip(',').split(',')
    if len(line_lst) < 2:
        continue
    index_0 = line.index(']')
    # 定义临时储存[]部分的分片
    ldap_fragment_0 = line[:index_0 + 1]
    # 定义临时存储[]之后部分的分片
    ldap_fragment_1 = line[index_0 + 1:]
    # 分别以‘,’分割，重新组成列表
    ldap_lst_0 = ldap_fragment_0.strip('[').strip(']').replace(',', ':').replace('\'', '')
    ldap_lst_1 = ldap_fragment_1.strip('\n').strip(',')
    # 定义本次处理要返回的单行LDAP数据
    ldap_tmp = []
    ldap_tmp.append(ldap_lst_0.strip('"'))
    for usr in ldap_lst_1.split(','):
        ldap_tmp.append(usr)
    print '要返回的规范化ldap数据为： ', ldap_tmp, '\n'
    # 注意！
    # 打印输出时会自动添加''/""作为字符串标识，其实变量中时不存在的
    # 同样，当向文件中写入时，默认带着变量类型，如果单项写入，不存在多余的'[]'/'''问题，而如果整体写入一个列表或者字符串，则会带上类型字符
    CERT52_LDAP_NOM.append(ldap_tmp)
print '..<<LDAP规范化完毕>>..\n\n'



print '....<<<<接下来开始为LDAP添加标号>>>>....\n\n'
# 为了能够以数字标识顺序，先初始化存储四个层次组织名称的列表
OS_Name_lst = [[] for i in range(4)]
# 定义一个存储LDAP标号的列表
CERT52_LDAP_ID = []
for line in CERT52_LDAP_NOM:
    ldap_part = line[0].split(':')
    ldap_ID = []
    i = 0
    while i < 4:
        if ldap_part[i] == ' ' or ldap_part[i] == '':
            ldap_ID.append(0)
            i += 1
            continue
        else:
            if ldap_part[i] not in OS_Name_lst[i]:
                OS_Name_lst[i].append(ldap_part[i])
                ldap_ID.append(OS_Name_lst[i].index(ldap_part[i]) + 1)
                i += 1
                continue
            else:
                ldap_ID.append(OS_Name_lst[i].index(ldap_part[i]) + 1)
                i += 1
                continue
    tmp_0 = []
    tmp_0.append(line)
    tmp_0.append(ldap_ID)
    CERT52_LDAP_ID.append(tmp_0)
print '....<<<<CERT5.2 LDAP数据结构化标记ID完成>>>>....\n\n'
for i in range(len(CERT52_LDAP_ID)):
    print i, CERT52_LDAP_ID[i][0], ' : \t', CERT52_LDAP_ID[i][1], '\n'
    i += 1

print '..<<将规范化的LDAP标记写入文件>>..\n\n'
f_0 = open(r'CERT5.2_LDAP_ID.csv', 'w')
for i in range(len(CERT52_LDAP_ID)):
    #print i, CERT52_LDAP_ID[i][0], ' : \t', CERT52_LDAP_ID[i][1], '\n'
    for ele in CERT52_LDAP_ID[i][0]:
        # 原始LDAP数据
        f_0.write(ele)
        f_0.write(',')
    for ele in CERT52_LDAP_ID[i][1]:
        f_0.write(str(ele))
        f_0.write(',')
    f_0.write('\n')
    i += 1



print '....<<<<得到了LDAP规范化标记，接下来结合用户LDAP数据和心理数据生成其最终的关系特征>>>>....\n\n'
# 组织结构数据LDAP
# 首先定义了三个用于保存用户的Big5-LDAP特征的文件，分别保存全体、第一事业部、第二事业部的数据
f_1 = open('CERT5.2_Big5_LDAP_All_Feats.csv', 'w')
f_2 = open('CERT5.2_Big5_LDAP_Part1_Feats.csv', 'w')
f_3 = open('CERT5.2_Big5_LDAP_Part2_Feats.csv', 'w')
# 定义对应于上述文件的数据列表
CERT52_All_Feats = []
CERT52_Part1_Feats = []
CERT52_Part2_Feats = []

for line in f_big5_lst:
    # UserID, O, C, E, A, N, ID1, ID2, ID3, ID4
    # employee_name,user_id,O,C,E,A,N
    # Maisie Maggy Kline,MMK1532,17,17,16,22,28
    # 首先输入OCEAN心理特征
    tmp_1 = []
    line_lst = line.strip('\n').strip(',').split(',')
    if line_lst[1] == 'user_id':
        continue
    #print 'line_lst is ', line_lst, '\n'
    tmp_1.append(line_lst[1])
    tmp_1.append(float(line_lst[2]))
    tmp_1.append(float(line_lst[3]))
    tmp_1.append(float(line_lst[4]))
    tmp_1.append(float(line_lst[5]))
    tmp_1.append(float(line_lst[6]))
    # 接着需要输入LDAP特征
    # 首先需要从LDAP_ID数据中定位
    j = 0
    while j < len(CERT52_LDAP_ID):
        # 1 - Executive: 1 - Adminstration: : ,BBB0012,CWC0006,1,1,0,0,
        # CERT52_LDAP_ID[j][0] =
        # ['1 - Executive: 1 - Adminstration: 2 - EmployeeRelations: ', 'KMM0014', 'NMM0026', 'TIR0025', 'UAR0024']
        if line_lst[1] in CERT52_LDAP_ID[j][0]:
            index_1 = j
            break
        else:
            j += 1
            continue
    for ele in CERT52_LDAP_ID[index_1][1]:
        tmp_1.append(float(ele))
    # 将得到的feats数据写入到对应的用户列表
    CERT52_All_Feats.append(tmp_1)
    if '1 - Executive' in CERT52_LDAP_ID[index_1][0][0]:
        # 这是第一事业部
        CERT52_Part1_Feats.append(tmp_1)
    if '2 - Executive' in CERT52_LDAP_ID[index_1][0][0]:
        CERT52_Part2_Feats.append(tmp_1)
print '....<<<<CERT5.2的用户的OCEAN与LDAP数据关联特征提取完毕，准备写入文件>>>>....\n\n'



print '....<<<<将用户的OCEAN数据与LDAP特征写入对应文件>>>>....\n\n'
for line in CERT52_All_Feats:
    for ele in line:
        f_1.write(str(ele))
        f_1.write(',')
    f_1.write('\n')

for line in CERT52_Part1_Feats:
    for ele in line:
        f_2.write(str(ele))
        f_2.write(',')
    f_2.write('\n')

for line in CERT52_Part2_Feats:
    for ele in line:
        f_3.write(str(ele))
        f_3.write(',')
    f_3.write('\n')

f_1.close()
f_2.close()
f_3.close()

print '....<<<<用户OCEAN与LDAP特征数据写入完毕>>>>....\n\n'








sys.exit()