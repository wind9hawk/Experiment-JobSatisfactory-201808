# coding:utf-8
# 经历了诸多实验，终于开始尝试写作基于用户工作满意度的主观分类器
# 其核心思想是基于提取的17维度的用户JS特征，
# 1. 首先，假设全体用户中存在者许多满意度相近的用户，反映在特征空间中，即是相近的样本聚为一个类；
# 2. 全部用户中，所有用户的工作满意度大致存在三种情况，根据正态分布，绝大多数用户的满意度在一个正常范围，少部分高于或者低于这个范围，
# 而我们所关注的即低于这个范围的用户；
# 为了找到这些用户，我们基于高于或等于正常范围的正常用户进行OCSVM训练，而这些用户通过聚类中心的JS分数高于中位数的群簇提供；
# 3. 通过训练OCSVM的样本整体上位于所有用户中上部分，因而其判断的用户异常可能存在中间水平边界的用户，对于这些用户，考虑JS分数高于均值的，
# 从异常用户集合中剔除，剩下的即为判定的高危用户；
# 为了实现上述算法，按照算法实现步骤，基本需要：
# 1. 17JS特征数据读入
# 2. KMeans聚类的最优K值确定[2,10]：计算
# 2.1 每个样本点的聚合度、分离度；
# 2.2 计算所有样本点的轮廓系数，得到其平均值；
# 2.3 选择轮廓系数最大的K值分类；
# 2.4 每个K值至少聚合三次，计算三组轮廓系数，保留最大的轮廓系数，避免局部最优值
# 3. 计算K个群簇中心的JS分数，然后排序，选择JS分数高于中位数的群簇作为OCSVM训练样本；
# 4. 训练OCSVM，得到一个主观分类器，然后判断所有样本，打标签；
# 5. 筛选出其中的异常样本，并计算这些样本的JS分数，若高于全部样本的均值特征计算得到的JS分数，则剔除；
# 6. 最后剩余的即为认定的内部高危用户集合，并计算其中所有用户的JS分数；

# 本脚本作为JS_CLF-KMeans-v0.1.py,主要用于计算KMeans的轮廓系数，
# 针对17JS特征从[2,10]中选择最好的K值（每个K值随机选择初始点聚类三次，选择最好的轮廓系数作为K值的候选参数；

#
#
#
# 最新更新：将本文件修改为一个输出选择KMeans的K值选择的函数模块，从而返回最好的K值参数以供选择
#
#
#

import sys
from sklearn.cluster import KMeans
from sklearn.preprocessing import scale
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
import numpy as np
import sklearn.metrics as skm
import sklearn.decomposition as skd
import copy

# 计算两个点的欧式距离
def Distance(Pa, Pb):
    dist = 0.0
    i = 0
    while i < len(Pa):
        dist += (Pa[i] - Pb[i]) * (Pa[i] - Pb[i])
        i += 1
    dist = np.sqrt(dist)
    return dist
# 定义一个列表的in比较方法
def ListA_In_ListB(A, B):
    # A是一个单独列表
    # B是一个列表集合
    FlagIn = False
    for x in B:
        i = 0
        while i < len(A):
            if A[i] != x[i]:
                break
            else:
                i += 1
        if i == len(A):
            FlagIn = True
    return FlagIn

# 1，计算样本i到同簇其他样本的平均距离ai。ai 越小，说明样本i越应该被聚类到该簇。将ai 称为样本i的簇内不相似度。
# 簇C中所有样本的a i 均值称为簇C的簇不相似度。
# 2，计算样本i到其他某簇Cj 的所有样本的平均距离bij，称为样本i与簇Cj 的不相似度。定义为样本i的簇间不相似度：bi =min{bi1, bi2, ..., bik}
# bi越大，说明样本i越不属于其他簇。

# 计算一个点到一个簇的所有点的平均距离
def Dist_Pt_Clst(Pa, Clst_a):
    dist = 0.0
    for pt in Clst_a:
        dist += Distance(Pa, pt)
    # 如果样本中包含Pa，那么计算平均距离时除以len(Clus_a) - 1
    if ListA_In_ListB(Pa, Clst_a):
    #if Pa in Clst_a:
        if len(Clst_a) > 1:
            dist = dist / (len( Clst_a) - 1)
            return  dist
        else:
            return 0.0
    # 如果样本中不包含Pa，那么计算平均距离时正常计算
    if ListA_In_ListB(Pa, Clst_a) == False:
    #if Pa not in Clst_a:
        dist = dist / len(Clst_a)
        return dist
# 计算样本点Pa的簇间不相似度
def B(Pa, Clusters_Users): # 输入群簇用户列表，且Pa不属于这些群簇
    B_lst = []
    for c_users in Clusters_Users:
        # c_users代表特定群簇中的所有用户,c_users中的每个用户即为Clst_a中的每个pt
        B_lst.append(Dist_Pt_Clst(Pa, c_users))
    return min(B_lst)

# 计算一个群簇用户集合的轮廓系数
def SC_Clusters(k, Clusters_Users_lst):
    # k表示现在有几个群簇
    SC_users = [] # 用于存储所有用户的轮廓系数
    i = 0
    while i < k:
        cnt_ = 0
        # 数据比较大小，如果一摸一样可以用np.all
        for user in Clusters_Users_lst[i]:
            Other_Clusters_Users = []
            j = 0
            while j < k:
                # print Clusters_Users_lst[j], '\n'
                # c = np.all([user, Clusters_Users_lst[j]], axis=0)
                # print c.all(), '\n'
                if ListA_In_ListB(user, Clusters_Users_lst[j]) == True:
                    j += 1
                    continue
                Other_Clusters_Users.append(Clusters_Users_lst[j])
                j += 1
            # 上步得到了用户不属于的群簇列表
            B_user = B(user, Other_Clusters_Users)
            A_user = Dist_Pt_Clst(user, Clusters_Users_lst[i])
            Cmp_lst = []
            Cmp_lst.append(A_user)
            Cmp_lst.append(B_user)
            SC_user = (B_user - A_user) / max(Cmp_lst)
            SC_users.append(SC_user)
            # print '第 ', cnt_, '个用户计算完毕...\n'
            cnt_ += 1
        print k, '第 ', i, '群簇轮廓系数计算完毕...\n'
        i += 1
    SC_users_array = np.array(SC_users)
    return SC_users_array.mean()

print '....<<<<KMeans关键参数K的自选择模块>>>>....\n\n'

print '....<<<<提供[2，3，4...10]的参数作为选择空间>>>>....\n\n'

print '开始KMeans模块选择算法，输出最优的K值和对应的轮廓系数...\n\n'

print '注意！请输出处理好的数组，返回最优的K值以及对应的轮廓系数...\n\n'


# print '开始测试选择最优的K值（KMeans）...\n'
# K值尝试从2-10
# 每个K值会计算三次，选择轮廓系数最高的一个值作为该K值的代表
# 最后输出轮廓系数的最大值以及对应的K值，返回该值
# 一个K值的KMeans的轮廓系数为SC_K = K个聚类中所有点的轮廓系数的均值
# SC_pt = B(pt) - A(Pt) / max(A(pt), B(pt))
# 轮廓系数越接近1越好，越大越好

def Auto_K_Choice(JS_lst, K_range):
    SC_lst = [] # 轮廓系数列表，保存K值与对应的轮廓系数
    # a = [2,3,4,5,6,7,8,9,10,11,12]
    a = range(K_range + 1)[2:]
    for k in a:
        print '现在实验的K值为 ', k, '\n'
        print '每个K值需要实验三次以避免局部最优偏见...\n'
        # 先做PCA降维到5（原先17）
        #pca = PCA(n_components=2)
        #pca.fit_transform(JS_lst)
        #JS_lst = MinMaxScaler().fit_transform(JS_lst)
        #print 'PCA降维完成...\n'
        print '..<<在进行KMeans分析前首先进行归一化MinMax>>..\n\n'
        JS_lst_minmax = MinMaxScaler().fit_transform(JS_lst)
        #JS_lst = scale(JS_lst)
        #JS_lst = skd.PCA().fit_transform(JS_lst)
        SC_tmp = [] # 保存本次K值的三次实验结果，K值与对应的轮廓系数
        i = 0
        while i < 3: # 同一个K值进行10次K均值聚类
            y_pred = KMeans(n_clusters=k).fit(JS_lst_minmax).labels_
            print k, 'KMeans单次聚类完成\n'
            # 接下来开始计算此时的轮廓系数
            SC_value = skm.silhouette_score(JS_lst_minmax, y_pred)
            # SC_value = SC_Clusters(k, clusters_users)
            print i, '完成\n'
            tmp_0 = []
            tmp_0.append(SC_value)
            tmp_0.append(y_pred)
            SC_tmp.append(tmp_0)
            print k, ':', i, ':', tmp_0[0], '\n'
            i += 1
        SC_values = [] # 用于存储选中的K-SC值对
        SC_values.append(k)
        # 修改后的代码需要从[SC1, y_pred1], [SC2, y_pred2], [SC3, y_pred3]中选出最大的SCx，返回对应的y_predx
        sc_tmp = []
        for ele in SC_tmp:
            sc_tmp.append(ele[0])
        sc_max = max(sc_tmp)
        for ele in SC_tmp:
            if ele[0] == sc_max:
                SC_values.append(sc_max)
                SC_values.append(ele[1])
        #SC_values.append(max(SC_tmp))
        SC_lst.append(SC_values)
    print '..<<K = [2, ', K_range, ' ]的KMeans聚类的轮廓系数计算完毕>>..\n\n'
    print '各个K值的K均值聚类的最优轮廓系数为： \n'
    for line in SC_lst:
        print 'SC_lst is ', '\n'
        print 'K值为： ',line[0], ' 轮廓系数为 ',line[1], '\n'
    print '其中轮廓系数最高的K值为: \n'
    SC_value = 0.0
    K_best = 0
    Y_Pred_0 = []
    for line in SC_lst:
        if line[1] > SC_value:
            SC_value = line[1]
            K_best = line[0]
            Y_Pred_0 = copy.copy(line[2])
    print '..<<最优的K值与对应的轮廓系数为： ',K_best, SC_value, '>>..\n\n'
    return K_best, SC_value, Y_Pred_0














