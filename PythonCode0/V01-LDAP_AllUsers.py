# coding:utf-8
# 在进一步落实了CERT5.2中的层级结构后，尝试建立所有事业部的员工列表，计划：
# (1)先统计形成每个事业部的部门列表，形式为[BU-X, FU-Y, DPT-Z, TEAM-P]，先列出部门列表，按顺序排列；
# (2)然后重新遍历2009-12的初始LDAP（2000用户），将其中LDAP不全的用户归为Others列表，剩余的按照第一步得到的部门列表进行分别对应构成成员列表
# (3)由于比照的部门列表，因此可以用用户的LDAP字段在部门列表中进行index匹配确定位置，然后写入到对应的列表即可；
# (4)最后依据部门列表将所有用户成员列表输出到一个CSV文件；
# (5)本程序输出两个文件，一个是CERT5.2中所有部门列表，一个是所有成员归属的列表文件；

import os
import sys


print '全面分析CERT5.2中用户的LDAP列表归属，依据2009-12建立初始2000用户归属文件...\n'
# 首先需要定位用户初始LDAP位置
# 目标位置：G:\GitHub\Essay-Experiments\Experiment-JobSatisfactory-201808\LDAP\2009-12.csv
# 当前程序位置：G:\GitHub\Essay-Experiments\Experiment-JobSatisfactory-201808\PythonCode0
# 通过当前目录的子目录的父目录定位
filePath = os.path.dirname(sys.path[0]) + '\\' + 'LDAP' + '\\' + '2009-12.csv'
f = open(filePath, 'r')
f_lines = f.readlines()
f.close()


# 然后依据读取的文件内容，提取部门列表信息，根据数据分析，构造四元数组
# [Business Units, Functional Units, Department, Team]
# employee_name,user_id,email,role,projects, /
# business_unit,functional_unit,department,team,supervisor
# 此次分析尚不考虑project信息
# 初始化一个大的部门四元组列表LDAP
# 记得排除不规则的LDAP信息（长度小于10）
LDAP = []
Others = []
for line in f_lines:
    line_lst = line.strip('\n').strip(',').split(',')
    if line_lst[1] == 'user_id':
        continue
    if len(line_lst) < 10:
        print '不规则用户LDAP是 : ',line, '\n'
        Others.append(line)
        continue
    # 排除了不规则，开始统计所有可能的四元组
    ldap = []
    # print line_lst, '\n'
    ldap.append(line_lst[5])
    ldap.append(line_lst[6])
    ldap.append(line_lst[7])
    ldap.append(line_lst[8])
    if ldap not in LDAP:
        LDAP.append(ldap)
        print 'Add into LDAP: ', ldap, '\n'
print 'LDAP 统计完毕，总共有： ',len(LDAP), ' 个部门列表\n'
LDAP.sort()
for i in range(5):
    print LDAP[i], '\n'


print '写入用户部门列表LDAP到文件CERT-LDAP.csv\n'
f = open('CERT5.2-LDAP.csv', 'w')
f.write('LDAP on BU/FU/DPT/TEAM in CERT5.2\t')
f.write(str(len(LDAP)))
f.write('\n')
for ldap in LDAP:
    f.write(str(ldap))
    f.write('\n')
print 'CERT5,2-LDAP.csv写入完毕...\n'
f.close()


# 有了部门的LDAP列表，开始重新遍历2000个用户，形成对应的成员列表
# 同时创建多个空列表不能使用[]*10，结果还是一个空列表，必须使用[[]]*100才可以
LDAP_Users = []
for i in range(len(LDAP)):
    LDAP_Users.append([])
for line in f_lines:
    line_lst = line.strip('\n').strip(',').split(',')
    if line_lst[1] == 'user_id':
        continue
    if len(line_lst) < 10:
        print '不规则用户LDAP是 : ',line, '\n'
        Others.append(line)
        continue
    # 提取当前用户的部门四元组列表
    ldap_user = []
    ldap_user.append(line_lst[5])
    ldap_user.append(line_lst[6])
    ldap_user.append(line_lst[7])
    ldap_user.append(line_lst[8])
    # 确定用户部门四元组在LDAP中的位置，并将该用户插入到对应成员列表中
    IndexUser = LDAP.index(ldap_user)
    #print line_lst, '\n'
    print 'IndexUser is ', IndexUser, '\n'
    #print LDAP_Users, '\n'
    #print 'LDAP_Users[IndexUsers] is :', LDAP_Users[IndexUser], '\n'
    if line_lst[1] not in LDAP_Users[IndexUser]:
        LDAP_Users[IndexUser].append(line_lst[1])
        print line_lst[1], '添加到LDAP_Users中...\n'
        continue
for users in LDAP_Users:
    users.sort()
for i in range(20):
    print LDAP_Users[i], '\n'


# 开始将上述成员列表写入到一个新文件CERT5.2-LDAPUsers.csv
f = open('CERT5.2-LDAPUsers.csv', 'w')
f.write('CERT5.2 LDAP Users\n')
f.write(str(len(LDAP_Users)))
f.write('\n')
i = 0
while i < len(LDAP_Users):
    f.write(str(LDAP[i]).replace(',', ':'))
    f.write(',')
    for user in LDAP_Users[i]:
        f.write(user)
        f.write(',')
    f.write('\n')
    i += 1
print 'CERT5.2-LDAPUsers.csv写入完毕...\n'
f.close()


sys.exit()


