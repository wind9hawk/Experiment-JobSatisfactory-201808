# coding:utf-8
# 鉴于最初建立初级JSR预测时，计算RLV的公式中直接将dis_ocean与dis_os相加，而没有采取反向处理
# 本模块直接处理初步得到的Current_JSR、Accumulate_JSR、以及High-Risk文件，得到新的更新列表

# 简要分析步骤
# 1. 读取CERT_5.2中的用户列表；
# 2. 进入每个月份目录：
# 2.1 读取该月份离职用户列表；
# 2.2 判断是否存在current_jsr文件，不存在则跳过
# 2.3 读取process文件
# 2.4 重新计算RLV，组合成对应于用户的JSR
# 2.5 结合上一个月的accumulate计算所有用户的JSR，去掉本月离职用户后，排序
# 2.6 输出前5%作为High-Risk

import os,sys
import numpy as np
import sklearn.preprocessing as skp
import shutil
import copy
import math



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

print '......<<<<<<修正原始RLV计算公式>>>>>>......\n\n\n'

print '....<<<<确定数据源>>>>....\n\n'

Dst_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.7'
LDAP_Path = os.path.dirname(sys.path[0]) + '\\' + 'LDAP' + '\\' + '2009-12.csv'

print '..<<构建CERT52用户初始列表>>..\n'
CERT52_Users = []
f_LDAP = open(LDAP_Path, 'r')
f_LDAP_lst = f_LDAP.readlines()
f_LDAP.close()
for line in f_LDAP_lst:
    # LDAP数据格式：
    # employee_name,user_id,email,role,projects,business_unit,functional_unit,department,team,supervisor
    line_lst = line.strip('\n').strip(',').split(',')
    if len(line_lst) < 10:
        continue
    if line_lst[1] == 'user_id':
        continue
    CERT52_Users.append(line_lst[1])


print '....<<<<开始依序月份重新计算RLV，生成JSR文件>>>>....\n\n'
# 定义一个计算JSR的月份列表
Month_lst = []
for month in os.listdir(Dst_Dir)[1:-1]:
    Month_dir = Dst_Dir + '\\' + month
    # 不用分析文件，仅关注目录
    if os.path.isdir(Month_dir) == False:
        continue
    # 判断是否存在JSR文件，不存在则跳过
    Current_jsr_path = Month_dir + '\\' + 'Current_Month_Leave_JSR.csv'
    Accumulate_jsr_path = Month_dir + '\\' + 'Accumulated_Months_JSR.csv'
    High_risk_path = Month_dir + '\\' + 'Next_Month_HighRisk.csv'
    RLF_process_path = Month_dir + '\\' + 'RLF_Process.csv'
    if os.path.exists(Current_jsr_path) == False:
        # 不存在JSR，不存在离职用户
        continue
    else:
        Month_lst.append(month)
        # 还需要一个leave_users的文件
        for file in os.listdir(Month_dir):
            # Leave_Users_2010-02.csv
            if 'Leave_Users' not in file:
                continue
            else:
                Leave_users_path = Month_dir + '\\' + file
        # 数据源准备完毕，开始进行计算
        # 我们先完整计算出当前JSR
        # 再筛选去掉Leave_users,计算累积JSR
        # 最后输出高风险用户
        # Process中间变量格式
        # AAB1302,WMH1300,13.9283882772,0.0,8.0,0.0,4.0,40840.75,0.0,4.0,2856906.75,8.0,
        # 定义一个中间变量的用户列表，即Current_JSR的用户列表
        current_users = [] # 与离职用户有关联的当前用户
        current_leavers_index = [] # 对应的关联离职联系人的索引
        current_process_feat = []
        f_process = open(RLF_process_path, 'r')
        f_process_lst = f_process.readlines()
        f_process.close()
        for line in f_process_lst:
            line_lst = line.strip('\n').strip(',').split(',')
            if line_lst[0] not in current_users:
                current_users.append(line_lst[0])
                tmp_index = []
                tmp_index.append(f_process_lst.index(line))
                current_leavers_index.append(tmp_index)
                tmp_feat = []
                for ele in line_lst[2:]:
                    tmp_feat.append(float(ele))
                current_process_feat.append(tmp_feat)
            else:
                current_leavers_index[current_users.index(line_lst[0])].append(f_process_lst.index(line))
                tmp_feat = []
                for ele in line_lst[2:]:
                    tmp_feat.append(float(ele))
                current_process_feat.append(tmp_feat)
                #
        #
        # 以一个具体用户为例子验证
        # print current_users[1], current_leavers_index[1], '\n'
        # AAG1136 [3]
        # AAC0904[1, 2]
        # 验证通过
        #
        current_jsr_lst = Cal_RLV(current_process_feat)
        print '..<<当月JSR计算完毕>>..\n'
        for i in range(10):
            print i, current_jsr_lst[i], '\n'
        # 进一步，依据索引将上述JSR结果合并到不同的用户，生成当前用户的JSR列表
        current_jsr_month = []
        i = 0
        while i < len(current_users):
            tmp_1 = []
            tmp_1.append(current_users[i])
            rlv_tmp = 0.0
            for j in current_leavers_index[i]:
                rlv_tmp += current_jsr_lst[j]
            tmp_1.append(rlv_tmp)
            current_jsr_month.append(tmp_1)
            i += 1
        print current_users[1], current_jsr_month[1], '\n'

        # 将该结果排序后写入新文件
        current_jsr_month_order = sorted(current_jsr_month, key=lambda t:t[1], reverse=True)
        f_current_jsr = open(Month_dir + '\\' + 'Current_Month_Leave_JSR_0.csv', 'w')
        for line in current_jsr_month_order:
            for ele in line:
                f_current_jsr.write(str(ele))
                f_current_jsr.write(',')
            f_current_jsr.write('\n')
        f_current_jsr.close()

        leave_users_month = []
        f_leave_users = open(Leave_users_path, 'r')
        f_leave_users_lst = f_leave_users.readlines()
        f_leave_users.close()
        for line in f_leave_users_lst:
            line_lst = line.strip('\n').strip(',').split(',')
            # leave格式
            # RMB1821,2010-02-09,ldap
            if line_lst[0] not in leave_users_month:
                leave_users_month.append(line_lst[0])


        for user in CERT52_Users:
            if user in leave_users_month:
                CERT52_Users.remove(user)

        accu_jsr_lst = [] # 最终保存的累积JSR
        for user in CERT52_Users:
            if user in current_users:
                tmp_2 = []
                tmp_2.append(user)
                tmp_2.append(current_jsr_month[current_users.index(user)][1])
                accu_jsr_lst.append(tmp_2)
            else:
                tmp_3 = []
                tmp_3.append(user)
                tmp_3.append(0.0)
                accu_jsr_lst.append(tmp_3)
        for i in range(10):
            print i, accu_jsr_lst[i], '\n'

        if Month_lst.index(month) > 0:
            add_index = Month_lst.index(month) - 1
            f_add_accu = open(Dst_Dir + '\\' + Month_lst[add_index] + '\\' + 'Accumulated_Months_JSR_0.csv', 'r')
            add_accu_jst_lst = f_add_accu.readlines()
            f_add_accu.close()
            for line_accu in accu_jsr_lst:
                flag_0 = False
                if line_accu[0] == 'JOE1672':
                    flag_0 = True
                for ele in add_accu_jst_lst:
                    line_accu_lst = ele.strip('\n').strip(',').split(',')
                    if line_accu[0] == line_accu_lst[0]:
                        line_accu[1] += float(line_accu_lst[1])
                        # j += 1
                        if flag_0:
                            print line_accu, ele, '\n'
                            # sys.exit()
                        break
                    else:
                        continue
        for i in range(10):
            print i, accu_jsr_lst[i], '\n'

        f_accu = open(Month_dir + '\\' + 'Accumulated_Months_JSR_0.csv', 'w')
        for line in sorted(accu_jsr_lst, key=lambda t:t[1], reverse=True):
            for ele in line:
                f_accu.write(str(ele))
                f_accu.write(',')
            f_accu.write('\n')
        f_accu.close()

        print Month_lst, '\n'

































