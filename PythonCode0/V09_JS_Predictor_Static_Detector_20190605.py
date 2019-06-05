# coding:utf-8

'''
版本说明：
一个提供了验证集的自动化CPB Static Detector
1. CPB_FEATSlow训练OCSVM；
2. CPB_FEATSleave中20%用于验证，80%用于测试（按比例选择）
'''

# 说明，出于对比实验的需要，本部分主要针对中高CPB来进行检测，即OCSVM测试集包括
# 1. Leave Users
# 2. KMeans未选中的在职用户

# 为了节省后续分析的代码量，这里我们还是来按照面向对象来写

# 主要过程：
# 基于26JS的CPB特征分析
# 1. 先按照是否在职离职将用户区分为[-1]与[+1]
# 2. 而后对于[-1]用户基于minmax后的JS特征进行自动KMeans；
# 3. 得到最好的K与群簇结果，并按照已有公式计算定性高低，筛选出定性高的用户；
# 4. 利用筛选的群簇用户训练OCSVM，并将排除的[-1]用户与[+1]用户一起作为测试集，进行测试输出高危用户集合；
# 5. 检查CERT5.2中三类Insiders的Recall与整体误报率FPR；

import os,sys
import random
import sklearn.preprocessing as skp
import sklearn.decomposition as skd
import copy
import numpy as np
import math

import V09_KMeans_Module
# import V09_KMeans_OCSVM_CLF_01
from sklearn import svm

# 一个根据预测与真实标签计算Recall/FPR/Cnt_P/Cnt_P_Ratio的小程序
def Cal_Messures(gt_lables, y_pred):
    recall = 0.0
    fpr = 0.0
    cnt_p = 0.0
    cnt_n = 0.0
    fn = 0.0
    tn = 0.0
    cnt_c_p = 0.0
    cnt_recall = 0.0
    cnt_fp = 0.0
    # [+1]为想要的离职用户
    recall_index = []
    tp_index = []
    fp_index = []
    i = 0
    while i < len(y_pred):
        if gt_lables[i] == 1: # 真实的[+1]
            cnt_p += 1
            tp_index.append(i) # 验证集中的索引，其所指为原始用户索引
            if y_pred[i] == 1:
                recall += 1.0
                recall_index.append(i)
                cnt_c_p += 1
                i += 1
            else:
                fn += 1
                i += 1
        else:
            cnt_n += 1
            if y_pred[i] == 1:
                cnt_fp += 1
                fp_index.append(i)
                cnt_c_p += 1
                i += 1
            else:
                tn += 1
                i += 1
    # cnt_c_p: 分类器预测为P的个数
    # cnt_p: 真实数据中P的个数
    # cnt_n: 真实数据中N的个数
    cnt_test_n = len(y_pred) - 69
    return recall, recall / cnt_p, cnt_fp, cnt_fp / 1899.0, cnt_fp / cnt_n, tp_index, recall_index, fp_index

def random_choice(src_data, ratio):
    len_max = int(float(len(src_data)) * ratio)
    print 'choose ', len_max, ' from train_set to test set...\n'
    test_index = []
    i = 0
    while i < len_max:
        random_index = random.randint(0, len(src_data) - 1) # randint(a,b)--> a<=x<=b is close
        # print 'random_index is', random_index, '\n'
        if src_data[random_index] not in test_index:
            test_index.append(src_data[random_index])
            i += 1
            continue
        else:
            continue
    return test_index

def Cal_Center_CPB(center):
    # CPB-I,CPB-O,
    # JS_Score,
    # Team_CPB-I-mean,Team_CPB-O-mean,Users-less-mean-A,Users-less-mean-A and C,Users-less-mean-C,Users-High-mean-N,Team_CPB-I-median,Team_CPB-O-median,leader-CPB-I,leader-CPB-O,
    # dis_ocean,avg_dis_ocean,dis_os,avg_dis_os,email_ratio,cnt_send/recv,cnt_s/r_size,cnt_s/r_attach,cnt_s/r_days,cnt_email_days,
    # cnt_late_days,cnt_early_days,month_work_days,
    # early_ratio, late_ratio
    print '要计算CPB的center is ', center, '\n'
    cpb_score = center[0] + center[1]
    js_score = center[2]
    # 3:12  [3:13]
    team_cpb_score = np.sum(center[3:13])
    # 13:26  [13:27]
    lce_cpb_score = np.sum(center[13:26]) # need cut off email_days in 02 version
    led_cpb_score = np.sum(center[26:28])
    #led_cpb_score = np.sum(center[30:32])
    #user_cpb = led_cpb_score
    user_cpb = cpb_score + math.log(math.e - js_score + team_cpb_score + lce_cpb_score, math.e) + led_cpb_score
    return user_cpb

def Cal_Cluster_CPB(kmeans_atf_lst, kmeans_led_lst, kmeans_cluster_minmax):
    # 用户自身的CPB倾向分数
    # 用户自身的JS + 用户工作环境CPB影响 + 用户离职用户联系影响
    # 用户的缺勤表现
    # 使用群簇的中心计算
    cluster_centers = []
    for cls in kmeans_cluster_minmax:
        center_mean = np.mean(cls, axis=0)
        center_median = np.median(cls, axis=0)
        cls_center = []
        cls_center.append(center_mean)
        cls_center.append(center_median)
        cluster_centers.append(cls_center)
    print 'KMeans群簇中心均值、中位数计算完毕:\n'
    for centers in cluster_centers:
        print 'cls mean:', centers[0], 'cls median:', centers[1], '\n'
    # sys.exit() 2个验证通过
    # 开始计算，最后的[-2]与[-1]是两个缺勤比例
    cls_no = 0
    cluster_centers_cpbs = []
    print 'Bug for cluster_centers: ', len(cluster_centers), cluster_centers, '\n'
    # sys.exit()
    cluster_cpbs = []
    for centers in cluster_centers:
        if cls_no > 1:
            break
        print '计算群簇编号：', cls_no, '\n'
        print 'centers is ', centers[0], '\n', centers[1], '\n'
        center_tmp = []
        center_tmp.append(Cal_Center_CPB(centers[0]))
        # sys.exit()
        center_tmp.append(Cal_Center_CPB(centers[1]))
        cluster_cpbs.append(center_tmp)
        cls_no += 1
    print '计算后的中心CPB数值为：\n'
    i = 0
    while i < len(kmeans_cluster_minmax):
        print i, cluster_cpbs[i], '\n'
        i += 1
    return cluster_centers


class KMeans_OCSVM_Predictor():
    def __init__(self, dst_dir):
        self.Dst_Dir = dst_dir
        self.Analyze_Path = self.Dst_Dir + '\\' + 'KMeans_OCSVM_Insiders_Predictor'
        # 初始化JS特征
        f_JS = open(self.Analyze_Path + '\\' + 'CERT5.2-200912-New-26JS-0.9.csv', 'r')
        # f_JS = open(self.Analyze_Path + '\\' + 'CERT6.2-2010-07-New-25JS.csv', 'r')
        f_JS_lst = f_JS.readlines()
        self.JS_lst = []
        self.CERT52_Users_JSOrder = []
        for line_js in f_JS_lst:
            line_lst = line_js.strip('\n').strip(',').split(',')
            if line_lst[0] == 'user_id':
                continue
            self.CERT52_Users_JSOrder.append(line_lst[0])
            js_tmp = []
            # js_tmp中不包含用户字段
            for ele in line_lst[1:]:
                js_tmp.append(float(ele))
            self.JS_lst.append(js_tmp)
        print 'JS_lst 初始化完毕..\n'
        '''
        add codes to cut off the email_days in next ATF-02 version and get
        ATF-03 version
        '''
        f_ATF = open(self.Analyze_Path + '\\' + 'CERT5.2_Leave_Static_CPB_ATF-02.csv', 'r')
        f_atf_03 = open(self.Analyze_Path + '\\' + 'CERT5.2_Leave_Static_CPB_ATF-03.csv', 'w')
        f_ATF_lst = f_ATF.readlines()
        self.ATF_lst = []
        self.CERT52_Users_ATFOrder = []
        self.Length_ATF_Feat = 0
        for line_atf in f_ATF_lst:
            line_lst = line_atf.strip('\n').strip(',').split(',')
            if line_lst[0] == 'user_id':
                del line_lst[23]
                for ele in line_lst:
                    f_atf_03.write(ele + ',')
                f_atf_03.write('\n')
                continue
            del line_lst[27]
            for ele in line_lst:
                f_atf_03.write(ele + ',')
            f_atf_03.write('\n')
            self.CERT52_Users_ATFOrder.append(line_lst[0])
            atf_tmp = []
            # js_tmp中不包含用户字段
            for ele in line_lst[1:]:
                atf_tmp.append(float(ele))
            self.ATF_lst.append(atf_tmp)
            if self.Length_ATF_Feat == 0:
                self.Length_ATF_Feat = len(line_lst[1:])
            else:
                if len(line_lst[1:]) > self.Length_ATF_Feat:
                    print 'Abnormal Length of ATF Feat: ', len(line_lst[1:]), line_lst[0], line_lst[1:], '\n'
        self.ATF_lst = skp.MinMaxScaler().fit_transform(self.ATF_lst)
        f_atf_03.close()
        print 'ATF_lst 初始化完毕..\n'
        # sys.exit()
        # 所有初始ATF特征均标准
        # 初始化Leave Users
        self.Leave_Users = []
        f_leave = open(self.Dst_Dir + '\\' + 'CERT5.2-Leave-Users_OnDays_0.6.csv', 'r')
        f_leave_lst = f_leave.readlines()
        for line_lv in f_leave_lst:
            line_lst = line_lv.strip('\n').strip(',').split(',')
            if len(line_lst) < 2:
                continue
            self.Leave_Users.append(line_lst[0])
        print 'Leave Users 初始化完毕..\n'
        # 初始化Insiders列表
        # insider, leave_month
        f_insider_1 = open(self.Dst_Dir + '\\' + 'Insiders-1_Leave.csv', 'r')
        f_insider_2 = open(self.Dst_Dir + '\\' + 'Insiders-2_Leave.csv', 'r')
        f_insider_3 = open(self.Dst_Dir + '\\' + 'Insiders-3_Leave.csv', 'r')
        # Extract_Lines函数返回的是特征数值，不包含用户名
        self.Insiders_1 = []
        self.Insiders_2 = []
        self.Insiders_3 = []
        for line in f_insider_1.readlines():
            line_lst = line.strip('\n').strip(',').split(',')
            #insider_tmp = []
            #insider_tmp.append(line_lst[0])
            #insider_tmp.append(line_lst[1])
            self.Insiders_1.append(line_lst[0])
        f_insider_1.close()

        for line in f_insider_2.readlines():
            line_lst = line.strip('\n').strip(',').split(',')
            #insider_tmp = []
            #insider_tmp.append(line_lst[0])
            #insider_tmp.append(line_lst[1])
            self.Insiders_2.append(line_lst[0])
        f_insider_2.close()

        for line in f_insider_3.readlines():
            line_lst = line.strip('\n').strip(',').split(',')
            #insider_tmp = []
            #insider_tmp.append(line_lst[0])
            #insider_tmp.append(line_lst[1])
            self.Insiders_3.append(line_lst[0])
        f_insider_3.close()

        print self.Insiders_1, '\n'
        print 'CERT5.2 Insiders1/2/3列表提取完毕..\n'

        print 'KMeans+OCSVM预测器数据初始化完毕..\n\n'

    def Auto_KMeans(self):
        print '新版本直接使用ATF-03进行分析即可..\n'
        # 依据在职[-1]与离职[+1]将原始用户重新分组，其中的[-1]用户用于接下来的KMeans聚类
        # 分组操作全部使用原始JS/ATF的特征进行，在真正分析的前一刻组装成数值feat
        self.KMeans_Index_JS = []
        self.KMeans_Index_ATF = []
        i = 0
        while i < len(self.CERT52_Users_JSOrder):
            if self.CERT52_Users_JSOrder[i] not in self.Leave_Users:
                self.KMeans_Index_JS.append(i)
                i += 1
            else:
                i += 1
                continue
        i = 0
        while i < len(self.CERT52_Users_ATFOrder):
            if self.CERT52_Users_ATFOrder[i] not in self.Leave_Users:
                self.KMeans_Index_ATF.append(i)
                i += 1
            else:
                i += 1
                continue
        print 'CERT5.2中去除离职用户还有：', len(self.KMeans_Index_ATF), '\t', \
        'CERT5.2中共有离职用户：', len(self.Leave_Users), '\n'
        # sys.exit()
        print '排除掉离职用户的剩余CERT5.2用户的索引为：\n'
        #for i in range(10):
        #    print i, self.CERT52_Users_JSOrder[self.KMeans_Index_JS[i]], '\n'
        print len(self.ATF_lst), '\n'
        for i in range(10):
            print i, self.CERT52_Users_ATFOrder[self.KMeans_Index_ATF[i]], '\n'


        print '开始映射成KMeans的用户满意度特征..\n'
        self.KMeans_JS_Feats = []
        self.KMeans_ATF_Feats = []
        #for index in self.KMeans_Index_JS:
        #    self.KMeans_JS_Feats.append(self.JS_lst[index])
        '''
        不再使用JS拼装，直接用ATF！！！
        '''
        for index in self.KMeans_Index_ATF:
            self.KMeans_ATF_Feats.append(self.ATF_lst[index])
        # 开始自动选择合适的K值进行KMeans聚类，并返回最佳的K值和对应的群簇标志
        print 'Bug for ATF:\n'
        print len(self.KMeans_ATF_Feats), len(self.KMeans_Index_ATF), '\n'
        for i in range(5):
            print i, self.KMeans_ATF_Feats[i], '\n'
        self.K, self.SC, self.K_Pred = V09_KMeans_Module.Auto_K_Choice(self.KMeans_ATF_Feats, 10)
        print '针对JS_lst的最佳自动K值为[2:10] ', self.K, ': ', self.SC, '\n'
        print '群簇标签示例为：', self.K_Pred[:5], '\n'
        # 这里都是默认聚成了两个群簇..
        # 试着将KMeans聚类的结果保存，以用于重新组成OCSVM的训练集与测试集
        # 先保存JS的聚类结果
        f_kmeans_pred = open(self.Analyze_Path + '\\' + 'CPB_ATF_KMeans_Pred.csv', 'w')
        self.KMeans_Clusters = [[] for i in range(self.K)] # 继续保存用户索引
        j = 0
        while j < len(self.KMeans_Index_ATF):
            user_index = self.KMeans_Index_ATF[j]
            f_kmeans_pred.write(self.CERT52_Users_ATFOrder[user_index] + ',')
            f_kmeans_pred.write(str(self.K_Pred[j]) + '\n')
            self.KMeans_Clusters[self.K_Pred[j]].append(j)
            j += 1
        f_kmeans_pred.close()
        print 'JS/ATF KMeans结果写入完毕..\n'
        print 'JS/ATF各个KMeans群簇用户数量：\n'
        for i in range(self.K):
            print i, len(self.KMeans_Clusters[i]), '\n'

        ##
        ##
        # 插入一个计算群簇中心值的CPB倾向的计算公式
        # 依据self.KMeans_Clusters中的索引数据，构建对应的群簇Feats
        # 提取KMeans部分用户最后的LED特征，转换成迟到比例与早退比例
        KMeans_LED_Ratios = []
        for line in self.KMeans_ATF_Feats:
            led_tmp = []
            led_tmp.append(float(line[-3]) / float(line[-1]))
            led_tmp.append(float(line[-2]) / float(line[-1]))
            KMeans_LED_Ratios.append(led_tmp)
        # 被选择KMeans的用户追加了缺勤率，而未参加KMeans的用户却没有，因此需要最后训练OCSVM时不需要缺勤率，去掉即可
        # 即若长度=30跳过，若=32去掉最后两个即可
        KMeans_ATF_MinMax_lst = copy.copy(self.KMeans_ATF_Feats)
        i = 0
        while i < len(KMeans_ATF_MinMax_lst):
            list(KMeans_ATF_MinMax_lst[i]).extend(KMeans_LED_Ratios[i])
            print 'KMeans_ATF_MinMax_lst', ':', i, 'is ', KMeans_ATF_MinMax_lst[i], '\n'
            i += 1
        #sys.exit()
        KMeans_ATF_MinMax_lst = skp.MinMaxScaler().fit_transform(KMeans_ATF_MinMax_lst)
        KMeans_Cluster_MinMax = [[] for i in range(self.K)]
        k = 0
        while k < self.K:
            for index_0 in self.KMeans_Clusters[k]:
                KMeans_Cluster_MinMax[k].append(KMeans_ATF_MinMax_lst[index_0])
            k += 1
        for i in range(self.K):
            print i, len(KMeans_Cluster_MinMax[i]), '\n'
        #print KMeans_Cluster_MinMax[0][1], '\n'
        #print '1 Cluster: ', KMeans_Cluster_MinMax[1][:10], '\n'
        # 基于KMeans_Cluster_MinMax + KMeans_LED_Ratios计算群簇的CPB公式

        cluster_centers = Cal_Cluster_CPB(self.KMeans_ATF_Feats, KMeans_LED_Ratios, KMeans_Cluster_MinMax)
        # sys.exit()




        print '自动KMeans聚类完成..\n'

    def OCSVM_Predictor(self):
        # 采用上一步聚类中的多数类作为训练OCSVM的依据；
        # 多数类训练OCSVM，因为其中心CPB较低
        # 少数类用于预测
        # 先简单实用最多的群簇作为训练
        t_cls_index = 0
        max_cls = 0
        i = 0
        while i < len(self.KMeans_Clusters):
            if len(self.KMeans_Clusters[i]) > max_cls:
                t_cls_index = i
                max_cls = len(self.KMeans_Clusters[i])
                i += 1
                continue
            else:
                i += 1
                continue
        print '选择用于训练的群簇标号为: ', t_cls_index, max_cls, '\n'

        '''
        # 在分隔训练集与测试集前先做PCA
        ATF_Lengths = []
        for line in self.ATF_lst[:10]:
            ATF_Lengths.append(len(line))
            print len(line), line, '\n'
        for line in self.ATF_lst:
            if len(line) > 30:
                line.remove(line[-1])
                line.remove(line[-1])
            else:
                continue
        print 'set of self.ATF_lst Lengths:', set(ATF_Lengths), '\n'
        '''
        self.ATF_PCA_lst = skd.PCA(n_components=1).fit_transform(self.ATF_lst)
        # scale
        self.ATF_PCA_Scale_lst = copy.copy(self.ATF_PCA_lst)
        self.ATF_PCA_Scale_lst = skp.scale(self.ATF_PCA_Scale_lst)

        '''
        在这里添加对于测试集的抽取验证集的工作
        1. 确定测试集中的正常用户索引与攻击者索引；
        2. 分别抽取20%组合成为验证集；
        3. 剩余作为测试集用来输出最后结果
        '''
        self.users_in_leave_index = []
        self.attackers_in_leave_index = []
        i = 0
        while i < len(self.Leave_Users):
            if self.Leave_Users[i] in self.Insiders_1 or \
               self.Leave_Users[i] in self.Insiders_2 or \
               self.Leave_Users[i] in self.Insiders_3:
                self.attackers_in_leave_index.append(self.CERT52_Users_ATFOrder.index(self.Leave_Users[i]))
                i += 1
                continue
            else:
                self.users_in_leave_index.append(self.CERT52_Users_ATFOrder.index(self.Leave_Users[i]))
                i += 1
                continue
        self.validation_index = []
        self.validation_users_index = random_choice(self.users_in_leave_index, 0.2)
        self.validation_attackers_index = random_choice(self.attackers_in_leave_index, 0.2)
        self.validation_index.extend(self.validation_users_index)
        self.validation_index.extend(self.validation_attackers_index)
        print 'Validation Set Extract Ok: ', len(self.validation_index), '\n'
        self.validation_feats = []
        self.validation_labels = []
        # sys.exit()  33 and 13 extracted from 169 and 69 = 238 leave users
        self.Train_Feats = []
        for index_t in self.KMeans_Clusters[t_cls_index]:
            self.Train_Feats.append(self.ATF_PCA_Scale_lst[index_t])
        self.Test_Feats = []
        self.Test_Index = []
        self.KMeans_Clusters.remove(self.KMeans_Clusters[t_cls_index])
        i = 0
        while i < len(self.CERT52_Users_ATFOrder):
            if self.CERT52_Users_ATFOrder[i] in self.Leave_Users:
                if i not in self.validation_index:
                    self.Test_Index.append(i)
                    self.Test_Feats.append(self.ATF_PCA_Scale_lst[i])
                    i += 1
                    continue
                else:
                    self.validation_feats.append(self.ATF_PCA_Scale_lst[i])
                    i += 1
                    continue
            else:
                i += 1
            ''' # 检测CPB_FEATSleave+CPB_FEATShigh时使用
            else:
                for cls in self.KMeans_Clusters:
                    if i in cls:
                        self.Test_Index.append(i)
                        self.Test_Feats.append(self.ATF_PCA_Scale_lst[i])
                        i += 1
                    else:
                        i += 1
            '''
        # 生成测试集的标签（以Insiders_1_2_3为标准）
        self.Labels = []
        self.Insiders = []
        self.Test_Insiders_1_Index = []
        self.Test_Insiders_2_Index = []
        self.Test_Insiders_3_Index = []
        j = 0
        while j < len(self.Test_Index):
            if self.CERT52_Users_ATFOrder[self.Test_Index[j]] in self.Insiders_1:
                self.Test_Insiders_1_Index.append(j)
                j += 1
                continue
            if self.CERT52_Users_ATFOrder[self.Test_Index[j]] in self.Insiders_2:
                self.Test_Insiders_2_Index.append(j)
                j += 1
                continue
            if self.CERT52_Users_ATFOrder[self.Test_Index[j]] in self.Insiders_3:
                self.Test_Insiders_3_Index.append(j)
                j += 1
                continue
            else:
                j += 1
                continue
        self.Insiders.extend(self.Insiders_1)
        self.Insiders.extend(self.Insiders_2)
        self.Insiders.extend(self.Insiders_3)
        for v_index in self.Test_Index:
            if self.CERT52_Users_ATFOrder[v_index] in self.Insiders:
                self.Labels.append(1)
            else:
                self.Labels.append(-1)
        for v_index in self.validation_index:
            if self.CERT52_Users_ATFOrder[v_index] in self.Insiders:
                self.validation_labels.append(1)
            else:
                self.validation_labels.append(-1)
        print 'Validation Set is ', self.validation_labels.count(1), self.validation_labels.count(-1), '\n'
        print 'TestSet is ', self.Labels.count(1), self.Labels.count(-1), '\n'
        # sys.exit()
        # 开始训练OCSVM
        nu_lst = range(1, 1000, 1)
        mix_lst = range(5,6,1)

        #
        # 对于ATF_10D而言不需要再做PCA了，直接scale就好
        #
        pca_k = len(self.Train_Feats[0])
        print 'PCA后维度为： ', pca_k, '\n'

        # All_Feats_pca_scale = skp.scale(All_Feats)
        # 进入到OCSVM最优参数计算
        # nu； [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]
        ocsvm_obj_lst = []
        ocsvm_count = 1.0
        for mix in mix_lst:
            miu = mix / 1000.0
            for nu_0 in nu_lst:
                nu_0 = nu_0 / 1000.0
                clf = svm.OneClassSVM(kernel='rbf', tol=0.01, nu=nu_0, gamma='auto', random_state=10)
                clf.fit(self.Train_Feats)
                pred = clf.predict(self.validation_feats)
                print '正在测试第 ', ocsvm_count, '次', '\n'
                ocsvm_count += 1
                # return cnt_recall, recall / cnt_p, cnt_fp, fpr / cnt_n, cnt_c_p / (cnt_n + cnt_p)
                # print 'Bug for Before Cal_Messure:', self.Labels[k], '\n'
                # print 'Bug for Before Cal_Messure:', pred, '\n'
                # print self.Labels[k][0], pred[0], self.Labels[k][0] == pred[0], '\n'
                # sys.exit()
                cnt_recall, recall, cnt_fp, fpr_total, fpr_leave, tp_index, recall_index, fp_index = Cal_Messures(self.validation_labels,
                                                                                                         pred)
                # print 'Bug for after Cal_Messure, tp_index:', tp_index, '\n'
                # print 'Bug for after Cal_Messure, recall_index:', recall_index, '\n'
                # sys.exit()
                # 上述验证通过
                #if fpr_total > 0.5:
                #    continue
                #miu = 1.0
                # m_score = miu * recall - (1 - miu) * fpr_leave
                #if recall < 0.85 or recall > 0.9:
                #    continue
                #if fpr_leave > 0.8:
                #    continue
                # m_score = recall * miu - (1 - miu) * fpr_leave
                m_score = recall / math.exp(fpr_leave)
                # m_score = math.exp(recall) / math.log(math.e + fpr_leave, math.e)
                # m_score = math.log(math.e + recall, math.e) / math.exp(fpr_leave)
                # m_score = recall / math.log(math.e + fpr_leave, math.e)
                # m_score = recall / (1 + math.exp(fpr_leave))



                ocsvm_tmp = []
                ocsvm_tmp.append(nu_0)
                ocsvm_tmp.append(miu)
                ocsvm_tmp.append(m_score)
                ocsvm_tmp.append(recall)
                ocsvm_tmp.append(fpr_total)
                ocsvm_tmp.append(cnt_fp)
                ocsvm_tmp.append(fpr_leave)
                ocsvm_tmp.append(clf)
                # 这里应该补充三类Insiders的召回率
                recall_1 = 0.0
                recall_2 = 0.0
                recall_3 = 0.0
                self.Val_Insiders_1_Index = []
                self.Val_Insiders_2_Index = []
                self.Val_Insiders_3_Index = []
                for v_index in self.validation_index:
                    if self.CERT52_Users_ATFOrder[v_index] in self.Insiders_1:
                        self.Val_Insiders_1_Index.append(self.validation_index.index(v_index))
                for v_index in self.validation_index:
                    if self.CERT52_Users_ATFOrder[v_index] in self.Insiders_2:
                        self.Val_Insiders_2_Index.append(self.validation_index.index(v_index))
                for v_index in self.validation_index:
                    if self.CERT52_Users_ATFOrder[v_index] in self.Insiders_3:
                        self.Val_Insiders_3_Index.append(self.validation_index.index(v_index))
                for index_i in self.Val_Insiders_1_Index:
                    if pred[index_i] == 1:
                        recall_1 += 1
                for index_i in self.Val_Insiders_2_Index:
                    if pred[index_i] == 1:
                        recall_2 += 1
                for index_i in self.Val_Insiders_3_Index:
                    if pred[index_i] == 1:
                        recall_3 += 1
                ocsvm_tmp.append(recall_1 / len(self.Val_Insiders_1_Index))
                ocsvm_tmp.append(recall_2 / len(self.Val_Insiders_2_Index))
                ocsvm_tmp.append(recall_3 / len(self.Val_Insiders_3_Index))
                ocsvm_tmp.append(pred)
                #ocsvm_tmp.append(tp_index)
                #ocsvm_tmp.append(recall_index)
                #ocsvm_tmp.append(fp_index)
                ocsvm_obj_lst.append(ocsvm_tmp)
        print 'nu参数遍历计算完成..\n'
        # 输出最高m_score
        ocsvm_obj_sort_lst = sorted(ocsvm_obj_lst, key=lambda t: t[2], reverse=True)
        # print 'Bug for:', '\n'
        # for line in ocsvm_obj_sort_lst:
        #    print line[2], line, '\n'
        # sys.exit()
        for i in range(3):
            print i, ocsvm_obj_sort_lst[i], '\n'
        # 将同步输出DF函数结果，并重新排序：
        self.Risk_Users = []
        self.Test_Pred = ocsvm_obj_sort_lst[0][-5].predict(self.Test_Feats)
        cnt_recall, recall, cnt_fp, fpr_total, fpr_leave, tp_index, recall_index, fp_index = \
                                    Cal_Messures(self.Labels, self.Test_Pred)
        print 'Recall is ', recall, '\n'
        print 'FPR total is ', fpr_total, '\n'
        print 'Count FPR is ', cnt_fp, '\n'
        print 'FPR leave is ', fpr_leave, '\n'
        recall_1 = 0.0
        recall_2 = 0.0
        recall_3 = 0.0
        self.Test_Insiders_1_Index = []
        self.Test_Insiders_2_Index = []
        self.Test_Insiders_3_Index = []
        for v_index in self.Test_Index:
            if self.CERT52_Users_ATFOrder[v_index] in self.Insiders_1:
                self.Test_Insiders_1_Index.append(self.Test_Index.index(v_index))
        for v_index in self.Test_Index:
            if self.CERT52_Users_ATFOrder[v_index] in self.Insiders_2:
                self.Test_Insiders_2_Index.append(self.Test_Index.index(v_index))
        for v_index in self.Test_Index:
            if self.CERT52_Users_ATFOrder[v_index] in self.Insiders_3:
                self.Test_Insiders_3_Index.append(self.Test_Index.index(v_index))
        for t_index in self.Test_Index:
            if self.CERT52_Users_ATFOrder[t_index] in self.Insiders_1 and \
                    self.Test_Pred[self.Test_Index.index(t_index)] == 1:
                recall_1 += 1
            if self.CERT52_Users_ATFOrder[t_index] in self.Insiders_2 and \
                    self.Test_Pred[self.Test_Index.index(t_index)] == 1:
                recall_2 += 1
            if self.CERT52_Users_ATFOrder[t_index] in self.Insiders_3 and \
                    self.Test_Pred[self.Test_Index.index(t_index)] == 1:
                recall_3 += 1
            else:
                continue
        recall = recall_1 + recall_2 + recall_3
        recall = recall / (len(self.Test_Insiders_1_Index)
                           + len(self.Test_Insiders_2_Index)
                           + len(self.Test_Insiders_3_Index))
        print 'Recall is ', recall, '\n'
        print 'Recall for 1 is ', recall_1 / len(self.Test_Insiders_1_Index), '\n'
        print 'Recall for 2 is ', recall_2 / len(self.Test_Insiders_2_Index), '\n'
        print 'Recall for 3 is ', recall_3 / len(self.Test_Insiders_3_Index), '\n'

print '..<<基于原始26维度JS特征的CERT5.2静态高危用户预测实验>>..\n\n'
Dst_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.9'
# 初始化对象
Predictor_obj = KMeans_OCSVM_Predictor(Dst_Dir)
Predictor_obj.Auto_KMeans()
Predictor_obj.OCSVM_Predictor()

