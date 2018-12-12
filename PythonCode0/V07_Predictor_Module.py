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
    # print user, 'float(OCEAN Score)提取完毕..\n', user_ocean, '\n'
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
    # print user, 'Project + LDAP提取完毕..\n', user_ldap, '\n'
    return user_ldap


def Build_Predictor(cert_users, f_ocean_lst, ldap_path, emails_path, f_leave_month_lst, dst_dir, month, have_left_users_month_lst):
    # 参数说明
    # cert_users: 全局变量 CERT52_Users，其中提出了CEO【AEH0001 】
    # OCEAN分数文件行：f_ocean_lst
    # 当前月份LDAP文件路径列表：ldap_path，第一个是Dir\2009-12.csv
    # 所有用户所有月份的邮件记录文件路径列表，可以用user_id作为检测关键字：emails_path
    # 截止到当月已经离职的用户列表，这些用户不需要计算当月的rlv_feat：Have_Left_Users_Month_lst
    # data like: RMB1821 2010-02-09 在  2010-03 前已经离职，不考虑...
    # 当前程序的结果输出目录，对于预测器而言，输出结果在本月，而检验器的输出在下一个月

    # 返回值为当月所有CERT52用户的Relationship_Level值列表
    # 初始化该函数内全局列表
    cert52_users_rlv = []

    # 初始化一个保存当月所有用户的relation_level_feats的目录
    rl_feats_dir_month = dst_dir + '\\' + 'Relationship_level_Feats'
    #if os.path.exists(rl_feats_dir_month) == False:
    #    os.mkdir(rl_feats_dir_month)
    # print 'cert_users 共有： ', len(cert_users), '\n'

    # 接下来针对每个用户分别生成其独特的Relation_Level_Feat文件
    # user_relation_level_feats.csv
    # contact_1, ocean_feat, os_feat, email_feat, rl_value

    # 定义一个存储所有用户的leave_contact_feat是大文件
    print month, '....<<<<建立该月的RLF文件>>>>....\n\n'
    f_users_rl = open(dst_dir + '\\' + month + '_CERT5.2_Users_RL_Feats_1.csv', 'w')
    # 新的格式：
    # user_id, leave_contact_user, rl-feat
    f_users_rl.write('user_id')
    f_users_rl.write(',')
    f_users_rl.write('leave_contact_user')
    f_users_rl.write(',')
    f_users_rl.write('O_Score')
    f_users_rl.write(',')
    f_users_rl.write('C_Score')
    f_users_rl.write(',')
    f_users_rl.write('E_Score')
    f_users_rl.write(',')
    f_users_rl.write('A_Score')
    f_users_rl.write(',')
    f_users_rl.write('N_Score')
    f_users_rl.write(',')
    f_users_rl.write('Dis_OCEAN')
    f_users_rl.write(',')
    f_users_rl.write('OS_Code_1')
    f_users_rl.write(',')
    f_users_rl.write('OS_Code_2')
    f_users_rl.write(',')
    f_users_rl.write('OS_Code_3')
    f_users_rl.write(',')
    f_users_rl.write('OS_Code_4')
    f_users_rl.write(',')
    f_users_rl.write('Dis_OS')
    f_users_rl.write(',')
    f_users_rl.write('Email_Ratio')
    f_users_rl.write(',')
    f_users_rl.write('Cnt_Send')
    f_users_rl.write(',')
    f_users_rl.write('Avg_Send_Size')
    f_users_rl.write(',')
    f_users_rl.write('Avg_Send_Attach')
    f_users_rl.write(',')
    f_users_rl.write('Cent_Recv')
    f_users_rl.write(',')
    f_users_rl.write('Avg_Recv_Size')
    f_users_rl.write(',')
    f_users_rl.write('Avg_Recv_Attach')
    f_users_rl.write(',')
    f_users_rl.write('Cnt_Send_Days')
    f_users_rl.write(',')
    f_users_rl.write('Cnt_Recv_Days')
    f_users_rl.write('\n')
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
        if user in have_left_users_month_lst:
            print user, month, '已经离职：...\n'
            continue
        user_email_feat = V07_Email_Filter_Feats.Extract_Email_Feat(user, leave_users_month, emails_path, dst_dir, month, have_left_users_month_lst)
        # 返回的离职邮件联系人特征数据格式为列表：
        # [[WMH1300,1.0,2.0,[2010-01-04; 2010-01-30],26533.5,0.0,0,[],0,0,2,1], ...]

        # 针对每一个离职联系人，生成与用户user对应的RL特征
        f_ldap = open(ldap_path, 'r')
        f_ldap_lst = f_ldap.readlines()
        f_ldap.close()
        user_ldap = Extract_LDAP(user, f_ldap_lst)
        # 定义一个保存用户user的离职联系人的特征列表
        user_leave_rl_feats = []
        # 为该用户建立一个储存RL特征的文件，该文件最后一个字段为计算的RL值
        # RL_Feat格式：
        # leave_contact, o,c,e,a,n,dis_ocean, os_1,os_2,os_3,os_4, dis_os, email_feat, rl_value
        if len(user_email_feat) == 0:
            # print user, month, '离职联系人不存在...\n'
            # 对于这些没有生成RL值的用户而言，默认其低满意度风险为0
            # 计算RL_Feat时没有这些用户的特征文件
            # 然而当计算总体JS_Risk排序时，需要补充进去，以0补充
            continue
        # 一旦该用户当月存在离职联系人，则需要计算其RL值预示的LJSR
        for em_feat in user_email_feat:
            user_leave_rl_feat_0 = []
            leave_contacter = em_feat[0]
            if leave_contacter == 'AEH0001':
                continue
            lcontacter_ocean = Extract_OCEAN(leave_contacter, f_ocean_lst)
            lcontacter_ldap = Extract_LDAP(leave_contacter, f_ldap_lst)
            #
            # 首先构建离职联系人的OCEAN距离
            #
            distance_ocean = 0.0
            i = 0
            while i < 5:
                #print 'i is :', i, '\n'
                #print 'user_ocean is :', user_ocean, '\n'
                #print 'lcontacter_ocean is ', lcontacter_ocean, '\n'
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
            #  ['WMH1300', 0.0, 4.0, "['2010-01-04'; '2010-01-06'; '2010-01-15'; '2010-01-30']", 40840.75, 0.0,
            # 4.0, "'2010-01-18'; '2010-01-19'; '2010-01-27'; '2010-01-29'", 2856906.75, 8.0]
            user_leave_rl_feat_0.append(user)
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
            j = 1  # user_id没必要再次写入
            while j < len(em_feat):
                if j != 3 and j != 7:
                    user_leave_rl_feat_0.append(em_feat[j])
                    j += 1
                else:
                    j += 1
                    continue
            print em_feat[0], 'rl_feat is ', user_leave_rl_feat_0, '\n'
            # sys.exit()

            # 下面开始将上述离职联系人的邮件特征写入到文件
            # 首先是第一行的字段说明
            # 为了方便将所有用户的离职联系人RL特征放到一起比较，计算，因此需要集合所有特征向量做归一化；
            # 而这就是也需要最终再分别计算单个用户的RL影响程度
            for ele in user_leave_rl_feat_0:
                f_users_rl.write(str(ele))
                f_users_rl.write(',')

            # 上述特征为：
            # AAB1302,WMH1300,39.0,36.0,20.0,40.0,20.0,13.9283882772,0,0,0,0,0.0,0.0,4.0,40840.75,0.0,4.0,2856906.75,8.0,4,4,4,4,
            # 最后没有附加RL值，因为RL值的计算需要利用归一化与RL计算公式
            f_users_rl.write('\n')

    f_users_rl.close()
    # 返回存储该月所有用户离职联系人RL特征的文件路径
    return dst_dir + '\\' + month + '_CERT5.2_Users_RL_Feats.csv'

def Cal_EmailInfo(email_feat):
    er = email_feat[0]
    cnt_send = email_feat[1]
    avg_size_send = email_feat[2]
    cnt_attach_send = email_feat[3]
    # 附件没有求平均
    cnt_recv = email_feat[4]
    avg_size_recv = email_feat[5]
    cnt_attach_recv = email_feat[6]
    rlv_e = math.exp(abs(0.5 - er)) * ((cnt_send * avg_size_send + cnt_recv * avg_size_recv) + (cnt_attach_send + cnt_attach_recv))
    return rlv_e
def Cal_RLV(rlf_process_month):
    # rlf_process_month为得到的10维度RL特征
    rlf_array = np.array(rlf_process_month)
    #print 'rlf_process_month is :\n'
    #for i in range(len(rlf_process_month)):
    #    print i, ':', rlf_process_month[i], '\n'
    # 中间过程在进一步代入公式计算时，全部进行了MinMax归一化
    # 否则，由于特征量纲的不同，导致无法直接在公式中计算
    rlf_minmax = skp.MinMaxScaler().fit_transform(rlf_array)

    # 归一化后顺便计算出各个行RLF的RLV
    # rlv = log(e + dis_ocean + dis_os + email_days + email_informaton)
    # email_information = exp(|0.5 - er|) * (Total email size + Total email Attach)
    # 首先定义一个要返回的RLV列表
    rlv_lst = []
    for line in rlf_minmax:
        # 数据字段顺序
        # AAB1302 WMH1300 [13.9283882772, 0.0, 8.0, 0.0, 4.0, 40840.75, 0.0, 4.0, 2856906.75, 8.0]
        rlv_dis_ocean = line[0]
        rlv_dis_os = line[1]
        rlv_edays = line[2]
        rlv_einfo = Cal_EmailInfo(line[3:])
        # rlv_line = math.log(math.e + rlv_dis_ocean + rlv_dis_os + rlv_edays + rlv_einfo, math.e)
        # 上述计算rlv_line的公式没有考虑dis_ocean与dis_ocean的反向关系
        rlv_line = math.log(math.e + pow(pow(math.e, rlv_dis_ocean), -1) + pow(pow(math.e, rlv_dis_os), -1) + rlv_edays + rlv_einfo, math.e)
        rlv_lst.append(rlv_line)
    #print 'RLV 数值列表统计计算完毕...\n'
    #for i in range(5):
        #print i, 'RLV:', rlv_lst[i], '\n'
    return rlv_lst


# 完成了预测器的生成模块，接下来是执行预测器模块得到JS_Risk值
def Run_Predictor(RL_Feat_Path, Dst_Dir, Risk_Ratio, cert_users, month, month_lst):
    # 生成的用户的RL_Feat_Path的值
    # 结果JSR文件的保存目录
    # month为当前分析的月份
    # month_lst为离职用户月份，不包括2009-12以及2010-01
    # 首先读入RLF结果文件，并生成：
    # 1. 存在RLF的用户列表，后续最终JSR计算需要补齐空白的用户，其JSR=0.0
    # 2. 根据Dis_OCEAN, Dis_OS, Email_Days, Email_Information四个领域分别计算中间特征文件，并保存
    # 3. 依据中间特征文件，进行全部1999个用户的列归一化，然后依据JSR公式计算得到其JSR值；
    # 4. 如果一个用户涉及多个离职联系人，则这些离职联系人JSR的和为该用户下月的JSR
    # 需要定义一个JSR函数模块

    # 正式开始前，先生成已有当月RLF文件中目标用户：离职联系人的索引信息
    # [user_id, [l_contact_0, index_0], [l_contact_1, index_1]]...
    # 定义一个RLF中user_id/leave_contacts/rl feat的关联列表
    # 格式如下：
    # [user_id, leave_contacts, index]
    # 注意！由于原始数据文件有标题行，这里的index是去掉标题行后的索引，原始i - 1
    cert_user_leave_index = []
    # 当月的中间RLF变量：Dis_OCEAN, Dis_OS, Email_Days, Email_Information
    rlf_process_month = []
    f_rlf = open(RL_Feat_Path, 'r')
    f_rlf_lst = f_rlf.readlines()
    f_rlf.close()
    i = 0
    while i < len(f_rlf_lst):
        line_lst = f_rlf_lst[i].strip('\n').strip(',').split(',')
        if line_lst[0] == 'user_id':
            i += 1
            continue
        else:
            tmp_0 = []
            tmp_0.append(line_lst[0])
            tmp_0.append(line_lst[1])
            tmp_0.append(i - 1)
            cert_user_leave_index.append(tmp_0)

            # 有了用户与RLF之间的对应关系，可以仅提取后面的数值部分，以建立
            rlf_process_tmp = []

            # RLF特征数据格式：
            # user_id,leave_contact_user,O_Score,C_Score,E_Score,A_Score,N_Score,Dis_OCEAN,
            # OS_Code_1,OS_Code_2,OS_Code_3,OS_Code_4,Dis_OS,
            # Email_Ratio,Cnt_Send,Avg_Send_Size,Avg_Send_Attach,
            # Cent_Recv,Avg_Recv_Size,Avg_Recv_Attach,
            # Cnt_Send_Days,Cnt_Recv_Days

            # AAB1302,WMH1300,39.0,36.0,20.0,40.0,20.0,13.9283882772,0,0,0,0,0.0,0.0,4.0,40840.75,0.0,4.0,2856906.75,8.0,4,4,
            rlf_process_tmp.append(float(line_lst[7]))
            rlf_process_tmp.append(float(line_lst[12]))
            rlf_process_tmp.append(float(line_lst[-2]) + float(line_lst[-1]))
            # AAB1302,WMH1300,13.9283882772,0.0,8.0,0.0,4.0,40840.75,0.0,4.0,2856906.75,8.0,
            # Process特征格式
            # user_id, leave_id, dis_ocean, dis_os, email_days, email_feat
            tmp_1 = []
            for ele in line_lst[13:20]:
                tmp_1.append(float(ele))
            rlf_process_tmp.extend(tmp_1)
            # 当行RLF提取完毕
            print line_lst[0], line_lst[1], rlf_process_tmp, '\n'
            rlf_process_month.append(rlf_process_tmp)
            i += 1
            continue
    print 'RLF user_id/leave_contacts的索引关联建立完毕...\n'
    #for i in range(5):
    #    print i, cert_user_leave_index[i], '\n'
    #    print i, rlf_process_month[i], '\n'
    # 中间结果需要保存
    # print 'rlf_process文件写入路径为：', Dst_Dir + '\\' + 'RLF_Process.csv', '\n'
    f_rlf_process = open(Dst_Dir + '\\' + 'RLF_Process_1.csv', 'w')
    j = 0
    while j < len(cert_user_leave_index):
        # print 'rlf_process写入第', j, '行..\n'
        f_rlf_process.write(cert_user_leave_index[j][0])
        f_rlf_process.write(',')
        f_rlf_process.write(cert_user_leave_index[j][1])
        f_rlf_process.write(',')
        for ele in rlf_process_month[cert_user_leave_index[j][2]]:
            f_rlf_process.write(str(ele))
            f_rlf_process.write(',')
        f_rlf_process.write('\n')
        j += 1
    f_rlf_process.close()
    print 'f_rlf_process文件写入完毕...\n'
    # sys.exit()

    # rlf_process_month为计算当月的RLV需要的四维度特征，该特征归一化后可以依据公式计算RLV
    # 开始将得到的rlf_process_month进行归一化后，计算各个部分的数值，返回RLV数值列表，对应于建立的用户关联索引
    rlf_month_lst = Cal_RLV(rlf_process_month)
    # 将该rlf_month_lst与用户匹配，计算用户的JS_Risk
    # 定义一个最终的JS_Risk_lst
    jsr_lst = []
    jsr_users = [] # 分析的jsr的最终用户名单
    jsr_values = [] # 定义jsr的具体数值
    j = 0
    while j < len(cert_user_leave_index):
        # 数据格式范例
        # ['AAC0904', 'JAT1218', 1]
        if cert_user_leave_index[j][0] not in jsr_users:
            jsr_users.append(cert_user_leave_index[j][0])
            # 开始计算该用户的JSR，是所有关联用户的RLV的和
            #print 'j index is ', cert_user_leave_index[j], '\n'
            #print 'rlf_month_lst j is ', rlf_month_lst[0], '\n\n'
            jsr_values.append(rlf_month_lst[cert_user_leave_index[j][2]])
            j += 1
        else:
            index_0 = jsr_users.index(cert_user_leave_index[j][0])
            jsr_values[index_0] += rlf_month_lst[cert_user_leave_index[j][2]]
            j += 1
    j = 0
    while j < len(jsr_users):
        tmp_2 = []
        tmp_2.append(jsr_users[j])
        tmp_2.append(jsr_values[j])
        jsr_lst.append(tmp_2)
        j += 1
    print 'JSR统计计算完毕...\n\n'
    #
    #
    #
    # 得到当前与离职用户关联的用户列表

        #for ele in jsr_lst[i]:
            #f_jsr.write(str(ele))
        #f_jsr.write('\n')
    #f_jsr.close()
    # print '本月JSR列表已经保存完毕..\n'
    #
    #
    #
    # 开始输出高危用户列表
    high_risk_lst = []
    # 保存文件
    f_hr = open(Dst_Dir + '\\' + 'Next_Month_HighRisk_1.csv', 'w')
    f_hr.write('Next Month High Risk Users from low Job Statisfactory\n')

    # 保存一个仅包含本月与离职用户关联的用户的JSR列表
    f_relate_leave = open(Dst_Dir + '\\' + 'Current_Month_Leave_JSR_1.csv', 'w')
    jsr_0_lst = sorted(jsr_lst, key=lambda t:t[1], reverse=True)
    jsr_users = []
    #f_jsr = open(Dst_Dir + '\\' + 'Current_Month_JSR.csv', 'w')
    for i in range(len(jsr_0_lst)):
        if i < 10:
            print i, jsr_0_lst[i], '\n'
        jsr_users.append(jsr_0_lst[i][0])
    j = 0
    while j < len(jsr_0_lst):
        f_relate_leave.write(jsr_0_lst[j][0])
        f_relate_leave.write(',')
        f_relate_leave.write(str(jsr_0_lst[j][1]))
        f_relate_leave.write('\n')
        j += 1
    f_relate_leave.close()
    print month, '....<<<<本月JSR数据保存完毕>>>>....\n\n'

    #
    #
    #
    # 最终分析预测的JS_lst应添加进入开始过滤掉的其他用户，这些用户在该月无离职关联，JS = 0
    # 这里需要注意的是，这些补充的用户仅作为最终的高危用户判断使用，而在计算JSR时显然默认为0不用考虑

    # 这里我们要生成对于下个月高危用户的预测，而这些用户显然不应包含本月离职的用户，因而
    # 我们这里的cert_users已经是去掉了本月离职用户的新用户即可，
    # 这里需要生成一个预测用户的新变量列表：

    jsr_new_lst = []
    for user in cert_users:
        if user not in jsr_users:
            tmp_4 = []
            tmp_4.append(user)
            tmp_4.append(0.0)
            jsr_new_lst.append(tmp_4)
        else:
            tmp_4 = []
            tmp_4.append(jsr_0_lst[jsr_users.index(user)][0])
            tmp_4.append(jsr_0_lst[jsr_users.index(user)][1])
            jsr_new_lst.append(tmp_4)

    print month, 'jsr_new_users扩充到全部最新的', len(cert_users), '个用户...\n\n'


    #
    # 每月的JS_Score应该是之前月份的和，即是一个累积结果；
    # 在补全了了jsr_lst之后，就可以进行各个月份JSR的累加
    # 形成一个需要累加的月份列表
    # 每次只需要加上前一个月JSR即可
    print 'Month_lst is ', month_lst, '\n'
    current_index = month_lst.index(month)
    print '当前月份为：', month, '\t', '月份索引为： ',current_index, '\n'
    jsr_new_order_lst = sorted(jsr_new_lst, key=lambda t: t[1], reverse=True)
    if current_index > 0:
        # 获取上一个月份
        add_month = month_lst[current_index - 1]
        #print 'add_month is ', add_month, '\n'
        #print 'current_month is ', month, '\n'
        # Dst_Dir是当前的月份目录
        # 获取存放上一个月的所有用户JSR文件的目录路径
        add_jsr_dir = os.path.dirname(Dst_Dir) + '\\' + add_month
        f_add_jsr = open(add_jsr_dir + '\\' + 'Accumulated_Months_JSR_1.csv', 'r')
        f_add_jsr_lst = f_add_jsr.readlines()
        f_add_jsr.close()
        # 累积更新JSR
        j = 0
        while j < len(jsr_new_order_lst):
            # 以现在的为准
            for line in f_add_jsr_lst:
                line_lst = line.strip('\n').strip(',').split(',')
                if jsr_new_order_lst[j][0] == line_lst[0]:
                    #print jsr_lst[j], '\n'
                    jsr_new_order_lst[j][1] += float(line_lst[1])
                    #print 'month is ', month, '\n'
                    #print 'add month is ', add_month, '\n'
                    #print 'line_lst is ', line_lst, '\n'
                    #print 'new jsr_lst is ', jsr_lst, '\n'
                    # sys.exit()
                    break
                else:
                    continue
            j += 1
    print '....<<<<本月JSR与历史JSR合并结束>>>>....\n\n'
    for i in range(10):
        print i, 'New：', jsr_new_order_lst[i], '\n'
    # sys.exit()
    # 准备写入当前本月的累积JSR
    f_jsr = open(Dst_Dir + '\\' + 'Accumulated_Months_JSR_1.csv', 'w')
    # 此时由于，jsr_new_order_lst融合了过去的JSR，因此需要重新排序
    jsr_final_order_lst = sorted(jsr_new_order_lst, key=lambda t:t[1], reverse=True)
    for i in range(len(jsr_final_order_lst)):
        #print i, jsr_lst[i], '\n'
        #jsr_users.append(jsr_lst[i][0])
        for ele in jsr_final_order_lst[i]:
            f_jsr.write(str(ele))
            f_jsr.write(',')
        f_jsr.write('\n')
    f_jsr.close()
    print '本月JSR列表已经保存完毕..\n'
    #
    #
    #
    # 对原先的结果按照JSR高到低排序
    # jsr_order_lst = sorted(jsr_lst, key=lambda t:t[1], reverse=True)
    k = 0
    # 参数传入的Risk_Ratio来自于一个多维列表，因此需要[0]才能取得里面的元素
    while float(k + 1) / len(jsr_final_order_lst) <= Risk_Ratio:
        tmp_3 = []
        #print 'k is ', k, '\n'
        #print len(jsr_order_lst), '\n'
        #print float(k + 1) / len(jsr_order_lst), '\n'
        #print 'RiskRatio is ', Risk_Ratio, '\n'
        tmp_3.append(jsr_final_order_lst[k][0])
        tmp_3.append(jsr_final_order_lst[k][1])
        f_hr.write(jsr_final_order_lst[k][0])
        f_hr.write(',')
        f_hr.write(str(jsr_final_order_lst[k][1]))
        f_hr.write('\n')
        high_risk_lst.append(tmp_3)
        k += 1
    f_hr.close()
    print '高危用户分析完毕，写入完毕...\n'






    return jsr_new_order_lst, high_risk_lst









