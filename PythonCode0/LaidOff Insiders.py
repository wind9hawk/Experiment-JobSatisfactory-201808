# coding:utf-8
# 本程序主要用于分析CERT5.2中LDAP文件集合中体现的用户中途离职的情况
# 初步结果应包括：
# 1. 2009-12至2011-05期间所有离开单位的员工
# 2. 2009-12至2011-05期间所有加入单位的员工
# 3. 所有离职与入职员工的LDAP信息
# 4. 跳槽场景中30个用户的LDAP信息
# 5. 30个跳槽用户所属组织团队、部门、职能部门以及事业部门中的离职、入职人员情况统计

import os
import sys

print '首先分析CERT5.2数据中所有离职与入职的员工信息...\t...[laid off/in month, user ldap]...\n'
# 首先比较发现变化的用户user_id
# 然后记录该用户信息到Users_Laid/In中
# 采用一个时间计数器来定位用户变化的月份
Users_CERT = [] # 原始用户列表，以user_id形式存储
Users_LDAP = [] # 原始用户的ldap信息
Users_LaidOff = []
Users_EngageIn = []
MonthCnt = 1 #从2010-01开始
MonthList = []
fileMonth = []
# 目标目录G:\GitHub\Essay-Experiments\Experiment-JobSatisfactory-201808\LDAP
dirPath = os.path.dirname(sys.path[0]) + '\\' + 'LDAP'
for file in os.listdir(dirPath):
    # 2009-12.csv
    MonthList.append(file[:7])
    file = dirPath + '\\' + file
    fileMonth.append(file)
print '所有需要分析的月份有： ', MonthList, '\n'
print '所有需要分析的LDAP文件有： ', fileMonth, '\n'
##
##
##程序块之间间断3行
# 以第一个月份的用户作为初始用户列表，从中提取全部用户user_id，然后开始比较之后每个用户的加入与离开
f = open(fileMonth[0], 'r')
f_lst = f.readlines()
f.close()
f_w = open('CERT5.2-LaidOff-Users.csv', 'w') # 定义一个记录离职员工的文件
f_w.write('Laid off Users in CERT5.2 from 2009-12 to 2011-05\n')
for usr in f_lst:
    line = usr.strip('\n').strip(',').split(',')
    if line[1] == 'user_id':
        continue
    Users_CERT.append(line[1])
    Users_LDAP.append(usr)
print 'CERT users初始化完毕...\t', Users_CERT[:10], '\n'
#
#
# 开始循环比较后续的LDAP文件，筛选出其中的变化用户
while MonthCnt <= len(MonthList) - 1:
    f = open(fileMonth[MonthCnt], 'r')
    f_lst = f.readlines()
    f.close()
    Users_Month = []
    for line in f_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        if line_lst[1] == 'user_id':
            continue
        Users_Month.append(line_lst[1])
    UsersCnt0 = len(Users_LaidOff)
    # 开始判断离职的用户
    for user in Users_CERT:
        if user not in Users_Month:
            # 该用户离职
            laid_ldap = []
            laid_ldap.append(user)
            laid_ldap.append(MonthList[MonthCnt])
            laid_ldap.append(Users_LDAP[Users_CERT.index(user)])
            Users_LaidOff.append(laid_ldap)
            Users_LDAP.remove(Users_LDAP[Users_CERT.index(user)])
            Users_CERT.remove(user) # 从当前用户集合中删除该用户
            print user, ' 离职 ', '月份 ', MonthList[MonthCnt], ':', laid_ldap, '\n'
    # 判断新入职用户
    for user in Users_Month:
        if user not in Users_CERT:
            Engage_ladp = []
            Engage_ladp.append(user)
            Engage_ladp.append(MonthList[MonthCnt])
            Engage_ladp.append(f_lst[Users_Month.index(user)])
            Users_EngageIn.append(Engage_ladp)
            Users_CERT.append(user)
            Users_LDAP.append(f_lst[Users_Month.index(user)])
    print MonthList[MonthCnt], '分析完毕...\n'
    print MonthList[MonthCnt], '离职用户为： \t', len(Users_LaidOff) - UsersCnt0, '\n'
    MonthCnt += 1


for usr in Users_LaidOff:
    print usr[0], '离职月份： ', usr[1], 'LDAP信息： ', usr[2], '\n'
    f_w.write(usr[0])
    f_w.write(',')
    f_w.write(usr[1])
    f_w.write(',')
    f_w.write(usr[2])
    f_w.write('\n')
print '总共离职用户为： ', len(Users_LaidOff), '\n'
print '入职用户为： ', Users_EngageIn, '\n'






sys.exit()




