# coding:utf-8
# 一般一个测试文件不宜超过五个模块，影响可读性

# 本实验模块解决以下几个问题：
# 1. 将Insiders_2中所有用户的离职联系人email_feat写入一个统一文件供分析；
# 2. CERT5.2中Insiders_2特定用户分析RLV特征时用到的四个维度的子特征在每个月中的位置（考虑正态分布）
# dis_ocean
# dis_os
# email_days
# email_info

import os,sys
import sklearn.preprocessing as skp
import numpy as np

# 初始化攻击者列表
Scene_1_Dir = os.path.dirname(sys.path[0]) + '\\' + 'r5.2-1'
Scene_2_Dir = os.path.dirname(sys.path[0]) + '\\' + 'r5.2-2'
Scene_3_Dir = os.path.dirname(sys.path[0]) + '\\' + 'r5.2-3'
Insiders_1 = []
Insiders_2 = []
Insiders_3 = []
for file in os.listdir(Scene_1_Dir):
    # r5.2-1-ALT1465.csv
    if file[7:14] not in Insiders_1:
        Insiders_1.append(file[7:14])
for file in os.listdir(Scene_2_Dir):
    # r5.2-1-ALT1465.csv
    if file[7:14] not in Insiders_2:
        Insiders_2.append(file[7:14])
for file in os.listdir(Scene_3_Dir):
    # r5.2-1-ALT1465.csv
    if file[7:14] not in Insiders_3:
        Insiders_3.append(file[7:14])

Father_Current_Dir = os.path.dirname(sys.path[0])
# CERT5.2中全体用户的LDAP数据
LDAP_Dir= Father_Current_Dir + '\\' + 'LDAP'
# 定义一个全局所有时间段的LDAP文件路径列表
All_LDAP_Path = []
for file in os.listdir(LDAP_Dir):
    All_LDAP_Path.append(LDAP_Dir + '\\' + file)
print 'check All_LDAP_Path: \n'
for i in range(5):
    print i, All_LDAP_Path[i], '\n'
f_cert_users = open(All_LDAP_Path[0], 'r')
f_cert_users_lst = f_cert_users.readlines()
f_cert_users.close()
CERT52_Users = []
for line in f_cert_users_lst:
    # LDAP数据格式为：
    # employee_name,user_id,email,role,projects,business_unit,functional_unit,department,team,supervisor
    line_lst = line.strip('\n').strip(',').split(',')
    if len(line_lst) < 10:
        print 'CEO is ', line_lst[1], '\n'
        continue
    if line_lst[1] != 'user_id':
        CERT52_Users.append(line_lst[1])
print '..<<CERT5.2 用户列表初始化完成>>..\t', len(CERT52_Users), '\n\n'
Flag_0 = True
if Flag_0:
    print '....<<<<统计所有Insiders_2用户的离职联系人特征>>>>....\n\n'

    Dst_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.7'
    f_insiders_2 = open(Dst_Dir + '\\' + 'CERT5.2_Users_Months_EmailFeats.csv', 'w')
    # 读入离职用户数据
    f_Leave_Users = open(sys.path[0] + '\\' + 'CERT5.2-Leave-Users_OnDays_0.6.csv', 'r')
    f_Leave_Users_lst = f_Leave_Users.readlines()
    f_Leave_Users.close()
    # leave data like:
    # RMB1821,2010-02-09,LDAP
    Leave_Users = []
    Leave_Users_Time = []
    for line in f_Leave_Users_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        if len(line_lst) < 2:
            continue
        Leave_Users.append(line_lst[0])
        Leave_Users_Time.append(line_lst[1])
    print '....<<<<首先按用户处理>>>>....\n\n'
    for insider in CERT52_Users:
        if insider in Leave_Users:
            insider_time = Leave_Users_Time[Leave_Users.index(insider)]
            f_insiders_2.write('<<' + insider + '_start>>' + ':' + insider_time + '\n')
        else:
            insider_time = '2011-06-30'
            f_insiders_2.write('<<' + insider + '_start>>' + ':' + '2011-06-30' + '\n')
        print '..<<按月顺序遍历处理>>..\n'
        for month in os.listdir(Dst_Dir):
            month_path = Dst_Dir + '\\' + month
            if month > insider_time[:7]:
                continue
            if os.path.isdir(month_path) == False:
                print insider, month, 'month_file false...\n'
                continue
            # 判断当月目录下是否有可分析的用户邮件信息
            flag_insider = False
            for dir in os.listdir(month_path):
                if 'CERT5.2_Users_EmailFeats-0.7' in dir:
                    flag_insider = True
                    feat_dir_path = month_path + '\\' + dir
                    break
                else:
                    continue
            if flag_insider == False:
                continue
            for file in os.listdir(feat_dir_path):
                if insider in file and 'feats' in file:
                    file_path = feat_dir_path + '\\' + file
                else:
                    continue
            if os.path.exists(file_path) == False:
                print '目标文件不存在...\n'
                sys.exit()
            f_insiders_2.write(month + ':\n')
            print insider, '开始分析', month, '\n'
            # 若存在，则data like:
            # contact_user_id,Email_Ratio,Cnt_Send,Send_Days,Avg_Send_Size,Avg_Send_Attach,Cent_Recv,Recv_Days,Avg_Recv_Size,Avg_Recv_Attach,Cnt_Send_Days,Cnt_Recv_Days
            # RMB1821,-0.2,14.0,[2010-01-13; 2010-01-15; 2010-01-21; 2010-01-22; 2010-01-25; 2010-01-26; 2010-01-28; 2010-02-08; 2010-02-09],338767.214286,5.0,21.0,[2010-01-05; 2010-01-06; 2010-01-07; 2010-01-11; 2010-01-12; 2010-01-18; 2010-01-20; 2010-01-26; 2010-01-27; 2010-01-29; 2010-02-01; 2010-02-02; 2010-02-03; 2010-02-04; 2010-02-08],165035.857143,5.0,9,15
            f_insider = open(file_path, 'r')
            insider_leave_feats = f_insider.readlines()
            if len(insider_leave_feats) < 2:
                print month, insider, '不存在离职联系人联系..\n'
                continue
            else:
                for line in insider_leave_feats:
                    line_lst = line.strip('\n').strip(',').split(',')
                    if line_lst[0] == 'contact_user_id':
                        continue
                    lc_time = Leave_Users_Time[Leave_Users.index(line_lst[0])]
                    if insider_time <= lc_time:
                        continue
                    else:
                        for ele in line_lst:
                            f_insiders_2.write(ele)
                            f_insiders_2.write(',')
                        f_insiders_2.write('\n')
        f_insiders_2.write('<<' + insider + '_end>>' + '\n\n\n')
        print insider, 'leave contacts feats统计写入完毕..\n\n'
    f_insiders_2.close()


Flag_1 = False
if Flag_1:
    # 统计2010-01：2011-04中，CERT5.2全部用户同时迟到与早退的天数与总工作天数
    # 分别建立两个列表，一一对应
    # CERT52_Users = []
    # LEDays = [ledays, work_days]
    CERT52_Users = []
    LEDays = []
    Dst_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.7'
    for month in os.listdir(Dst_Dir)[:]:
        if os.path.isdir(Dst_Dir + '\\' + month) == False:
            continue
        else:
            month_path = Dst_Dir + '\\' + month
            flag_file = False
            for file in os.listdir(month_path):
                # Month_early_late_team_feats.csv
                if 'early_late_team_feats' in file:
                    flag_file = True
                    file_path = month_path + '\\' + file
                else:
                    continue
            if flag_file == False:
                continue
            f_led_team = open(file_path, 'r')
            for line in f_led_team.readlines():
                line_lst = line.strip('\n').strip(',').split(',')
                if len(line_lst) < 7:
                    continue
                if line_lst[0] not in CERT52_Users:
                    # data like: MPK1844,8.5,16.0,0.0,0.0,21,-1
                    # SEL1062,8.0,16.0,11.0,13.0,31,8,2010-07-01,2010-07-02,2010-07-06,2010-07-17,2010-07-19,2010-07-27,2010-07-30,2010-07-31,
                    CERT52_Users.append(line_lst[0])
                    tmp_0 = []
                    print line_lst, '\n'
                    if line_lst[6] == '-1':
                        tmp_0.append(float(0))
                    else:
                        tmp_0.append(float(line_lst[6]))
                    tmp_0.append(float(line_lst[5]))
                    tmp_0.append(0.0)
                    LEDays.append(tmp_0)
                else:
                    index_0 = CERT52_Users.index(line_lst[0])
                    if line_lst[6] != '-1':
                        LEDays[index_0][0] += float(line_lst[6])
                    LEDays[index_0][1] += float(line_lst[5])
            print month, line_lst[0], '..分析完毕...\n'
            f_led_team.close()
    for line in LEDays:
        # print line, '\n'
        line[-1] += line[0] / line[1]
    f_led_team = open(Dst_Dir + '\\' + 'CERT5.2_Users_LEDays_Team.csv', 'w')
    Insiders_2_LEDays = []
    i = 0
    while i < len(CERT52_Users):
        f_led_team.write(CERT52_Users[i])
        f_led_team.write(',')
        for ele in LEDays[i]:
            f_led_team.write(str(ele))
            f_led_team.write(',')
        f_led_team.write('\n')
        if CERT52_Users[i] in Insiders_2:
            # print CERT52_Users[i], LEDays[i], '\n'
            tmp_1 = []
            tmp_1.append(CERT52_Users[i])
            tmp_1.extend(LEDays[i])
            Insiders_2_LEDays.append(tmp_1)
        i += 1
    f_led_team.close()

    j = 1
    Cnt_Null = 0
    for line in sorted(Insiders_2_LEDays):
        # data like:
        # 24 ['SNK1280', 97.0, 261.0, ratio]
        print j, line, '\n'
        if line[1] == 0:
            Cnt_Null += 1
        j += 1

    print 'Cnt_Null is :', Cnt_Null, '\n'

    LEDays_Sort = []
    f_led_team = open(Dst_Dir + '\\' + 'CERT5.2_Users_LEDays_Team.csv', 'r')
    f_led_team_w = open(Dst_Dir + '\\' + 'CERT5.2_Users_LEDays_Team_order.csv', 'w')
    for line in f_led_team.readlines():
        line_lst = line.strip('\n').strip(',').split(',')
        tmp_2 = []
        for ele in line_lst:
            tmp_2.append(ele)
        LEDays_Sort.append(tmp_2)
    LEDays_Sort = sorted(LEDays_Sort, key=lambda t:t[-1], reverse=True)
    for line in LEDays_Sort:
        if line[0] in Insiders_2:
            print LEDays_Sort.index(line), line, '\n'
        for ele in line:
            f_led_team_w.write(str(ele))
            f_led_team_w.write(',')
        f_led_team_w.write('\n')
    f_led_team.close()
    f_led_team_w.close()

    sys.exit()



Flag_2 = False
if Flag_2:
    # 之前统计邮件特征时，[]的split结果始终为1，而不是0，导致结果的错误
    # 为了提高效率，直接修改了源代码，并直接修改结果特征文件
    Dst_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.7'
    for month in os.listdir(Dst_Dir)[:]:
        # 作为测试，我们针对2010-03，的BYO1846
        #if '2010-03' not in month:
        #    continue
        month_path = Dst_Dir + '\\' + month
        if os.path.isdir(month_path) == False:
            continue
        # 判断当月目录下是否有可分析的用户邮件信息
        flag_insider = False
        for dir in os.listdir(month_path):
            if 'CERT5.2_Users_EmailFeats-0.7' in dir:
                flag_insider = True
                feat_dir_path = month_path + '\\' + dir
                break
            else:
                continue
        if flag_insider == False:
            continue
        for file in os.listdir(feat_dir_path)[:]:
            # 每一个用户都要分析了
            if 'efeats' not in file:
                continue
            #if 'BYO1846' not in file:
            #    continue
            file_path = feat_dir_path + '\\' + file
            f_user_old = open(feat_dir_path + '\\' + file, 'r')
            f_user_feat = f_user_old.readlines()
            f_user_old.close()
            f_user_new = open(feat_dir_path + '\\' + file, 'w')
            # 若存在，则data like:
            # contact_user_id,Email_Ratio,Cnt_Send,Send_Days,Avg_Send_Size,Avg_Send_Attach,Cent_Recv,Recv_Days,Avg_Recv_Size,Avg_Recv_Attach,Cnt_Send_Days,Cnt_Recv_Days
            # RMB1821,-0.2,14.0,[2010-01-13; 2010-01-15; 2010-01-21; 2010-01-22; 2010-01-25; 2010-01-26; 2010-01-28; 2010-02-08; 2010-02-09],338767.214286,5.0,21.0,[2010-01-05; 2010-01-06; 2010-01-07; 2010-01-11; 2010-01-12; 2010-01-18; 2010-01-20; 2010-01-26; 2010-01-27; 2010-01-29; 2010-02-01; 2010-02-02; 2010-02-03; 2010-02-04; 2010-02-08],165035.857143,5.0,9,15
            user_email_feat = []
            for line in f_user_feat:
                line_lst = line.strip('\n').strip(',').split(',')
                #print line_lst, '\n'
                #print len(line_lst[7].strip('[').strip(']').split(';')), '\n'
                #print line_lst[7].strip('[').strip(']'), '\n'
                #print len(line_lst[7].strip('[').strip(']')), '\n'
                if len(line_lst[3].strip('[').strip(']')) == 0:
                    line_lst[-2] = '0'
                    #print line_lst, '\n'
                if len(line_lst[7].strip('[').strip(']')) == 0:
                    line_lst[-1] = '0'
                    #print line_lst, '\n'
                user_email_feat.append(line_lst)
            for line_new in user_email_feat:
                for ele in line_new:
                    f_user_new.write(str(ele))
                    f_user_new.write(',')
                f_user_new.write('\n')
            print month, file, '修改完毕...\n'
    sys.exit()


Flag_3 = False
if Flag_3:
    # 联系类的使用
    class Test:
        Name = 'None'
        def __init__(self, name):
            print 'class Test init...\n'
            self.Name = name

        def __del__(self):
            print '阐述类别的变量...\n'
            print 'self.Name is ', self.Name, '\n'
            del self.Name

    ts = Test('GY')

    print getattr(ts, 'Name'), '\n'
    del ts
