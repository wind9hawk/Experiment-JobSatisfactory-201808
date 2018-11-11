# coding:utf-8

# 本模块是实验系列7的预测器模块
# 首先是需要导入的模块

import os,sys
import numpy as np
import sklearn.preprocessing as skp
import sklearn.metrics as skm
import sklearn.decomposition as skd
import shutil
import copy
import math

import V07_Email_Filter_Feats

# 其次是关于预测器的功能说明
# 预测器模块：
# 1.构建预测器模块：
# 分析当月CERT5.2所有用户的邮件通信情况，与当月离职情况交叉匹配后得到该月该用户需分析的离职联系人；
# 从当月及以前的邮件通讯中提取该用户的邮件9元特征，
# 提取该用户的离职联系人的OCEAN特征；
# 提取该用户与离职联系人的OS距离（四位OS异或码的十进制）
# 将上述三类特诊按照人格、OS距离、邮件的形式拼接得到该用户的离职联系人Relationship Level特征，并按照公式计算其对应的RL值，写入到文件中user-id_RL_feat-version.csv
# 2.运行预测器模块：
# 依据该用户的离职联系人的RL数值，求其和作为该用户的JS_Risk值；
# 重复上述步骤，计算完毕CERT5.2所有用户（除去CEO），并保存到本次预测器的结果文件（JS_Risk由高到低）【两个文件，一个是排序的全部JS_Risk文件，一个是按照既定比例输出的低满意度嫌疑用户：month_ratio_LJSR.csv】

# 函数调用形式
# rl_value_month = Build_Predictor(cert_users, f_ocean_lst. ldaps_path, emails_path, f_leave_month_lst, dst_dir)
#     # data-1：原始邮件目录All_Email_Rcds_Path，用于匹配提取该月及以前的邮件通信
#     # data-2: 当月离职用户文件信息：f_Leave_OnMonth
#     # data-3: CERT5.2全体用户列表，用于该月份循环遍历，生成每个用户的RL特征表与JS_Risk特征
#     # data-4: CERT5.2全体用户的OCEAN数据，f_OCEAN_lst
#     # data-5: CERT5.2全体用户的LDAP数据All_LDAP_Path【month_no筛选即可】
#     # data-6: 结果的输出目录
#     # 返回携带有RL值的用户RL特征表

# 定义一个给定user_id与OCEAN_src，自动返回其对应的大五人格分数的函数调用
def Extract_OCEAN(user, f_ocean_lst):
    user_ocean = []
    for line in f_ocean_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        # OCEAN数据格式
        # employee_name,user_id,O,C,E,A,N
        if line_lst[1] == 'user_id':
            continue
        else:
            if line_lst[1] == user:
                user_ocean.append(float(line_lst[2]))
                user_ocean.append(float(line_lst[3]))
                user_ocean.append(float(line_lst[4]))
                user_ocean.append(float(line_lst[5]))
                user_ocean.append(float(line_lst[6]))
                break
    print user, 'float(OCEAN Score)提取完毕..\n', user_ocean, '\n'
    return user_ocean

# 定义一个给定user与ldap_src，自动返回其组织结构OS信息的函数
def Extract_LDAP(user, f_ldap_lst):
    user_ldap = []
    for line in f_ldap_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        # LDAP文件内容格式
        # employee_name,user_id,email,role,projects,business_unit,functional_unit,department,team,supervisor
        if line_lst[1] == 'user_id':
            continue
        if len(line_lst) < 10:
            # CEO
            continue
        if line_lst[1] == user:
            # 补充上了项目+LDAP信息
            # 项目信息用于日后分析备用
            user_ldap.append(line_lst[4])
            user_ldap.append(line_lst[5])
            user_ldap.append(line_lst[6])
            user_ldap.append(line_lst[7])
            user_ldap.append(line_lst[8])
            break
    print user, 'Project + LDAP提取完毕..\n', user_ldap, '\n'
    return user_ldap


def Build_Predictor(cert_users, f_ocean_lst, ldap_path, emails_path, f_leave_month_lst, dst_dir, month):
    # 参数说明
    # cert_users: 全局变量 CERT52_Users，其中提出了CEO【AEH0001 】
    # OCEAN分数文件行：f_ocean_lst
    # 当前月份LDAP文件路径列表：ldap_path，第一个是Dir\2009-12.csv
    # 所有用户所有月份的邮件记录文件路径列表，可以用user_id作为检测关键字：emails_path
    # 当月离职用户文件行：f_leave_month_lst
    # 当前程序的结果输出目录，对于预测器而言，输出结果在本月，而检验器的输出在下一个月

    # 返回值为当月所有CERT52用户的Relationship_Level值列表
    # 初始化该函数内全局列表
    cert52_users_rlv = []

    # 初始化一个保存当月所有用户的relation_level_feats的目录
    rl_feats_dir_month = dst_dir + '\\' + 'Relationship_level_Feats'
    if os.path.exists(rl_feats_dir_month) == False:
        os.mkdir(rl_feats_dir_month)
    print 'cert_users 共有： ', len(cert_users), '\n'

    # 接下来针对每个用户分别生成其独特的Relation_Level_Feat文件
    # user_relation_level_feats.csv
    # contact_1, ocean_feat, os_feat, email_feat, rl_value
    for user in cert_users:
        # 首先生成该用户的OCEAN分数，该分数需要之后与离职联系人比较生成ocean_feat
        # ocean_feat: distance(ocean)
        # os_feat: distance(os)
        user_ocean = Extract_OCEAN(user, f_ocean_lst)
        print user, 'OCEAN特征分数为：', user_ocean, '\n'

        # 接下来需要确定离职联系人有谁，并依据此确定其relation_level_feat
        # 接下来在生成该用户的Relation_Level_Feats前，需要首先确定要分析该用户的哪些离职的邮件联系人
        # 首先读入当月组织内部所有离职的用户
        # 其次应读入该用户当月及以前的所有邮件记录，与当月离职用户列表取交集，仅对离职的联系人提取邮件特征
        # 定义当月离职用户列表
        leave_users_month = []
        for line in f_leave_month_lst:
            line_lst = line.strip('\n').strip(',').split(',')
            # 当月离职用户数据格式
            # RMB1821,2010-02-09,Rose Maisie Blackwell,RMB1821,Rose.Maisie.Blackwell@dtaa.com,Salesman,,1 - Executive,5 - SalesAndMarketing,2 - Sales,5 - RegionalSales,Donna Erin Black,
            leave_users_month.append(line_lst[0])
        # 生成用户该月与离职联系人的邮件通讯特征
        user_email_feat = V07_Email_Filter_Feats.Extract_Email_Feat(user, leave_users_month, emails_path, dst_dir, month)
        # 返回的离职邮件联系人特征数据格式为列表：
        # [[WMH1300,1.0,2.0,[2010-01-04; 2010-01-30],26533.5,0.0,0,[],0,0,2,1], ...]

        # 针对每一个离职联系人，生成与用户user对应的RL特征
        f_ldap = open(ldap_path, 'r')
        f_ldap_lst = f_ldap.readlines()
        f_ldap.close()
        user_ldap = Extract_LDAP(user, f_ldap_lst)
        # 定义一个保存用户user的离职联系人的特征列表
        user_leave_rl_feats = []
        if len(user_email_feat) == 0:
            print user, month, '离职联系人不存在...跳过\n'
            continue
        for em_feat in user_email_feat:
            user_leave_rl_feat_0 = []
            leave_contacter = em_feat[0]
            lcontacter_ocean = Extract_OCEAN(leave_contacter, f_ocean_lst)
            lcontacter_ldap = Extract_LDAP(leave_contacter, f_ldap_lst)
            #
            # 首先构建离职联系人的OCEAN距离
            #
            distance_ocean = 0.0
            i = 0
            while i < 5:
                distance_ocean += math.pow(user_ocean[i] - lcontacter_ocean[i], 2)
                i += 1
            distance_ocean = math.pow(distance_ocean, 0.5)
            print user, leave_contacter, 'OCEAN距离计算完毕...\n'
            #
            # 其次构建四位二进制OS距离
            #
            os_code = []
            i = 1
            while i < 5:
                print i, '\n'
                if user_ldap[i] == lcontacter_ldap[i]:
                    os_code.append(0)
                    i += 1
                    continue
                else:
                    os_code.append(1)
                    i += 1
                    continue
            distance_os = 0.0
            print os_code, '\n'
            i = 0
            while i < 4:
                distance_os += os_code[i] * math.pow(2, len(os_code) - i)
                i += 1
            print user, leave_contacter, 'LDAP距离计算完毕...\n'
            #
            # 从函数中得到的用户与离职联系人的邮件通信特征中提取最终计算需要的邮件特征
            # 都在em_feat中
            # # [[WMH1300,1.0,2.0,[2010-01-04; 2010-01-30],26533.5,0.0,0,[],0,0,2,1], ...]
            user_leave_rl_feat_0.append(em_feat[0])
            # o,c,e,a,n, dis_ocean
            for ele in lcontacter_ocean:
                user_leave_rl_feat_0.append(ele)
            user_leave_rl_feat_0.append(distance_ocean)
            # business, function, dpt, team, dis_os
            for ele in os_code:
                user_leave_rl_feat_0.append(ele)
            user_leave_rl_feat_0.append(distance_os)
            # email的九元特征，去掉两个天数列表



        #sys.exit()


