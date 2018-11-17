# coding:utf-8

# 实验系列七配套的实验验证小程序

import os,sys

Flag_0 = False
if Flag_0:
    f_leave_month = open(r'G:\GitHub\Essay-Experiments\Experiment-JobSatisfactory-201808\PythonCode0\JS-Risks_Analyze-0.7\2010-02\Leave_Users_2010-02.csv', 'r')
    f_lm_lst = f_leave_month.readlines()
    f_leave_month.close()
    leave_users = []
    for line in f_lm_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        leave_users.append(line_lst[0])
    for i in range(10):
        print i, leave_users[i], '\n'

    f_user_contacts = open(r'G:\GitHub\Essay-Experiments\Experiment-JobSatisfactory-201808\PythonCode0\JS-Risks_Analyze-0.7\2010-02\CERT5.2_Users_EmailFeats-0.7\BYO1846_email_contacts.csv', 'r')
    f_uc_lst = f_user_contacts.readlines()
    f_user_contacts.close()

    leave_contacts = []
    for user in f_uc_lst:
        user_0 = user.strip('\n').strip(',').split('\n')
        if user_0[0] in leave_users:
            if user_0[0] not in leave_contacts:
                leave_contacts.append(user_0[0])
                print '离职联系人: ', user_0[0], '\n'


Flag_1 = False
if Flag_1:
    Email_Feats_Dir = r'G:\GitHub\Essay-Experiments\Experiment-JobSatisfactory-201808\PythonCode0\JS-Risks_Analyze-0.7\2010-02\CERT5.2_Users_EmailFeats-0.7'
    Email_Rcds_Dir = r'G:\GitHub\Essay-Experiments\CERT5.2-Results\CERT5.2-Users-EmailRecords'

    Lost_Users = []

    Users_On_EF = []
    Users_On_ER = []

    for file in os.listdir(Email_Feats_Dir):
        if 'contact' not in file:
            Users_On_EF.append(file[:7])
    for file in os.listdir(Email_Rcds_Dir):
        if 'feat' not in file:
            Users_On_ER.append(file[:7])

    for i in range(10):
        print i, Users_On_EF[i]

    for i in range(10):
        print i, Users_On_ER[i]

    for user in Users_On_ER:
        if user not in Users_On_EF:
            Lost_Users.append(user)

    print 'Lost Users : ', len(Lost_Users), '\n'
    for i in range(len(Lost_Users)):
        print i, sorted(Lost_Users)[i]

    print len(Users_On_ER), len(Users_On_EF), '\n'

# 实验3
Flag_2 = False
if Flag_2:
    # 根据CERT5.2离职用户信息，分别给出前个攻击场景用户的离职时间
    Dst_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.7'
    f_Leave_Users = open(sys.path[0] + '\\' + 'CERT5.2-Leave-Users_OnDays_0.6.csv', 'r')
    f_Leave_Users_lst = f_Leave_Users.readlines()
    f_Leave_Users.close()
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

    Insiders_1_Leave = []
    Insiders_2_Leave = []
    Insiders_3_Leave = []

    for line in f_Leave_Users_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        # data like:
        # Laid off Users in CERT5.2 from 2009-12 to 2011-05
        # RMB1821,2010-02-09,Rose Maisie Blackwell,RMB1821,Rose.Maisie.Blackwell@dtaa.com,Salesman
        if len(line_lst) == 1:
            continue
        if line_lst[0] in Insiders_1:
            tmp_0 = []
            tmp_0.append(line_lst[0])
            tmp_0.append(line_lst[1])
            Insiders_1_Leave.append(tmp_0)
        if line_lst[0] in Insiders_2:
            tmp_0 = []
            tmp_0.append(line_lst[0])
            tmp_0.append(line_lst[1])
            Insiders_2_Leave.append(tmp_0)
        if line_lst[0] in Insiders_3:
            tmp_0 = []
            tmp_0.append(line_lst[0])
            tmp_0.append(line_lst[1])
            Insiders_3_Leave.append(tmp_0)
    print '数据统计结果示例：\n'
    for i in range(10):
        print '1:', i, sorted(Insiders_1_Leave, key=lambda t:t[1])[i], '\n'
        print '2:', i, sorted(Insiders_2_Leave, key=lambda t: t[1])[i], '\n'
        print '3:', i, sorted(Insiders_3_Leave, key=lambda t: t[1])[i], '\n'

    f_Insider_1_Leave = open(Dst_Dir + '\\' + 'Insiders-1_Leave.csv', 'w')
    f_Insider_2_Leave = open(Dst_Dir + '\\' + 'Insiders-2_Leave.csv', 'w')
    f_Insider_3_Leave = open(Dst_Dir + '\\' + 'Insiders-3_Leave.csv', 'w')

    for line in sorted(Insiders_1_Leave, key=lambda t:t[1]):
        for ele in line:
            f_Insider_1_Leave.write(str(ele))
            f_Insider_1_Leave.write(',')
        f_Insider_1_Leave.write('\n')
    f_Insider_1_Leave.close()

    for line in sorted(Insiders_2_Leave, key=lambda t:t[1]):
        for ele in line:
            f_Insider_2_Leave.write(str(ele))
            f_Insider_2_Leave.write(',')
        f_Insider_2_Leave.write('\n')
    f_Insider_2_Leave.close()

    for line in sorted(Insiders_3_Leave, key=lambda t:t[1]):
        for ele in line:
            f_Insider_3_Leave.write(str(ele))
            f_Insider_3_Leave.write(',')
        f_Insider_3_Leave.write('\n')
    f_Insider_3_Leave.close()

    sys.exit()


Flag_3 = True
if Flag_3:
    Dst_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.7'
    month_lst  = ['2010-07', '2010-08', '2010-09', '2010-10', '2010-11', '2010-12', '2011-01', '2011-02', '2011-03', '2011-04', '2011-05']
    for month in month_lst:
        f_c_jsr = open(Dst_Dir + '\\' + month + '\\' + 'Current_Month_Leave_JSR.csv', 'r')
        f_a_jsr = open(Dst_Dir + '\\' + month + '\\' + 'Accumulated_Months_JSR.csv', 'r')
        f_hr = open(Dst_Dir + '\\' + month + '\\' + 'Next_Month_HighRisk.csv', 'r')

        f_c_jsr_lst = f_c_jsr.readlines()
        f_c_jsr.close()
        f_a_jsr_lst = f_a_jsr.readlines()
        f_a_jsr.close()
        f_hr_lst = f_hr.readlines()
        f_hr.close()

        c_jsr_lst = []
        a_jsr_lst = []
        hr_lst = []

        f_c_jsr_w = open(Dst_Dir + '\\' + month + '\\' + 'Current_Month_Leave_JSR_old.csv', 'w')
        for line in f_c_jsr_lst:
            line_lst = line.strip('\n').strip(',').split(',')
            tmp_1 = []
            tmp_1.append(line_lst[0])
            tmp_1.append(float(line_lst[1]))
            c_jsr_lst.append(tmp_1)
        c_jsr_order = sorted(c_jsr_lst, key=lambda t:t[1], reverse=True)
        for ele in c_jsr_order:
            for ele_0 in ele:
                f_c_jsr_w.write(str(ele_0))
                f_c_jsr_w.write(',')
            f_c_jsr_w.write('\n')
        f_c_jsr_w.close()

        f_a_jsr_w = open(Dst_Dir + '\\' + month + '\\' + 'Accumulated_Months_JSR_old.csv', 'w')
        for line in f_a_jsr_lst:
            line_lst = line.strip('\n').strip(',').split(',')
            tmp_1 = []
            tmp_1.append(line_lst[0])
            tmp_1.append(float(line_lst[1]))
            a_jsr_lst.append(tmp_1)
        a_jsr_order = sorted(a_jsr_lst, key=lambda t:t[1], reverse=True)
        for ele in a_jsr_order:
            for ele_0 in ele:
                f_a_jsr_w.write(str(ele_0))
                f_a_jsr_w.write(',')
            f_a_jsr_w.write('\n')
        f_a_jsr_w.close()

        f_hr_jsr_w = open(Dst_Dir + '\\' + month + '\\' + 'Next_Month_HighRisk_old.csv', 'w')
        for line in f_hr_lst:
            line_lst = line.strip('\n').strip(',').split(',')
            if len(line_lst) < 2:
                continue
            tmp_1 = []
            tmp_1.append(line_lst[0])
            tmp_1.append(float(line_lst[1]))
            hr_lst.append(tmp_1)
        hr_jsr_order = sorted(hr_lst, key=lambda t:t[1], reverse=True)
        for ele in hr_jsr_order:
            for ele_0 in ele:
                f_hr_jsr_w.write(str(ele_0))
                f_hr_jsr_w.write(',')
            f_hr_jsr_w.write('\n')
        f_hr_jsr_w.close()


