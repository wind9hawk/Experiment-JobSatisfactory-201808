# coding:utf-8
# 由于需要对1000-2000个用户特征进行聚类，而如果直接使用KMeans聚类则无法很好确定K值遍历的上限
# 故首先采用尝试使用密度聚类DBSCAN来发现其中的核心（聚类中心），然后再使用KMeans聚类

import numpy as np
import sklearn.cluster as skc
import sklearn.preprocessing as skp
from sklearn import metrics
import matplotlib.pyplot as plt
import sys, os



def DBSCAN_Clustering(Data_lst, EPS, MiniSamples):
    # Data_lst应该为一个原始纯碎的数值数组
    X = np.array(Data_lst)
    db = skc.DBSCAN(eps=EPS, min_samples=MiniSamples).fit(X)
    # 和X同一个维度，labels对应索引序号的值 为她所在簇的序号。若簇编号为-1，表示为噪声
    labels = db.labels_

    print ('每个样本的簇标号：\n')
    print labels, '\n'

    ratio = len(labels[labels[:] == -1]) / len(labels) # 计算噪声点个数占综述比例
    print '噪声比： ', ratio, '\n'

    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0) # 获取分簇数目
    n_core_ = len(db.core_sample_indices_)
    print '总共识别群簇数目为： ', n_clusters_, '\n'
    print '总共识别核心点为： ', n_core_, '\n'

    if len(set(labels)) == 1:
        score = 0.0
        return n_clusters_, n_core_, labels, score
    score = metrics.silhouette_score(X, labels) # [-1,1]，1最好，-1最差
    print '轮廓系数指标为： ', score, '\n'

    for i in range(n_clusters_):
        print '群簇 ', i, ' 所有样本为： \n'
        one_cluster = X[labels == i]
        print one_cluster, '\n'
        plt.plot(one_cluster[:, 0], one_cluster[:, 1], 'o')
    #plt.show()
    return n_clusters_, n_core_, labels, score

# 指定数据源
f_0 = open('CERT5.2_Big5_LDAP_Part1_Feats.csv', 'r')
f_0_lst = f_0.readlines()
f_0.close()

# 读取数据源，输入
# 数据样例：
# MMK1532,17.0,17.0,16.0,22.0,28.0,2.0,5.0,20.0,40.0,
Data_lst = []
Users_lst = []
for line in f_0_lst[:]:
    line_lst = line.strip('\n').strip(',').split(',')
    Users_lst.append(line_lst[0])
    tmp_0 = []
    print line_lst[1:], '\n'
    for ele in line_lst[1:]:
        tmp_0.append(float(ele))
    Data_lst.append(tmp_0)

# 将数据送入DBSCAN聚类
Data_lst = skp.MinMaxScaler().fit_transform(Data_lst)
Choice_lst = []
for minisample in range(2,20,1):
    for eps in range(1,100,2):
        eps_0 = float(eps) / 100
        N_Clusters, N_Cores, Labels, Score = DBSCAN_Clustering(Data_lst, eps_0, minisample)
        tmp_1 = []
        tmp_1.append(N_Clusters)
        tmp_1.append(N_Cores)
        tmp_1.append(Labels)
        tmp_1.append(Score)
        Choice_lst.append(tmp_1)
b = sorted(Choice_lst, key=lambda t:t[3], reverse=True)
for i in range(10):
    print i, '\n'
    for ele in b[i]:
        print ele, '\n'
    print '\n\n'


sys.exit()