# coding:utf-8
# 本脚本主要根据统计出的CERT5.2中用户邮件通讯的7元组特征进行KMeans聚类，并利用中心数值标记出亲密度关系好的群簇作为Friends集合；
# 然后依据五个层次的组织架构关系依据对应的五个层次计算每个层次离职friend的个数，加权计算得到该用户的JS_Risk指数；
# 该做法的理论假设是用户的人际关系中，离职/被解雇的朋友会对该用户的JS产生影响，除去攻击场景中指标的leave为，默认全部为被解雇离开；

import numpy as np
import KMeans_Module
from sklearn.cluster import KMeans
import os,sys
import shutil



print '....<<<<CERT5.2用户邮件联系特征数据定位准备开始>>>>....\n\n'
# 首先需要指定几个文件夹目录
# 存放邮件统计7元组特征的文件目录：
# Insiders_2目录：
Insiders_2_EmailFeats_Dir = r'G:\GitHub\Essay-Experiments\CERT5.2-Results\CERT5.2-Insiders_2-EmailRecords'
# 1000个普通用户的邮件统计7元组特征文件目录：
Users_EmailFeats_Dir = r'G:\GitHub\Essay-Experiments\CERT5.2-Results\CERT5.2-Users-EmailRecords'
# 由于邮件feats文件名称类似[BYO1846-feats.csv]，因此，需要在上述目录下过滤掉邮件记录
# 将上述所有要分析的用户的邮件联系人七元组特征拷贝到程序目录下
EmailFeats_Dir = sys.path[0] + '\\' + r'CERT5.2_EmailContactFeats-0.1'
if os.path.exists(EmailFeats_Dir) == False:
    os.makedirs(EmailFeats_Dir)
# 之后所有的数据分析就在[CERT5.2_EmailContactFeats-1030]目录下进行即可
print '....<<<<CERT5.2用户邮件联系特征数据定位完毕>>>>....\n\n'



print '....<<<<将Insiders与Users的邮件通讯特征文件导入到既定的CERT5.2_EmailContactFeats目录下>>>>....\n\n'
print '..<<先导入Insiders_2攻击者邮件通讯特征文件>>..\n\n'
for file in os.listdir(Insiders_2_EmailFeats_Dir):
    if 'feat' not in file:
        continue
    else:
        # 这是需要的用户邮件通讯特征文件
        # 利用shutil库的copy命令实现文件的复制
        shutil.copy(Insiders_2_EmailFeats_Dir + '\\' + file, EmailFeats_Dir)
        print 'Insiders_2: ', file, '复制到目标目录，完毕...\n'
print '..<<再导入普通用户Users邮件通讯特征文件>>..\n\n'
for file in os.listdir(Users_EmailFeats_Dir):
    if 'feat' not in file:
        continue
    else:
        # 这是需要的用户邮件通讯特征文件
        # 利用shutil库的copy命令实现文件的复制
        shutil.copy(Users_EmailFeats_Dir + '\\' + file, EmailFeats_Dir)
        print 'Users: ', file, '复制到目标目录，完毕...\n'
print '....<<<<将Insiders与Users的邮件通讯特征文件导入到既定的CERT5.2_EmailContactFeats目录下，完毕>>>>....\n\n'



print '....<<<<开始就每个用户的邮件通讯特征依次进行聚类、群簇中心计算与标记、JS_Risk计算>>>>....\n\n'
# 邮件联系特征数据样例
# BYO1846-feats.csv
# Macy_Patterson,0.472222222222,17.0,362672.941176,0.411764705882,36.0,104119.388889,0.138888888889,
# Carol_Copeland,-1.0,5.0,285675.2,0.2,0.0,0.0,0.0,
# WAS1823,1.0,47.0,157937.87234,0.148936170213,47.0,118080.361702,0.170212765957,
# 定义一个存放所有用户ID顺序的列表
CERT52_Users = []
for file in os.listdir(EmailFeats_Dir)[:1]:
    CERT52_Users.append(file[0:7])
    # 读取该文件，并提取出单独的通讯用户列表以及通讯特征
    print '..<<提取', file[0:7], ' 的邮件通讯列表及其通讯特征>>..\n\n'
    # 存储该用户的邮件通讯用户顺序
    user_contacts = []
    # 存储该用户的数组化邮件通讯特征列表
    user_contacts_feats = []
    f_0 = open(EmailFeats_Dir + '\\' + file, 'r')
    f_0_lst = f_0.readlines()
    f_0.close()
    for line in f_0_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        if len(line_lst) < 2:
            continue
        user_contacts.append(line_lst[0])
        tmp_0 = []
        for ele in line_lst[1:]:
            tmp_0.append(float(ele))
        user_contacts_feats.append(tmp_0)
    print '..<<', file[0:7], '邮件通讯特征读取完毕>>..\n\n'

    print '..<<首先计算适合的聚类K值>>..\n\n'
    k, para, y_pred = KMeans_Module.Auto_K_Choice(user_contacts_feats)
    print '..<<对于', file[:7], '而言KMeans最好的聚类个数是： ', k, para, '>>..\n\n'
    #print '最佳的分类结果是： \n'
    #for ele in y_pred:
    #    print ele, '\t'
    print '..<<考虑将最好的结果分类写入到文件中保存起来>>..\n\n'
    # 保存后格式为：Darryl_J_Hays,0.0,0.0,0.0,0.0,1.0,609625.0,1.0,0
    f_1 = open(EmailFeats_Dir + '\\' + file[:7] + '_KMeans_Pred.csv', 'w')
    i = 0
    while i < len(user_contacts):
        f_1.write(user_contacts[i])
        f_1.write(',')
        for ele in user_contacts_feats[i]:
            f_1.write(str(ele))
            f_1.write(',')
        f_1.write(str(y_pred[i]))
        f_1.write('\n')
        i += 1
    f_1.close()
    print '..<<考虑将最好的结果分类写入到文件中保存起来，完毕>>..\n\n'
print '....<<<<将Insiders与Users的邮件通讯特征文件导入到既定的CERT5.2_EmailContactFeats目录下，完毕>>>>....\n\n'




sys.exit()





