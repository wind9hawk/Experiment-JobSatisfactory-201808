# coding:utf-8
# 本模块为实验系列0.4的前置分析与处理
import os,sys
import numpy as np
import sklearn.preprocessing as skp
import sklearn.metrics as skm
import sklearn.decomposition as skd


# 可能用到的数据源
Single_Email_Dir = sys.path[0] + '\\' + 'CERT5.2_EmailContactFeats-0.2'
Multiple_Email_Dir = sys.path[0] + '\\' + 'CERT5.2_JS-Risk_Analyze-0.4'
CERT52_LDAP_Dir = os.path.dirname(sys.path[0]) + '\\' + 'LDAP'


# 分析模块一启动开关
Flag_0 = True
if Flag_0:
    print '....<<<<CERT5.2 Insiders_2 邮件联系人的OS分布>>>>....\n\n'
    Target_User = 'ACH1831'

    # 获取LDAP信息，其中包含OS数据
    f_LDAP = open(CERT52_LDAP_Dir + '\\' + '2009-12.csv', 'r')
    f_LDAP_lst = f_LDAP.readlines()
    f_LDAP.close()

    # 获取目标用户的联系人列表
    # 1. 单向通信的列表
    Email_Contacts_S = []
    Email_Contacts_S_Send = []
    for file in os.listdir(Single_Email_Dir):
        if Target_User in file and 'feat' in file:
            f_0 = open(Single_Email_Dir + '\\' + file, 'r')
            # JLF1315,-0.130434782609,10.0,222931.8,0.5,13.0,390778.153846,0.538461538462,
            for line in f_0.readlines():
                line_lst = line.strip('\n').strip(',').split(',')
                # -1表示单纯的接收邮件，如果仅考虑存在用户发送的邮件
                if line_lst[1] != '-1.0':
                    Email_Contacts_S.append(line_lst[0])
                    Email_Contacts_S_Send.append(float(line_lst[2]))
            f_0.close()

    # 2. 多向通信列表
    Email_Contacts_M = []
    for file in os.listdir(Multiple_Email_Dir):
        if Target_User in file and 'feat' in file:
            f_0 = open(Single_Email_Dir + '\\' + file, 'r')
            # JLF1315,-0.130434782609,10.0,222931.8,0.5,13.0,390778.153846,0.538461538462,
            for line in f_0.readlines():
                line_lst = line.strip('\n').strip(',').split(',')
                Email_Contacts_M.append(line_lst[0])
            f_0.close()

    # 输出匹配的OS信息
    OS_Contacts_S = []
    Cnt_OS_S = []
    Cnt_OS_S_Send = []
    OS_Contacts_M = []
    Cnt_OS_M = []
    Abnormal_lst = []
    Target_User_LDAP = []
    # employee_name,user_id,email,role,projects,business_unit,functional_unit,department,team,supervisor
    for usr in Email_Contacts_S:
        i = 0
        while i < len(f_LDAP_lst):
            line_lst = f_LDAP_lst[i].strip('\n').strip(',').split(',')
            if len(line_lst) < 10:
                Abnormal_lst.append(f_LDAP_lst[i])
                i += 1
                continue
            if Target_User == line_lst[1]:
                if len(Target_User_LDAP) == 0:
                    # 保存目标用户的LDAP
                    for ele in line_lst[5:9]:
                        Target_User_LDAP.append(ele)
            if usr != line_lst[1]:
                # 未匹配到用户LDAP记录
                i += 1
                continue
            else:
                OS_0 = line_lst[5:9]
                if OS_0 not in OS_Contacts_S:
                    OS_Contacts_S.append(OS_0)
                    Cnt_OS_S.append(1)
                    Cnt_OS_S_Send.append(Email_Contacts_S_Send[Email_Contacts_S.index(line_lst[1])])
                    break
                else:
                    Cnt_OS_S[OS_Contacts_S.index(OS_0)] += 1
                    Cnt_OS_S_Send[OS_Contacts_S.index(OS_0)] += Email_Contacts_S_Send[Email_Contacts_S.index(line_lst[1])]
                    break
    print Target_User, '单向通信分析完毕...\n'
    OS_Contacts_S_Count = []
    i = 0
    while i < len(OS_Contacts_S):
        tmp_0 = []
        for ele in OS_Contacts_S[i]:
            tmp_0.append(ele)
        tmp_0.append(Cnt_OS_S[i])
        tmp_0.append(Cnt_OS_S_Send[i])
        OS_Contacts_S_Count.append(tmp_0)
        print OS_Contacts_S_Count, '\n'
        # sys.exit()
        i += 1
    for i in range(len(Cnt_OS_S)):
        print i, OS_Contacts_S[i], Cnt_OS_S[i], '\n'

    # 将上述结果写入到文件
    f_1 = open('0.4_' + Target_User + '_Send_OS_Statistic.csv', 'w')
    f_1.write(Target_User)
    f_1.write(',')
    for ele in Target_User_LDAP:
        f_1.write(ele)
        f_1.write(',')
    f_1.write('\n')
    print sorted(OS_Contacts_S_Count, key=lambda t:t[-1]), '\n'

    i = 0
    while i < len(OS_Contacts_S_Count):
        for ele in sorted(OS_Contacts_S_Count, key=lambda t:t[-1],reverse=True)[i]:
            f_1.write(str(ele))
            f_1.write(',')
        f_1.write('\n')
        i += 1
    f_1.close()




