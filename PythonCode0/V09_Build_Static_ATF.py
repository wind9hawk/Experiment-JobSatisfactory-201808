# coding:utf-8
# 为了应用全局静态假设，我们需要重新合并CERT5.2用户中所有用户的最终ATF
# 从2011-05月份开始，初始化CERT5.2用户的ATF列表，并由后向前倒向回溯补充离职用户的ATF；

import os,sys
import copy

print '..<<建立CERT5.2全局静态ATF特征>>..\n'
Dst_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.9'
# 读取2011-05月份的ATF特征，并初始化全局ATF特征CERT52_Static_ATF
# 读取离职用户列表，并依据离职日期匹配选择要读入的ATF数据目录
CERT52_Static_ATF_lst = []
CERT52_Static_Users = []
f_init = open(Dst_Dir + '\\' + '2011-05' + '\\' + 'CERT5.2_LaidOff_ATF_0.1.csv', 'r')
for line in f_init.readlines():
    line_lst = line.strip('\n').strip(',').split(',')
    if line_lst[0] == 'user_id':
        continue
    CERT52_Static_Users.append(line_lst[0])
    CERT52_Static_ATF_lst.append(line_lst)
f_init.close()
print '全局静态ATF初始化完毕..\n'

print '开始倒向补充离职用户的ATF..\n'
Leave_Users = []
f_leave = open(Dst_Dir + '\\' + 'CERT5.2-Leave-Users_OnDays_0.6.csv', 'r')
for line in f_leave.readlines():
    line_lst = line.strip('\n').strip(',').split(',')
    if line_lst[0] == 'user_id' or len(line_lst) < 2:
        continue
    leave_tmp = []
    leave_tmp.append(line_lst[0]) # 2010-02-09
    leave_tmp.append(line_lst[1])
    Leave_Users.append(leave_tmp)
f_leave.close()
print '离职用户数据初始化完毕..\n'
for i in range(5):
    print i, Leave_Users[i], '\n'

print '倒向建立全局静态ATF..\n'
feat_flag = []
for user_feat in Leave_Users:
    if user_feat[0] in CERT52_Static_Users:
        continue
    leave_month = user_feat[1][:7]
    f_leave_month = open(Dst_Dir + '\\' + leave_month + '\\' + 'CERT5.2_Leave_ATF_02.csv', 'r')
    for line in f_leave_month.readlines():
        line_lst = line.strip('\n').strip(',').split(',')
        if line_lst[0] == 'user_id':
            feat_flag = copy.copy(line_lst)
            continue
        if line_lst[0] == user_feat[0]:
            CERT52_Static_ATF_lst.append(line_lst)
            print user_feat, '补充进入到全局静态ATF..\n'
            print line_lst, '\n'
        else:
            continue

print '重新写入全局静态ATF..\n'
f_static_atf = open(Dst_Dir + '\\' + 'KMeans_OCSVM_Insiders_Predictor' + '\\' + 'CERT5.2_Leave_Static_CPB_ATF-02.csv', 'w')
feat_flag_0 = [] #去掉OCEAN部分
feat_flag_0.append(feat_flag[0])
for ele in feat_flag[6:]:
    feat_flag_0.append(ele)
for ele in feat_flag_0:
    f_static_atf.write(ele + ',')
f_static_atf.write('\n')
for line_atf in CERT52_Static_ATF_lst:
    f_static_atf.write(line_atf[0] + ',')
    for ele in line_atf[6:]:
        f_static_atf.write(ele + ',')
    f_static_atf.write('\n')
f_static_atf.close()
print 'CERT5.2全局静态ATF文件写入完毕..\n'

# 继续执行一个拼接，将原始全部的26JS特征全部拼接进入到0.1版本的All_ATF特征中
# 26JS:
# user_id,
# O_Score,C_Score,E_Score,A_Score,N_Score,
# Team_CPB-I-mean,Team_CPB-O-mean,Users-less-mean-A,Users-less-mean-A and C,Users-less-mean-C,Users-High-mean-N,Team_CPB-I-median,Team_CPB-O-median,
# No-JobState-in-Team,
# Dpt-CPB-I-mean,Dpt_CPB-O-mean,Dpt-Less-A-mean,Dpt-Less-AC-mean,Dpt-less-C-mean,Dpt-High-N-mean,Dpt_CPB-I-median,Dpt_CPB-O-median,
# No-JobState-in-Dpt,
# Job State,
# Leader_CPB-I,Leader_CPB-O
sys.exit()

