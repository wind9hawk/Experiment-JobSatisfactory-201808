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
