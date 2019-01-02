# coding:utf-8
# 这是一个面向对象的，借助SVM构建的用户JSR的预测器类
# 该类具有以下核心方法/属性：
# class_method_1: 构造初始化（数据复制准备）
# class_method_2: 析构函数
# class_method_3: JS特征提取函数
# class_method_4: train_predictor
# class_method_5: validate_predictor
# class_method_6: run_predicotr
# 下面，开始集中精力，完成该大类的编写实现，注意：
# 1. 阶段性验证，确保每一步完成后都是正确的；
# 2. 特殊事例验证；

import sys,os
import numpy as np
import sklearn.preprocessing as skp
import copy
import shutil
import math
from sklearn.svm import SVC
import pandas as pd
import sklearn.preprocessing as skp
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
import sklearn.decomposition as skd



def Get_User_OCEAN(user, f_ocean_lst):
    for line in f_ocean_lst:
        # data like:
        # employee_name,user_id,O,C,E,A,N
        # Maisie Maggy Kline,MMK1532,17,17,16,22,28
        line_lst = line.strip('\n').strip(',').split(',')
        if line_lst[1] == 'user_id':
            continue
        if line_lst[1] == user:
            tmp_ocean = []
            tmp_ocean.append(line_lst[1])
            for ele in line_lst[2:]:
                tmp_ocean.append(float(ele))
            return tmp_ocean  # 6-format: user_id, o, c, e, a, n
        else:
            continue

def Cal_CPB(user_ocean):
    # 给定一个上述格式的6-format: user_id, o, c, e, a, n
    # 计算该用户的CPB-I与CPB-O分数
    # 这里使用的是CERT文献中的三元显著关联特征：
    # CPB-I = -0.34 * A_Score + 0.36 * A_Score * (-0.40)
    # CPB-O = -0.52 * C_Score + 0.36 * A_Score * (-0.41)
    CPB_I = user_ocean[4] * (-0.34) + user_ocean[4] * 0.36 * (-0.40)
    CPB_O = user_ocean[2] * (-0.52) + user_ocean[4] * 0.36 * (-0.41)
    return CPB_I, CPB_O
# 定义一个给定user与ldap_src，自动返回其组织结构OS信息的函数
def Get_User_LDAP(user, f_ldap_lst):
    # 不考虑CEO的特征，因为CEO压根没有离职，也不是Insiders
    user_ldap = []
    Find_Label = False
    for line in f_ldap_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        # LDAP文件内容格式
        # employee_name,user_id,email,role,projects,business_unit,functional_unit,department,team,supervisor
        if line_lst[1] == 'user_id':
            continue
        if len(line_lst) < 10:
            # CEO
            continue
        if line_lst[1] == user:
            Find_Label = True
            # 补充上了项目+LDAP信息
            # 项目信息用于日后分析备用
            user_ldap.append(user)
            user_ldap.append(line_lst[4]) # projects
            user_ldap.append(line_lst[5])
            user_ldap.append(line_lst[6])
            user_ldap.append(line_lst[7])
            user_ldap.append(line_lst[8]) # team
            break
    # print user, 'Project + LDAP提取完毕..\n', user_ldap, '\n'
    if Find_Label == True:
        return user_ldap  # 6-format: user_id, project, bu, fu, dpt, team
    else:
        return 'Not Found'

def Get_User_LC_Feat(user_id, lc_lst, month):
    # 通过该函数，可以得到与user_id在划定时间周期内通讯的离职员工邮件特征
    # 把该时间段内所有与离职员工通讯看作和一个虚拟的离职用户通讯
    print '开始计算', user_id, '的leave_contacts邮件特征..\n'
    user_lc_feat = []

    user_lcontacts = [] # 时间段内与目标用户关联的离职用户列表，用于后续计算dis_OCEAN/dis_OS
    user_email_ratio = 0.0
    user_cnt_send = 0.0
    user_cnt_recv = 0.0
    user_send_size = 0.0
    user_recv_size = 0.0
    user_send_attach = 0.0
    user_recv_attach = 0.0
    user_send_days = []
    user_recv_days = []

    i = 0
    while i < len(lc_lst):
        lc_0 = lc_lst[i].strip('\n').strip(',').split(',')
        # data like:
        # <<MMK1532_start>>:2011-06-30
        # 2010-02:
        # WMH1300,1.0,1.0,[2010-01-25],38275.0,0.0,0,[],0,0,1,0,
        # 2010-03:
        # MIB1265,1.0,1.0,[2010-03-05],26650.0,0.0,0,[],0,0,1,0,
        if len(lc_0) == 1 and user_id + '_start' in lc_0[0]:
            index_s = i + 1
            while index_s < len(lc_lst):
                lc_lst_0 = lc_lst[index_s].strip('\n').strip(',').split(',')
                if len(lc_lst_0) == 1 and lc_lst_0[0].strip(':') > month:
                    print '超出的月份为：', user_id, lc_lst_0[0].strip(':'), '\n'
                    break
                if len(lc_lst_0) == 1 and user_id + '_end' in lc_lst_0[0]:
                    break
                if len(lc_lst_0) > 1:
                    # 计算通信的天数，如果有重复，需要去掉重复的天
                    if lc_lst_0[0] not in user_lcontacts:
                        user_lcontacts.append(lc_lst_0[0])
                    # MIB1265,1.0,1.0,[2010-03-05],26650.0,0.0,0,[],0,0,1,0,
                    # print 'test:', lc_lst_0, '\n'
                    user_cnt_send += float(lc_lst_0[2])
                    user_cnt_recv += float(lc_lst_0[6])
                    user_send_size += float(lc_lst_0[4])
                    user_recv_size += float(lc_lst_0[8])
                    user_send_attach += float(lc_lst_0[5])
                    user_recv_attach += float(lc_lst_0[9])
                    for day in lc_lst_0[3].strip('[').strip(']').split(';'):
                        if len(day) == 0:
                            continue
                        if day not in user_send_days:
                            user_send_days.append(day)
                    for day in lc_lst_0[7].strip('[').strip(']').split(';'):
                        if len(day) == 0:
                            continue
                        if day not in user_recv_days:
                            user_recv_days.append(day)
                    print user_id, 'leave_contact:', lc_lst_0[0], user_send_days, user_recv_days, '\n'
                    index_s += 1
                    continue
                else:
                    index_s += 1
                    continue
            print user_id, month, 'lc 提取完毕..跳出循环..\n' # 没有这一步将无限循环
            break
        else:
            i += 1
            continue
    user_lc_feat.append(user_id)
    X = len(user_send_days)
    Y = len(user_recv_days)
    if X + Y > 0:
        user_lc_feat.append(float(X - Y) / (X + Y))
    else:
        user_lc_feat.append(0.0)
    user_lc_feat.append(user_cnt_send)
    user_lc_feat.append(user_cnt_recv)
    user_lc_feat.append(user_send_size)
    user_lc_feat.append(user_recv_size)
    user_lc_feat.append(user_send_attach)
    user_lc_feat.append(user_recv_attach)
    user_lc_feat.append(float(len(user_send_days)))
    user_lc_feat.append(float(len(user_recv_days)))
    user_send_days.extend(user_recv_days)
    # [].extend()没有返回值，直接修改原列表
    #同理，对于直接修改原对象的方法而言，[].append()也没有返回值
    user_email_days = set(user_send_days)
    user_lc_feat.append(float(len(user_email_days)))
    print user_id, 'email_feat提取完毕...\n'
    return user_lcontacts, user_lc_feat # 12-format: user_id, email_ratio, cnt_send/recv, cnt_s/r_size, cnt_s/r_attach, cnt_s/r_days, cnt_email_days

def Cal_Distance_OCEAN(user_a_ocean, user_b_ocean):
    distance_a_b = 0.0
    i = 1
    while i < len(user_a_ocean):
        distance_a_b += math.pow(user_a_ocean[i] - user_b_ocean[i], 2)
        i += 1
    distance_a_b = math.pow(distance_a_b, 0.5)
    return distance_a_b

def Cal_Distance_LDAP(user_a_ldap, user_b_ldap):
    distance_a_b = 0.0
    i = 1
    while i < len(user_a_ldap):
        if user_a_ldap[i] == user_b_ldap[i]:
            distance_a_b += math.pow(2, len(user_a_ldap) - i)
            i += 1
        else:
            distance_a_b += 0
            i += 1
    return distance_a_b


def Cal_Personality_Feat(user_a, user_lcontacts, f_ocean_lst):

    distance_ocean = 0.0
    user_a_ocean = Get_User_OCEAN(user_a, f_ocean_lst)
    for lcontact in user_lcontacts:
        lc_ocean = Get_User_OCEAN(lcontact, f_ocean_lst)
        distance_ocean += Cal_Distance_OCEAN(user_a_ocean, lc_ocean)
    user_cpb_i, user_cpb_o = Cal_CPB(user_a_ocean)
    user_p_feat = []
    user_p_feat.append(user_a)
    user_p_feat.extend(user_a_ocean[1:])
    user_p_feat.append(user_cpb_i)
    user_p_feat.append(user_cpb_o)
    user_p_feat.append(distance_ocean)
    if len(user_lcontacts) > 0:
        user_p_feat.append(distance_ocean / len(user_lcontacts))
    else:
        # 默认处理方法：对于没有leave_contacts的用户，暂时先默认设置为0
        user_p_feat.append(0.0)


    return user_p_feat  # [user_id, o, c, e, a, n, cpb-i, cpb-o, dis_ocean, avg_dis_ocean]

def Cal_OS_Feat(user_a, user_lcontacts, f_ldap_lst):

    distance_ldap = 0.0
    dis_ladp = 0.0
    user_a_ldap = Get_User_LDAP(user_a, f_ldap_lst)
    for lcontact in user_lcontacts:
        lc_ldap = Get_User_LDAP(lcontact, f_ldap_lst)
        dis_ladp = Cal_Distance_LDAP(user_a_ldap, lc_ldap)
        distance_ldap += dis_ladp
    if len(user_lcontacts) == 0:
        return dis_ladp, 0.0
    else:
        return dis_ladp, dis_ladp / len(user_lcontacts)

class JS_SVM_Predictor():

    # 定义构造函数：
    # 1. 训练目录、验证目录以及测试目录的生成；
    # 2. 对应目录下，出勤率的统计以及离职用户列表的复制整理
    def __init__(self, src_dir, dst_dir): # 主要功能：重要数据复制，以及月份目录创建
        # 数据与结果目录，确保存在
        self.Dst_Dir = dst_dir
        self.Src_Dir = src_dir
        if os.path.exists(dst_dir) == False:
            os.mkdir(self.Dst_Dir)

        # 提取CERT5.2中分析的月份目录
        self.Leave_Users = [] # CERT5.2中离职用户
        self.Leave_Users_Time = [] # 对应于离职用户的离职时间，具体到了天
        self.Month_lst = []
        f_leave_months = open(dst_dir + '\\' + 'CERT5.2-LaidOff-Users_OnDays_0.6.csv', 'r')
        f_lm_lst = f_leave_months.readlines()
        f_leave_months.close()
        for line in f_lm_lst:
            # data like:
            # Laid off Users in CERT5.2 from 2009-12 to 2011-05
            # RMB1821,2010-02-09,ldap
            line_lst = line.strip('\n').strip(',').split(',')
            if len(line_lst) < 2:
                continue
            if line_lst[1][:7] not in self.Month_lst:
                self.Month_lst.append(line_lst[1][:7])
            tmp_lu = []
            tmp_lu.append(line_lst[0])
            tmp_lu.append(line_lst[1])
            self.Leave_Users.append(line_lst[0])
            self.Leave_Users_Time.append(tmp_lu)
        self.Month_lst.insert(0,'2010-01') # 补充上没有用户离职的2010-01
        print 'CERT5.2月份提取完毕：', self.Month_lst, '\n'

        # 提取CERT5.2中所有用户的Leave_Contacts信息
        # 数据文件self.*_lst基本提供的都是原始行读入文件
        # 数据涉及LDAP/OCEAN/LC等
        # self.CERT52_LC_lst
        #
        f_LC = open(self.Dst_Dir + '\\' + 'CERT5.2_Users_LeaveContacts_EmailFeats.csv', 'r')
        self.CERT52_LC_lst = f_LC.readlines()
        f_LC.close()
        # 提取CERT52用户的LDAP信息
        f_LDAP = open(self.Dst_Dir + '\\' + '2009-12.csv', 'r')
        self.CERT52_LDAP_lst = f_LDAP.readlines()
        f_LDAP.close()
        # 提取CERT5.2用户的OCEAN信息
        f_OCEAN = open(self.Dst_Dir + '\\' + 'psychometric-5.2.csv', 'r')
        self.CERT52_OCEAN_lst = f_OCEAN.readlines()
        f_OCEAN.close()

        # 建立训练目录、验证目录与测试目录
        # 训练目录：数据涵盖2010-01：2010-04
        # 验证目录：数据涵盖2010-05
        # 测试目录：数据分别涵盖2010-06:2011-05
        self.Train_Dir = dst_dir + '\\' + 'Train_Dir'
        if os.path.exists(self.Train_Dir) == False:
            os.mkdir(self.Train_Dir)
        self.Validate_Dir = dst_dir + '\\' + 'Validate_Dir'
        if os.path.exists(self.Validate_Dir) == False:
            os.mkdir(self.Validate_Dir)
        for month in self.Month_lst[5:]:
            month_path = dst_dir + '\\' + month
            if os.path.exists(month_path) == False:
                os.mkdir(month_path)
        print 'CERT5.2分析月份目录构建完毕..\n'



    def Data_Copy(self):
        # 将原先的出勤统计数据，分别组合拷贝到新的目录下(2个/月）
        # 将原先离职用户列表，分别拷贝到新的目录下（1个/月）
        # 首先是拷贝出勤数据
        # 1. 每月的logon数据容易拷贝，为了便于分析，分月拷贝；
        # 2. 出勤率统计需要进行累加重新组合
        Train_Months = self.Month_lst[:4]
        for month in Train_Months:
            src_month_path = self.Src_Dir + '\\' + month
            dst_train_path = self.Train_Dir
            for file in os.listdir(src_month_path):
                # 2010-10_logon_data.csv
                # 2010-10_early_late_team_feats.csv
                # Leave_Users_2010-02.csv
                if file == month + '_logon_data.csv' or file == month + '_early_late_team_feats.csv':
                    file_path = src_month_path + '\\' + file
                    shutil.copy(file_path, self.Train_Dir)
                if file == 'Leave_Users_' + month + '.csv':
                    file_path = src_month_path + '\\' + file
                    shutil.copy(file_path, self.Train_Dir)
        # 2010-01：2010-04的训练集合的登录出勤数据拷贝完毕
        # 接下来需要计算合并后的训练集出勤特征
        self.Train_LED_Feats = []
        self.CERT52_Users = []
        for file in os.listdir(self.Train_Dir):
            if '_early_late_team_feats.csv' in file:
                file_path = self.Train_Dir + '\\' + file
                f_led = open(file_path, 'r')
                for line_led in f_led.readlines():
                    # data like:
                    # AMC0265,6.5,18.5,7.0,2.0,21,-1
                    # ERB0921,6.5,18.0,11.0,2.0,21,1,2010-10-11,
                    line_led_lst = line_led.strip('\n').strip(',').split(',')
                    if line_led_lst[0] not in self.CERT52_Users:
                        self.CERT52_Users.append(line_led_lst[0])
                        tmp_0 = []
                        tmp_0.append(line_led_lst[0])
                        for ele in line_led_lst[1:6]:
                            tmp_0.append(float(ele))
                        self.Train_LED_Feats.append(tmp_0)
                    else:
                        user_index = self.CERT52_Users.index(line_led_lst[0])
                        # 迟到天数
                        self.Train_LED_Feats[user_index][3] += float(line_led_lst[3])
                        # 早退天数
                        self.Train_LED_Feats[user_index][4] += float(line_led_lst[4])
                        # 工作天数
                        self.Train_LED_Feats[user_index][5] += float(line_led_lst[5])
                print file, '训练集LED特征已分析..\n'
                f_led.close()
            else:
                continue
        print '训练集CERT5.2用户出勤率累积分析完毕..\n'
        for i in range(5):
            print i, self.Train_LED_Feats[i], '\n'
        # 重新写入：
        f_Train_LED = open(self.Train_Dir + '\\' + 'CERT5.2_Train_LaidOff_LED_OnTeam_v01.csv', 'w')
        for feat in self.Train_LED_Feats:
            for ele in feat:
                f_Train_LED.write(str(ele))
                f_Train_LED.write(',')
            f_Train_LED.write('\n')
        f_Train_LED.close()
        print '训练集CERT5.2用户出勤率结果保存完毕..\n'

        # 接下来开始拷贝验证集与测试集的logon.data以及LED数据
        for month in self.Month_lst[4:]:
            src_month_path = self.Src_Dir + '\\' + month
            if month == '2010-05':
                dst_train_path = self.Validate_Dir
            else:
                dst_train_path = self.Dst_Dir + '\\' + month
            for file in os.listdir(src_month_path):
                # 2010-10_logon_data.csv
                # 2010-10_early_late_team_feats.csv
                # Leave_Users_2010-02.csv
                if file == month + '_logon_data.csv' or file == month + '_early_late_team_feats.csv':
                    file_path = src_month_path + '\\' + file
                    shutil.copy(file_path, dst_train_path)
                if file == 'Leave_Users_' + month + '.csv':
                    file_path = src_month_path + '\\' + file
                    shutil.copy(file_path, dst_train_path)
        print '2010-05：2011-05的Logon.data/LED/Leave_Users数据拷贝完毕..\n'
    ####################################################################
    ####################################################################
    # CERT5.2的JS特征提取函数
    # CERT5.2用户的JS特征：
    # 1. user_id:
    # 2. OCEAN分数；
    # 3. CPB-I/CPB-O分数；
    # 4. 训练期间的出勤表现，迟到天数，早退天数，总工作天数
    # 5. 与离职员工群体的人格差异：Distance_OCEAN
    # 6. 与离职员工群体的组织差异：Distance_OS
    # 7. 与离职员工群体通信特征;
    # 7.1 Cnt_Send_Emails, Cnt_Recv_Emails
    # 7.2 Send_Size, Recv_Size
    # 7.3 Cnt_Send_Attach, Cnt_Recv_Attach
    # 7.4 Cnt_Send_Days, Cnt_Recv_Days
    # 7.5 Cnt_Email_Days
    #
    # Extract_JS_Feat函数将为预测器提供输入与输出支持
    # 一个目录中应包含的数据文件：
    # 1. 预测器的输入：用户的JS特征
    # 2. 预测器参数；
    # 3. 预测器的输出结果判定（类别及判断距离）
    # 4. Ground Truth标记
    # 5. 预测器的效果Assessment
    def Extract_JS_Feats(self, type):
        # type用于标识是训练集、验证集还是测试集
        # Extract_JS_Feats模块用于获取预测器的输入以及GroundTruth
        # 前期已经获取了CERT5.2中的self.Leave_Users与self.Leave_Users_Time

        if type == 'Train':
            # 我们先来计算训练集的GroundTruth
            self.TrainSet_GT = []
            for user in self.CERT52_Users:
                if user in self.Leave_Users and self.Leave_Users_Time[self.Leave_Users.index(user)][1][:7] < '2010-05':
                    tmp_gt = []
                    tmp_gt.append(user)
                    # SVM输出+1与-1
                    tmp_gt.append(0)
                    self.TrainSet_GT.append(tmp_gt)
                else:
                    tmp_gt = []
                    tmp_gt.append(user)
                    tmp_gt.append(1)
                    self.TrainSet_GT.append(tmp_gt)
            f_Train_GT = open(self.Train_Dir + '\\' + 'TrainSet_GroundTruth.csv_v01.csv', 'w')
            for user_gt in self.TrainSet_GT:
                for ele in user_gt:
                    f_Train_GT.write(str(ele))
                    f_Train_GT.write(',')
                f_Train_GT.write('\n')
            f_Train_GT.close()
            print 'TrainSet的Ground Truth计算完毕..\n'

            # 开始构造CERT5.2用户训练集的JS特征
            # 首先是OCEAN特征
            f_OCEAN = open(self.Dst_Dir + '\\' + 'psychometric-5.2.csv', 'r')
            self.CERT52_OCEAN_lst = f_OCEAN.readlines()
            f_OCEAN.close()
            print 'CERT5.2用户OCEAN分数读取完毕..\n'

            CERT52_Users_Train_JS_Feats = []
            for user in self.CERT52_Users[:]:
                print '开始分析用户', user, '\n'
                # 开始构造该用户的JS特征
                if Get_User_LDAP(user, self.CERT52_LDAP_lst) == 'Not Found':
                    print user, 'LDAP长度不标准...\n'
                    continue
                else:
                    print user, '首先提取用户的LC_Feat\n'
                    user_lcontacts, user_lc_feat = Get_User_LC_Feat(user, self.CERT52_LC_lst, '2010-04')
                    print user, '提取用户的OCEAN_Feat\n'
                    user_p_feat = Cal_Personality_Feat(user, user_lcontacts, self.CERT52_OCEAN_lst)
                    print user, '提取用户的OS_Feat\n'
                    dis_ldap, avg_dis_ldap = Cal_OS_Feat(user, user_lcontacts, self.CERT52_LDAP_lst)

                    # user_p_feat: [user_id, o, c, e, a, n, cpb-i, cpb-o, dis_ocean, avg_dis_ocean]
                    # user_lc_feat: # 12-format: user_id, email_ratio, cnt_send/recv, cnt_s/r_size, cnt_s/r_attach, cnt_s/r_days, cnt_email_days
                    # user_oc_feat: dis_ldap, avg_dis_ldap
                    user_js_feat = []
                    user_js_feat.extend(user_p_feat)
                    user_js_feat.append(dis_ldap)
                    user_js_feat.append(avg_dis_ldap)
                    user_js_feat.extend(user_lc_feat[1:])
                    CERT52_Users_Train_JS_Feats.append(user_js_feat)
                    print user, 'Until 2010-04, js feat is like: ', user_js_feat, '\n\n'

            # 特征写入
            f_Train_JS_Feats = open(self.Train_Dir + '\\' + 'CERT5.2_Train_JS_Feats-0.1.csv', 'w')
            f_Train_JS_Feats.write('user_id, o, c, e, a, n, cpb-i, cpb-o, dis_ocean, avg_dis_ocean, dis_os, avg_dis_os, email_ratio, cnt_send/recv, cnt_s/r_size, cnt_s/r_attach, cnt_s/r_days, cnt_email_days\n')
            for line in CERT52_Users_Train_JS_Feats:
                for ele in line:
                    f_Train_JS_Feats.write(str(ele))
                    f_Train_JS_Feats.write(',')
                f_Train_JS_Feats.write('\n')
            f_Train_JS_Feats.close()
            print 'CERT5.2 TrainSet JS Feats Write Done...\n\n'

        if type == 'Validate':
            pass
        if type == 'Test':
            pass

    def Build_Predictor(self, analyze_path):
        # type字段表示：Train, Validate, month(具体月份)
        # 依靠analyze_path来区分Train,Validate以及测试月份的SVM
        JS_Feats_lst = []
        JS_GT_lst = []
        for file in os.listdir(analyze_path):
            # CERT5.2_Train_JS_Feats-0.1.csv
            if '_JS_Feats-0.1' in file:
                file_path = analyze_path + '\\' + file
                f_js_feats = open(file_path, 'r')
                for line in f_js_feats.readlines():
                    line_lst = line.strip('\n').strip(',').split(',')
                    if line_lst[0] == 'user_id':
                        continue
                    js_feat_tmp = []
                    js_feat_tmp.append(line_lst[0])
                    for ele in line_lst[1:]:
                        js_feat_tmp.append(float(ele))
                    JS_Feats_lst.append(js_feat_tmp)
            # GroundTruth文件
            # TrainSet_GroundTruth.csv_v01.csv
            if '_GroundTruth' in file:
                file_path = analyze_path + '\\' + file
                f_js_gt = open(file_path, 'r')
                for line in f_js_gt.readlines():
                    line_lst = line.strip('\n').strip(',').split(',')
                    if line_lst[0] == 'user_id':
                        continue
                    js_gt_tmp = []
                    js_gt_tmp.append(line_lst[0])
                    for ele in line_lst[1:]:
                        js_gt_tmp.append(float(ele))
                    JS_GT_lst.append(js_gt_tmp)
        print analyze_path, 'JS Feats与GroundTruth文件提取完毕..\n'

        # 建立SVM分类器
        # 基于当此训练数据构建SVM分类器
        # 1. 建立X_Train与Y_Train;
        # 以当前的JS_Feats用户顺序为主，生成对应的Labels
        JS_Feats = []
        Lables_lst = []
        Train_Users = []
        i = 0
        while i < len(JS_Feats_lst):
            Train_Users.append(JS_Feats_lst[i][0])
            JS_Feats.append(JS_Feats_lst[i][1:])
            j = 0
            while j < len(JS_GT_lst):
                if JS_Feats_lst[i][0] == JS_GT_lst[j][0]:
                    Lables_lst.append(JS_GT_lst[j][1])
                    break
                else:
                    j += 1
                    continue
            i += 1
            continue
        print 'SVM的训练集JS_Feats/Labels生成完毕..\n'
        # 使用五折交叉验证，实现2010-01：2010-04月份用户JS_Feats的自动训练
        svr = SVC()
        parameters = {'C': [0.001, 0.003, 0.006, 0.009, 0.01, 0.04, 0.08, 0.1], 'kernel': ['linear', 'rbf'],
                      'gamma': [0.001, 0.005, 0.1, 0.15, 0.20, 0.23, 0.27], 'decision_function_shape': ['ovo', 'ovr'],
                      'class_weight': [{1: 1, 0: 10}]}
        # parameters = {'C': [0.1], 'kernel':('rbf'),}
        JS_Feats_array = np.array(JS_Feats)
        # 先做PCA
        JS_Feats_PCA = skd.PCA().fit_transform(JS_Feats_array)
        # 然后再做scale
        JS_Feats_scale = skp.scale(JS_Feats_PCA)
        Lables_array = np.array(Lables_lst)
        X_train, X_test, y_train, y_test = train_test_split(JS_Feats_scale, Lables_array, test_size=0.2, random_state=1)

        # print np.isnan(JS_Feats_scale).any(), '\n'

        #clf = SVC(gamma='auto', kernel='rbf', cache_size=500)
        #clf.fit(X_train, y_train)
        #print 'X_test[0] is ', X_test[0], y_test[0], '\n'
        #print clf.predict([X_test[0]]), '\n' # SVM的预测必须输入一个[]形式的参数，即使只有一个样本需要预测

        #sys.exit()
        # GridSearchCV，sklearn的自动调优函数
        print '开始使用GridSearchCV自动调优参数..\n'
        clf = GridSearchCV(svr, parameters)
        clf.fit(X_train, y_train)


        # 使用a储存调优后的参数结果
        print '储存调优后的参数结果..\n'
        a = pd.DataFrame(clf.cv_results_)

        # 按照mean_test_score降序排列
        # a.sort(['mean_test_score'], ascending=False)

        # 输出最好的分类器参数，以及测试集的平均分类正确率
        print clf.best_estimator_, '\n', clf.best_score_, '\n'




    def Run_Predictor(self):
        pass








