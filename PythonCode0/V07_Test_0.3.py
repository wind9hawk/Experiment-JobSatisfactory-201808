# coding:utf-8
import os,sys
import numpy as np
import sklearn.preprocessing as skp
import copy
import shutil
import math


# 实验二：统计下CERT5.2中有多少用户没有与离职员工有过通信
Flag_0 = True
if Flag_0:
    Dst_Dir = r'G:\GitHub\Essay-Experiments\Experiment-JobSatisfactory-201808\PythonCode0\JS-Risks_Analyze-0.7'
    f_LC = open(Dst_Dir + '\\' + 'CERT5.2_Users_LeaveContacts_EmailFeats.csv')
    LC_lst = f_LC.readlines()
    f_LC.close()

    print '开始处理统计...\n'
    No_LC_lst = []
    for line in LC_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        # print line_lst, '\n'
        # <<MMK1532_start>>:2011-06-30
        # 2010-02:
        # WMH1300,1.0,1.0,[2010-01-25],38275.0,0.0,0,[],0,0,1,0,
        # 2010-03:
        # MIB1265,1.0,1.0,[2010-03-05],26650.0,0.0,0,[],0,0,1,0,
        if len(line_lst) == 1 and '_start' in line_lst[0]:
            user = line_lst[0][2:9]
            cnt_lc = 0
            i = LC_lst.index(line) + 1
            while i < len(LC_lst):
                line_lst_0 = LC_lst[i].strip('\n').strip(',').split(',')
                if len(line_lst_0) == 1 and '_end' in line_lst_0[0]:
                    break
                if len(line_lst_0) == 1:
                    i += 1
                    continue
                if len(line_lst_0) > 1:
                    cnt_lc += 1
                    i += 1
                    continue
                i += 1
                continue
            if cnt_lc == 0:
                No_LC_lst.append(user)
            print user, '统计完毕...\n'
    print 'No LC Users is ', len(No_LC_lst), '\n'
    i = 0
    while i < len(No_LC_lst):
        if i % 10 == 0:
            print No_LC_lst[i], '\n'
            i += 1
        else:
            print No_LC_lst[i], ','
            i += 1
    f_No_LC = open(Dst_Dir + '\\' + 'CERT5.2_No_LC_Users.csv', 'w')
    for line in No_LC_lst:
        f_No_LC.write(line)
        f_No_LC.write('\n')
    f_No_LC.close()
    sys.exit()




# 实验一，分析CERT5.2中全周期下Insiders_2用户于离职用户联系的数量位置
# 需要准备两个数据
# 1. CERT5.2中全部用户于离职用户联系特征
# 2. CERT52用户列表
# 3. Insiders_2列表
print '数据准备\n'
Dst_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.7'
f_Insiders2 = open(Dst_Dir + '\\' + 'Insiders-2_Leave.csv', 'r')
f_CERT52 = open(Dst_Dir + '\\' + 'V07_CERT5.2_Users_WorkOn-Off_Time_Oneself.csv', 'r')
f_LC = open(Dst_Dir + '\\' + 'CERT5.2_Users_LeaveContacts_EmailFeats.csv', 'r')
f_Leave_Users = open(sys.path[0] + '\\' + 'CERT5.2-Leave-Users_OnDays_0.6.csv', 'r')
Insiders_2 = []
Insiders_2_Leave_Time = []
CERT52_Users = []
# LC_lst = []
for line in f_Insiders2.readlines():
    # data like:
    # VCF1602,2010-08-20,
    # CKP0630,2010-08-26,
    # ZIE0741,2010-08-27,
    line_lst = line.strip('\n').strip(',').split(',')
    Insiders_2.append(line_lst[0])
    Insiders_2_Leave_Time.append(line_lst[1])
f_Insiders2.close()
for line in f_CERT52.readlines():
    # data like:
    # AAB1302,WorkOn:9.0,WorkOff:19.0
    line_lst = line.strip('\n').strip(',').split(',')
    CERT52_Users.append(line_lst[0])
f_CERT52.close()
# 获取CERT5.2所有用户全生命周期的联系人列表
Leave_Users = []
Leave_Time = []
for line in f_Leave_Users.readlines():
    # data like
    # Laid off Users in CERT5.2 from 2009-12 to 2011-05
    # RMB1821,2010-02-09,Rose Maisie Blackwell,RMB1821,Ro
    line_lst = line.strip('\n').strip(',').split(',')
    if len(line_lst) == 1:
        continue
    Leave_Users.append(line_lst[0])
    Leave_Time.append(line_lst[1])
f_Leave_Users.close()
Contacts_0_lst = []
CERT52_Users.remove('AEH0001')
i = 0
while i < len(CERT52_Users):
    if CERT52_Users[i] in Leave_Users:
        user_time = Leave_Time[Leave_Users.index(CERT52_Users[i])]
    else:
        user_time = '2011-05-31'
    user = CERT52_Users[i]
    user_month = user_time[:7]
    user_month_path = Dst_Dir + '\\' + user_month + '\\' + 'CERT5.2_Users_EmailFeats-0.7'
    flag_user = False
    for file in os.listdir(user_month_path):
        # data like:
        # AAB1302_email_contacts.csv
        #if user == 'ZXR1452':
        #    print user, '\n'
            #sys.exit()
        if user in file and '_email_contacts' in file:
            flag_user = True
            file_path = user_month_path + '\\' + file
            f_user_contacts = open(file_path, 'r')
            # 只需要统计个数即可
            # cnt_user_c = 0
            cnt_user_c = len(f_user_contacts.readlines()) - 2
            if user == 'ZXR1452':
                print 'file_path is ', file_path, '\n'

                print user, cnt_user_c, '\n'
                # sys.exit()
            f_user_contacts.close()
            tmp_c = []
            tmp_c.append(user)
            tmp_c.append(cnt_user_c)
            Contacts_0_lst.append(tmp_c)
            break
        else:
            continue
    if flag_user == False:
        print user, user_time, '不存在contacts记录...\n'

    i += 1

print 'length of Contacts_0_lst is ', len(Contacts_0_lst), '\n'
print 'Length of CERT52 is ', len(CERT52_Users), '\n'
# sys.exit()
print '统计全生命周期LC个数\n'
f_CERT52_LC_Statis = open(Dst_Dir + '\\' + 'CERT5.2_Users_LC_Statistical.csv', 'w')
f_CERT52_LC_Statis.write('user_id' + ',')
f_CERT52_LC_Statis.write('cnt_lc_all-life' + ',')
f_CERT52_LC_Statis.write('sequence_0' + '\n')

LC_Statis_0 = []
LC_lst = f_LC.readlines()
f_LC.close()

for line in LC_lst:
    # data like
    # <<MMK1532_start>>:2011-06-30
    # 2010-02:
    # WMH1300,1.0,1.0,[2010-01-25],38275.0,0.0,0,[],0,0,1,0,
    line_lst = line.strip('\n').strip(',').split(',')
    if len(line_lst) == 1 and '_start' in line_lst[0]:
        user_0 = line_lst[0][2:9]
        cnt_lc = 0
        index_s = LC_lst.index(line)
        while index_s < len(LC_lst):
            line_lst_0 = LC_lst[index_s].strip('\n').strip(',').split(',')
            if user_0 in line_lst_0[0] and '_end' in line_lst_0[0]:
                # end
                break
            else:
                if len(line_lst_0) > 3:
                    cnt_lc += 1
                    index_s += 1
                    continue
                else:
                    index_s += 1
                    continue
        lc_0 = []
        lc_0.append(user_0)
        # 计算比例
        #print user_0, CERT52_Users.index(user_0), '\n'
        #print len(Contacts_0_lst), '\n'
        if CERT52_Users.index(user_0) >= len(Contacts_0_lst):
            continue
        cnt_c = float(Contacts_0_lst[CERT52_Users.index(user_0)][1])
        lc_0.append(cnt_lc / cnt_c)
        LC_Statis_0.append(lc_0)
for i in range(5):
    print 'LC_Statis_0 ', i, LC_Statis_0[i], '\n'
LC_Statis_0_sort = sorted(LC_Statis_0, key=lambda t: t[1], reverse=True)
for i in range(5):
    print 'LC_Statis_0_sort ', i, LC_Statis_0_sort[i], '\n'
j = 0
while j < len(LC_Statis_0):
    if LC_Statis_0_sort[j][0] in Insiders_2:
        print LC_Statis_0_sort[j][0], LC_Statis_0_sort[j][1], j, '\n'
        j += 1
    else:
        j += 1


sys.exit()



