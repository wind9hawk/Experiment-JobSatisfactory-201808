# coding:utf-8
# 本脚本主要根据统计出的CERT5.2中用户邮件通讯的7元组特征进行KMeans聚类，并利用中心数值标记出亲密度关系好的群簇作为Friends集合；
# 然后依据五个层次的组织架构关系依据对应的五个层次计算每个层次离职friend的个数，加权计算得到该用户的JS_Risk指数；
# 该做法的理论假设是用户的人际关系中，离职/被解雇的朋友会对该用户的JS产生影响，除去攻击场景中指标的leave为，默认全部为被解雇离开；

import numpy as np
import KMeans_Module
from sklearn.cluster import KMeans
import os,sys
import shutil
from sklearn.preprocessing import MinMaxScaler
import math
# b_lst = a_lst (浅复制，同一个内存对象)
# c_lst = copy.copy(a_lst)  (深复制，不同的内存对象，相互独立)
import copy # 列表深复制

# 定义一个群簇中心点的定性指标计算函数
def Cal_RelationLevel(sr, s1, s2, s3, r1, r2, r3):
    RL = math.log10(1 + (1 - abs(sr)) * (s1 * s2 + r1 * r2) * (s1 * s3 + r1 * r3))
    return RL

# 定义了一个自动输出由大到小的索引函数
# 如输入杂乱的五个群簇中心点的定性量表示，要求依次输出定性表示最高的K/2个中心点代表的群簇索引
def Center2FriendIndex(Centers, K):
    # 要求输入一个原始的中心值定性表示列表
    Index_dic = {}
    i = 0
    while i < len(Centers):
        Index_dic[Centers[i]] = i
        i += 1
    if K % 2 == 0:
        turn = K/2
    else:
        turn = K/2 + 1
    Index_Friends = []
    j = 0
    while j < turn:
        index_0 = Index_dic[max(Centers)]
        Index_Friends.append(index_0)
        Centers.remove(max(Centers))
        j += 1
    return Index_Friends


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
# 打开离职人员关系文件
#f_laidoff = open(r'CERT5.2-LaidOff_Relationship.csv', 'r')
f_laidoff = open(r'CERT5.2-Leave-Relationship.csv', 'r')
f_lo_lst = f_laidoff.readlines()
f_laidoff.close()
# 初始化最终的用户JS_Risk列表
JS_Risk = []
# 初始化建立一个用于记录所有用户JS_Risk数据的文件CERT5.2_JS_Risks.csv
f_JS_Risks = open('CERT5.2_JS-Risks-0.1.csv', 'w')
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
        # 如果邮件名不是企业规范名称，不分析，跳过
        if len(line_lst[0]) != 7:
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



    # 接下来需要根据KMeans得到的聚类群簇，形成K个群簇的用户集合，并计算中心点的统计特征，并以此标记出亲密关系强的群簇
    print '..<<考虑依据群簇中心点特征，标记出亲密群簇>>..\n\n'
    # 简单列举以下群簇标记的方法步骤
    # 1. 对原始数据进行MinMax归一化
    # 2. 依据既定的群簇标记，形成K个用户群簇集合
    # 3. 计算每个群簇集合中的定性的RelationLevel
    # 3.1 RelationLevle = ln(1 + |1 - Email_Ratio| * (MinMax_Cnt_Snd * MinMax_Avg_Snd + MinMax_Cnt_Recv * MinMax_Avg_Recv +
    # MinMax_Cnt_Snd * MinMax_Avg_S_Attach + MinMax_Cnt_Recv * MinMax_Avg_R_Attach))
    # 创建两个用于保存用户群簇的大列表，一个保存用户ID，一个保存用户特征
    Clusters_Users = [[] for i in range(k)]
    Clusters_Feats = [[] for i in range(k)]
    # 重新读取用户对应的邮件通讯特征，并进行MinMax化；
    # 需要用到读取的通讯特征user_contacts，user_contacts_feats以及标签列表y_pred
    i = 0
    while i < len(user_contacts):
        user_contacts_feats_mm = MinMaxScaler().fit_transform(user_contacts_feats)
        Clusters_Users[y_pred[i]].append(user_contacts[i])
        Clusters_Feats[y_pred[i]].append(user_contacts_feats_mm[i])
        i += 1
    print '..<<群簇用户列表以及对应特征整理完毕>>..\n\n'

    print '..<<开始计算各个群簇中心点坐标，并依据公式计算其对应的RelationLevel定性指标>>..\n\n'
    # 定义一个存放群簇中心点的RelationLevel数值
    Cluster_RL = []
    for cls in Clusters_Feats:
        # 数据示例：0.298245614035,37.0,399952.513514,0.351351351351,20.0,30114.15,0.0,
        sr = 0.0
        s1 = 0
        s2 = 0
        s3 = 0
        r1 = 0
        r2 = 0
        r3 = 0
        for line in cls:
            sr += line[0]
            s1 += line[1]
            s2 += line[2]
            s3 += line[3]
            r1 += line[4]
            r2 += line[5]
            r3 += line[6]
        sr = sr / len(cls)
        s1 = s1 / len(cls)
        s2 = s2 / len(cls)
        s3 = s3 / len(cls)
        r1 = r1 / len(cls)
        r2 = r2 / len(cls)
        r3 = r3 / len(cls)
        print '本群簇大小为： ', len(cls), '中心点坐标为： ', sr, s1, s2, s3, r1, r2, r3, '\n\n'
        rl = Cal_RelationLevel(sr, s1, s2, s3, r1, r2, r3)
        Cluster_RL.append(rl)
    print file[0:7], '\n群簇中心RelationLevel计算完毕...\n\n'
    # 选择RL最大的一个中心代表的群簇，作为Friends级别
    Cluster_RL_0 = copy.copy(Cluster_RL)
    Index_Friends = Center2FriendIndex(Cluster_RL_0, k)
    print file[:7], k, '选中的friends群簇标号为： \n'
    print 'Cluster_RL is ', Cluster_RL, '\n'
    for line in Index_Friends:
        print line, Cluster_RL[line], '\n'
    # 将该用户此次KMeans的全部分类结果存放到该用户的聚类结果文件中
    # 选中的Friends群簇自然用户表示为Cluster_Users[Index_Friends]和Cluster_Feats[Index_Friends]
    f_2 = open(EmailFeats_Dir + '\\' + file[0:7] + '_KMeans_Clusters.csv', 'w')
    i = 0
    while i < k:
        f_2.write('Cluster' + str(i) + '\n')
        for user in Clusters_Users[i]:
            f_2.write(user)
            f_2.write(',')
        f_2.write('\n')
        i += 1
    f_2.close()
    # single cluster: Cluster_Friends
    # multiple clusters: Clusters_Users
    # Cluster_Friends = copy.copy(Clusters_Users[Index_Friends])
    # Cluster_Friends_Feats = copy.copy(Clusters_Feats[Index_Friends])
    Cluster_Friends = []
    # 不区分朋友亲密等级，而仅仅二元区分是不是朋友
    for index in Index_Friends:
        for usr in Clusters_Users[index]:
            Cluster_Friends.append(usr)
    Cluster_Friends_Feats = []
    for index in Index_Friends:
        for feat in Clusters_Feats[index]:
            Cluster_Friends_Feats.append(feat)


    print '..<<', file[0:7], 'Friends群簇分析完毕>>..\n\n'
    print '朋友共有： ', len(Cluster_Friends), '\n'
    i = 0
    while i < len(Cluster_Friends):
        print i, Cluster_Friends[i], Cluster_Friends_Feats[i], '\n'
        i += 1
    print '..<<朋友群簇信息分析完毕>>..\n\n'

    # 开始结合离职人员数据计算该用户的JS_Risk
    # 离职人员数据格式：CERT5.2-LaidOff_Relationship.csv
    # MTD0971,2010-10:
    # Insider_LaidOff_0,NWH0960,GWH0961,
    # Insider_LaidOff_1,FAM0495,BNS0484,GWG0497,
    # Insider_LaidOff_2,SDL0541,LRF0549,NTV1777,HBH0111,BRM0126,HFF0560,MMB0556,PTV0067,MGM0539,OJC0930,
    # Insider_LaidOff_3,RMB1821,WSW1091,CTH1812,JBG1375,JHP1654,NWP1609,JDM0208,HSF1115,FDS1841,GMM1037,MAF0467,ZAD1621,XMG1579,KBC0818,TAG1610,EAL1813,WBP0828,MAR1075,JXH1061,UAM1108,LSM1382,CIM1095,CKP0630,JKM1790,ZHB1104,PTM1432,CIF1430,KLB0918,TNB1616,IVS1411,DHS0204,DDR1649,MFM1400,TTR1792,
    # Insider_LaidOff_4,JAT1218,ADL1898,KSW0708,WMH1300,LAS0256,GWO1660,MIB1265,TCP0380,CBC1504,JSB0860,CDO0684,KDP1706,CDG0770,FKH0864,CLL0306,JRC1963,QSG1150,QAP0266,BAR1328,OCW1127,PKS1187,GER0350,BSS0847,OCD1985,USM0703,RKW1936,RFP1918,RDP1751,FKS1696,BMR0865,AWW0718,EJO0236,HKK0881,ESP1198,MMR1458,JIB1258,SCO1719,ZJN1492,ZIE0741,DTB0722,CEW1960,ILG0879,DMP0344,DEO1964,CNM0787,NBL1190,ALT1465,WHG1669,SMS0432,WFV0687,STH0353,RPJ1159,JKB0287,ELM1123,
    # NHB1529,No:
    #　直接分析本目录下的离职人员数据，从中找到对应用户的信息
    j = 0
    while j < len(f_lo_lst):
        line_lst = f_lo_lst[j].strip('\n').strip(',').split(',')
        # 首先需要定位目标用户的离职人员关系数据位置
        if file[:7] not in line_lst[0]:
            j += 1
            continue
        else:
            # 此时第j行正好时目标用户
            Cnt_LaidOff_Friends = [[0.0] for i in range(5)]
            # N个关系层级，1/N为级差，这里N为5，故而选择0.2
            Weight_Level = [[float(i/5)] for i in range(5)]
            # q表示五个组织层次，p表示每个层次中的用户坐标
            q = 0
            while q < 5:
                # 分别分析每个层级中离职的friends个数
                p = 1
                while p < len(f_lo_lst[j + q + 1]):
                    if f_lo_lst[j + q + 1][p] in Cluster_Friends:
                        Cnt_LaidOff_Friends[q] += 1
                        p += 1
                        continue
                    else:
                        p += 1
                        continue
                q += 1
                continue
            js_risk = 0.0
            n = 0
            while n < 5:
                js_risk += Cnt_LaidOff_Friends[n][0] * Weight_Level[n][0]
                n += 1
            tmp_1 = []
            tmp_1.append(file[0:7])
            tmp_1.append(js_risk)
            JS_Risk.append(tmp_1)
            print '\n....<<<<',file[0:7], 'JS_Risk is ', js_risk, '>>>>.....\n\n'
            break
    f_JS_Risks.write(tmp_1[0])
    f_JS_Risks.write(',')
    f_JS_Risks.write(str(tmp_1[1]))
    f_JS_Risks.write('\n')


print '....<<<<将Insiders与Users的邮件通讯特征文件导入到既定的CERT5.2_EmailContactFeats目录下，完毕>>>>....\n\n'




sys.exit()





