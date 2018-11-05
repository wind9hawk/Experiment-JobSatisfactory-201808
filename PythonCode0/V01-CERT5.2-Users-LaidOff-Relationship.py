# coding:utf-8
# 本程序主要用于分析CERT5.2中全部员工的组织关系中存在关联的被解雇员工数目

import os
import sys


##
print '......<<<<<<', '解雇人员不同于离开单位的人员>>>>>>......\n\n'
## 添加一个可以自动获取场景1-2-3涉及离开单位人员的列表，从而从起初的leave列表中去掉主动离职的用户，
## 重点分析被解雇的用户，即laid off users
def Extract_Insiders():
    Insiders = []
    InsiderDir_1 = os.path.dirname(sys.path[0]) + '\\' + 'r5.2-1'
    InsiderDir_2 = os.path.dirname(sys.path[0]) + '\\' + 'r5.2-2'
    InsiderDir_3 = os.path.dirname(sys.path[0]) + '\\' + 'r5.2-3'
    # r5.2-1-ALT1465.csv
    for user in os.listdir(InsiderDir_1):
        Insiders.append(user[7:-4])
    for user in os.listdir(InsiderDir_2):
        Insiders.append(user[7:-4])
    for user in os.listdir(InsiderDir_3):
        Insiders.append(user[7:-4])
    return Insiders


print '分析CERT5.2所有用户与离职员工的关联...\n'


print '首先提取离职的员工列表...\n'
f = open('CERT5.2_Leave_Users_0.6.csv', 'r')
# Laid off Users in CERT5.2 from 2009-12 to 2011-05
# RMB1821,2010-02,Rose Maisie Blackwell,RMB1821,Rose.Maisie.Blackwell@dtaa.com,Salesman,,1 - Executive,5 - SalesAndMarketing,2 - Sales,5 - RegionalSales,Donna Erin Black
f_lst = f.readlines()
f.close()
Users_LaidOff = []
for line in f_lst:
    line_lst = line.strip('\n').strip(',').split(',')
    if len(line_lst) < 2: # 空行与标题行
        continue
    user = []
    user.append(line_lst[0])
    user.append(line_lst[1])
    user.append(line_lst[2:])
    Users_LaidOff.append(user)
print '离职员工读取完毕...\t', len(Users_LaidOff), '\n'
for i in range(5):
    print Users_LaidOff[i], '\n'
    # ['WSW1091', '2010-02',
    # ['Wing Scott Weeks', 'WSW1091', 'Wing.Scott.Weeks@dtaa.com', 'Technician', '', '1 - Executive', '5 - SalesAndMarketing', '3 - FieldService', '2 - RegionalFieldService', 'Moana Gemma Talley']]
# sys.exit()



print '提取CERT5.2全部用户列表..\n'
# 文件位置G:\GitHub\Essay-Experiments\Experiment-JobSatisfactory-201808\r5.2-2
# CERT5.2全体用户列表G:\GitHub\Essay-Experiments\Experiment-JobSatisfactory-201808\LDAP\2009-12.csv
dirPath = os.path.dirname(sys.path[0]) + '\\' + 'LDAP' + '\\' + '2009-12.csv'
f = open(dirPath, 'r')
f_lst = f.readlines()
f.close()
Users_CERT52 = []
for line in f_lst:
    # employee_name,user_id,email,role,projects,business_unit,functional_unit,department,team,supervisor
    line_lst = line.strip('\n').strip(',').split(',')
    if line_lst[1] == 'user_id':
        continue
    if len(line_lst) < 10:
        # CEO不需要分析
        continue
    # 记录user_id, 部门四元组；
    # 对于离职用户需要考虑离职时间
    # 对于未离职用户不需要考虑离职时间的影响
    user_cert52 = []
    user_cert52.append(line_lst[1])
    user_cert52.append(line_lst[5])
    user_cert52.append(line_lst[6])
    user_cert52.append(line_lst[7])
    user_cert52.append(line_lst[8])
    Users_CERT52.append(user_cert52)
print 'CERT5.2全部用户ID与LDAP提取完毕...\n'
for i in range(30):
    print Users_CERT52[i], '\n'




# 分析一个特定user与周围离职人员的关系
# 方法：
# 遍历选择一个用户
# 若该用户属于离职列表，则需要提取其离职时间作为筛选器；
# 若其不属于离职列表，则不需要考虑时间筛选器；
# 然后根据部门四元组输出五个层次的人际关系离职人员
# 写入文件

# 从238个用户中选择离职时间早于该Insider的用户
def ExtTime(time): # time = '2010-02'
    year = float(time[:4])
    month = float(time[5:])
    return year, month

# 从用户列表中过滤掉制定列表，即从A中过滤掉B
def FilterUser(A, B):
    for user in A:
        if user[0] in B:
            # ['RMB1821', '2010-02',
            # ['Rose Maisie Blackwell', 'RMB1821', 'Rose.Maisie.Blackwell@dtaa.com', 'Salesman', '', '1 - Executive', '5 - SalesAndMarketing', '2 - Sales', '5 - RegionalSales', 'Donna Erin Black']]
            A.remove(user)
    return A

print '开始分析所有用户的离职关系...\n'
print '将CERT5.2所有用户的离职关系数据写入文件...\n'
f = open('CERT5.2-Leave-Relationship_Counts.csv','w')
f_1 = open('CERT5.2-Leave-Relationship.csv', 'w')  # 存储每个用户的关系中离开的用户列表
f_2 = open('CERT5.2-LaidOff_Relationship.csv', 'w') # 存储每个用户关系中解雇的用户列表
f_3 = open('CERT5.2-LaidOff-Relationship_Counts.csv', 'w')
f.write('CERT5.2 Leave Company Relationships Counts for all Users\n')
f_1.write('CERT5.2 Leave Company Relationships Users for all Users\n')
f_2.write('CERT5.2 Laid Off Company Relationships Users for all Users\n')
f_3.write('CERT5.2 Laid Off Company Relationships Counts for all Users\n')
# [user_id, LaidOff Time, a1,a2,a3,a4,a5]记录用户的ID，离职时间以及数字化的五个层次离职人数
LaidOff_Users_Relationships = []
# ['HBW0057', '1 - Executive', '2 - ResearchAndEngineering', '1 - ProjectManagement', '']
LaidOff_Users = [] # 离职人员列表
print 'Users_LaidOff is like...', Users_LaidOff[0], '\n'
print 'Users_CERT52 is like...', Users_CERT52[0], '\n'
for usr in Users_LaidOff:
    LaidOff_Users.append(usr[0])
Insiders = Extract_Insiders()
# 建立一个文件，用于存放1999个用户的周围被解雇的用户关系

for user in Users_CERT52[:]:
    Insider_LaidOff_0 = [] # 同一团队
    Insider_LaidOff_1 = [] # 同一部门不同团队
    Insider_LaidOff_2 = [] # 同一职能部门不同具体部门
    Insider_LaidOff_3 = [] # 同一事业部不同职能部门
    Insider_LaidOff_4 = [] # 不同事业部
    Insider_Tmp = [] # 存储时间筛选后的离职人员列表
    User_LDAP = [] # 目标用户的LDAP信息
    User_LDAP.append(user[1])
    User_LDAP.append(user[2])
    User_LDAP.append(user[3])
    User_LDAP.append(user[4])
    User_Time = 'No'
    if user[0] in LaidOff_Users:
        # 说明该用户离职
        # 需要分析时间
        # 接下来要分析比较的依据就是User_Time与User_LDAP
        User_Time = Users_LaidOff[LaidOff_Users.index(user[0])][1]
        #print 'User is ', user[0], '\t', User_Time, '\t', User_LDAP, '\n'
        # 开始进行时间筛选
        i_year, i_month = ExtTime(User_Time)
        # 数字0-3表示用户与insider的组织距离，同一个团队为0，同一个部门不同团队为1，然后依次是2，3
        for usr in Users_LaidOff:
            # Insider 2010-12
            u_year, u_month = ExtTime(usr[1])
            if u_year > i_year:
                continue
            else:
                # 年份是2010或2009
                if u_year == i_year:
                    if u_month > i_month:
                        continue
                    else:
                    # 同年更早的月份，可以考虑
                        Insider_Tmp.append(usr)
                        continue
                else:
                    # u_year < i_year
                    Insider_Tmp.append(usr)
        print '初步筛选结果完成...\t', len(Insider_Tmp), '\n'
        #for i in range(len(Insider_Tmp)):
        #    print Insider_Tmp[i], '\n'
        # ['1 - Executive', '5 - SalesAndMarketing', '2 - Sales', '5 - RegionalSales'] 2010-12
    # 如果经过时间筛选，要分析比较的离职人员列表为Insider_Tmp
    # 如果没有经过时间筛选，则分析比较的离职人员列表为原始列表Users_LaidOff
    LaidOff_Users_Last = []
    if len(Insider_Tmp) > 1:
        for ele in Insider_Tmp:
            LaidOff_Users_Last.append(ele)
    else:
        for ele in Users_LaidOff:
            LaidOff_Users_Last.append(ele)
    for usr in LaidOff_Users_Last: # User表示要分析的目标用户，usr表示其关联的离职用户
        # if usr[0] == 'BYO1846':
        #if usr[0] == 'CHP1711':
        #    continue
        if user[0] == usr[0]:
            continue
        usr_ldap = []
        usr_ldap.append(usr[2][5])
        usr_ldap.append(usr[2][6])
        usr_ldap.append(usr[2][7])
        usr_ldap.append(usr[2][8])
        #print usr_ldap, '\n'
        # 开始比较两个LDAP
        if User_LDAP[0] != usr_ldap[0]: # 事业部都不一样
            Insider_LaidOff_4.append(usr)
            #print 'usr_ldap is ', usr_ldap, '\n'
        # sys.exit()
        else:
        # 同一个事业部
            if User_LDAP[1] != usr_ldap[1]: #同一个事业部，但是职能部不同
                Insider_LaidOff_3.append(usr)
            else:
            # 同一个部门
                if User_LDAP[2] != usr_ldap[2]: # 同一个事业部下的职能部下，但是具体部门不同
                    Insider_LaidOff_2.append(usr)
                else:
                # 同一个团队
                    if User_LDAP[3] != usr_ldap[3]:
                        Insider_LaidOff_1.append(usr)
                    else:
                        Insider_LaidOff_0.append(usr)
    print user[0], '分析完毕...\n'
    # print '分析完毕，开始输出不同的用户分组...\n'
    laidoff_relationship = []
    laidoff_relationship.append(user[0])
    laidoff_relationship.append(User_Time)
    laidoff_relationship.append(len(Insider_LaidOff_0))
    laidoff_relationship.append(len(Insider_LaidOff_1))
    laidoff_relationship.append(len(Insider_LaidOff_2))
    laidoff_relationship.append(len(Insider_LaidOff_3))
    laidoff_relationship.append(len(Insider_LaidOff_4))
    LaidOff_Users_Relationships.append(laidoff_relationship)
    f.write(user[0])
    f.write(',')
    f.write(User_Time)
    f.write(',')
    f.write(str(len(Insider_LaidOff_0)))
    f.write(',')
    f.write(str(len(Insider_LaidOff_1)))
    f.write(',')
    f.write(str(len(Insider_LaidOff_2)))
    f.write(',')
    f.write(str(len(Insider_LaidOff_3)))
    f.write(',')
    f.write(str(len(Insider_LaidOff_4)))
    f.write('\n')
    ##
    ##
    ## Leave用户的统计计数完毕, 开始计入Leave用户列表
    print '......<<<<<<开始记录', user[0], ' Leave用户列表>>>>>>......\n\n'
    f_1.write(user[0])
    f_1.write(',')
    f_1.write(User_Time)
    f_1.write(':\n')
    f_1.write('Insider_LaidOff_0')
    f_1.write(',')
    for ele in Insider_LaidOff_0:
        f_1.write(ele[0])
        f_1.write(',')
    f_1.write('\n')
    f_1.write('Insider_LaidOff_1')
    f_1.write(',')
    #print Insider_LaidOff_0[0], '\n'
    #print Insider_LaidOff_1[0], '\n'
    #print Insider_LaidOff_2[0], '\n'
    #print Insider_LaidOff_3[0], '\n'
    #print Insider_LaidOff_4[0], '\n'
    for ele in Insider_LaidOff_1:
        #print 'ele is ', ele, '\n'
        f_1.write(ele[0])
        f_1.write(',')
    f_1.write('\n')
    f_1.write('Insider_LaidOff_2')
    f_1.write(',')
    for ele in Insider_LaidOff_2:
        f_1.write(ele[0])
        f_1.write(',')
    f_1.write('\n')
    f_1.write('Insider_LaidOff_3')
    f_1.write(',')
    for ele in Insider_LaidOff_3:
        f_1.write(ele[0])
        f_1.write(',')
    f_1.write('\n')
    f_1.write('Insider_LaidOff_4')
    f_1.write(',')
    for ele in Insider_LaidOff_4:
        f_1.write(ele[0])
        f_1.write(',')
    f_1.write('\n')
    ##
    ##
    ##
    ## Leave用户统计完毕，开始写入LaidOff用户
    print '开始过滤Insiders用户...\n'
    Insider_LaidOff_0 = FilterUser(Insider_LaidOff_0, Insiders)
    Insider_LaidOff_1 = FilterUser(Insider_LaidOff_1, Insiders)
    Insider_LaidOff_2 = FilterUser(Insider_LaidOff_2, Insiders)
    Insider_LaidOff_3 = FilterUser(Insider_LaidOff_3, Insiders)
    Insider_LaidOff_4 = FilterUser(Insider_LaidOff_4, Insiders)
    print '......<<<<<<开始记录', user[0], ' Laid off用户列表>>>>>>......\n\n'
    f_2.write(user[0])
    f_2.write(',')
    f_2.write(User_Time)
    f_2.write(':\n')
    f_2.write('Insider_LaidOff_0')
    f_2.write(',')
    for ele in Insider_LaidOff_0:
        f_2.write(ele[0])
        f_2.write(',')
    f_2.write('\n')
    f_2.write('Insider_LaidOff_1')
    f_2.write(',')
    for ele in Insider_LaidOff_1:
        f_2.write(ele[0])
        f_2.write(',')
    f_2.write('\n')
    f_2.write('Insider_LaidOff_2')
    f_2.write(',')
    for ele in Insider_LaidOff_2:
        f_2.write(ele[0])
        f_2.write(',')
    f_2.write('\n')
    f_2.write('Insider_LaidOff_3')
    f_2.write(',')
    for ele in Insider_LaidOff_3:
        f_2.write(ele[0])
        f_2.write(',')
    f_2.write('\n')
    f_2.write('Insider_LaidOff_4')
    f_2.write(',')
    for ele in Insider_LaidOff_4:
        f_2.write(ele[0])
        f_2.write(',')
    f_2.write('\n')

    f_3.write(user[0])
    f_3.write(',')
    f_3.write(User_Time)
    f_3.write(',')
    f_3.write(str(len(Insider_LaidOff_0)))
    f_3.write(',')
    f_3.write(str(len(Insider_LaidOff_1)))
    f_3.write(',')
    f_3.write(str(len(Insider_LaidOff_2)))
    f_3.write(',')
    f_3.write(str(len(Insider_LaidOff_3)))
    f_3.write(',')
    f_3.write(str(len(Insider_LaidOff_4)))
    f_3.write('\n')

f.close()
f_1.close()
f_2.close()
f_3.close()
print '所有用户的离职关系分析完毕..\n'
for i in range(10):
    print LaidOff_Users_Relationships[i], '\n'






print '尝试将上述结果输出到'

sys.exit()





