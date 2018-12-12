# coding:utf-8
# 这是我的第一个面向对象的类文件
# 定义了一个用户与离职用户通信特征类，该类中应具备以下几个基本元素：
# 1. 构造与析构函数
# 2. 提取特定用户截止到特定月份需分析的邮件联系特征
# 3. 基于提取的邮件联系特征计算截止到该月的离职用户对该用户的显性影响
# 3.1 提取原则依据通讯天数（不重复）由多到少选取高于等于均值/中位数的结果（需要实验高于/等于/均值/中位数）

import os, sys
import sklearn.preprocessing as skp
import numpy as np
import copy
import math

def Cal_EmailInfo(email_feat):
    # data like: 应当进行了MinMax
    # [0.4        0.48275862 1.         0.55555556 0.63636364 0.30998456
    #  0.26315789 0.45       0.68181818 0.61764706]
    er = float(email_feat[0])
    cnt_send = float(email_feat[1])
    avg_size_send = float(email_feat[2])
    cnt_attach_send = float(email_feat[3])
    # 附件没有求平均
    cnt_recv = float(email_feat[4])
    avg_size_recv = float(email_feat[5])
    cnt_attach_recv = float(email_feat[6])
    cnt_email_days = float(email_feat[-1])
    #rlv_e = math.exp(abs(0.5 - er)) * (
    # 公式1：仅考虑了通信天数+通信封数+通信附件个数的线性和
    print 'cal feat is ', email_feat, '\n'
    # rlv_e = math.log(1.0 + cnt_email_days + (cnt_send * avg_size_send + cnt_recv * avg_size_recv) + (cnt_attach_send + cnt_attach_recv), math.e)
    rlv_e = math.log(1.0 + cnt_email_days + cnt_send  + cnt_recv  + cnt_attach_send + cnt_attach_recv, math.e)
    print 'rlv_e is ', rlv_e, '\n'
    # sys.exit()
    return rlv_e


class U2Lu_EMFeats_Cls():
    # 定义几个类内全局变量
    # 类内用户
    # 需考虑的当前月份
    # 特征来源数据列表
    # 结果数据目录
    # 该用户，截止到当月的离职用户的显性影响因子RLV
    # 定义构造函数
    # 类对象的变量可以在构造函数中进行全部初始化
    def __init__(self, user, month, emf_lst, dst_dir, f_mean, f_median):
        self.User = user
        self.Month = month
        self.Reslut_Dir = dst_dir + '\\' + month
        self.Emf_lst = emf_lst
        self.User_Rlv = 0.0
        self.User_EM_Month_Feats = []
        self.f_mean = f_mean
        self.f_median = f_median
        # print self.User_rlv, '\n'
        print self.User, self.Month, '初始化完毕...\n'
    # 定义析构函数
    def __del__(self):
        print self.User, self.Month, '析构完毕...\n'
        del self.User
        del self.Month
        del self.Emf_lst
        del self.Reslut_Dir
        del self.User_Rlv
        del self.User_EM_Month_Feats
        del self.f_median
        del self.f_mean
    # 定义一个月份特征提取函数
    def Extract_Month_EMF(self):
        # 可以在类函数中定义函数变量与类对象变量
        # 我们需要首先遍历Emf_lst中的数据内容，确定我们要分析的用户内容位置
        # 定义用户特征起始索引
        user_emf_month_lst = []
        # Data like:
        # <<MMK1532_start>>
        # 2010-02:
        # WMH1300,1.0,1.0,[2010-01-25],38275.0,0.0,0,[],0,0,1,0,
        # 2010-03:
        # MIB1265,1.0,1.0,[2010-03-05],26650.0,0.0,0,[],0,0,1,0,
        i = 0
        while i < len(self.Emf_lst):
            line_lst = self.Emf_lst[i].strip('\n').strip(',').split(',')
            if len(line_lst) == 1 and (self.User + '_start') in line_lst[0]:
                # print self.User, 'find\n'
                # sys.exit()
                index_start = i + 1
                # 根据月份筛选记录
                while index_start < len(self.Emf_lst):
                    line_lst_0 = self.Emf_lst[index_start].strip('\n').strip(',').split(',')
                    if len(line_lst_0) == 1 and '-' in line_lst_0[0]:
                        # 这是一个日期
                        if line_lst_0[0].strip(':') > self.Month:
                            # 不需要再分析
                            #print line_lst_0[0], self.Month, line_lst_0[0] > self.Month, '\n'
                            #print line_lst_0[0], 'break'
                            #sys.exit()
                            break
                        else:
                            user_emf_month_lst.append(line_lst_0)
                            index_start += 1
                            continue
                    else:
                        user_emf_month_lst.append(line_lst_0)
                        index_start += 1
                        continue
                break
            else:
                i += 1
                continue
        for line in user_emf_month_lst:
            if len(line) < 2:
                continue
            else:
                self.User_EM_Month_Feats.append(line)
        print self.User, self.Month, 'EM Feats示例：\n'
        for i in range(len(self.User_EM_Month_Feats)):
            print i, self.User_EM_Month_Feats[i], '\n'
    # 定义一个从月份特征中提取显著特征的函数
    # 仅当月份特征元素个数大于1时才比较均值/中位数
    # 在实际编写时发现的问题：
    # 1. 必须依据通信天数的均值或者中位数选择哪些联系人特征用作计算RLV；
    # 2. 实际计算时必须进行归一化，归一化的对象是原始的User_EM_Month_Feats，由此才能体现出筛选特征在原有通讯行为中的重要性
    # 否则，会出现单纯的极值情况
    # 当前数据格式示例
    # 3 ['JSB0860', '-1.0', '0', '[]', '0', '0', '1.0', '[2010-01-21]', '22047.0', '0.0', '0', '1']
    def Extract_Key_EMF(self):
        # 从原始的月份特征中提取通信天数达到要求的KEY特征
        # 首先对原始特征数值化，并提取无重合的通信天数
        self.User_EM_Month_Feats_Array = []
        i = 0
        while i < len(self.User_EM_Month_Feats):
            tmp_0 = []
            j = 1
            while j < len(self.User_EM_Month_Feats[i]):
                if j != 3 and j != 7:
                    tmp_0.append(float(self.User_EM_Month_Feats[i][j]))
                    j += 1
                else:
                    j += 1
            # 在题还原有特征前，需要保存该用户的通信天数
            # print self.User_EM_Month_Feats[i], '\n'
            email_days = []
            if tmp_0[-2] != 0.0:
                # 有发送邮件
                for day in self.User_EM_Month_Feats[i][3].strip('[').strip(']').split(';'):
                    if day not in email_days:
                        email_days.append(day)
            if tmp_0[-1] != 0.0:
                for day in self.User_EM_Month_Feats[i][7].strip('[').strip(']').split(';'):
                    if day not in email_days:
                        email_days.append(day)
            tmp_0.append(float(len(email_days)))
            self.User_EM_Month_Feats_Array.append(tmp_0)
            print self.User_EM_Month_Feats[i], '\n'
            print self.User_EM_Month_Feats_Array[i], 'email days is ', email_days, '\n'
            i += 1
        # 已经提取了纯数值特征，此时顺序仍未打乱，因此，可以记录筛选的显著性特征的归属：User_id:index
        # 打开一个新文件用于记录当月下，筛选出的用户邮件特征
        Cnt_Email_Days = []
        for feat in self.User_EM_Month_Feats_Array:
            # data like
            # [-1.0, 0.0, 0.0, 0.0, 1.0, 22047.0, 0.0, 0.0, 1.0, 1.0]
            Cnt_Email_Days.append(feat[-1])
        EMD_Mean = np.mean(Cnt_Email_Days)
        EMD_Median = np.median(Cnt_Email_Days)
        print 'Mean is: ', EMD_Mean, 'Median is ', EMD_Median, '\n'
        self.f_mean.write('<<' + self.User + '>>\n')
        self.f_median.write('<<' + self.User + '>>\n')
        print Cnt_Email_Days, '\n'
        # sys.exit()


        self.User_Key_EMF_OnMean = []
        self.User_Key_EMF_OnMedian = []
        # 计算RLV的数值需要先经过MinMax
        self.On_Mean_Index = []
        self.On_Median_Index = []
        i = 0
        while i < len(self.User_EM_Month_Feats_Array):
            print self.User_EM_Month_Feats_Array[i], '\n'
            if self.User_EM_Month_Feats_Array[i][-1] >= EMD_Mean:
                #self.User_Key_EMF_OnMean.append(self.User_EM_Month_Feats_Array[i])
                self.On_Mean_Index.append(i)
                self.f_mean.write(self.User_EM_Month_Feats[i][0])
                self.f_mean.write(',')
                for ele in self.User_EM_Month_Feats_Array[i]:
                    self.f_mean.write(str(ele))
                    self.f_mean.write(',')
                self.f_mean.write('\n')
                i += 1
            else:
                i += 1
        print self.User, '写入完毕...\n'

        i = 0
        while i < len(self.User_EM_Month_Feats_Array):
            print self.User_EM_Month_Feats_Array[i], '\n'
            if self.User_EM_Month_Feats_Array[i][-1] >= EMD_Median:
                #self.User_Key_EMF_OnMedian.append(self.User_EM_Month_Feats_Array[i])
                self.On_Median_Index.append(i)
                self.f_median.write(self.User_EM_Month_Feats[i][0])
                self.f_median.write(',')
                for ele in self.User_EM_Month_Feats_Array[i]:
                    self.f_median.write(str(ele))
                    self.f_median.write(',')
                self.f_median.write('\n')
                i += 1
            else:
                i += 1
        print self.User, '写入完毕...\n'

        if len(self.User_EM_Month_Feats_Array) < 2:
            self.User_Key_EMF_OnMean = copy.copy(self.User_EM_Month_Feats_Array)
            self.User_Key_EMF_OnMedian = copy.copy(self.User_EM_Month_Feats_Array)
        else:
            self.User_Key_EMF_MinMax = skp.MinMaxScaler().fit_transform(self.User_EM_Month_Feats_Array)
            for index in self.On_Mean_Index:
                self.User_Key_EMF_OnMean.append(self.User_Key_EMF_MinMax[index])
            for index in self.On_Median_Index:
                self.User_Key_EMF_OnMedian.append(self.User_Key_EMF_MinMax[index])

        for i in range(len(self.On_Mean_Index)):
            print i, self.User_Key_EMF_OnMean[i], '\n'
        for i in range(len(self.On_Median_Index)):
            print i, self.User_Key_EMF_OnMedian[i], '\n'

    def Cal_RLV(self):
        print '开始计算', self.User, self.Month, '的RLV值\n'
        self.RLV_Mean = 0.0
        self.RLV_Median = 0.0
        for line in self.User_Key_EMF_OnMean:
            self.RLV_Mean += Cal_EmailInfo(line)
        for line in self.User_Key_EMF_OnMedian:
            self.RLV_Median += Cal_EmailInfo(line)
        print 'RLV on Mean is ', self.RLV_Mean, '\n'
        print 'RLF on Median is ', self.RLV_Median, '\n'
        return self.RLV_Mean, self.RLV_Median





















print '....<<<<类测试>>>>....'
Dst_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.7'
f_Users_EM_Feats_Path = Dst_Dir + '\\' + 'CERT5.2_Users_Final_LeaveContacts_EmailFeats_V0.7.csv'
f_Users_EM_Feats = open(f_Users_EM_Feats_Path, 'r')
f_Users_EMF_lst = f_Users_EM_Feats.readlines()
f_Users_EM_Feats.close()

f_Leave_Users = open(sys.path[0] + '\\' + 'CERT5.2-Leave-Users_OnDays_0.6.csv', 'r')
f_Leave_Users_lst = f_Leave_Users.readlines()
f_Leave_Users.close()

# 定义一个全局所有时间段的LDAP文件路径列表
Father_Current_Dir = os.path.dirname(sys.path[0])
LDAP_Dir= Father_Current_Dir + '\\' + 'LDAP'
All_LDAP_Path = []
for file in os.listdir(LDAP_Dir):
    All_LDAP_Path.append(LDAP_Dir + '\\' + file)
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

for dir in os.listdir(Dst_Dir)[:]:
    print 'dir is ', dir, '\n'
    if '2010-07' not in dir:
        continue
    if os.path.isdir(Dst_Dir + '\\' + dir) == True:
        Month = dir
        f_Users_Month_Key_EMF_OnMean = open(Dst_Dir + '\\' + Month + '\\' + '_Users_Key_EmailFeats_OnMean.csv', 'w')
        f_Users_Month_Key_EMF_OnMedian = open(Dst_Dir + '\\' + Month + '\\' + '_Users_Key_EmailFeats_OnMedian.csv', 'w')
        CERT52_Users_RLV_OnMean = []
        CERT52_Users_RLV_OnMedian = []
        for user in CERT52_Users:
            a = U2Lu_EMFeats_Cls(user, Month, f_Users_EMF_lst, Dst_Dir, f_Users_Month_Key_EMF_OnMean, f_Users_Month_Key_EMF_OnMedian)
            a.Extract_Month_EMF()
            a.Extract_Key_EMF()
            rlv_0, rlv_1 = a.Cal_RLV()
            tmp_0 = []
            tmp_1 = []
            tmp_0.append(user)
            tmp_0.append(rlv_0)
            tmp_1.append(user)
            tmp_1.append(rlv_1)
            CERT52_Users_RLV_OnMean.append(tmp_0)
            CERT52_Users_RLV_OnMedian.append(tmp_1)
            #Rlv_Mean, Rlv_Median = a.Cal_RLV()
            del a
        f_Users_Month_Key_EMF_OnMean.close()
        f_Users_Month_Key_EMF_OnMedian.close()

        print Month, '所有用户的RLV统计完毕...\n'
        for i in range(5):
            print 'mean:', i, CERT52_Users_RLV_OnMean[i], '\n'
            print 'median:', i, CERT52_Users_RLV_OnMedian[i], '\n'
        f_CERT52_Month_RLV_Mean = open(Dst_Dir + '\\' + Month + '\\' + Month + '_Users_LC_EmailFeats_OnMean.csv', 'w')
        f_CERT52_Month_RLV_Median = open(Dst_Dir + '\\' + Month + '\\' + Month + '_Users_LC_EmailFeats_OnMedian.csv', 'w')

        for line in sorted(CERT52_Users_RLV_OnMean, key=lambda t:t[1], reverse=True):
            for ele in line:
                f_CERT52_Month_RLV_Mean.write(str(ele))
                f_CERT52_Month_RLV_Mean.write(',')
            f_CERT52_Month_RLV_Mean.write('\n')
        f_CERT52_Month_RLV_Mean.close()

        for line in sorted(CERT52_Users_RLV_OnMedian, key=lambda t:t[1], reverse=True):
            for ele in line:
                f_CERT52_Month_RLV_Median.write(str(ele))
                f_CERT52_Month_RLV_Median.write(',')
            f_CERT52_Month_RLV_Median.write('\n')
        f_CERT52_Month_RLV_Median.close()

