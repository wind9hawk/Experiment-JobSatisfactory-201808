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


Flag_1 = True
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
