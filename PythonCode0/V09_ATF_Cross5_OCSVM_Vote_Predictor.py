# coding:utf-8
# ATF_Cross5_OCSVM_Vote_Predictor
# 本文件为上述基于攻击倾向特征（ATF）的5折交叉验证多OCSVM投票预测对象类

# 可能导入的库
import os,sys
import sklearn.preprocessing as skp
import sklearn.decomposition as skd
import numpy as np
import random
from sklearn import svm



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
            feats_lst.append(float(line_lst[1]))

    return feats_lst

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
    i = 0
    while i < len(y_pred):
        if gt_lables[i] == 1: # 真实的[+1]
            cnt_p += 1
            tp_index.append(i) # 验证集中的列表
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
                cnt_c_p += 1
                i += 1
            else:
                tn += 1
                i += 1
    # cnt_c_p: 分类器预测为P的个数
    # cnt_p: 真实数据中P的个数
    # cnt_n: 真实数据中N的个数
    return cnt_recall, recall / cnt_p, cnt_fp, fpr / cnt_n, cnt_c_p / (cnt_n + cnt_p), tp_index, recall_index

# 类定义
class ATF_Cross5_OCSVM_Vote_Predictor():
    def __init__(self, dst_dir, month, next_month):
        # month: 2010-02:2011-04
        # next_month: 2010-03:2011-05
        self.Dst_Dir = dst_dir
        self.Month = month
        self.ATF_Path = self.Dst_Dir + '\\' + self.Month + '\\' + 'CERT5.2_ATF_0.1.csv'
        self.GT_Path = self.Dst_Dir + '\\' + self.Month + '\\' + self.Month + '_CERT5.2_Users_GroundTruth.csv_v01.csv'
        self.Next_Month = next_month
        self.Next_ATF_Path = self.Dst_Dir + '\\' + self.Next_Month + '\\' + 'CERT5.2_ATF_0.1.csv'
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
        self.ATF_lst = Extract_Lines(self.ATF_Path)
        self.GT_lst = Extract_Lines(self.GT_Path)
        self.Next_ATF_lst = Extract_Lines(self.Next_ATF_Path)
        self.Next_GT_lst = Extract_Lines(self.Next_GT_Path)
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
            self.Validate_Indexes[i].extend(self.OffJob_Index)
            self.Validate_Indexes[i].sort()
        # 生成对应的验证集的Labels
        for i in range(5):
            for ele in self.Validate_Indexes[i]:
                if ele in self.OnJob_Index:
                    self.Labels[i].append(-1)
                if ele in self.OffJob_Index:
                    self.Labels[i].append(+1)

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
            split_index = len(All_Feats)
            for feat in self.Validate_Feats[k]:
                All_Feats.append(feat)
            All_Feats_pca = skd.PCA().fit_transform(All_Feats)
            pca_k = len(All_Feats_pca[0])
            # scale
            All_Feats_pca_scale = skp.scale(All_Feats_pca)
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
                cnt_recall, recall, cnt_fp, fpr, risk_ratio, tp_index, recall_index = Cal_Messures(self.Labels[k], pred)
                miu = 0.8
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





