# coding:utf-8
# 本模块为实验七的主程序模块，主要功能有：
# 1. 整体预测程序的逻辑控制；
# 2. 全局变量定义
# 3. 全局数据源指定
# 4. 功能函数模块的调用，比如我们的预测器（Predictor）以及验证反馈器（Check_Feedback_Module）

# 主要控制逻辑
# 1. 确定数据源，确定程序结果的输出目录
# 2. 确定预测与验证反馈的时间月份列表，以存在离职的第一个月为起点，以存在离职的最后一个月或者下一个月为起点
# 3. 按月份生成预测器
# 4. 按月份生成验证反馈器
# 5. 按月份生成预测器更新器（Predictor_Update_Module）
# 6. 一个月份中，上述三类功能器的存在状况只有三种情况：
# 6.1 第一个月，只有预测器；
# 6.2 最后一个月，只有验证器和反馈器
# 6.3 中间的月份，同时具有上述三种
# 6.4 因此需要三种子逻辑

# 注意！：
# 1. 功能函数化编程；Main + Function_Module(sub-logic + sub-function-modules)
# 2. 清楚的数据源、全局变量定义
# 3. 言简意赅的注释
# 4. 避免重复使用循环变量，若使用，一定避免多次重复操作

import os,sys
import shutil
import sklearn.preprocessing as skp
import sklearn.decomposition as skd
import sklearn.metrics as skm
import copy
import math

import V07_Predictor_Module

# 定义一个自动从date数据中提取年月日格式的函数
def Extract_Date(date):
    # date: 2010-02-09
    year = date[:4]
    month = date[5:7]
    day = date[8:]
    return year + '-' + month + '-' + day



print '......<<<<<<实验系列七：基于用户离职联系人关联性建模低满意度风险研究>>>>>>.....\n\n'

print '....<<<<定义全局数据源>>>>....\n\n'
# CERT5.2中全体用户的大五人格数据
Father_Current_Dir = os.path.dirname(sys.path[0])
f_OCEAN = open(Father_Current_Dir + '\\' + 'psychometric-5.2.csv', 'r')
f_OCEAN_lst = f_OCEAN.readlines()
f_OCEAN.close()
# CERT5.2中全体用户的LDAP数据
LDAP_Dir= Father_Current_Dir + '\\' + 'LDAP'
# 定义一个全局所有时间段的LDAP文件路径列表
All_LDAP_Path = []
for file in os.listdir(LDAP_Dir):
    All_LDAP_Path.append(LDAP_Dir + '\\' + file)
print 'check All_LDAP_Path: \n'
for i in range(5):
    print i, All_LDAP_Path[i], '\n'


#
# CERT5.2中所有用户的邮件数据
Email_Rcd_Dir = r'G:\GitHub\Essay-Experiments\CERT5.2-Results\CERT5.2-Users-EmailRecords'
# 定义一个存放CERT5.2中所有用户邮件内容文件名的文件路径列表
All_Email_Rcds_Path = []
for file in os.listdir(Email_Rcd_Dir):
    if 'feat' not in file:
        All_Email_Rcds_Path.append(Email_Rcd_Dir + '\\' + file)
print 'check All_Email_Rcds_Path: \n'
for i in range(5):
    print i, All_Email_Rcds_Path[i], '\n'
#
# Check Pass!
#
# CERT5.2中离职用户数据（最新的，具体到天）
f_Leave_Users = open(sys.path[0] + '\\' + 'CERT5.2-Leave-Users_OnDays_0.6.csv', 'r')
f_Leave_Users_lst = f_Leave_Users.readlines()
f_Leave_Users.close()
#
# 开始指定预测器与验证反馈器的结果和相关数据文件存放位置
Dst_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.7'
print '....<<<<基本数据源、结果输出目录确定完毕>>>>....\n\n'


print '....<<<<在输出目录按月份生成子目录>>>>....\n\n'
# 主要算法
# 1. 读取离职用户数据表中所有用户涉及的月份；
# 2. 将第一个离职月作为起点，最后一个离职月作为终点；
# 3. 起点只有预测器，终点只有验证反馈器；
# Leave_Users文件数据格式：
# Laid off Users in CERT5.2 from 2009-12 to 2011-05
# RMB1821,2010-02-09,
# Rose Maisie Blackwell,RMB1821,
# Rose.Maisie.Blackwell@dtaa.com,Salesman,,1 - Executive,5 - SalesAndMarketing,
# 2 - Sales,5 - RegionalSales,Donna Erin Black
# 定义适用于预测器与验证反馈器的月份列表
# 与此同时，还生成了每个月份的离职用户列表
Months_lst = []
for line in f_Leave_Users_lst:
    line_lst = line.strip('\n').strip(',').split(',')
    if len(line_lst) < 2:
        # 标题行跳过
        continue
    else:
        date = Extract_Date(line_lst[1])
        # # date: 2010-02-09
        if date[:7] not in Months_lst:
            Months_lst.append(date[:7])
        else:
            continue
print '....<<<<在输出目录顺序生成新的月份目录>>>>....\n\n'
for month in Months_lst:
    month_dir = Dst_Dir + '\\' + month
    if os.path.exists(month_dir) == False:
        os.mkdir(month_dir)
    else:
        continue
# 在每个月份目录下生成当月离职用户文件
for month in Months_lst:
    month_dir = Dst_Dir + '\\' + month
    f_month_luser = open(month_dir + '\\' + 'Leave_Users_' + month + '.csv', 'w')
    for line in f_Leave_Users_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        if len(line_lst) < 2:
            # 标题行跳过
            continue
        else:
            date = Extract_Date(line_lst[1])
            if date[:7] == month:
                for ele in line_lst:
                    f_month_luser.write(ele)
                    f_month_luser.write(',')
                f_month_luser.write('\n')
            else:
                continue
    f_month_luser.close()
print '....<<<<月份目录生成完毕，月份离职用户表分离存储完毕>>>>....\n\n'


## 预测器功能说明
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


print '....<<<<开始为CERT5.2的所有用户，根据月份构建预测器、预测并验证反馈>>>>....\n\n'
# 初始化CERT52中的用户列表
f_cert_users = open(All_LDAP_Path[0], 'r')
f_cert_users_lst = f_cert_users.readlines()
f_cert_users.close()
CERT52_Users = []
for line in f_cert_users_lst:
    # LDAP数据格式为：
    # employee_name,user_id,email,role,projects,business_unit,functional_unit,department,team,supervisor
    line_lst = line.strip('\n').strip(',').split(',')
    if len(line_lst) < 10:
        print 'CEO is ', line_lst[1], '\n'
        continue
    if line_lst[1] != 'user_id':
        CERT52_Users.append(line_lst[1])
print '..<<CERT5.2 用户列表初始化完成>>..\t', len(CERT52_Users), '\n\n'
for i in range(10):
    print i, CERT52_Users[i], '\n'
# sys.exit()
### 上述代码验证通过
#

# 初始化需要的风险阈值比例初始值
Risk_Ratios = [0.05 for i in range(len(Months_lst))]
# Month_lst中本身就只包含离职月份
#Months_lst.insert(0, '2010-01')
Month_No = 0
while Month_No < 1:#len(Months_lst):
    print '....<<<<现在开始分析CERT5.2的', Months_lst[Month_No], '月份数据>>>>....\n\n\n'
    month = Months_lst[Month_No]
    # 执行预测器的月份，为总月份个数-1
    # 核实构建预测器所需要的数据源是否齐备？
    # data-1：原始邮件目录All_Email_Rcds_Path，用于匹配提取该月及以前的邮件通信
    # data-2: 当月离职用户文件信息：f_Leave_OnMonth
    # data-3: CERT5.2全体用户列表，用于该月份循环遍历，生成每个用户的RL特征表与JS_Risk特征
    # data-4: CERT5.2全体用户的OCEAN数据，f_OCEAN_lst
    # data-5: CERT5.2全体用户的LDAP数据All_LDAP_Path【month_no筛选即可】
    # data-6: 结果的输出目录
    # 返回携带有RL值的用户RL特征表
    # 注意，预测器与检验器中的dst_dir是不同的！
    # 预测器发生在本月
    # 检验器发生在下一个月

    # 初始化本月的离职用户文件路径
    for file in os.listdir(Dst_Dir + '\\' + Months_lst[Month_No]):
        if 'Leave_Users' in file and Months_lst[Month_No] in file:
            # 说明这是我们要的当月离职用户文件
            filePath = Dst_Dir + '\\' + Months_lst[Month_No] + '\\' + file
            f_leave_month = open(filePath, 'r')
            f_leave_month_lst = f_leave_month.readlines()
            f_leave_month.close()
            break
        else:
            continue
    # 构建当月邮件特征时，不应考虑当月之前已经离职的用户
    # 当月之前已经离职的用户列表为：Have_Left_Users_Month_lst
    Have_Left_Users_Month_lst = []
    for line in f_Leave_Users_lst:
        # # RMB1821,2010-02-09,LDAP
        line_lst = line.strip('\n').strip(',').split(',')
        if len(line_lst) < 2:
            continue
        # print line_lst, '\n'
        if line_lst[1][:7] < month:
            # 说明该用户已经离职
            print line_lst[0], line_lst[1], '在 ', month, '前已经离职，不考虑...\n'
            Have_Left_Users_Month_lst.append(line_lst[0])
    # 验证通过
    # sys.exit()
    rl_value_month_path = V07_Predictor_Module.Build_Predictor(sorted(CERT52_Users)[:], f_OCEAN_lst, All_LDAP_Path[0], Email_Rcd_Dir, f_leave_month_lst, Dst_Dir + '\\' + Months_lst[Month_No], Months_lst[Month_No], Have_Left_Users_Month_lst)
    print Months_lst[Month_No], '..<<Build_Predictor Success>>..\n\n'
    # sys.exit()
    #
    # 在进行预测前，应去除本月离职的用户
    for leavers in f_leave_month_lst:
        # 离职用户格式
        # RMB1821,2010-02-09,LDAP
        l_user = leavers.strip('\n').strip(',').split(',')
        if l_user[0] in CERT52_Users:
            CERT52_Users.remove(l_user[0])
            print Months_lst[Month_No], '预测时去除用户: ', l_user[0], '\n'
            continue
    #print 'RMB1821' in CERT52_Users, '\n'
    #sys.exit()
    # 执行预测模块，生成JS_Risk表
    users_month_jsr_lst, high_risk_lst = V07_Predictor_Module.Run_Predictor(rl_value_month_path, Dst_Dir + '\\' + Months_lst[Month_No], Risk_Ratios[Month_No], sorted(CERT52_Users), Months_lst[Month_No], Months_lst)
    # sys.exit()
    # 执行检验模块
    # 首先自动标记
    #users_label = Auto_Label(cert_users, f_work_time, f_logon_month, dst_dir)
    # 计算FN与FP
    #fn_users, fnr, fp_users, fpr = Cal_Messurement(users_label, risk_users, dst_dir)
    # 更新反馈器
    #Risk_Ratios[Month_No + 1] = Update_Risk_Ratio(Risk_Ratios[Month_No], fnr, fpr, dst_dir)
    # 本月分析结束，进入下一个月
    Month_No += 1
    print '....<<<<', Month_No - 1 , ' 预测器建立完毕，继续下一个月>>>>....\n\n\n'







