# coding:utf-8
# 本模块提供一种使用随机森林实现的ATF特征重要性分析，以在实际实验前增加了解

import os,sys
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import RandomForestClassifier
import sklearn.preprocessing as skp
import sklearn.decomposition as skd
import numpy as np

def Cal_RF_Feat_Imporance(X_lst, Y_lst):
    x_train, x_test, y_train, y_test = train_test_split(X_lst, Y_lst, test_size=0.2, random_state=0)
    # feat_labels = df.columns[1:]
    forest = RandomForestClassifier(n_estimators=10000, random_state=0, n_jobs=-1)
    forest.fit(x_train, y_train)


    # 格式化特征重要性输出
    Feat_Nms = ['CPB-I','CPB-O','JS_Score','Team_CPB-I-mean','Team_CPB-O-mean','Users-less-mean-A','Users-less-mean-A and C','Users-less-mean-C','Users-High-mean-N','Team_CPB-I-median','Team_CPB-O-median','leader-CPB-I','leader-CPB-O','dis_ocean','avg_dis_ocean','dis_os','avg_dis_os','email_ratio','cnt_send', 'cnt_recv','cnt_s_size','cnt_r_size','cnt_s_attach','cnt_r_attach','cnt_s_days','cnt_r_days','cnt_late_days','cnt_early_days','month_work_days']
    importances = forest.feature_importances_
    Feat_Importance = []
    i = 0
    while i < len(importances):
        tmp = []
        tmp.append(Feat_Nms[i])
        tmp.append(importances[i])
        Feat_Importance.append(tmp)
        i += 1
    Feat_Importance_sort = sorted(Feat_Importance, key=lambda t:t[1], reverse=True)
    print len(Feat_Importance_sort), len(importances), len(Feat_Nms), '\n'
    for i in range(len(importances)):
        print i, Feat_Importance_sort[i], '\n'

def Cal_RF_FeatGroup_Imporance(X_lst, Y_lst):
    # 将CPB特征变为几个组特征，子特征求和
    CPB_Group_Feats = []
    for line in X_lst:
        tmp = []
        tmp.extend(line[:3])
        tmp.append(sum(line[3:13]))
        tmp.append(sum(line[13:26]))
        tmp.append(sum(line[26:-1]))
        CPB_Group_Feats.append(tmp)

    x_train, x_test, y_train, y_test = train_test_split(CPB_Group_Feats, Y_lst, test_size=0.2, random_state=0)
    # feat_labels = df.columns[1:]
    forest = RandomForestClassifier(n_estimators=10000, random_state=0, n_jobs=-1)
    forest.fit(x_train, y_train)


    # 格式化特征重要性输出
    Feat_Nms = ['CPB-I','CPB-O','JS_Score','Work_CPBs', 'Leave_Contacts', 'WorkTime']
    importances = forest.feature_importances_
    Feat_Importance = []
    i = 0
    while i < len(importances):
        tmp = []
        tmp.append(Feat_Nms[i])
        tmp.append(importances[i])
        Feat_Importance.append(tmp)
        i += 1
    Feat_Importance_sort = sorted(Feat_Importance, key=lambda t:t[1], reverse=True)
    print len(Feat_Importance_sort), len(importances), len(Feat_Nms), '\n'
    for i in range(len(importances)):
        print i, Feat_Importance_sort[i], '\n'

# 小测试：train_test_split支持单类数据划分么
test_flag = False
if test_flag:
    #X = [1,1,1,1,1,0,0,0,0,0,2,3,4,2,4] # 如果是0:1， 非0:0
    #Y = [0,0,0,0,0,1,1,1,1,1,0,0,0,0,0]
    # 对于双类数据而言，train_test_split自然是训练集与测试集中同时包含两类数据
    # [0, 4, 1, 1, 2, 2, 0, 3, 1, 1, 0, 4]
    # [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0]
    #
    # [1, 0, 0]
    # [0, 1, 1]
    # 若对于一个蛋类数据呢？
    X = [1,2,3,4,5,1,2,4,5,7]
    Y = [0,0,0,0,0,0,0,0,0,0]
    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=0)
    print x_train, '\n', y_train, '\n'
    print x_test, '\n', y_test, '\n'


Dst_Dir = r'G:\GitHub\Essay-Experiments\Experiment-JobSatisfactory-201808\PythonCode0\JS-Risks_Analyze-0.9\KMeans_OCSVM_Insiders_Predictor'
# month = '2010-09'
# 2010-08_CERT5.2_Users_GroundTruth.csv_v01.csv
# CERT5.2_ATF_0.1.csv

# 先生成对应Static用户特征的的标签
# CERT5.2_Leave_Static_GroundTruth
# 先获取Insiders列表
Insiders_lst = []
for file in os.listdir(sys.path[0] + '\\' + 'JS-Risks_Analyze-0.9'):
    if os.path.isfile(sys.path[0] + '\\' + 'JS-Risks_Analyze-0.9' + '\\' + file) == True:
        if 'Insiders-' in file and '_Leave.csv' in file:
            print file, '\n'
            f_insider = open(sys.path[0] + '\\' + 'JS-Risks_Analyze-0.9' + '\\' + file, 'r')
            for line in f_insider.readlines():
                line_lst = line.strip('\n').strip(',').split(',')
                if line_lst[0] not in Insiders_lst:
                    Insiders_lst.append(line_lst[0])
        else:
            continue
print 'CERT5.2 Insiders is ', len(Insiders_lst), Insiders_lst[:10], '\n'

f_CERT52_GT = open(Dst_Dir + '\\' + 'CERT5.2_Leave_Static_GroundTruth', 'w')
for line in open(Dst_Dir + '\\' + 'CERT5.2_Leave_Static_CPB_ATF-02.csv', 'r').readlines():
    line_lst = line.strip('\n').strip(',').split(',')
    if line_lst[0] == 'user_id':
        continue
    else:
        f_CERT52_GT.write(line_lst[0] + ',')
        if line_lst[0] in Insiders_lst:
            f_CERT52_GT.write('1' + '\n')
        else:
            f_CERT52_GT.write('-1' + '\n')
f_CERT52_GT.close()
# sys.exit()
for file in os.listdir(Dst_Dir):
    if 'CERT5.2_Leave_Static_CPB_ATF-02.csv' in file:
        f_ATF_path = Dst_Dir + '\\' +  file
    if 'CERT5.2_Leave_Static_GroundTruth' in file:
        f_GT_path = Dst_Dir + '\\'  + file
f_ATF = open(f_ATF_path, 'r')
f_ATF_lst = f_ATF.readlines()
f_ATF.close()
f_GT = open(f_GT_path, 'r')
f_GT_lst = f_GT.readlines()
f_GT.close()
ATF_lst = []
GT_lst = []
for line_atf in f_ATF_lst:
    line_lst = line_atf.strip('\n').strip(',').split(',')
    if line_lst[0] == 'user_id':
        continue
    atf_tmp = []
    for ele in line_lst[1:]:
        atf_tmp.append(float(ele))
    atf_tmp.remove(atf_tmp[26])
    ATF_lst.append(atf_tmp)
for line_gt in f_GT_lst:
    line_lst = line_gt.strip('\n').strip(',').split(',')
    if line_lst[0] == 'user_id':
        continue
    gt_tmp = []
    for ele in line_lst[1:]:
        gt_tmp.append(float(ele))
    GT_lst.extend(gt_tmp)

for i in range(5):
    print i, ATF_lst[i], '\n', GT_lst[i], '\n'


# 试着对原始的ATF_lst进行PCA或者MinMax
ATF_MinMax_lst = skp.MinMaxScaler().fit_transform(ATF_lst)
#ATF_pca_lst = skd.PCA().fit_transform(ATF_lst)
#ATF_pca_MinMax = skp.MinMaxScaler().fit_transform(ATF_pca_lst)
#ATF_pca_scale = skp.scale(ATF_pca_lst)
#ATF_scale = skp.scale(ATF_lst)
#ATF_scale_pca = skd.PCA().fit_transform(ATF_scale)
#print len(ATF_pca_lst[0]), '\n'
# ATF_array = np.array(ATF_MinMax_lst)
#Cal_RF_Feat_Imporance(ATF_MinMax_lst, GT_lst)
Cal_RF_FeatGroup_Imporance(ATF_MinMax_lst, GT_lst)
