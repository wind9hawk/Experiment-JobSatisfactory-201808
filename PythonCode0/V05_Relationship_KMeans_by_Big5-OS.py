# coding:utf-8
# 本模块主要转变视角，从用户自身的角度出发，与全体用户进行聚类匹配
# 从而发现包含该用户的群簇作为其不可见的Relationship
# 后续将使用上述Relationshop与离职用户分析

import os,sys
import sklearn.preprocessing as skp
import sklearn.cluster as skc
import sklearn.decomposition as skd
import sklearn.metrics as skm
import shutil
import copy
import math
import V_05_KMeans_Module

import KMeans_Module

print '......<<<<<<以用户为中心的关系特征聚类算法>>>>>>......\n\n'

print '....<<<<首先需要构造用户的关系特征>>>>....\n\n'

# 构造用户的OCEAN特征
def Build_OCEAN_Feat(f_ocean_lst):
    # f_ocean_lst为psychometric文件readlines()结果
    # 定义返回的OCEAN特征列表
    user_ocean_fests = []
    # 数据样例
    # employee_name,user_id,O,C,E,A,N
    # Maisie Maggy Kline,MMK1532,17,17,16,22,28
    for line in f_ocean_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        if line_lst[1] == 'user_id':
            continue
        else:
            tmp_0 =[]
            tmp_0.append(line_lst[1])
            for ele in line_lst[2:]:
                tmp_0.append(float(ele))
            user_ocean_fests.append(tmp_0)
            continue
    return user_ocean_fests


# 定义一个函数获取用户的LDAP数据，并计算OS距离
def Cal_Distance_OS(user_src, user_dst, f_ldap_lst):
    # f_ldap_lst为LDAP文件readlines()结果
    # 定义返回的OS距离
    distance_os = 0.0
    # 数据格式样例
    # employee_name,user_id,email,role,projects,business_unit,functional_unit,department,team,supervisor
    # 分析时去掉不够10个的CEO
    for line in f_ldap_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        if line_lst[1] == 'user_id':
            continue
        if len(line_lst) < 10:
            # CEO
            continue
        if line_lst[1] == user_src:
            user_src_ldap = line_lst[5:9]
            continue
        if line_lst[1] == user_dst:
            user_dst_ldap = line_lst[5:9]
            continue
    # 诸位比较user_src/dst_ldap
    for i in range(4):
        #print user_dst, '\n'
        if user_src_ldap[i] == user_dst_ldap[i]:
            # 相同为1
            distance_os += math.pow(2, 3 - i) * 1
            i += 1
            continue
        else:
            # 不同为0
            distance_os += 0
            i += 1
            continue
    return distance_os


# 定义一个函数提取邮件特征
# user_src发给user_dst的邮件封数，占所有发送邮件的比例；
# user_src收到user_dst的邮件封数，占所有收到邮件的比例；
# user_src的特征需要单独构造，即默认为发送邮件总数，1，收到邮件总数，1， 此时其他用户的邮件特征使用上述默认即可；
# 如果构造user_src的邮件特征为0，0，0，0，则其他用户的邮件特征为pow(Cnt_Send/Cnt_Recv, e)的倒数
def Cal_Email_Feat(user_src, user_dst, f_email_feat_lst):
    # f_email_feat_lst为事先user_src的邮件通讯用户特征列表，其中仅考虑了1vs1的发送邮件
    # JLF1315,-0.130434782609,10.0,222931.8,0.5,13.0,390778.153846,0.538461538462,
    # RBA1723,1.0,1.0,23014.0,0.0,0.0,0.0,0.0,
    email_feat = [0,0,0,0]
    total_send_cnt = 0
    total_recv_cnt = 0
    for line in f_email_feat_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        if line_lst[0] == user_dst:
            if float(line_lst[1]) != -1.0:
                email_feat[0] = float(line_lst[2])
                email_feat[2] = float(line_lst[5])
                total_send_cnt += float(line_lst[2])
                total_recv_cnt += float(line_lst[5])
                continue
            else:
                continue
        else:
            if float(line_lst[1]) != -1.0:
                total_send_cnt += float(line_lst[2])
                total_recv_cnt += float(line_lst[5])
                continue
    email_feat[1] = email_feat[0] / total_send_cnt
    email_feat[0] = math.pow(math.pow(math.e, email_feat[0]), -1)
    email_feat[3] = email_feat[2] / total_recv_cnt
    email_feat[2] = math.pow(math.pow(math.e, email_feat[2]), -1)
    return email_feat, total_send_cnt, total_recv_cnt


print '....<<确定分析的用户列表，并提取基于该用户的所有用户的特征>>>>....\n\n'
Single_Email_Dir = sys.path[0] + '\\' + 'CERT5.2_EmailContactFeats-0.2'
Multiple_Email_Dir = sys.path[0] + '\\' + 'CERT5.2_JS-Risk_Analyze-0.4'
CERT52_LDAP_Path = os.path.dirname(sys.path[0]) + '\\' + 'LDAP' + '\\' + '2009-12.csv'
OCEAN_Path = os.path.dirname(sys.path[0]) + '\\' + 'psychometric-5.2.csv'

Insiders_2_Dir = os.path.dirname(sys.path[0]) + '\\' + 'r5.2-2'
Insiders_2_lst = []
for file in os.listdir(Insiders_2_Dir):
    Insiders_2_lst.append(file[7:-4])


# 创建一个新的目录，用于保存新提取得到的关系特征
if os.path.exists(sys.path[0] + '\\' + 'CERT5.2_Big5_OS_Relationship_v0.5') == False:
    os.makedirs('CERT5.2_Big5_OS_Relationship_v0.5')

#用于保存用户所处的群簇信息，其中包含了其所在各自关系的群簇标号，以及群簇人数
Users_Cluster_Info_lst = []
CERT52_Users = []
f_LDAP = open(CERT52_LDAP_Path, 'r')
f_LDAP_lst = f_LDAP.readlines()
f_LDAP.close()
for line in f_LDAP_lst:
    line_lst = line.strip('\n').strip(',').split(',')
    # print line_lst, '\n'
    if len(line_lst) < 10:
        continue
    if line_lst[1] == 'user_id':
        continue
    if line_lst[1] == 'AEH0001':
        # print 'continue\n'
        continue
    print 'line_lst is ', line_lst, '\n'
    CERT52_Users.append(line_lst[1])
#for usr in Insiders_2_lst[:]:
# print 'CERT52_Users is', CERT52_Users, '\n'
for usr in CERT52_Users:
    print '开始分析用户', usr, '\n\n'
    Users_OCEAN_lst = Build_OCEAN_Feat(open(OCEAN_Path, 'r').readlines())
    # Users_OCEAN_lst数据样例格式为[user_1, O, C, E, A, N]
    Relation_Feats = []
    # 接下来需要遍历除去CEO的1999个CERT5.2用户，从而形成以目标用户usr为中心基准的其余用户的关系特征
    i = 0
    while i < len(Users_OCEAN_lst):
        #Users_OCEAN_lst[i][0]为user_id
        if Users_OCEAN_lst[i][0] == usr:
            # 目标用户本人
            tmp_1 = []
            tmp_1.extend(Users_OCEAN_lst[i])
            tmp_1.extend([0.0,0.0,0.0,0.0,0.0])
            Relation_Feats.append(tmp_1)
            i += 1
            continue
        else:
            if Users_OCEAN_lst[i][0] == 'AEH0001':
                print 'CEO不分析\n\n'
                i += 1
                continue
            tmp_2 = []
            tmp_2.extend(Users_OCEAN_lst[i])
            f_2 = open(CERT52_LDAP_Path, 'r')
            tmp_2.append(Cal_Distance_OS(usr, Users_OCEAN_lst[i][0], f_2.readlines()))
            #print Users_OCEAN_lst[i][0], 'OS_Ditance is', tmp_2, '\n\n'

            for file in os.listdir(Single_Email_Dir):
                if usr in file and 'feat' in file:
                    f_3 = open(Single_Email_Dir + '\\' + usr + '-feats.csv', 'r')
                    f_3_lst = f_3.readlines()
                    break
                else:
                    continue
            email_feat, total_send_cnt, total_recv_cnt = Cal_Email_Feat(usr, Users_OCEAN_lst[i][0], f_3_lst)
            tmp_2.extend(email_feat)
            print i, ':', Users_OCEAN_lst[i][0], ' Relation Feat is ', tmp_2, '\n\n'
            Relation_Feats.append(tmp_2)
            i += 1

    print '..<<尝试将', usr, '的关系数据写入文件保存>>..\n\n'
    f_4 = open(sys.path[0] + '\\' + 'CERT5.2_Big5_OS_Relationship_v0.5' + '\\' + usr + '_Relation_Feats.csv', 'w')
    for feat in Relation_Feats:
        for ele in feat:
            f_4.write(str(ele))
        f_4.write('\n')
    f_4.close()
    print '..<<', usr,'的关系数据写入文件保存>>..\n\n'


    print '....<<<<对得到的用户关系特征进行KMeans聚类，以发现其关系群簇>>>>....\n\n'
    # 提取数值部分族称数组
    User_Relation_Names = []
    User_Relation_Feats = []
    for line in Relation_Feats:
        User_Relation_Names.append(line[0])
        User_Relation_Feats.append(line[1:])

    # Minmax归一化,并进行KMeans聚类
    User_Relation_Feats_MinMax = skp.MinMaxScaler().fit_transform(User_Relation_Feats)
    K_best, SC_best, Y_pred = V_05_KMeans_Module.Auto_K_Choice(User_Relation_Feats_MinMax, 10)
    print '最佳的K值以及轮廓系数为： ', K_best, ':', SC_best, '\n'

    # 将聚类结果保存到文件
    User_Clusters = [[] for i in range(K_best)]
    f_5 = open(sys.path[0] + '\\' + 'CERT5.2_Big5_OS_Relationship_v0.5' + '\\' + usr + '_Relation_Clusters.csv', 'w')
    j = 0
    while j < len(User_Relation_Names):
        User_Clusters[Y_pred[j]].append(User_Relation_Names[j])
        j += 1
    Index_Usr = User_Relation_Names.index(usr)
    print usr, '所在群簇为 ', Y_pred[Index_Usr], '人数有： ', len(User_Clusters[Y_pred[Index_Usr]]), '\n'
    j = 0
    for cls in User_Clusters:
        f_5.write('Cluster_' + str(j) + '\n')
        j += 1
        for ele in cls:
            f_5.write(ele)
            f_5.write(',')
        f_5.write('\n')
    f_5.close()
    tmp_3 = []
    tmp_3.append(usr)
    tmp_3.append(Y_pred[Index_Usr])
    tmp_3.append(len(User_Clusters[Y_pred[Index_Usr]]))
    Users_Cluster_Info_lst.append(tmp_3)



print 'Insiders_2的关系特征聚类结果为： \n\n'
for line in Users_Cluster_Info_lst:
    print line, '\n'














