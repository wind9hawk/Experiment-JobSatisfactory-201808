# coding:utf-8
# 本脚本在前期KMeans聚类的基础上，针对识别出的高满意度用户进行OCSVM训练，然后对剩余的测试用户进行判断

import sys
import numpy as np
from sklearn.preprocessing import Normalizer
from sklearn.decomposition import PCA
from sklearn.svm import OneClassSVM

print '首先读入两个目标文件...\n'
f_cert = open(r'CERT6.2-2009-12-New-26JS.csv', 'r')
f_cert_lst = f_cert.readlines()
f_cert.close()
f_5JS = open(r'CERT6.2-2009-12-5JS-Label-0.2.csv', 'r')
f_5JS_lst = f_5JS.readlines()
f_5JS.close()
f_insiders = open(r'CERT4.2-Insiders.csv', 'r')
f_insiders_lst = f_insiders.readlines()
f_insiders.close()
print 'CERT数据与5JS标签数据读取完毕...\n'

print '选择训练集与测试集...\n'
Users_5JS = []
Train_index = []
Test_index = []
Users_nm = []
Cnt_Scorehigh4 = 0.0
JS_Local= []
i = 0
while i < len(f_5JS_lst):
    # NFP2441,0,1,1,0,1,3,7
    line_lst = f_5JS_lst[i].strip('\n').strip(',').split(',')
    print line_lst, '\n'
    # print line_lst[1:6], '\n'
    #sys.exit()
    # CERT4.2中：
    # 风险均值为：  15.4054054054
    # 风险中位数为： 12.0
    # AGE1244,0,1,1,0,1,3,7
    Users_nm.append(line_lst[0])
    if float(line_lst[6]) > 2:
        Train_index.append(i)
        i += 1
        # if float(line_lst[7]) > 4:
        #     Cnt_Scorehigh4 += 1
        continue
    else:
        # Test_index.append(i)
        JS_Local.append(float(line_lst[7]))
        # 风险均值为：  4.70770770771
        # 风险中位数为： 5.0
        # 局部JS值均值与中位数为： 4.00925266904 	4.0; 5.4348864994 	6.0
        if float(line_lst[7]) > 4:
            Cnt_Scorehigh4 += 1
            Train_index.append(i)
            # Test_index.append(i)
            i += 1
        else:
            Test_index.append(i)
            i += 1
            continue
# ACM2278:line 2840;
# CMP2946:line 2330;
# PLJ1771:line 1282;
# CDE1846:line 655;
# MBG3183:line 1494;
print f_5JS_lst[2839], '\n'
print '训练集有： ', len(Train_index), '\n'
print '测试集有： ', len(Test_index), '\n'

print '补充测试...\n'
print 'count(1)《=3的用户中，分数大于10的用户有 ', Cnt_Scorehigh4, '\n'
# sys.exit()
JS_Local_array = np.array(JS_Local)
print '局部JS值均值与中位数为：', JS_Local_array.mean(), '\t', np.median(JS_Local_array), '\n'
# sys.exit()
# NFP2441,0,1,1,0,1,3,7
# 需要判断此时的新测试集中包含恶意Insiders多少？
Insiders_1 = f_insiders_lst[0].strip('\n').strip(',').split(',')
Insiders_2 = f_insiders_lst[1].strip('\n').strip(',').split(',')
Insiders_3 = f_insiders_lst[2].strip('\n').strip(',').split(',')
Recall_all = 0.0
Recall_1 = 0.0
Recall_2 = 0.0
Recall_3 = 0.0
Insiders_lst =[]
j = 0
while j < len(Test_index):
    user_lst = f_5JS_lst[j].strip('\n').strip(',').split(',')
    if user_lst[0] in Insiders_1:
        print 'Insiders_1:', user_lst, '\n'
        Insiders_lst.append(user_lst)
        Recall_1 += 1
        j += 1
        continue
    if user_lst[0] in Insiders_2:
        print 'Insiders_2:', user_lst, '\n'
        Insiders_lst.append(user_lst)
        Recall_2 += 1
        j += 1
        continue
    if user_lst[0] in Insiders_3:
        print 'Insiders_3:', user_lst, '\n'
        Insiders_lst.append(user_lst)
        Recall_3 += 1
        j += 1
        continue
    j += 1
    continue
print 'Insiders_1:', Recall_1, Recall_1 / (len(Insiders_1) - 1), '\n'
print 'Insiders_2:', Recall_2, Recall_2 / (len(Insiders_2) - 1), '\n'
print 'Insiders_3:', Recall_3, Recall_3 / (len(Insiders_3) - 1), '\n'
for one in Insiders_lst:
    print one, '\n'
# sys.exit()

# 训练集1843
# 测试集2156

print '依据得到的训练集与测试集索引构建训练集与测试集...\n'
# 由于5JS文件中用户没有标题行，因此其索引对应在26JS文件中需要+1
# 然而在提取26JS文件中信息时，跳过了标题行，因此索引重新一致
Users_26JS = []
for line in f_cert_lst:
    User_26JS = []
    line_lst = line.strip('\n').strip(',').split(',')
    if line_lst[0] == 'user_id':
        continue
    i = 1
    while i < len(line_lst):
        User_26JS.append(float(line_lst[i]))
        i += 1
    Users_26JS.append(User_26JS)
print 'Users_26 共有用户： ', len(Users_26JS), '\n'

print '开始准备OCSVM训练，需要首先进行PCA与Normalizer...\n'
# 归一化与PCA顺序不可颠倒，由于初始特征量纲接近，不需事先做归一化
pca = PCA(n_components=3)
Users_26JS_pca = pca.fit_transform(Users_26JS)
Users_26JS_pca_nor = Normalizer().fit_transform(Users_26JS_pca)
Train_lst = []
Test_lst = []
j = 0
while j < len(f_5JS_lst):
    if j in Train_index:
        Train_lst.append(Users_26JS_pca_nor[j])
        j += 1
    if j in Test_index:
        Test_lst.append(Users_26JS_pca_nor[j])
        j += 1
print '训练集有： ',len(Train_lst), '\n'
print '测试集有： ', len(Test_lst), '\n'


print 'OCSVM开始训练...\n'
clf = OneClassSVM(kernel='rbf', tol=0.01, nu=0.35, gamma='auto')
Train_array = np.array(Train_lst)
Test_array = np.array(Test_lst)
clf.fit(Train_array)
pred = clf.predict(Test_array)

print '开始输出分类结果...\n'
# ACM2278:line 2840;
# CMP2946:line 2330;
# PLJ1771:line 1282;
# CDE1846:line 655;
# MBG3183:line 1494;
print 'ACM2278 is ', clf.predict(Users_26JS_pca_nor[2839]), '\t', clf.decision_function(Users_26JS_pca_nor[2839]), '\n'
print 'CMP2946 is ', clf.predict(Users_26JS_pca_nor[2329]), '\n', clf.decision_function(Users_26JS_pca_nor[2329]), '\n'
print 'PLJ1771 is ', clf.predict(Users_26JS_pca_nor[1281]), '\t', clf.decision_function(Users_26JS_pca_nor[1281]), '\n'
print 'CDE1846 is ', clf.predict(Users_26JS_pca_nor[654]), '\n',  clf.decision_function(Users_26JS_pca_nor[654]), '\n'
print 'MBG3183 is ', clf.predict(Users_26JS_pca_nor[1493]), '\n', clf.decision_function(Users_26JS_pca_nor[1493]), '\n'

print '开始将高危用户存储到对应文件,,,\n'
f_risk = open(r'CERT6.2-2009-12-High Risk-0.1.csv', 'w')
i = 0
while i < len(Test_index):
    if clf.predict(Users_26JS_pca_nor[Test_index[i]]) < 0:
        f_risk.write(Users_nm[Test_index[i]])
        f_risk.write(',')
        f_risk.write(str(clf.decision_function(Users_26JS_pca_nor[Test_index[i]])[0][0]))
        f_risk.write('\n')
    i += 1
print '高危用户存储完毕...\n'
f_risk.close()
print 'ACM2278 is ', clf.predict(Users_26JS_pca_nor[2839]), '\t', clf.decision_function(Users_26JS_pca_nor[2839]), '\n'
print 'CMP2946 is ', clf.predict(Users_26JS_pca_nor[2329]), '\n', clf.decision_function(Users_26JS_pca_nor[2329]), '\n'
print 'PLJ1771 is ', clf.predict(Users_26JS_pca_nor[1281]), '\t', clf.decision_function(Users_26JS_pca_nor[1281]), '\n'
print 'CDE1846 is ', clf.predict(Users_26JS_pca_nor[654]), '\n',  clf.decision_function(Users_26JS_pca_nor[654]), '\n'
print 'MBG3183 is ', clf.predict(Users_26JS_pca_nor[1493]), '\n', clf.decision_function(Users_26JS_pca_nor[1493]), '\n'

sys.exit()
Recall_all = 0.0
Recall_1 = 0.0
Recall_2 = 0.0
Recall_3 = 0.0
j = 0
while j < len(Test_index):
    user_lst = f_5JS_lst[j].strip('\n').strip(',').split(',')
    if user_lst[0] in Insiders_1:
        print 'Insiders_1:', user_lst, '\n'
        if clf.predict(Users_26JS_pca_nor[j]) == -1:
            Recall_1 += 1
            j += 1
            continue
        else:
            j += 1
            continue
    if user_lst[0] in Insiders_2:
        print 'Insiders_2:', user_lst, '\n'
        if clf.predict(Users_26JS_pca_nor[j]) == -1:
            Recall_2 += 1
            j += 1
            continue
        else:
            j += 1
            continue
    if user_lst[0] in Insiders_3:
        print 'Insiders_3:', user_lst, '\n'
        if clf.predict(Users_26JS_pca_nor[j]) == -1:
            Recall_3 += 1
            j += 1
            continue
        else:
            j += 1
            continue
    j += 1
    continue
print '分类出[-1]类用户数目为： ', len(Test_array[pred == -1]), '\n'
print '总共测试集用户为： ', len(Test_array), '\n'
print '训练集总共有： ', len(Train_array), '\n'
print 'Insiders_1:', Recall_1, Recall_1 / (len(Insiders_1) - 1), '\n'
print 'Insiders_2:', Recall_2, Recall_2 / (len(Insiders_2) - 1), '\n'
print 'Insiders_3:', Recall_3, Recall_3 / (len(Insiders_3) - 1), '\n'

sys.exit()

