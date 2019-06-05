# coding:utf-8
'''
this code is for compare of our insider detection with Supervisor Detection in 5 cross-folds
basic steps:
1. read cert5.2 static 1999 users atf-feats;
2. read cert5.2 leave employees and malicious insiders in 3 scenarios;
3. execute 5 cross-folds with all non-malicious users,
    and train ocsvm  with best recall and best fpr;
4. return average/best 3 recalls and total fpr;
for little trick:
we compute ONCE best recall and fpr as the presentative resulst of supervisor detection
and
we compute all data feat index other than data itself for train and test split
'''

import os,sys
import random
import numpy as np
from sklearn.svm import OneClassSVM
import sklearn.preprocessing as skp
import sklearn.decomposition as skd
import sklearn.svm as sks
import math

# calculate Recall/FPR/Cnt_P/Cnt_P_Ratio
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
    return recall, recall / cnt_p, cnt_fp, cnt_fp / 1899.0, cnt_fp / cnt_test_n, tp_index, recall_index, fp_index


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

class CompareDetection():
    def __init__(self, dir_path,
                 user_feats_path,
                 leave_users_path,
                 insiders_1_path, insiders_2_path, insiders_3_path, insiders_4_path):
        self.dir_name = dir_path
        # read all necessary source data
        f_atf = open(user_feats_path, 'r')
        atf_lst = f_atf.readlines()
        f_atf.close()
        f_luser = open(leave_users_path, 'r')
        luser_lst = f_luser.readlines()
        f_luser.close()
        self.cert52_users = [] # build 1-1 map between cert52 user and atf-feats
        self.cert52_feats = []
        for line_atf in atf_lst:
            line_lst = line_atf.strip('\n').strip(',').split(',')
            if line_lst[0] == 'user_id':
                continue
            self.cert52_users.append(line_lst[0])
            atf_tmp = []
            for ele in line_lst[1:]:
                atf_tmp.append(float(ele))
            self.cert52_feats.append(atf_tmp)
        print 'cert52 users and atf-feats read done..\n'
        print len(self.cert52_feats), '\t'
        print self.cert52_users[:3], '\n'
        print self.cert52_feats[:3], '\n'
        self.leave_users = []
        for line_lu in luser_lst:
            line_lst = line_lu.strip('\n').strip(',').split(',')
            if len(line_lst) < 2:
                continue
            self.leave_users.append(line_lst[0])
        print 'cert52 leave users read done..\n'
        self.insiders_1 = []
        self.insiders_2 = []
        self.insiders_3 = []
        self.insiders_4 = []
        # insider name like: r5.2-1-ALT1465.csv
        for file in os.listdir(insiders_1_path):
            self.insiders_1.append(file[7:14])
        for file in os.listdir(insiders_2_path):
            self.insiders_2.append(file[7:14])
        for file in os.listdir(insiders_3_path):
            self.insiders_3.append(file[7:14])
        for file in os.listdir(insiders_4_path):
            self.insiders_4.append(file[7:14])
        print 'cert52 insiders read done..\n'
        print len(self.insiders_1), '\n', len(self.insiders_2), '\n', len(self.insiders_3), '\n',\
                len(self.insiders_4), '\n'

    def train_test_split(self): # determine the train and test set
        self.train_set_index = range(len(self.cert52_users))
        self.test_set_index = []
        for ts_index in self.train_set_index:
            if self.cert52_users[ts_index] in self.insiders_1 or \
               self.cert52_users[ts_index] in self.insiders_2 or \
               self.cert52_users[ts_index] in self.insiders_3 or \
               self.cert52_users[ts_index] in self.insiders_4:
                self.test_set_index.append(ts_index)
        for tt_index in self.test_set_index:
            self.train_set_index.remove(tt_index)
        # cut off insiders_4 without cpb from test
        self.test_set_index = self.test_set_index[:69]
        print 'train index:', len(self.train_set_index), 'test index:', len(self.test_set_index), '\n'
        self.test_plus_index = random_choice(self.train_set_index, 0.2)
        print 'test_plus_index to test:', len(self.test_plus_index), '\n', self.test_plus_index, '\n'
        for tt_index in self.test_plus_index:
            self.train_set_index.remove(tt_index)
            self.test_set_index.append(tt_index)
        print 'train index after 80% random choice:', len(self.train_set_index), 'test index:', len(self.test_set_index), '\n'

    def OCSVM_Predictor(self):
        # execute PCA before train OCSVM to test
        self.ATF_PCA_lst = skd.PCA(n_components=1).fit_transform(self.cert52_feats)
        # scale
        self.ATF_PCA_Scale_lst = skp.scale(self.ATF_PCA_lst)

        self.train_feats = []
        for tr_index in self.train_set_index:
            self.train_feats.append(self.ATF_PCA_Scale_lst[tr_index])
        self.test_feats = []
        for te_index in self.test_set_index:
            self.test_feats.append(self.ATF_PCA_Scale_lst[te_index])
        print 'self.test_feats 共有：', len(self.test_feats), '\n'
        # build test labels according to insiders_1-2-3-4
        self.labels = []
        self.insiders = []
        self.test_insiders_1_index = []
        self.test_insiders_2_index = []
        self.test_insiders_3_index = []
        self.test_insiders_4_index = []
        j = 0
        while j < len(self.test_set_index):
            if self.cert52_users[self.test_set_index[j]] in self.insiders_1:
                self.test_insiders_1_index.append(j)
                j += 1
                continue
            if self.cert52_users[self.test_set_index[j]] in self.insiders_2:
                self.test_insiders_2_index.append(j)
                j += 1
                continue
            if self.cert52_users[self.test_set_index[j]] in self.insiders_3:
                self.test_insiders_3_index.append(j)
                j += 1
                continue
            #if self.cert52_users[self.test_set_index[j]] in self.insiders_4:
            #    self.test_insiders_4_index.append(j)
            #    j += 1
            #    continue
            else:
                j += 1
                continue
        self.insiders.extend(self.insiders_1)
        self.insiders.extend(self.insiders_2)
        self.insiders.extend(self.insiders_3)
        self.insiders.extend(self.insiders_4)
        for v_index in self.test_set_index:
            if self.cert52_users[v_index] in self.insiders:
                self.labels.append(1)
            else:
                self.labels.append(-1)
        print 'test_set has: ', self.labels.count(1), '1 and ', self.labels.count(-1), '\n'
        #print '-1 begin at: ', self.labels.index(-1), '\n'
        # sys.exit()

        # begin train OCSVM
        nu_lst = range(1, 1000, 1)
        pca_k = len(self.train_feats[0])
        print 'PCA后维度为： ', pca_k, '\n'
        # search best parameters for best recall and better fpr
        # nu； [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]
        ocsvm_obj_lst = []
        cnt_oscvm = 0.0
        for nu_0 in nu_lst:
            print 'train ossvm: ', cnt_oscvm, '\n'
            cnt_oscvm += 1
            nu_0 = nu_0 / 1000.0
            clf = sks.OneClassSVM(kernel='rbf', tol=0.01, nu=nu_0, gamma='auto', random_state=10)
            clf.fit(self.train_feats)
            pred = clf.predict(self.test_feats)
            cnt_test_n = len(self.test_feats) - 69
            cnt_recall, recall, cnt_fp, fpr_total, fpr_leave, tp_index, recall_index, fp_index = Cal_Messures(self.labels,
                                                                                                         pred)
            # print 'Bug for after Cal_Messure, tp_index:', tp_index, '\n'
            # print 'Bug for after Cal_Messure, recall_index:', recall_index, '\n'
            # sys.exit()
            # 上述验证通过
            miu = 1.0
            # m_score = miu * recall - (1 - miu) * fpr
            m_score = recall / math.exp(fpr_leave)
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
            recall_4 = 0.0
            for index_i in self.test_insiders_1_index:
                if pred[index_i] == 1:
                    recall_1 += 1
            for index_i in self.test_insiders_2_index:
                if pred[index_i] == 1:
                    recall_2 += 1
            for index_i in self.test_insiders_3_index:
                if pred[index_i] == 1:
                    recall_3 += 1
            for index_i in self.test_insiders_4_index:
                if pred[index_i] == 1:
                    recall_4 += 1
            ocsvm_tmp.append(recall_1 / len(self.insiders_1))
            ocsvm_tmp.append(recall_2 / len(self.insiders_2))
            ocsvm_tmp.append(recall_3 / len(self.insiders_3))
            ocsvm_tmp.append(recall_4 / len(self.insiders_4))
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
        for i in range(5):
            print i, ocsvm_obj_sort_lst[i], '\n'

    def __del__(self):
        del self.dir_name
        del self.cert52_users
        del self.cert52_feats
        del self.leave_users
        del self.insiders_1
        del self.insiders_2
        del self.insiders_3
        print 'del method has finished..\n'


print 'This is a compare detection for supervisor...\n'
dir_path = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.9'
user_feats_path = dir_path + '\\' + 'CERT5.2_Leave_Static_CPB_ATF-03.csv'
leave_users_path = dir_path + '\\' + 'CERT5.2-Leave-Users_OnWeekDays_0.9.csv'
insiders_1_path = dir_path + '\\' + 'r5.2-1'
insiders_2_path = dir_path + '\\' + 'r5.2-2'
insiders_3_path = dir_path + '\\' + 'r5.2-3'
insiders_4_path = dir_path + '\\' + 'r5.2-4'
detector = CompareDetection(
                            dir_path, user_feats_path,
                            leave_users_path, insiders_1_path,
                            insiders_2_path, insiders_3_path,
                            insiders_4_path
                            )
detector.train_test_split()
detector.OCSVM_Predictor()


