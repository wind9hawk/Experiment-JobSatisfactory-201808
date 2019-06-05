# coding:utf-8
# 之前的v0.8版本JS_SVM_Predictor类目标不明确，带有过多冗余函数，这次在0.9版本中一并精简

# coding:utf-8
# 这是一个面向对象的，借助SVM构建的用户JSR的预测器类
# 该类具有以下核心方法/属性：
# class_method_1: 构造初始化（处理数据的环境路径确定）
# class_method_2: 析构函数（删除对象变量）
# class_method_3: JS特征提取函数
# class_method_4: train_predictor（Build_Predictor and Choose_Predictor）
# class_method_5: validate_predictor
# class_method_6: run_predicotr
# class_method_7: update_predictor(目前主要通过更新Train_set和调整训练比例进行)
# 下面，开始集中精力，完成该大类的编写实现，注意：
# 1. 阶段性验证，确保每一步完成后都是正确的；
# 2. 特殊事例验证；
# 3. 重申：我们的目标1是尽可能识别出离职的Insiders，其次是尽可能识别出离职者，同时减少可疑范围；


import sys,os
import numpy as np
import sklearn.preprocessing as skp
import copy
import shutil
import math
from sklearn.svm import SVC
import pandas as pd
import sklearn.preprocessing as skp
import sklearn.decomposition as skd
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
import sklearn.decomposition as skd


# 部分使用的计算函数
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
    if len(user_lcontacts) == 0:
        cnt_lc = 1
    else:
        cnt_lc = len(user_lcontacts)
    X = len(user_send_days)
    Y = len(user_recv_days)
    if X + Y > 0:
        user_lc_feat.append(float(X - Y) / (X + Y))
    else:
        user_lc_feat.append(0.0)
    user_lc_feat.append(user_cnt_send / cnt_lc)
    user_lc_feat.append(user_cnt_recv / cnt_lc)
    user_lc_feat.append(user_send_size / cnt_lc)
    user_lc_feat.append(user_recv_size / cnt_lc)
    user_lc_feat.append(user_send_attach / cnt_lc)
    user_lc_feat.append(user_recv_attach / cnt_lc)
    user_lc_feat.append(float(len(user_send_days)) / cnt_lc)
    user_lc_feat.append(float(len(user_recv_days)) / cnt_lc)
    user_send_days.extend(user_recv_days)
    # [].extend()没有返回值，直接修改原列表
    #同理，对于直接修改原对象的方法而言，[].append()也没有返回值
    user_email_days = set(user_send_days)
    user_lc_feat.append(float(len(user_email_days)) / cnt_lc)
    print user_id, 'email_feat提取完毕...\n'
    return user_lcontacts, user_lc_feat # 12-format: user_id, email_ratio, cnt_send/recv, cnt_s/r_size, cnt_s/r_attach, cnt_s/r_days, cnt_email_days


def Cal_Distance_OCEAN(user_a_ocean, user_b_ocean):
    distance_a_b = 0.0
    i = 1
    while i < len(user_a_ocean):
        distance_a_b += math.pow(user_a_ocean[i] - user_b_ocean[i], 2)
        i += 1
    # dis_ocean = 1 / log(dis_ocean)
    distance_a_b = math.pow(math.log(math.e + math.pow(distance_a_b, 0.5), math.e), -1)
    #distance_a_b = math.pow(distance_a_b, 0.5) # 将OCEAN看作五维度向量，计算你彼此间欧式距离
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
    distance_a_b = math.pow(math.log(math.e + distance_a_b, math.e), -1)
    # 直接返回异或代表的二进制值
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
        return distance_ldap, 0.0
    else:
        return distance_ldap, distance_ldap / len(user_lcontacts)

def Cal_Month_LED(user, f_led_lst):
    user_led = []
    i = 0
    while i < len(f_led_lst):
        if f_led_lst[i][0] == user:
            for ele in f_led_lst[i][1:]:
                user_led.append(ele)
            break
        else:
            i += 1
            continue
    return user_led

# SVM_Predictor对象所有的操作都在一个特定的目录上进行；
# 对于提取特征而言，由于训练集划分可能需要包括多个月，因此存在一个月份列表的判断；


# 类JS_Feats()用于从原始数据中，提取出当月的JS_Feats，可以根据需求灵活修改定制，添加模块
class JS_Feats():

    # 定义构造函数：
    # 初始化各种关键路径
    # 明确预测器训练数据所在根目录：dst_dir
    # 明确要考虑的月份列表，最少一个月份，可以多个元素
    def __init__(self, dst_dir, month, months_lst):
        # 数据与结果目录，确保存在
        self.Dst_Dir = dst_dir
        if os.path.exists(dst_dir) == False:
            os.mkdir(self.Dst_Dir)
        self.Month = month
        self.Months_lst = months_lst
        for month in self.Months_lst:
            if os.path.exists(self.Dst_Dir + '\\' + self.Month) == False:
                os.mkdir(self.Dst_Dir + '\\' + self.Month)


        # 提取CERT5.2中分析的月份目录
        self.Leave_Users = [] # CERT5.2中离职用户
        self.Leave_Users_Time = [] # 对应于离职用户的离职时间，具体到了天
        f_leave_months = open(self.Dst_Dir + '\\' + 'CERT5.2-Leave-Users_OnDays_0.6.csv', 'r')
        f_lm_lst = f_leave_months.readlines()
        f_leave_months.close()
        for line in f_lm_lst:
            # data like:
            # Laid off Users in CERT5.2 from 2009-12 to 2011-05
            # RMB1821,2010-02-09,ldap
            line_lst = line.strip('\n').strip(',').split(',')
            if len(line_lst) < 2:
                continue
            tmp_lu = []
            tmp_lu.append(line_lst[0])
            tmp_lu.append(line_lst[1])
            self.Leave_Users.append(line_lst[0])
            self.Leave_Users_Time.append(tmp_lu)

        # 提取CERT5.2中所有用户的Leave_Contacts信息
        # 数据文件self.*_lst基本提供的都是原始行读入文件
        # 数据涉及LDAP/OCEAN/LC等
        # self.CERT52_LC_lst
        #
        f_LC = open(self.Dst_Dir + '\\' + 'CERT5.2_Users_LeaveContacts_EmailFeats.csv', 'r')
        self.CERT52_LC_lst = f_LC.readlines()
        f_LC.close()
        print 'CERT5.2用户Leave_Contacts数据提取完毕...\n'
        # 提取CERT52用户的LDAP信息
        f_LDAP = open(self.Dst_Dir + '\\' + '2009-12.csv', 'r')
        self.CERT52_LDAP_lst = f_LDAP.readlines()
        f_LDAP.close()
        print 'CERT5.2用户LDAP数据提取完毕...\n'
        # 提取CERT5.2用户的OCEAN信息
        f_OCEAN = open(self.Dst_Dir + '\\' + 'psychometric-5.2.csv', 'r')
        self.CERT52_OCEAN_lst = f_OCEAN.readlines()
        f_OCEAN.close()
        print 'CERT5.2用户OCEAN数据提取完毕...\n'

    def __del__(self):
        print '开始删除JS_Feats对象..\n'
        del self.Dst_Dir
        del self.Month
        del self.Months_lst
        del self.Leave_Users
        del self.Leave_Users_Time
        del self.CERT52_Users_lst
        del self.LED_Feats
        del self.Month_Users_GT
        del self.CERT52_LDAP_lst
        del self.CERT52_OCEAN_lst
        del self.CERT52_LC_lst
        print 'JS_Feats对象清除完毕..\n'

    def Extract_JS_Feats(self):
        # 如果是一个月，已经有该特征，跳过；
        # 如果是多个月的列表，则说明多个月作为了一个整体，统计出勤率的和
        print '单个月合并截止到该月的出勤率特征..\n'
        # 打开self.Month_lst[0]下的2010-01_early_late_team_feats.csv即可，将天数读取为float
        self.LED_Feats = []
        self.LED_Users = []
        # 需要认真区分self.Month与month的不同：
        # self.Month是类对象属性，表示当前分析的目录，决定了分析月份序列的终点
        # month是循环中间变量，month需要从2010-01遍历到self.Month
        # self.Months_lst表示所有的月份列表
        for month in self.Months_lst:
            print month, self.Month, month <= self.Month, '\n'
            if month <= self.Month:
                month_path = self.Dst_Dir + '\\' + month
                for file in os.listdir(month_path):
                    if month in file and '_early_late_team_feats' in file:
                        # 说明找到对应的LED文件
                        file_path = month_path + '\\' + file
                        f_Train_LED = open(file_path, 'r')
                        for line in f_Train_LED.readlines():
                            # data like:
                            # AAW0914,6.5,18.0,7.0,1.0,20,-1
                            # CRC1132,6.5,16.0,6.0,6.0,20,-1
                            line_led_lst = line.strip('\n').strip(',').split(',')
                            #if line_led_lst[0] != 'MMK1532':
                            #    continue
                            #print 'Bug for:', line_led_lst[0], line_led_lst,  '\n'
                            if line_led_lst[0] not in self.LED_Users:
                                self.LED_Users.append(line_led_lst[0])
                                tmp_led = []
                                tmp_led.append(line_led_lst[0])
                                # 迟到次数，早退次数，总工作天数
                                tmp_led.append(float(line_led_lst[3]))
                                tmp_led.append(float(line_led_lst[4]))
                                tmp_led.append(float(line_led_lst[5]))
                                print 'after create:', line_led_lst[0], line_led_lst[1:], '\n'
                                self.LED_Feats.append(tmp_led)
                                print 'LED_Users is ', self.LED_Users, '\n'
                                continue
                            else:
                                user_index = self.LED_Users.index(line_led_lst[0])
                                print 'before add:', line_led_lst[0], line_led_lst[1:], '\n'
                                self.LED_Feats[user_index][1] += float(line_led_lst[3])
                                self.LED_Feats[user_index][2] += float(line_led_lst[4])
                                self.LED_Feats[user_index][3] += float(line_led_lst[5])
                                continue
                        f_Train_LED.close()
                print self.Month, '单月CERT5.2用户出勤率特征统计完毕..\n'
                print self.LED_Feats[0], '\n'
                #for i in range(5):
                 #   print i, 'LED_Feats:', self.LED_Feats[i], '\n'
            else:
                break
        f_Train_LED_w = open(self.Dst_Dir + '\\' + self.Month + '\\' + self.Month + '_CERT5.2_Leave_LED_Feats-0.2.csv', 'w')
        for line in self.LED_Feats:
            for ele in line:
                f_Train_LED_w.write(str(ele))
                f_Train_LED_w.write(',')
            f_Train_LED_w.write('\n')
        f_Train_LED_w.close()
        #for i in range(5):
        #    print i, 'LED_Feats:', self.LED_Feats[i], '\n'

        # 得到一个初始的CERT5.2用户列表
        self.CERT52_Users_lst = []
        for line in self.CERT52_LDAP_lst:
            line_ldap_lst = line.strip('\n').strip(',').split(',')
            # data like:
            # employee_name,user_id,email,role,projects,business_unit,functional_unit,department,team,supervisor
            if len(line_ldap_lst) < 10:
                continue
            if line_ldap_lst[1] == 'user_id':
                continue
            self.CERT52_Users_lst.append(line_ldap_lst[1])
        print 'self.CERT52_Users初始化完成（不包含CEO）..\n'

        # 构建完成了当月/月组的LED特征，接下来，开始构造JS_Feat的其余部分
        # 尝试不再单独考虑，因为单独一个月份其实就是月列表只有一个元素的特例
        # 我们先来计算每个月的GroundTruth(含当月数据)
        self.Month_Users_GT = [] # Ground Truth for current month
        self.Month_Crt_Users = copy.copy(self.CERT52_Users_lst) # 当月还在职的用户
        for user in self.CERT52_Users_lst:
            if user in self.Leave_Users and self.Leave_Users_Time[self.Leave_Users.index(user)][1][:7] <= self.Month:
                tmp_gt = []
                tmp_gt.append(user)
                # SVM输出+1与-1
                tmp_gt.append(1)
                self.Month_Users_GT.append(tmp_gt)
                if self.Leave_Users_Time[self.Leave_Users.index(user)][1][:7] < self.Month:
                    self.Month_Crt_Users.remove(user) # 去掉当月已经不在单位的用户，还包含当月离职用户
            else:
                tmp_gt = []
                tmp_gt.append(user)
                tmp_gt.append(-1)
                self.Month_Users_GT.append(tmp_gt)
        f_Month_Users_GT = open(self.Dst_Dir + '\\' + self.Month + '\\' + self.Month + '_CERT5.2_Users_GroundTruth.csv_v02.csv', 'w')
        for user_gt in self.Month_Users_GT:
            if user_gt[0] not in self.Month_Crt_Users:
                continue # 如此，得到的GroundTruth与当月JS_Feats中只包含当月还在职的用户
            for ele in user_gt:
                f_Month_Users_GT.write(str(ele))
                f_Month_Users_GT.write(',')
            f_Month_Users_GT.write('\n')
        f_Month_Users_GT.close()
        print self.Month, ' 的在职用户的Ground Truth计算完毕..\n'
        # sys.exit() 验证通过

        # 开始构造CERT5.2用户每个月份的JS特征
        # 首先是OCEAN特征

        CERT52_Users_Month_JS_Feats = []
        for user in self.Month_Crt_Users[:]:
            #print '开始分析用户', user, '\n'
            #if user != 'MMK1532':
            #    continue
            # 开始构造该用户的JS特征
            if Get_User_LDAP(user, self.CERT52_LDAP_lst) == 'Not Found':
                print user, 'LDAP长度不标准...\n'
                continue
            else:
                print user, '首先提取用户的LC_Feat\n'
                user_lcontacts, user_lc_feat = Get_User_LC_Feat(user, self.CERT52_LC_lst, self.Month)
                print user, '提取用户的OCEAN_Feat\n'
                user_p_feat = Cal_Personality_Feat(user, user_lcontacts, self.CERT52_OCEAN_lst)
                print user, '提取用户的OS_Feat\n'
                dis_ldap, avg_dis_ldap = Cal_OS_Feat(user, user_lcontacts, self.CERT52_LDAP_lst)
                print user, '提取用户当月的出勤率情况\n'
                user_led_feat = Cal_Month_LED(user, self.LED_Feats)
                # user_p_feat: [user_id, o, c, e, a, n, cpb-i, cpb-o, dis_ocean, avg_dis_ocean]
                # user_lc_feat: # 12-format: user_id, email_ratio, cnt_send/recv, cnt_s/r_size, cnt_s/r_attach, cnt_s/r_days, cnt_email_days
                # user_oc_feat: dis_ldap, avg_dis_ldap
                user_js_feat = []
                user_js_feat.extend(user_p_feat)
                user_js_feat.append(dis_ldap)
                user_js_feat.append(avg_dis_ldap)
                user_js_feat.extend(user_led_feat)
                user_js_feat.extend(user_lc_feat[1:])
                CERT52_Users_Month_JS_Feats.append(user_js_feat)
                print user, 'Until ', self.Month, 'js feat is like: ', user_js_feat, '\n\n'
        # 特征写入
        f_Train_JS_Feats = open(self.Dst_Dir + '\\' + self.Month + '\\' + 'CERT5.2_Month_AvgLC_Leave_JS_Feats_v02.csv', 'w')
        f_Train_JS_Feats.write('user_id, o, c, e, a, n, cpb-i, cpb-o, dis_ocean, avg_dis_ocean, dis_os, avg_dis_os, cnt_late_days, cnt_early_days, month_work_days, email_ratio, cnt_send/recv, cnt_s/r_size, cnt_s/r_attach, cnt_s/r_days, cnt_email_days\n')
        for line in CERT52_Users_Month_JS_Feats:
            for ele in line:
                f_Train_JS_Feats.write(str(ele))
                f_Train_JS_Feats.write(',')
            f_Train_JS_Feats.write('\n')
        f_Train_JS_Feats.close()
        print 'CERT5.2 TrainSet JS Feats Write Done...\n\n'


# 在定义了JS_Feats.class后，我们继续定义一个新的核心类：JS_SVM_Predictor()
# 该类需要指定目标分析目录，训练月份、测试月份等，然后在每个月输出其预测结果（同一个预测器的输入输出都在当月目录）

class JS_SVM_Predictor():
    def __init__(self, dst_dir, train_months_lst, test_months_lst):
        # 目标目录
        self.Dst_Dir = dst_dir
        # 训练月份
        self.Train_Months_lst = train_months_lst
        # 测试月份
        self.Test_Months_lst = test_months_lst
        # 所有的训练与测试都在对应的下一级目录中进行
        self.Train_Dir = self.Dst_Dir + '\\' + 'Train_Dir'
        self.Test_Dir = self.Dst_Dir + '\\' + 'Test_Dir'
        if os.path.exists(self.Train_Dir) == False:
            os.mkdir(self.Train_Dir)
        if os.path.exists(self.Test_Dir) == False:
            os.mkdir(self.Test_Dir)
        # Test_Dir目录下集中存放生诚器与预测结果，全部以月份开头的文件格式
        # month_labels
        # month_predicotor_results
        # all_month_recall_fp
        print 'JS_SVM_Predicoter对象初始化完毕..\n'

    # 训练集方法
    def Build_TrainSet(self):
        # 1. 首先需要确定本次训练的用户JS_Feats与用户的实际Labels；
        # 2. 再次基础上构建分类器，调优的最佳分类器参数输出，并保存其预测结果；
        # 3. 得到的最佳分类器需要输出给测试函数
        ###### 训练集的确定Train_Set/Train_Set_Label
        # 训练集中分析对象为原始的CERT5.2全体用户
        # 最终的Lable依据训练月最后一个月份时所有离职的用户确定
        # 从训练月最后一个月开始，倒向回溯用户JS_Feats（因为用户JS_Feat的LC部分已经时累积变量，而契约部分相同）
        # 新的JS_Feats处理后，包括LED特征在内的所有user自身的ocean/ldap特征以及dis_ocear/dis_ldap
        # 和最重要的LC信息，都已经是累加结果了
        # user_id, o, c, e, a, n, cpb-i, cpb-o,
        # dis_ocean, avg_dis_ocean, dis_os, avg_dis_os,
        # cnt_late_days, cnt_early_days, month_work_days, (本项需要更新)
        # email_ratio, cnt_send/recv, cnt_s/r_size, cnt_s/r_attach, cnt_s/r_days, cnt_email_days

        print '开始生成训练集CERT5.2用户的JS_Feats，并保存..\n'
        self.CERT52_Users = []
        self.TrainSet_JSF_lst = [] # 2010-01:2010-04
        self.ValidateSet_JSF_lst = [] # 2010-05
        self.ValidateSet_Lables = []
        i = 0
        # -2 -i: 意味着从2010-01:2010-04， 最后的2010-05作为验证集以训练最好的泛化误差
        while len(self.Train_Months_lst) - 2 - i >= 0:
            # 打开当月的用户JS_Feats文件
            f_month_js_feats = open(self.Dst_Dir + '\\' + self.Train_Months_lst[len(self.Train_Months_lst) - 1 - i] + '\\' + 'CERT5.2_Month_JS_Feats_v01.csv', 'r')
            f_month_jsf_lst = f_month_js_feats.readlines()
            f_month_js_feats.close()

            for line in f_month_jsf_lst:
                line_jsf = line.strip('\n').strip(',').split(',')
                if line_jsf[0] == 'user_id':
                    continue
                if line_jsf[0] not in self.CERT52_Users:
                    self.CERT52_Users.append(line_jsf[0])
                    jsf_tmp = []
                    jsf_tmp.append(line_jsf[0])
                    for ele in line_jsf[1:]:
                        jsf_tmp.append(float(ele))
                    self.TrainSet_JSF_lst.append(jsf_tmp)
                    continue
                else:
                    # 新JS_Feats特征不需要更新LED部分
                    #index_user = CERT52_Users.index(line_jsf[0])
                    #self.TrainSet_JSF_lst[index_user][12] += float(line_jsf[12])
                    #self.TrainSet_JSF_lst[index_user][13] += float(line_jsf[13])
                    #self.TrainSet_JSF_lst[index_user][14] += float(line_jsf[14])
                    continue
            print self.Train_Months_lst[len(self.Train_Months_lst) - 2 - i], '训练集：JS_Feats提取完毕..\n'
            i += 1
        f_train_jsf = open(self.Train_Dir + '\\' + self.Train_Months_lst[-2] + '_CERT5.2_TrainSet_JSF.csv', 'w')
        for line in self.TrainSet_JSF_lst:
            for ele in line:
                f_train_jsf.write(str(ele) + ',')
            f_train_jsf.write('\n')
        f_train_jsf.close()

        print '接下来为训练集的所有用户打上标签..\n'
        # 读取所有用户的离职列表以及时间
        self.Leave_Users = [] # CERT5.2中离职用户
        self.Leave_Users_Time = [] # 对应于离职用户的离职时间，具体到了天
        f_leave_months = open(self.Dst_Dir + '\\' + 'CERT5.2-Leave-Users_OnDays_0.6.csv', 'r')
        f_lm_lst = f_leave_months.readlines()
        f_leave_months.close()
        for line in f_lm_lst:
            # data like:
            # Laid off Users in CERT5.2 from 2009-12 to 2011-05
            # RMB1821,2010-02-09,ldap
            line_lst = line.strip('\n').strip(',').split(',')
            if len(line_lst) < 2:
                continue
            tmp_lu = []
            tmp_lu.append(line_lst[0])
            tmp_lu.append(line_lst[1])
            self.Leave_Users.append(line_lst[0])
            self.Leave_Users_Time.append(tmp_lu)

        self.TrainSet_Lables = []
        last_month = self.Train_Months_lst[-2]
        for user in self.CERT52_Users:
            if user in self.Leave_Users:
                if self.Leave_Users_Time[self.Leave_Users.index(user)][1][:7] <= last_month:
                    # 说明在训练集该用户已经离职
                    lable_0 = []
                    lable_0.append(user)
                    lable_0.append(+1)
                    # 离职+1，在职-1
                    self.TrainSet_Lables.append(lable_0)
                    continue
                else:
                    lable_0 = []
                    lable_0.append(user)
                    lable_0.append(-1)
                    self.TrainSet_Lables.append(lable_0)
            else:
                lable_0 = []
                lable_0.append(user)
                lable_0.append(-1)
                self.TrainSet_Lables.append(lable_0)
        print 'self.CERT52_Users:', len(self.CERT52_Users), '\n'
        f_train_labels = open(self.Train_Dir + '\\' + self.Train_Months_lst[-2] + '_CERT5.2_TrainSet_Lables.csv', 'w')
        for line in self.TrainSet_Lables:
            for ele in line:
                f_train_labels.write(str(ele) + ',')
            f_train_labels.write('\n')
        f_train_labels.close()

    def Build_ValidateSet(self):
        # 提取训练月份最后一个月的数据作为验证集，以训练泛化误差
        validate_month = self.Train_Months_lst[-1]
        f_validate_jsf = open(self.Dst_Dir + '\\' + validate_month + '\\' + 'CERT5.2_Month_JS_Feats_v01.csv', 'r')
        validate_jsf_lst = f_validate_jsf.readlines()
        f_validate_jsf.close()
        self.Validate_Users = []
        for line in validate_jsf_lst:
            line_lst = line.strip('\n').strip(',').split(',')
            if line_lst[0] == 'user_id':
                continue
            if line_lst[0] not in self.Validate_Users:
                self.Validate_Users.append(line_lst[0])
            validate_jsf_tmp = []
            validate_jsf_tmp.append(line_lst[0])
            for ele in line_lst[1:]:
                validate_jsf_tmp.append(float(ele))
            self.ValidateSet_JSF_lst.append(validate_jsf_tmp)
        f_validate_jsf_w = open(self.Train_Dir + '\\' + self.Train_Months_lst[-1] + '_CERT5.2_ValidateSet_JSF.csv', 'w')
        for line in self.ValidateSet_JSF_lst:
            for ele in line:
                f_validate_jsf_w.write(str(ele) + ',')
            f_validate_jsf_w.write('\n')
        f_validate_jsf_w.close()
        print self.Train_Months_lst[-1], '验证集JS_Feats提取完毕..\n'

        self.ValidateSet_Lables = []
        last_month = self.Train_Months_lst[-1]
        for user in self.Validate_Users:
            if user in self.Leave_Users:
                if self.Leave_Users_Time[self.Leave_Users.index(user)][1][:7] <= last_month:
                    # 说明在训练集该用户已经离职
                    lable_0 = []
                    lable_0.append(user)
                    lable_0.append(+1)
                    # 离职+1，在职-1
                    self.ValidateSet_Lables.append(lable_0)
                    continue
                else:
                    lable_0 = []
                    lable_0.append(user)
                    lable_0.append(-1)
                    self.ValidateSet_Lables.append(lable_0)
            else:
                lable_0 = []
                lable_0.append(user)
                lable_0.append(-1)
                self.ValidateSet_Lables.append(lable_0)
        f_validate_labels = open(self.Train_Dir + '\\' + self.Train_Months_lst[-1] + '_CERT5.2_ValidateSet_Lables.csv', 'w')
        for line in self.ValidateSet_Lables:
            for ele in line:
                f_validate_labels.write(str(ele) + ',')
            f_validate_labels.write('\n')
        f_validate_labels.close()
        print self.Train_Months_lst[-1], '验证集标签完毕..\n'


    def Train_SVM_Predictor(self):
        # 数据准备与分析过程分离开
        # 核心：基于用户前N个月的JS_Feats与对应离职在职Lables，建立SVM Predictor预测第N+1个月；
        # 之后循环，再次基于第N+1个月训练来预测第N+2个月
        # 特征的scale
        # 当前训练集共有5个月，选择其中前四个月为Train_train_set, 后一个月为Train_test_set进行训练SVM

        print '构建前N个月训练集的Train_JS_Feats与对应的Train_Lables..\n'
        # self.TrainSet_JSF_lst, self.TrainSet_Lables
        # 顺序与CERT52_Users顺序一致
        Train_JSF_lst = []
        Train_Lables_lst = []
        i = 0
        while i < len(self.CERT52_Users):
            Train_JSF_lst.append(self.TrainSet_JSF_lst[i][1:])
            Train_Lables_lst.append(self.TrainSet_Lables[i][1])
            i += 1
        print '验证：\n'
        print 9, self.CERT52_Users[9], self.TrainSet_Lables[9], '\n'
        print self.TrainSet_JSF_lst[9], '\n'
        Train_JSF_array = np.array(Train_JSF_lst)
        Train_Lables_array = np.array(Train_Lables_lst)
        pca = skd.PCA()
        Train_JSF_PCA = pca.fit_transform(Train_JSF_array)
        n_components = pca.n_components_
        Train_JSF_Scale = skp.scale(Train_JSF_PCA)

        # 开始确定SVM的遍历参数空间
        Parameter_C = [0.2, 0.4, 0.8, 1, 10, 100, 1000, 10000, 100000]
        Parameter_K = ['rbf', 'linear']
        Parameter_Gama = [0.001,0.005,0.1,0.15,0.20,0.23,0.27]
        Count_1 = float(Train_Lables_lst.count(1))
        Ratio_1 = float(Count_1 / len(Train_Lables_lst))
        Parameter_CW = {1: 1000, -1: 1}
        # Parameter_CW = 'balanced'
        # 确定验证集的数据形式与Lables
        Validate_JSF_lst = []
        Validate_JSF_Labels = []
        i = 0
        while i < len(self.Validate_Users):
            Validate_JSF_lst.append(self.ValidateSet_JSF_lst[i][1:])
            Validate_JSF_Labels.append(self.ValidateSet_Lables[i][1])
            i += 1
        Validate_JSF_scale = skp.scale(skd.PCA(n_components=n_components).fit_transform(np.array(Validate_JSF_lst)))

        self.SVM_Choice_Results = []

        for para_c in Parameter_C:
            for para_k in Parameter_K:
                for para_g in Parameter_Gama:
                    Cnt_Error = 0.0
                    Cnt_Recall = 0.0
                    Cnt_FN = 0.0
                    Cnt_TN = 0.0
                    Cnt_FP = 0.0
                    clf = SVC(para_c, para_k, para_g, cache_size=300, class_weight=Parameter_CW)
                    clf.fit(Train_JSF_Scale, Train_Lables_array)
                    Y_Pred = clf.predict(Validate_JSF_lst)
                    j = 0
                    while j < len(Y_Pred):
                        if Y_Pred[j] != Validate_JSF_Labels[j]:
                            Cnt_Error += 1

                        if Validate_JSF_Labels[j] == 1.0:
                            if Y_Pred[j] == 1.0:
                                Cnt_Recall += 1

                            else:
                                Cnt_FN += 1

                        if Validate_JSF_Labels[j] == -1.0:
                            if Y_Pred[j] == -1.0:
                                Cnt_TN += 1

                            else:
                                Cnt_FP += 1
                        j += 1
                    svm_relust = []
                    svm_relust.append(para_c)
                    svm_relust.append(para_k)
                    svm_relust.append(para_g)
                    svm_relust.append(Cnt_Recall / len(Validate_JSF_Labels))
                    svm_relust.append(Cnt_Error /  len(Validate_JSF_Labels))
                    svm_relust.append(Cnt_TN /  len(Validate_JSF_Labels))
                    svm_relust.append(Cnt_FP /  len(Validate_JSF_Labels))
                    svm_relust.append(Cnt_FN /  len(Validate_JSF_Labels))
                    self.SVM_Choice_Results.append(svm_relust)
        print 'Train SVM Predictor结果为： \n'
        sorted(self.SVM_Choice_Results, key=lambda t:t[3], reverse=True)
        for i in range(len(self.SVM_Choice_Results)):
            print i, self.SVM_Choice_Results[i], '\n'












