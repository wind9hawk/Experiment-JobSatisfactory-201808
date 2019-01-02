# coding:utf-8
# ATF_Cross5_OCSVM_Vote_Predictor
# 本文件为上述基于攻击倾向特征（ATF）的5折交叉验证多OCSVM投票预测对象类
# 本类与原始模块预测器的区别在于：
# old: 以在职[-1]与离职[+1]作为标签
# new: 以普通用户[-1]与Insiders[+1]作为标签；

# 需要在初始化阶段导入Insiders_1-4的用户列表，且一直存在

# 可能导入的库
import os,sys
import sklearn.preprocessing as skp
import sklearn.decomposition as skd
import numpy as np
import random
from sklearn import svm
import numpy as np




def Extract_Lines(f_path):
    f = open(f_path, 'r')
    f_lst = f.readlines()
    f.close()
    feats_lst = []
    for line in f_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        if line_lst[0] == 'user_id':
            continue
        feat_tmp = []
        if len(line_lst) > 2:
            for ele in line_lst[1:]:
                feat_tmp.append(float(ele))
            feats_lst.append(feat_tmp)
        # 注意， 1与[1]是不同的，需要计算区分
        else:
            if '-' not in line_lst[1]:
                feats_lst.append(float(line_lst[1]))
            else:
                feats_lst.append(line_lst[1])

    return feats_lst

# 定义一个可以有Crt_Users与Insiders计算出依据Insiders的Labels列表
def Build_Insider_Labels(cert_users, month, insiders_1, insiders_2, insiders_3):
    gt_lst = [-1 for i in range(len(cert_users))]
    for insider in insiders_1:
        # 2010-01-01
        if insider[1][:7] == month:
            # 该月离职的insider，标识为1
            index_i = cert_users.index(insider[0])
            gt_lst[index_i] = 1
            continue
        else:
            continue
    for insider in insiders_2:
        # 2010-01-01
        if insider[1][:7] == month:
            # 该月离职的insider，标识为1
            index_i = cert_users.index(insider[0])
            gt_lst[index_i] = 1
            continue
        else:
            continue
    for insider in insiders_3:
        # 2010-01-01
        if insider[1][:7] == month:
            # 该月离职的insider，标识为1
            index_i = cert_users.index(insider[0])
            gt_lst[index_i] = 1
            continue
        else:
            continue
    return gt_lst

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
                fpr += 1
                fp_index.append(i)
                cnt_c_p += 1
                i += 1
            else:
                tn += 1
                i += 1
    # cnt_c_p: 分类器预测为P的个数
    # cnt_p: 真实数据中P的个数
    # cnt_n: 真实数据中N的个数
    return recall, recall / cnt_p, cnt_fp, fpr / cnt_n, cnt_c_p / (cnt_n + cnt_p), tp_index, recall_index, fp_index

# 类定义
class ATF_Cross5_OCSVM_Vote_Predictor():
    def __init__(self, dst_dir, month, next_month):
        # month: 2010-02:2011-04
        # next_month: 2010-03:2011-05
        self.Dst_Dir = dst_dir
        self.Month = month
        # self.ATF_Path = self.Dst_Dir + '\\' + self.Month + '\\' + 'CERT5.2_ATF_0.1.csv'
        self.ATF_Path = self.Dst_Dir + '\\' + self.Month + '\\' + 'CERT5.2_LaidOff_ATF_0.1.csv'
        # self.ATF_Path = self.Dst_Dir + '\\' + self.Month + '\\' + 'CERT5.2_ATF_10D.csv'
        self.GT_Path = self.Dst_Dir + '\\' + self.Month + '\\' + self.Month + '_CERT5.2_Users_GroundTruth.csv_v01.csv'
        self.Next_Month = next_month
        self.Next_ATF_Path = self.Dst_Dir + '\\' + self.Next_Month + '\\' + 'CERT5.2_LaidOff_ATF_0.1.csv'
        # self.Next_ATF_Path = self.Dst_Dir + '\\' + self.Next_Month + '\\' + 'CERT5.2_ATF_10D.csv'
        self.Next_GT_Path = self.Dst_Dir + '\\' + self.Next_Month + '\\' + self.Next_Month + '_CERT5.2_Users_GroundTruth.csv_v01.csv'
        self.CERT52_Crt_Users = [] # 当月在职的CERT5.2用户
        f_ATF = open(self.ATF_Path, 'r')
        f_ATF_lst = f_ATF.readlines()
        f_ATF.close()
        f_GT = open(self.GT_Path, 'r')
        f_GT_lst = f_GT.readlines()
        f_GT.close()
        for line_gt in f_GT_lst:
            line_lst = line_gt.strip('\n').strip(',').split(',')
            if line_lst[0] == 'user_id':
                continue
            self.CERT52_Crt_Users.append(line_lst[0])
        # 再保存下个月的用户列表
        self.Next_CERT52_Crt_Users = []
        f_Next_GT = open(self.Next_GT_Path, 'r')
        f_Next_GT_lst = f_Next_GT.readlines()
        f_Next_GT.close()
        for line_gt in f_Next_GT_lst:
            line_lst = line_gt.strip('\n').strip(',').split(',')
            if line_lst[0] == 'user_id':
                continue
            self.Next_CERT52_Crt_Users.append(line_lst[0])

        self.ATF_lst = Extract_Lines(self.ATF_Path)
        self.GT_lst = Extract_Lines(self.GT_Path)
        self.Next_ATF_lst = Extract_Lines(self.Next_ATF_Path)
        self.Next_GT_lst = Extract_Lines(self.Next_GT_Path)

        # 新方法以Insiders为标识，而不再是以在职离职作为标识
        # 出于处理编程的需要，后续处理过程变量名称不再改变，而是仅修改初始化的用户标签
        # 这里可以假设N月结束时知晓了谁是Insiders；抑或以当月主动离职用户作为标签；（这里仅考虑主动离职的三类Insiders，不考虑第四类）
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
            insider_tmp = []
            insider_tmp.append(line_lst[0])
            insider_tmp.append(line_lst[1])
            self.Insiders_1.append(insider_tmp)
        f_insider_1.close()

        for line in f_insider_2.readlines():
            line_lst = line.strip('\n').strip(',').split(',')
            insider_tmp = []
            insider_tmp.append(line_lst[0])
            insider_tmp.append(line_lst[1])
            self.Insiders_2.append(insider_tmp)
        f_insider_2.close()

        for line in f_insider_3.readlines():
            line_lst = line.strip('\n').strip(',').split(',')
            insider_tmp = []
            insider_tmp.append(line_lst[0])
            insider_tmp.append(line_lst[1])
            self.Insiders_3.append(insider_tmp)
        f_insider_3.close()

        print self.Insiders_1, '\n'


        # 开始以Crt_Users生成当月的Labels
        # 2011-05_CERT5.2_Users_GroundTruth.csv_v01.csv
        f_Insiders_GT = open(self.Dst_Dir + '\\' + self.Month + '\\' + self.Month + '_CERT5.2_Insiders_GroundTruth.csv_v01.csv', 'w')
        # 基于Insiders标签重新标记
        self.GT_lst = Build_Insider_Labels(self.CERT52_Crt_Users, self.Month, self.Insiders_1, self.Insiders_2, self.Insiders_3)
        # print 'New self.GT_lst is ', self.GT_lst[110], '\n'
        i = 0
        while i < len(self.CERT52_Crt_Users):
            f_Insiders_GT.write(self.CERT52_Crt_Users[i] + ',' + str(self.GT_lst[i]) + '\n')
            i += 1
        f_Insiders_GT.close()

        # sys.exit()
        print self.Month, '预测器对象初始化完成..\n\n'

    def __del__(self):
        print self.Month, '预测器对象析构开始..\n\n'
        del self.Month
        del self.Next_Month
        del self.Dst_Dir
        del self.ATF_Path
        del self.GT_Path
        del self.Next_ATF_Path
        del self.Next_GT_Path

        del self.CERT52_Crt_Users
        del self.ATF_lst
        del self.GT_lst
        del self.Next_ATF_lst
        del self.Next_GT_lst

        del self.Insiders_1
        del self.Insiders_2
        del self.Insiders_3

    def Split_Cross5_Index(self):
        # 通过操作索引，将训练集的ATF_Feats的索引号区分为在职的[-1]与离职的[+1]
        # 从所有的[-1]类索引中随机分成基本均等的五个部分
        # 逐个使用其中一个部分+[+1]作为验证集，其余四个部分[-1]作为训练集训练OCSVM
        # 输出五组上述的[训练集：验证集]索引列表对
        # 后续函数将负责由索引映射为实际向量，并进行实际训练

        # 首先计算[-1]与[+1]的索引列表
        self.OnJob_Index = []
        self.OffJob_Index = []
        i = 0
        while i < len(self.GT_lst):
            if self.GT_lst[i] > 0:
                self.OffJob_Index.append(i)
                i += 1
                continue
            else:
                self.OnJob_Index.append(i)
                i += 1
                continue
        print self.Month, '[+1]类用户索引为: ', self.OffJob_Index, '\n'

        # 接下来需要使用随机函数生成五个[Train:Validation]索引对
        Have_Used_Index = []  # 已经生成的索引号
        Cnt_OnJob_Index = len(self.OnJob_Index)
        self.Train_Indexes = [[] for i in range(5)]
        self.Validate_Indexes = [[] for i in range(5)]
        self.Labels = [[] for i in range(5)]
        j = 0
        while j < 5:
            if j != 4:
                # 按照均分构造即可
                k = 0
                while k < Cnt_OnJob_Index / 5:
                    index_t = random.randint(0, Cnt_OnJob_Index - 1)
                    if index_t not in Have_Used_Index:
                        Have_Used_Index.append(index_t)
                        # index_t --> self.OnJob_Index --> ATF/GT index
                        # print Cnt_OnJob_Index, j, index_t, k, Cnt_OnJob_Index / 5, '\n'
                        self.Validate_Indexes[j].append(self.OnJob_Index[index_t])
                        k += 1
                        continue
                    else:
                        continue
                j += 1
            else:
                # j = 4
                k = 0
                cnt_left_index = Cnt_OnJob_Index - len(Have_Used_Index)
                while k < cnt_left_index:
                    index_t = random.randint(0, Cnt_OnJob_Index - 1)
                    if index_t not in Have_Used_Index:
                        Have_Used_Index.append(index_t)
                        # index_t --> Cnt_OnJob_Index --> ATF/GT index
                        self.Validate_Indexes[j].append(self.OnJob_Index[index_t])
                        k += 1
                        continue
                    else:
                        continue
                j += 1
        print self.Month, '初始验证分组为：\n'
        for i in range(5):
            print i, len(self.Validate_Indexes[i]), self.Validate_Indexes[i], '\n'
        # 基于上述初始Validate_Indexex构建Train_Indexes
        # 初始的意思是：仅包含了分组的[-1]数据，还未合并[+1]数据
        # 对于第N个验证集，将除去N以外的其他验证集索引合并为训练集，如此重复5次
        i = 0
        while i < 5:
            for j in range(5):
                if j != i:
                    for ele in self.Validate_Indexes[j]:
                        self.Train_Indexes[i].append(ele)
                    self.Train_Indexes[i].sort()
                else:
                    continue
            i += 1
        # 将[+1]合并到验证分组中
        for i in range(5):
            print self.Validate_Indexes[i], '\n'
            self.Validate_Indexes[i].extend(self.OffJob_Index)
            print self.Validate_Indexes[i], '\n'
            # self.Validate_Indexes[i].sort()
            # 验证通过
        # 生成对应的验证集的Labels
        for i in range(5):
            for ele in self.Validate_Indexes[i]:
                if ele in self.OnJob_Index:
                    self.Labels[i].append(-1)
                if ele in self.OffJob_Index:
                    self.Labels[i].append(+1)
            print 'Lables for ', self.Labels[i], '\n'
            # 验证通过
            # sys.exit()

        print self.Month, '5折训练与验证索引对生成完毕..\n'
        #print 'Train / Validate Index: [0]\n'
        #print self.Train_Indexes[0], '\n'
        #print self.Validate_Indexes[0], '\n'

    def Map_Index2Feat(self):
        self.Train_Feats = [[] for i in range(5)]
        self.Validate_Feats = [[] for i in range(5)]
        for i in range(5):
            for ele in self.Train_Indexes[i]:
                feat_line = self.ATF_lst[ele]
                self.Train_Feats[i].append(feat_line)
            for ele in self.Validate_Indexes[i]:
                feat_line = self.ATF_lst[ele]
                self.Validate_Feats[i].append(feat_line)
        #print '验证Train/Validate Feats [0]: \n'
        #print self.Train_Indexes[0][0], self.Train_Feats[0][0], '\n'
        print self.Validate_Indexes[0][0], self.Labels[0][0], self.Validate_Feats[0][0], '\n'
    # 验证通过
    # # #
    # 截止到上述代码，已经将N月的用户数据依据[-1]与[+1]：
    # 1. 分成了5组[train:validate:labels]

    # 2. 接下来需要依据度量分数训练OCSVM得到最优分类器，然后保存；
    # 3. 使用得到的五个新OCSVM对于N+1月份的数据进行提取分析，并输出预测与GT真实数据比较；

    def Train_5_OCSVMs(self):
        # 基本调用形式
        # clf = OneClassSVM(kernel='rbf', tol=0.01, nu=0.35, gamma='auto')
        # Train_array = np.array(Train_lst)
        # Test_array = np.array(Test_lst)
        # clf.fit(Train_array)
        # pred = clf.predict(Test_array)
        nu_lst = range(5, 105, 5)
        i = 0
        while i < len(nu_lst):
            nu_lst[i] = nu_lst[i] / 100.0
            i += 1
        print nu_lst, '\n'
        self.OCSVM_Obj_lst = []
        # 开始针对五个OCSVM，遍历nu参数
        k = 0
        while k < 5:
            ocsvm_obj_lst = []
            # 先做PCA，然后做scale
            All_Feats = []
            for feat in self.Train_Feats[k]:
                All_Feats.append(feat)
                #All_Feats.append(feat[5:])
            split_index = len(All_Feats)
            for feat in self.Validate_Feats[k]:
                All_Feats.append(feat)
                #All_Feats.append(feat[5:]) # 不分析用户的OCEAN分数，直接从CPB分数开始
            self.n_pca_components = 3
            All_Feats_pca = skd.PCA(self.n_pca_components).fit_transform(All_Feats)
            #
            # 对于ATF_10D而言不需要再做PCA了，直接scale就好
            #
            pca_k = len(All_Feats_pca[0])
            # scale
            All_Feats_pca_scale = skp.scale(All_Feats_pca)
            # All_Feats_pca_scale = skp.scale(All_Feats)
            # 分隔出训练集与验证集
            X_Train = All_Feats_pca_scale[:split_index]
            X_Val = All_Feats_pca_scale[split_index:]
            # 进入到OCSVM最优参数计算
            # nu； [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]
            for nu_0 in nu_lst:
                clf = svm.OneClassSVM(kernel='rbf', tol=0.01, nu=nu_0, gamma='auto')
                clf.fit(X_Train)
                pred = clf.predict(X_Val)
                # return cnt_recall, recall / cnt_p, cnt_fp, fpr / cnt_n, cnt_c_p / (cnt_n + cnt_p)
                #print 'Bug for Before Cal_Messure:', self.Labels[k], '\n'
                #print 'Bug for Before Cal_Messure:', pred, '\n'
                #print self.Labels[k][0], pred[0], self.Labels[k][0] == pred[0], '\n'
                # sys.exit()
                cnt_recall, recall, cnt_fp, fpr, risk_ratio, tp_index, recall_index, fp_index = Cal_Messures(self.Labels[k], pred)
                #print 'Bug for after Cal_Messure, tp_index:', tp_index, '\n'
                #print 'Bug for after Cal_Messure, recall_index:', recall_index, '\n'
                # sys.exit()
                # 上述验证通过
                miu = 0.7
                m_score = miu * recall - (1 - miu) * fpr
                ocsvm_tmp = []
                ocsvm_tmp.append(nu_0)
                ocsvm_tmp.append(miu)
                ocsvm_tmp.append(m_score)
                ocsvm_tmp.append(recall)
                ocsvm_tmp.append(fpr)
                ocsvm_tmp.append(risk_ratio)
                ocsvm_tmp.append(clf)
                ocsvm_tmp.append(tp_index)
                ocsvm_tmp.append(recall_index)
                ocsvm_tmp.append(fp_index)
                ocsvm_obj_lst.append(ocsvm_tmp)
            print k, 'nu参数遍历计算完成..\n'
            # 输出最高m_score
            ocsvm_obj_sort_lst = sorted(ocsvm_obj_lst, key=lambda t: t[2], reverse=True)
            #print 'Bug for:', '\n'
            #for line in ocsvm_obj_sort_lst:
            #    print line[2], line, '\n'
            # sys.exit()
            self.OCSVM_Obj_lst.append(ocsvm_obj_sort_lst[0])
            k += 1
        print self.Month, '五个最优OCSVM依次为：\n'
        for i in range(5):
            print 'No:', i, self.OCSVM_Obj_lst[i], '\n'

        # 考虑输出五个OCSVM的验证结果，其中，主要涵盖recall/tp/fp三类
        # 格式
        # user_id, tp/fp, recall/Null

        print 'Bug for: \n'
        print self.Validate_Indexes[0], '\n'
        print self.Validate_Indexes[0][0], '\n'
        # sys.exit()

        k = 0
        while k < 5:
            tp_set = self.OCSVM_Obj_lst[k][-3]
            recall_set = self.OCSVM_Obj_lst[k][-2]
            fp_set = self.OCSVM_Obj_lst[k][-1]
            print 'tp_set is ', tp_set, '\n'
            print 'fp_set is ', fp_set, '\n'

            # 上述索引为验证集元素索引，其所指内容为ATF中用户索引
            f_ocsvm_rst = open(self.Dst_Dir + '\\' + self.Month + '\\' + self.Month + '_' + str(k) + '_Cross5_OCSVM_Recall.csv', 'w')
            f_ocsvm_rst.write('OCSVM:,')
            f_ocsvm_rst.write(str(self.OCSVM_Obj_lst[k][-4]) + '\n')
            j = 0
            while j < len(self.Validate_Indexes[k]):
                user_index = j
                if user_index in tp_set:
                    # print k, 'validate_set', user_index, '\n'
                    f_ocsvm_rst.write(self.CERT52_Crt_Users[self.Validate_Indexes[k][j]])
                    f_ocsvm_rst.write(',')
                    f_ocsvm_rst.write('True Positive')
                    if user_index in recall_set:
                        f_ocsvm_rst.write(',' + 'Recall' + '\n')
                        j += 1
                    else:
                        f_ocsvm_rst.write('\n')
                        j += 1
                else:
                    if user_index in fp_set:
                        f_ocsvm_rst.write(self.CERT52_Crt_Users[self.Validate_Indexes[k][j]])
                        f_ocsvm_rst.write(',')
                        f_ocsvm_rst.write('False Positive')
                        f_ocsvm_rst.write('\n')
                        j += 1
                    else:
                        j += 1
            f_ocsvm_rst.close()
            print k, 'OCSVM Recall Results Write Done..\n'
            k += 1

    # 执行对下个月用户的预测
    # 基于Insiders标签重新标记
    def Run_Predictor(self):
        self.Next_GT_lst = Build_Insider_Labels(self.Next_CERT52_Crt_Users, self.Next_Month, self.Insiders_1, self.Insiders_2, self.Insiders_3)
        # 先PCA，再scale
        # 五个OCSVM投票决定
        # 投票阈值
        K_Vote = 5
        Next_ATF_pca = skd.PCA(self.n_pca_components).fit_transform(self.Next_ATF_lst)
        # Next_ATF_pca_scale = skp.scale(self.Next_ATF_lst)
        Next_ATF_pca_scale = skp.scale(Next_ATF_pca)
        # 直接用上述数据预测,保存每个用户的预测结果
        self.ATF_Predict_Results = []
        turn = 0 # 分类器编号
        while turn < 5:
            if turn == 0:
                predictor_results = self.OCSVM_Obj_lst[turn][-4].predict(Next_ATF_pca_scale)
                predictor_decision_function = self.OCSVM_Obj_lst[turn][-4].decision_function(Next_ATF_pca_scale)
                i = 0
                while i < len(self.Next_CERT52_Crt_Users):
                    predictor_tmp = []
                    predictor_tmp.append(self.Next_CERT52_Crt_Users[i])
                    predictor_tmp.append(predictor_results[i])
                    # predictor_tmp.append(self.OCSVM_Obj_lst[turn][-4].decision_function(Next_ATF_pca_scale[i]))
                    predictor_tmp.append(predictor_decision_function[i])
                    self.ATF_Predict_Results.append(predictor_tmp)
                    i += 1
                turn += 1
            else:
                predictor_results = self.OCSVM_Obj_lst[turn][-4].predict(Next_ATF_pca_scale)
                predictor_decision_function = self.OCSVM_Obj_lst[turn][-4].decision_function(Next_ATF_pca_scale)
                i = 0
                while i < len(self.Next_CERT52_Crt_Users):
                    self.ATF_Predict_Results[i].append(predictor_results[i])
                    self.ATF_Predict_Results[i].append(predictor_decision_function[i])
                    i += 1
                turn += 1

        # 将结果写入到新结果文件
        # Month_ATF_Predictor_Results，其中最后一位统计'1'的个数，并降序排列
        self.Next_Pred = []
        for result in self.ATF_Predict_Results:
            result.append(result.count(1))
            if result[0] in ['SLL0193', 'TNB1616', 'WDT1634', 'OSS1463', 'IHC0561']:
                print result, '\n'
            if result[-1] >= K_Vote:
                result.append(1)
                self.Next_Pred.append(1)
            else:
                result.append(-1)
                self.Next_Pred.append(-1)
        # result: user_id, 1,1,0,1,0,3,0 (if K_Vote = 5)
        self.ATF_Predict_Results_sort = sorted(self.ATF_Predict_Results, key=lambda t:t[-2], reverse=True)
        cnt_recall, recall, cnt_fp, fpr, risk_ratio, tp_index, recall_index, fp_index = Cal_Messures(self.Next_GT_lst, self.Next_Pred)
        print self.Next_GT_lst.count(1), '\n' # 2010-09月：10个 验证正确
        print self.Next_Month, 'Predicotr Results:', 'recall:', cnt_recall, recall, 'fpr:', fpr, 'risk_ratio:', risk_ratio, '\n'
        # 按照顺序写入ATF预测结果
        f_Next_ATF_Predictor = open(self.Dst_Dir + '\\' + self.Next_Month + '\\' + self.Next_Month + '_CERT5.2_ATF_Cross5_OCSVM_Predictor_Results-0.1.csv', 'w')
        for line in self.ATF_Predict_Results_sort:
            for ele in line:
                f_Next_ATF_Predictor.write(str(ele) + ',')
            f_Next_ATF_Predictor.write('\n')
        f_Next_ATF_Predictor.close()
        # 输出最终结果下各个字段的均值与中位数
        # 这里应当分析的是
        # ATF_Predict_Results_sort_1DF = sorted(self.ATF_Predict_Results_sort, key=lambda t:t[2][0], reverse=True)
        # f_PRS_1DF = open(self.Dst_Dir + '\\' + self.Next_Month + '\\' + self.Next_Month + '_CERT5.2_ATF_Cross5_OCSVM_PR_1DF.csv', 'w')
        # for line in ATF_Predict_Results_sort_1DF:
        #     for ele in line:
        #         f_PRS_1DF.write(str(ele) + ',')
        #     f_PRS_1DF.write('\n')
        # f_PRS_1DF.close()
        # 将原来的ATF_Sort数值提取后，针对五个OCSVM的预测函数值做归一化，然后观察Insiders的分布
        # 此外，在最后追加一列是DF和的归一化结果
        # 这里我们分两步进行，一步是包含所有用户的DF之和和DF和均值化的归一化结果，
        # 另一个则是仅针对先期被判定为[+1]的用户而言进行；

        DF_lst = []
        for line in self.ATF_Predict_Results_sort:
            # user_id, flag_1, df_1,flag_2, df_2...
            df_tmp = []
            df_tmp.append(line[2][0])
            df_tmp.append(line[4][0])
            df_tmp.append(line[6][0])
            df_tmp.append(line[8][0])
            df_tmp.append(line[10][0])
            # 追加五个OCSVM预测DF函数和的均值和中位数
            df_mean = np.mean(df_tmp)
            df_median = np.median(df_tmp)
            df_tmp.append(df_mean)
            df_tmp.append(df_median)
            DF_lst.append(df_tmp)
        DF_MinMax = skp.MinMaxScaler().fit_transform(DF_lst)
        # DF_MinMax = skp.scale(DF_lst)

        j = 0
        while j < len(self.ATF_Predict_Results_sort):
            # user_id, flag_1, df_1,flag_2, df_2...
            self.ATF_Predict_Results_sort[j][2] = DF_MinMax[j][0]
            self.ATF_Predict_Results_sort[j][4] = DF_MinMax[j][1]
            self.ATF_Predict_Results_sort[j][6] = DF_MinMax[j][2]
            self.ATF_Predict_Results_sort[j][8] = DF_MinMax[j][3]
            self.ATF_Predict_Results_sort[j][10] = DF_MinMax[j][4]
            self.ATF_Predict_Results_sort[j].append(DF_MinMax[j][5])
            self.ATF_Predict_Results_sort[j].append(DF_MinMax[j][6])
            j += 1
        f_PRS_MinMax = open(self.Dst_Dir + '\\' + self.Next_Month + '\\' + self.Next_Month + '_CERT5.2_ATF_Cross5_OCSVM_DF_MinMax-0.1.csv','w')
        for line in self.ATF_Predict_Results_sort:
            for ele in line:
                f_PRS_MinMax.write(str(ele) + ',')
            f_PRS_MinMax.write('\n')
        f_PRS_MinMax.close()
        print 'ATF预测结果保存完毕..\n'

        # 统计下判定为[+1]且DF和中位数>0.89的用户个数













