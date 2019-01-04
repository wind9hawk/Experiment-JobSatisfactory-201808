# coding:utf-8
# 为了节省后续分析的代码量，这里我们还是来按照面向对象来写

# 主要过程：
# 基于26JS的CPB特征分析
# 1. 先按照是否在职离职将用户区分为[-1]与[+1]
# 2. 而后对于[-1]用户基于minmax后的JS特征进行自动KMeans；
# 3. 得到最好的K与群簇结果，并按照已有公式计算定性高低，筛选出定性高的用户；
# 4. 利用筛选的群簇用户训练OCSVM，并将排除的[-1]用户与[+1]用户一起作为测试集，进行测试输出高危用户集合；
# 5. 检查CERT5.2中三类Insiders的Recall与整体误报率FPR；

import os,sys
import sklearn.preprocessing as skp
import sklearn.decomposition as skd
import copy
import numpy as np

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
    return recall, recall / cnt_p, cnt_fp, fpr / 1899.0, cnt_c_p / 1999, tp_index, recall_index, fp_index


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
        f_ATF = open(self.Analyze_Path + '\\' + 'CERT5.2_Static_ATF-0.1.csv', 'r')
        f_ATF_lst = f_ATF.readlines()
        self.ATF_lst = []
        self.CERT52_Users_ATFOrder = []
        for line_atf in f_ATF_lst:
            line_lst = line_atf.strip('\n').strip(',').split(',')
            if line_lst[0] == 'user_id':
                continue
            self.CERT52_Users_ATFOrder.append(line_lst[0])
            atf_tmp = []
            # js_tmp中不包含用户字段
            for ele in line_lst[1:]:
                atf_tmp.append(float(ele))
            self.ATF_lst.append(atf_tmp)
        print 'ATF_lst 初始化完毕..\n'
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
        print '首先进行数据重新分组，确定要进行KMeans聚类的用户群簇..\n'
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
        print '排除掉离职用户的剩余CERT5.2用户的索引为：\n'
        #for i in range(10):
        #    print i, self.CERT52_Users_JSOrder[self.KMeans_Index_JS[i]], '\n'
        print len(self.ATF_lst), '\n'
        for i in range(10):
            print i, self.CERT52_Users_ATFOrder[self.KMeans_Index_ATF[i]], '\n'


        print '开始映射成KMeans的用户满意度特征..\n'
        self.KMeans_JS_Feats = []
        self.KMeans_ATF_Feats = []
        for index in self.KMeans_Index_JS:
            self.KMeans_JS_Feats.append(self.JS_lst[index])
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
        f_kmeans_pred = open(self.Analyze_Path + '\\' + 'ATF_KMeans_Pred.csv', 'w')
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


        print '自动KMeans聚类完成..\n'

    def OCSVM_Predictor(self):
        # 采用上一步聚类中的多数类作为训练OCSVM的依据；
        # 多数类训练OCSVM
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

        # 在分隔训练集与测试集前先做PCA
        self.ATF_PCA_lst = skd.PCA(n_components=1).fit_transform(self.ATF_lst)
        # scale
        self.ATF_PCA_Scale_lst = skp.scale(self.ATF_PCA_lst)

        self.Train_Feats = []
        for index_t in self.KMeans_Clusters[t_cls_index]:
            self.Train_Feats.append(self.ATF_PCA_Scale_lst[index_t])
        self.Test_Feats = []
        self.Test_Index = []
        self.KMeans_Clusters.remove(self.KMeans_Clusters[t_cls_index])
        i = 0
        while i < len(self.CERT52_Users_ATFOrder):
            if self.CERT52_Users_ATFOrder[i] in self.Leave_Users:
                self.Test_Index.append(i)
                self.Test_Feats.append(self.ATF_PCA_Scale_lst[i])
                i += 1
            else:
                i += 1
                continue
                for cls in self.KMeans_Clusters:
                    if i in cls:
                        self.Test_Index.append(i)
                        self.Test_Feats.append(self.ATF_PCA_Scale_lst[i])
                        i += 1
                    else:
                        i += 1
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

        # 开始训练OCSVM
        nu_lst = range(5, 105, 5)

        #
        # 对于ATF_10D而言不需要再做PCA了，直接scale就好
        #
        pca_k = len(self.Train_Feats[0])
        print 'PCA后维度为： ', pca_k, '\n'

        # All_Feats_pca_scale = skp.scale(All_Feats)
        # 进入到OCSVM最优参数计算
        # nu； [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]
        ocsvm_obj_lst = []
        for nu_0 in nu_lst:
            nu_0 = nu_0 / 100.0
            clf = svm.OneClassSVM(kernel='rbf', tol=0.01, nu=nu_0, gamma='auto', random_state=10)
            clf.fit(self.Train_Feats)
            pred = clf.predict(self.Test_Feats)
            # return cnt_recall, recall / cnt_p, cnt_fp, fpr / cnt_n, cnt_c_p / (cnt_n + cnt_p)
            # print 'Bug for Before Cal_Messure:', self.Labels[k], '\n'
            # print 'Bug for Before Cal_Messure:', pred, '\n'
            # print self.Labels[k][0], pred[0], self.Labels[k][0] == pred[0], '\n'
            # sys.exit()
            cnt_recall, recall, cnt_fp, fpr, risk_ratio, tp_index, recall_index, fp_index = Cal_Messures(self.Labels,
                                                                                                         pred)
            # print 'Bug for after Cal_Messure, tp_index:', tp_index, '\n'
            # print 'Bug for after Cal_Messure, recall_index:', recall_index, '\n'
            # sys.exit()
            # 上述验证通过
            miu = 1.0
            m_score = miu * recall - (1 - miu) * fpr
            ocsvm_tmp = []
            ocsvm_tmp.append(nu_0)
            ocsvm_tmp.append(miu)
            ocsvm_tmp.append(m_score)
            ocsvm_tmp.append(recall)
            ocsvm_tmp.append(fpr)
            ocsvm_tmp.append(risk_ratio)
            ocsvm_tmp.append(clf)
            # 这里应该补充三类Insiders的召回率
            recall_1 = 0.0
            recall_2 = 0.0
            recall_3 = 0.0
            for index_i in self.Test_Insiders_1_Index:
                if pred[index_i] == 1:
                    recall_1 += 1
            for index_i in self.Test_Insiders_2_Index:
                if pred[index_i] == 1:
                    recall_2 += 1
            for index_i in self.Test_Insiders_3_Index:
                if pred[index_i] == 1:
                    recall_3 += 1
            ocsvm_tmp.append(recall_1 / len(self.Insiders_1))
            ocsvm_tmp.append(recall_2 / len(self.Insiders_2))
            ocsvm_tmp.append(recall_3 / len(self.Insiders_3))
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
        self.Risk_DF = ocsvm_obj_sort_lst[0][-5].decision_function(self.Test_Feats)
        j = 0
        while j < len(self.Test_Feats):
            risk_tmp =[]
            risk_tmp.append(self.CERT52_Users_ATFOrder[self.Test_Index[j]])
            risk_tmp.append(ocsvm_obj_sort_lst[0][-1][j])
            risk_tmp.append(self.Labels[j])
            risk_tmp.append(self.Risk_DF[j][0])
            self.Risk_Users.append(risk_tmp)
            j += 1
        self.Risk_Users_Sort = sorted(self.Risk_Users, key=lambda t:t[-1], reverse=True)
        f_Risk_DF = open(self.Analyze_Path + '\\' + 'CERT5.2_KMeans_OCSVM_ATF_Predictor_Risk-0.11.csv', 'w')
        for line in self.Risk_Users_Sort:
            for ele in line:
                f_Risk_DF.write(str(ele) + ',')
            f_Risk_DF.write('\n')
        f_Risk_DF.close()

        # 针对Insiders_1/2/3输出三类攻击用户在测试集合中的DF函数值，以及对应的次序
        print 'Insiders_1 in Risk_Users_Sort:...\n'
        for insider_1 in self.Insiders_1:
            i = 0
            while i < len(self.Risk_Users_Sort):
                if self.Risk_Users_Sort[i][0] == insider_1:
                    print self.Risk_Users_Sort[i], ':', i, '\n'
                    i += 1
                else:
                    i += 1

        print 'Insiders_2 in Risk_Users_Sort:...\n'
        for insider_2 in self.Insiders_2:
            i = 0
            while i < len(self.Risk_Users_Sort):
                if self.Risk_Users_Sort[i][0] == insider_2:
                    print self.Risk_Users_Sort[i], ':', i, '\n'
                    i += 1
                else:
                    i += 1

        print 'Insiders_3 in Risk_Users_Sort:...\n'
        for insider_3 in self.Insiders_3:
            i = 0
            while i < len(self.Risk_Users_Sort):
                if self.Risk_Users_Sort[i][0] == insider_3:
                    print self.Risk_Users_Sort[i], ':', i, '\n'
                    i += 1
                else:
                    i += 1




print '..<<基于原始26维度JS特征的CERT5.2静态高危用户预测实验>>..\n\n'
Dst_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.9'
# 初始化对象
Predictor_obj = KMeans_OCSVM_Predictor(Dst_Dir)
Predictor_obj.Auto_KMeans()
Predictor_obj.OCSVM_Predictor()

