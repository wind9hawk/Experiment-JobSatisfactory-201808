# coding:utf-8
# 本程序主要用于分析跳槽员工与其关联被解雇员工的关联

import os
import sys

print '分析跳槽Insiders与离职员工的关联...\n'


print '首先提取离职的员工列表...\n'
f = open('CERT5.2-LaidOff-Users.csv', 'r')
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
# sys.exit()



print '提取场景二的跳槽Insiders列表..\n'
# 文件位置G:\GitHub\Essay-Experiments\Experiment-JobSatisfactory-201808\r5.2-2
dirPath = os.path.dirname(sys.path[0]) + '\\' + 'r5.2-2'
Insiders = []
for name in os.listdir(dirPath):
    # r5.2-2-ZIE0741.csv
    Insiders.append(name[7:-4])
print '攻击者提取完毕...\n'
for i in range(30):
    print Insiders[i], '\n'



print '验证30个跳槽Insiders是否全在离职员工列表中...\n'
YesFlag = True
Users_LaidOff_0 = []
for line in Users_LaidOff:
    Users_LaidOff_0.append(line[0])
for usr in Insiders:
    if usr not in Users_LaidOff_0:
        YesFlag = False
        print usr, '\n'
print '30个跳槽Insiders是否全在离职员工列表中？ \n', YesFlag, '\n'




# 分析一个特定Insider与周围离职人员的关系
# 方法：确定一个特定的Insider，然后提取其表示部门的四元组和离职时间，然后从238个用户中选出部门最为接近以及离职时间在其之前的用户
# 需要定义一个时间函数
# 先试着将BYO1846 作为案例分析
# print Users_LaidOff[Users_LaidOff_0.index('BYO1846')], '\n'
# TargetInsider = Users_LaidOff[Users_LaidOff_0.index('BYO1846')]
TargetInsider = Users_LaidOff[Users_LaidOff_0.index('CHP1711')]
InsiderLDAP = []
print TargetInsider,'\n'
print TargetInsider[2], '\n'
InsiderLDAP.append(TargetInsider[2][5])
InsiderLDAP.append(TargetInsider[2][6])
InsiderLDAP.append(TargetInsider[2][7])
InsiderLDAP.append(TargetInsider[2][8])
InsiderTime = TargetInsider[1]
print '目标Insider信息提取完毕..\n'
print InsiderLDAP, InsiderTime, '\n'


# 从238个用户中选择离职时间早于该Insider的用户
def ExtTime(time): # time = '2010-02'
    year = float(time[:4])
    month = float(time[5:])
    return year, month

i_year, i_month = ExtTime(InsiderTime)
print 'Insider 离职时间为: ', i_year, i_month, '\n'
# 数字0-3表示用户与insider的组织距离，同一个团队为0，同一个部门不同团队为1，然后依次是2，3
Insider_Tmp = []
Insider_LaidOff_0 = []
Insider_LaidOff_1 = []
Insider_LaidOff_2 = []
Insider_LaidOff_3 = []
Insider_LaidOff_4 = []
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
for i in range(len(Insider_Tmp)):
    print Insider_Tmp[i], '\n'
# 此时得到163个用户，需要进一步依据部门进行排除
# ['1 - Executive', '5 - SalesAndMarketing', '2 - Sales', '5 - RegionalSales'] 2010-12
for usr in Insider_Tmp:
    # if usr[0] == 'BYO1846':
    if usr[0] == 'CHP1711':
        continue
    usr_ldap = []
    usr_ldap.append(usr[2][5])
    usr_ldap.append(usr[2][6])
    usr_ldap.append(usr[2][7])
    usr_ldap.append(usr[2][8])
    #print usr_ldap, '\n'
    # 开始比较两个LDAP
    if InsiderLDAP[0] != usr_ldap[0]: # 事业部都不一样
        Insider_LaidOff_4.append(usr)
        print 'usr_ldap is ', usr_ldap, '\n'
        # sys.exit()
    else:
        # 同一个事业部
        if InsiderLDAP[1] != usr_ldap[1]: #同一个事业部，但是职能部不同
            Insider_LaidOff_3.append(usr)
        else:
            # 同一个部门
            if InsiderLDAP[2] != usr_ldap[2]: # 同一个事业部下的职能部下，但是具体部门不同
                Insider_LaidOff_2.append(usr)
            else:
                # 同一个团队
                if InsiderLDAP[3] != usr_ldap[3]:
                    Insider_LaidOff_1.append(usr)
                else:
                    Insider_LaidOff_0.append(usr)
print '分析完毕，开始输出不同的用户分组...\n'
print '不同事业部的离职员工为: ', len(Insider_LaidOff_4), '\n'
for i in range(len(Insider_LaidOff_4)):
    print Insider_LaidOff_4[i], '\n'
print '不同事业部离职员工分析完毕...\n'

print '同一事业部下不同职能部的离职员工为: ', len(Insider_LaidOff_3), '\n'
for i in range(len(Insider_LaidOff_3)):
    print Insider_LaidOff_3[i], '\n'
print '同一事业部下不同职能部的离职员工分析完毕...\n'

print '相同职能部下不同部门的离职员工为: ', len(Insider_LaidOff_2), '\n'
for i in range(len(Insider_LaidOff_2)):
    print Insider_LaidOff_2[i], '\n'
print '相同职能部下不同部门的离职员工分析完毕...\n'

print '相同部门下不同个团队的离职员工为: ', len(Insider_LaidOff_1), '\n'
for i in range(len(Insider_LaidOff_1)):
    print Insider_LaidOff_1[i], '\n'
print '相同部门下不同个团队的离职员工分析完毕...\n'

print '同一团队的离职员工为: ', len(Insider_LaidOff_0), '\n'
for i in range(len(Insider_LaidOff_0)):
    print Insider_LaidOff_0[i], '\n'
print '同一团队离职员工分析完毕...\n'



print '尝试将上述结果输出到'







