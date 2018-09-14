# coding:utf-8
# 本程序主要用于统计分析CERT5.2的LDAP表示的组织架构中，各个组织单元的隶属关系
# Business Units: 事业部
# Functional Units： 业务部
# Department: 部门
# Team: 团队

import sys
import os

# 确定CERT5.2 LDAP存放路径
filePath = os.path.dirname(sys.path[0]) + '\\' + 'LDAP' + '\\' + '2009-12.csv'
print '要分析的文件路径为： ', filePath, '\n'


# 建立初始化职能部门列表，并逐行统计
BU = []
FU = []
DPT = []
SPS = []
PJS = []
TEAM = []
Others = [] # 用于存储长度非标准的用户LDAP信息
Lack_Flag = [0] * 6
f = open(filePath, 'r')
for line in f.readlines():
    # employee_name,user_id,email,role,projects,business_unit,functional_unit,department,team,supervisor
    line_lst = line.strip('\n').strip(',').split(',')
    if line_lst[1] == 'user_id':
        continue
    if len(line_lst) < 10:
        print 'The abnormal user LDAP is : ', line_lst, '\n'
        Others.append(line)
        Lack_Flag[5] += 1
        continue
    if line_lst[4] not in PJS:
        #if line_lst[4] == '': # 把字段为空的用户写入Others，只有所有字段都不为空的才是normal
        #    Others.append(line)
        #    continue
        PJS.append(line_lst[4])
    if line_lst[5] not in BU:
        if line_lst[5] == '':
            Others.append(line)
            Lack_Flag[1] += 1
            continue
        BU.append(line_lst[5])
    if line_lst[6] not in FU:
        if line_lst[6] == '':
            Others.append(line)
            Lack_Flag[2] += 1
            continue
        FU.append(line_lst[6])
    if line_lst[7] not in DPT:
        if line_lst[7] == '':
            Others.append(line)
            Lack_Flag[3] += 1
            continue
        DPT.append(line_lst[7])
    if line_lst[8] not in TEAM:
        if line_lst[8] == '':
            Others.append(line)
            Lack_Flag[4] += 1
            continue
        TEAM.append(line_lst[8])
    if line_lst[9] not in SPS:
        if line_lst[9] == '':
            Others.append(line)
            Lack_Flag[5] += 1
            continue
        SPS.append(line_lst[9])
    print line, ' 分析完毕...\n'
f.close()


f = open('CERT5.2-Organaztion Units List.csv', 'w')
print 'Projects is ', len(PJS), ':\n'
PJS.sort()
f.write('Project List')
f.write(':')
f.write(str(len(PJS)))
f.write('\n')
for line in PJS:
    print line, '\n'
    f.write(line)
    f.write('\n')
f.write('\n')


print 'Business Unit is ', len(BU), ':\n'
BU.sort()
f.write('Business Unit List')
f.write(':')
f.write(str(len(BU)))
f.write('\n')
for line in BU:
    print line, '\n'
    f.write(line)
    f.write('\n')
f.write('\n')

print 'Functional Unit is ', len(FU), ':\n'
FU.sort()
f.write('Functional Unit List')
f.write(':')
f.write(str(len(FU)))
f.write('\n')
for line in FU:
    print line, '\n'
    f.write(line)
    f.write('\n')
f.write('\n')

print 'Department ', len(DPT), ':\n'
DPT.sort()
f.write('Department List')
f.write(':')
f.write(str(len(DPT)))
f.write('\n')
for line in DPT:
    print line, '\n'
    f.write(line)
    f.write('\n')
f.write('\n')

print 'Team is ', len(TEAM), ':\n'
TEAM.sort()
f.write('Team List')
f.write(':')
f.write(str(len(TEAM)))
f.write('\n')
for line in TEAM:
    print line, '\n'
    f.write(line)
    f.write('\n')
f.write('\n')

print 'Supervisor is ', len(SPS), ':\n'
SPS.sort()
f.write('Supervisor List')
f.write(':')
f.write(str(len(SPS)))
f.write('\n')
i = 1
for line in SPS:
    print line, '\n'
    f.write(line)
    if i / 10 == 0:
        f.write('\n')
        i += 1
    f.write('\t')
    i += 1
f.write('\n')

print '输出Others用户..\n'
f.write('Others in abnormal format LDAP : ')
f.write(',')
f.write(str(len(Others)))
f.write('\n')
# print Others, '\n'
for line in Others:
    print line, '\n'
    f.write(line)
    f.write('\n')


f.write('Lack Flags: 0-projects, 1-BU, 2-FU, 3-Department, 4-Team, 5-Supervisor\n')
for ele in Lack_Flag:
    f.write(str(ele))
    f.write('\n')
f.close()



sys.exit()