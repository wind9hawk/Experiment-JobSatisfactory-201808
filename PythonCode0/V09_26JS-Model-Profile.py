# coding:utf-8
# 本脚本主要根据提出的12个满意度特征，依据psychometric.csv文件建立用户的JS特征；
# 主要算法：
# 1. 读入psychometric.csv\2010-07-DptUsers.csv\2010-07-TeamUsers.csv；
# 2. 依据2010-07.csv中用户顺序，依次关联其部门人员--团队人员--领导者；
# 2.1 对于关联的部门人员，直接计算全部人员的A与C特质的均值/中位数，依据公式计算CPB-I/CPB-O;
# 2.2 对于关联的团队人员，直接计算全部人员的A与C特质的均值/中位数，依据公式计算CPB-I/CPB-O；
# 2.3 对于关联的领导者，基于领导者的A与C特质分数直接计算其CPB-I/CPB-O
# 2.4 将上述所有特征依次写入JS_Users_tmp中，最后关联到JS_Users_lst中

import sys, os
import numpy as np
from sklearn import preprocessing

print '本脚本基于CERT数据建立用户的12维度的工作满意度特征...\n'
print '开始读入三个数据援文件...\n'
Dst_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.9'
# f_cert = open(r'2010-07.csv', 'r')
f_cert = open(Dst_Dir + '\\' + '2009-12.csv', 'r')
# f_cert = open(r'CERT6.2-2009-12.csv', 'r')
f_cert_lst = f_cert.readlines()
# f_psy = open(r'psychometric.csv', 'r')
f_psy = open(Dst_Dir + '\\' + 'psychometric-5.2.csv', 'r')
f_psy_lst = f_psy.readlines()
# f_team = open(r'CERT6.2-2009-12-New-TeamUsers.csv', 'r')
f_team = open(Dst_Dir + '\\' + 'CERT5.2-2009-12-New-TeamUsers.csv', 'r')
f_team_lst = f_team.readlines()
# f_dpt = open(r'CERT6.2-2009-12-New-DptUsers.csv', 'r')
f_dpt = open(Dst_Dir + '\\' + 'CERT5.2-2009-12-New-DptUsers.csv', 'r')
f_dpt_lst = f_dpt.readlines()
# f_jobs = open(r'CERT6.2-2009-12-JobState.csv', 'r')
f_jobs = open(Dst_Dir + '\\' + 'CERT5.2-2010-09-JobState.csv', 'r')
f_jobs_lst = f_jobs.readlines()
f_cert.close()
f_psy.close()
f_team.close()
f_dpt.close()
f_jobs.close()
print '四个数据源文件已经读取完毕...\n'

# 预定义几个频繁使用的功能函数
# CERT-2010-07格式：
# employee_name,user_id,email,role,projects,business_unit,functional_unit,department,team,supervisor
# psy格式
# employee_name,user_id,O,C,E,A,N
# team格式
# 1 - Medical,James Linus Arnold,BDP0031,JLA0030,JCL0446,LRT0447,DRS0032,5
# Dpt格式
# 1 - Accounting,ACA0360,HET0359,MFL0355,RLH0358,4
# 第一个函数是：根据指定的关键项与列表，查找返回包含该关键项的行记录
def LocateLine(keywords, f_lst):
    # 关联涉及到用户时全部使用user_id
    # 其他关联应使用team或dpt名称
    # 输入一个普通文件内容行列表即可
    for line in f_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        if line_lst[1] == 'user_id':
            # print '标题行，跳过...\n'
            continue
        else:
            if keywords in line_lst:
                return line_lst
            else:
                continue
    return 'No Match'
# 第二个函数为CPB-I与CPB-O计算函数
# CPB-I = A_Score * （-0.34） + A_Score * 0.36 * （-0.40）
# CPB-O = C_Score * (-0.52) + A_Score * 0.36 * (-0.41)
# 这里使用新的全OCEAN与CPB的关系
# CPB-I_Self = (-0.43) * A_Score + (-0.16) * C_Score + (-0.24) * -N_Score + 0.25 * E_Score + (-0.30) * O_Score
# CPB-O_Self = (-0.41) * A_Score + (-0.44) * C_Score + (-0.47) * -N_Score + (-0.12) * E_Score + (-0.25) * O_Score
def CalCPBs(O_Score, C_Score, E_Score, A_Score, N_Score):
    CPB_1Score = A_Score * (-0.34) + A_Score * 0.36 * (-0.40)
    CPB_2Score = C_Score * (-0.52) + A_Score * 0.36 * (-0.41)
    #CPB_1Score = (-0.43) * A_Score + (-0.16) * C_Score + (-0.24) * (-1 * N_Score) + 0.25 * E_Score + (-0.30) * O_Score
    # CPB_2Score = (-0.41) * A_Score + (-0.44) * C_Score + (-0.47) * (-1 * N_Score) + (-0.12) * E_Score + (-0.25) * O_Score
    return CPB_1Score, CPB_2Score
# 第三个函数，由User_names--->user_id
def Map2UserId(UName, f_lst):
    # psy格式
    # employee_name,user_id,O,C,E,A,N
    line = LocateLine(UName, f_lst)
    if line == 'No Match':
        # print 'No Match...\n'
        return 'No Match'
    else:
        return line[1]

print '预处理函数定义完成，开始进入特征提取阶段...\n'
JS_Users_lst = []   # 用于存储最后的用户JS特征
A_mean_lst = []   # 用于计算Team-CPB-I/O时，统计其中CPBs高于均值的个体数目
C_mean_lst = []
N_mean_lst = [] # 用于存储团队中N高于均值的用户数目
for line in f_cert_lst:
    line_lst = line.strip('\n').strip(',').split(',')
    if line_lst[1] == 'user_id':
        continue
    line_psy = LocateLine(line_lst[1], f_psy_lst)
    A_mean_lst.append(float(line_psy[-2]))   # 存储用户的A-C分数以便于计算全体均值
    C_mean_lst.append(float(line_psy[3]))
    N_mean_lst.append(float(line_psy[-1]))
A_mean_array = np.array(A_mean_lst)
C_mean_array = np.array(C_mean_lst)
N_mean_array = np.array(N_mean_lst)
A_mean_total = A_mean_array.mean()
C_mean_total = C_mean_array.mean()
N_mean_total = N_mean_array.mean()

User_Short = []
Cnt = 0
for line in f_cert_lst:
    JS_user_tmp = []
    # CERT-2010-06格式：
    # employee_name,user_id,email,role,projects,business_unit,functional_unit,department,team,supervisor
    # CERT4.2:
    # employee_name,user_id,email,role,business_unit,functional_unit,department,team,supervisor
    # CERT5.2:
    # employee_name,user_id,email,role,projects,business_unit,functional_unit,department,team,supervisor
    line_lst = line.strip('\n').strip(',').split(',')
    if len(line_lst) < 10:
        print '记录格式太短，跳过...\n'
        User_Short.append(line_lst)
        continue
    if line_lst[1] == 'user_id':
        # print '标题行，跳过...\n'
        continue
    # 依据user_id开始构建其JS特征
    # 首先是用户的OCEAN分数
    line_psy = LocateLine(line_lst[1], f_psy_lst)
    if line_psy == 'No Match':
        print line_lst[1], 'No Match...\n'
        continue
    else:
        # 顺利找到了用户的OCEAN记录
        # psy格式
        # employee_name,user_id,O,C,E,A,N
        i = 2
        while i < len(line_psy):
            JS_user_tmp.append(float(line_psy[i]))  #写入一个float型数据
            i += 1
        # 现在JS_user_tmp中保存了用户的O-C-E-A-N分数
        # 接下来需要开始构建其团队Team的CPB-I\CPB-O
        # 区分两种记录提取其team名称
        # CERT-2010-06格式：
        # employee_name,user_id,email,role,projects,business_unit,functional_unit,department,team,supervisor
        # CERT5.2:
        # employee_name,user_id,email,role,projects,business_unit,functional_unit,department,team,supervisor
        team_nm_0 = [] # 存储团队的绝对名称
        team_nm_1 = [] # 存储团队的名称
        if len(line_lst) == 10:
            team_nm_1 = line_lst[-2]
            team_nm_0.append(line_lst[5])
            team_nm_0.append(line_lst[6])
            team_nm_0.append(line_lst[7])
            team_nm_0.append(line_lst[8])
            team_nm_0 = str(team_nm_0)
            print team_nm_0, '\n'
            team_nm = team_nm_0.replace(',', '-')
            print team_nm, '\n'
            # team_nm = line_lst[-2]
        if len(line_lst) == 9:
            team_nm_1 = line_lst[-1]
            # team_nm = line_lst[-1]
            team_nm_0 = []
            team_nm_0.append(line_lst[5])
            team_nm_0.append(line_lst[6])
            team_nm_0.append(line_lst[7])
            team_nm_0.append(line_lst[8])
            team_nm_0 = str(team_nm_0)
            team_nm = team_nm_0.replace(',', '-')
        if team_nm_1 == '':
            print line_lst[1], '不属于任何团队...跳过计算team反生产行为...\n'
            JS_user_tmp.append(0)
            JS_user_tmp.append(0)
            JS_user_tmp.append(0)
            JS_user_tmp.append(0)
            JS_user_tmp.append(0)
            JS_user_tmp.append(0)
            JS_user_tmp.append(0)
            JS_user_tmp.append(0)
            JS_user_tmp.append(0)
        else:
            # 用户附属某个团队，需要计算团队的分数
            line_team = LocateLine(team_nm, f_team_lst)
            if line_team == 'No Match':
                # print team_nm, ' No Match...\n'
                continue
            else:
                # team格式
                # 1 - Medical,James Linus Arnold,BDP0031,JLA0030,JCL0446,LRT0447,DRS0032,5
                user_team = []
                for user_t in line_team[2:-1]:
                    if user_t == line_lst[1]: # 如果发现用户名，则去掉，我们只计算该用户外的团队关系影响
                        continue
                    else:
                        user_team.append(user_t)
                # 对于该用户所涉及的团队成员，分别计算其A与C特质的均值与中位数
                # V09需要计算Team的OCEAN五个特质的均值与中位数
                user_team_AC = []
                Cnt_Less_A = 0  # 用于统计团队中低于均值A与C的个体数目
                Cnt_Less_C = 0
                Cnt_High_N = 0
                Cnt_Less_AC = 0  # 用于统计团队中同时低于均值A与C的个体数目
                Cnt_NoJobs = 0
                for user_t in user_team:
                    user_team_AC_tmp = []
                    line_psy = LocateLine(user_t, f_psy_lst)
                    if line_psy == 'No Match':
                        continue
                    # psy格式
                    # employee_name,user_id,O,C,E,A,N
                    if float(line_psy[-2]) < A_mean_total:
                        Cnt_Less_A += 1
                        if float(line_psy[3]) < C_mean_total:
                            Cnt_Less_AC += 1
                    if float(line_psy[3]) < C_mean_total:
                        Cnt_Less_C += 1
                    if float(line_psy[-1]) > N_mean_total:
                        Cnt_High_N += 1
                    # 我们是的user_team_AC_tmp中按照OCEAN的顺序记录
                    for ele in line_psy[2:]:
                        user_team_AC_tmp.append(float(ele))
                    #user_team_AC_tmp.append(float(line_psy[3])) # C分数
                    #user_team_AC_tmp.append(float(line_psy[-2])) # A分数
                    user_team_AC.append(user_team_AC_tmp)
                    # 再来计算其所在团队中用户的工作状态，即提前离职的有几个
                    line_jobs = LocateLine(user_t, f_jobs_lst)
                    if line_jobs == 'No Match':
                        continue
                    # NFP2441,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
                    # print user_t, '\t', line_jobs, '\t', line_jobs.count('1'), '\n'
                    if line_jobs.count('1') < 18:
                        Cnt_NoJobs += 1
                user_team_array = np.array(user_team_AC)
                # list[1:-1]不包括最后一个元素，如果是List[1:-2]则不包括最后两个元素，最后只到list[-3]
                # print line_lst[1], 'user_team_array is ', user_team_array, '\n'
                if len(user_team_array) < 1:
                    C_mean = 0.0
                    A_mean = 0.0
                    C_median = 0.0
                    A_median = 0.0
                    # A_Score, C_Score, N_Score, E_Score, O_Score
                    N_mean = 0.0
                    N_median = 0.0
                    O_mean = 0.0
                    O_median = 0.0
                    E_mean = 0.0
                    E_median = 0.0

                else:
                    O_mean, C_mean, E_mean, A_mean, N_mean = user_team_array.mean(axis=0)
                    O_median, C_median, E_median, A_median, N_median = np.median(user_team_array, axis=0)
                # 先用均值计算CPBs
                CPB1, CPB2 = CalCPBs(O_mean, C_mean, E_mean, A_mean, N_mean)
                JS_user_tmp.append(CPB1)
                JS_user_tmp.append(CPB2)
                JS_user_tmp.append(Cnt_Less_A)
                JS_user_tmp.append(Cnt_Less_AC)
                JS_user_tmp.append(Cnt_Less_C)
                JS_user_tmp.append(Cnt_High_N)
                CPB1, CPB2 = CalCPBs(O_median, C_median, E_median, A_median, N_median)
                JS_user_tmp.append(CPB1)
                JS_user_tmp.append(CPB2)
                JS_user_tmp.append(Cnt_NoJobs)
                print line_lst[1], JS_user_tmp, '\n'
                print Cnt, '\t', line_lst[1], ' 团队CPBs计算完毕...\n'
                Cnt += 1
        # 开始计算部门分数，大体方法类似与团队分数计算
        # 先判断部门名称
        # CERT5.2
        # employee_name,user_id,email,role,projects,business_unit,functional_unit,department,team,supervisor
        print '开始计算', line_lst[1], '部门CPBs...\n'
        dpt_nm_0 = []
        if len(line_lst) == 10:
            dpt_nm_1 = line_lst[-3]
            dpt_nm_0.append(line_lst[5])
            dpt_nm_0.append(line_lst[6])
            dpt_nm_0.append(line_lst[7])
            dpt_nm_0 = str(dpt_nm_0)
            dpt_nm = dpt_nm_0.replace(',', '-')
        if len(line_lst) == 9:
            dpt_nm_1 = line_lst[-2]
            dpt_nm_0.append(line_lst[5])
            dpt_nm_0.append(line_lst[6])
            dpt_nm_0.append(line_lst[7])
            dpt_nm_0 = str(dpt_nm_0)
            dpt_nm = dpt_nm_0.replace(',', '-')
        # 如果是空部门，则部门分数为0
        if dpt_nm_1 == '':
            print line_lst[1], ' 不属于任何部门...\n'
            JS_user_tmp.append(0)
            JS_user_tmp.append(0)
            JS_user_tmp.append(0)
            JS_user_tmp.append(0)
            JS_user_tmp.append(0)
            JS_user_tmp.append(0)
            JS_user_tmp.append(0)
            JS_user_tmp.append(0)
            JS_user_tmp.append(0)
        else:
            # dpt_nm_0: 部门的绝对名称
            # dpt_nm_1: 部门的直接名称
            # dpt_nm: 部门dpt_nm_0中将','替换为'-'的名称，可以用于在部门用户文件中查找匹配
            line_dpt = LocateLine(dpt_nm, f_dpt_lst)
            print line_lst, '\n'
            print 'Bug: line_dpt is ', dpt_nm, line_dpt, '\n'
            # Dpt格式
            # 1 - Accounting,ACA0360,HET0359,MFL0355,RLH0358,4
            user_dpt = []
            for user_d in line_dpt[1:-1]:
                if user_d == line_lst[1]:
                    continue
                user_dpt.append(user_d)
            # 对于该用户所涉及的团队成员，分别计算其A与C特质的均值与中位数
            user_dpt_AC = []
            Dpt_Cnt_Less_A = 0  # 用于统计团队中低于均值A与C的个体数目
            Dpt_Cnt_Less_C = 0
            Dpt_Cnt_High_N = 0
            Dpt_Cnt_Less_AC = 0  # 用于统计团队中同时低于均值A与C的个体数目
            Cnt_NoJobs_dpt = 0
            for user_d in user_dpt:
                user_dpt_AC_tmp = []
                line_psy = LocateLine(user_d, f_psy_lst)
                if line_psy == 'No Match':
                    continue
                # psy格式
                # employee_name,user_id,O,C,E,A,N
                if float(line_psy[-2]) < A_mean_total:
                    Dpt_Cnt_Less_A += 1
                    if float(line_psy[3]) < C_mean_total:
                        Dpt_Cnt_Less_AC += 1
                if float(line_psy[3]) < C_mean_total:
                    Dpt_Cnt_Less_C += 1
                if float(line_psy[-1]) > N_mean_total:
                    Dpt_Cnt_High_N += 1
                for ele in line_psy[2:]:
                    user_dpt_AC_tmp.append(float(ele))
                #user_dpt_AC_tmp.append(float(line_psy[3])) # C分数
                #user_dpt_AC_tmp.append(float(line_psy[-2])) # A分数
                user_dpt_AC.append(user_dpt_AC_tmp)
                line_jobs = LocateLine(user_d, f_jobs_lst)
                if line_jobs == 'No Match':
                    continue
                if line_jobs.count('1') < 18:
                    Cnt_NoJobs_dpt += 1
            user_dpt_array = np.array(user_dpt_AC)
            print 'Bug: user_dpt is ', user_dpt, '\n'
            print 'Bug: user_dpt_array is ', line_lst[1], dpt_nm_1,  user_dpt_array[:3], '\n'
            O_mean, C_mean, E_mean, A_mean, N_mean = user_dpt_array.mean(axis=0)
            O_median, C_median, E_median, A_median, N_median = np.median(user_dpt_array, axis=0)
            # 先用均值计算CPBs
            CPB1, CPB2 = CalCPBs(O_mean, C_mean, E_mean, A_mean, N_mean)
            JS_user_tmp.append(CPB1)
            JS_user_tmp.append(CPB2)
            JS_user_tmp.append(Dpt_Cnt_Less_A)
            JS_user_tmp.append(Dpt_Cnt_Less_AC)
            JS_user_tmp.append(Dpt_Cnt_Less_C)
            JS_user_tmp.append(Dpt_Cnt_High_N)
            CPB1, CPB2 = CalCPBs(O_median, C_median, E_median, A_median, N_median)
            JS_user_tmp.append(CPB1)
            JS_user_tmp.append(CPB2)
            JS_user_tmp.append(Cnt_NoJobs_dpt)
            # print line_lst[1], JS_user_tmp, '\n'
            print line_lst[1], ' 部门CPBs计算完毕...\n'
        # 在写入领导人分数前先写入其工作状态，写入18个月中在职的数目，即其中[1]的数目
        line_jobstate = LocateLine(line_lst[1], f_jobs_lst)
        if line_jobstate == 'No Match':
            print 'Job State无匹配...\n'
            # [-1]表示没有找到Job State记录
            JS_user_tmp.append(-1)
        else:
            # CMP2946,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,
            # 统计工作状态中在职的时间月份
            Cnt_JobState = line_jobstate.count('1')
            JS_user_tmp.append(Cnt_JobState)
        # 开始计算用户的领导人分数
        if len(line_lst) == 9:
            print line_lst[1], 'No Supervisor...\n'
            JS_user_tmp.append(0)
            JS_user_tmp.append(0)
        if len(line_lst) == 10:
            line_leader = LocateLine(line_lst[-1], f_psy_lst)
            # psy格式
            # employee_name,user_id,O,C,E,A,N
            O_Score = float(line_leader[2])
            C_Score = float(line_leader[3])
            E_Score = float(line_leader[4])
            A_Score = float(line_leader[-2])
            N_Score = float(line_leader[-1])
            CPB1, CPB2 = CalCPBs(O_Score, C_Score, E_Score, A_Score, N_Score)
            JS_user_tmp.append(CPB1)
            JS_user_tmp.append(CPB2)
            JS_user_tmp.insert(0, line_lst[1])
            print JS_user_tmp, '\n'
        JS_Users_lst.append(JS_user_tmp)
        # print line_lst[1], '的JS特征为： ', JS_user_tmp, '\n'
print '数据特征提取阶段完成...\n'

print '开始将26个JS特征写入到新文件...\n'
f_15JS = open(Dst_Dir + '\\' + 'CERT5.2-200912-New-26JS-0.9-0.11.csv', 'w')
# f_15JS = open(r'CERT6.2-2009-12-New-26JS.csv', 'w')
f_15JS.write('user_id')
f_15JS.write(',')
f_15JS.write('O_Score')
f_15JS.write(',')
f_15JS.write('C_Score')
f_15JS.write(',')
f_15JS.write('E_Score')
f_15JS.write(',')
f_15JS.write('A_Score')
f_15JS.write(',')
f_15JS.write('N_Score')
f_15JS.write(',')
f_15JS.write('Team_CPB-I-mean')
f_15JS.write(',')
f_15JS.write('Team_CPB-O-mean')
f_15JS.write(',')
f_15JS.write('Users-less-mean-A')
f_15JS.write(',')
f_15JS.write('Users-less-mean-A and C')
f_15JS.write(',')
f_15JS.write('Users-less-mean-C')
f_15JS.write(',')
f_15JS.write('Users-High-mean-N')
f_15JS.write(',')
f_15JS.write('Team_CPB-I-median')
f_15JS.write(',')
f_15JS.write('Team_CPB-O-median')
f_15JS.write(',')
f_15JS.write('No-JobState-in-Team')
f_15JS.write(',')
f_15JS.write('Dpt-CPB-I-mean')
f_15JS.write(',')
f_15JS.write('Dpt_CPB-O-mean')
f_15JS.write(',')
f_15JS.write('Dpt-Less-A-mean')
f_15JS.write(',')
f_15JS.write('Dpt-Less-AC-mean')
f_15JS.write(',')
f_15JS.write('Dpt-less-C-mean')
f_15JS.write(',')
f_15JS.write('Dpt-High-N-mean')
f_15JS.write(',')
f_15JS.write('Dpt_CPB-I-median')
f_15JS.write(',')
f_15JS.write('Dpt_CPB-O-median')
f_15JS.write(',')
f_15JS.write('No-JobState-in-Dpt')
f_15JS.write(',')
f_15JS.write('Job State')
f_15JS.write(',')
f_15JS.write('Leader_CPB-I')
f_15JS.write(',')
f_15JS.write('Leader_CPB-O')
f_15JS.write('\n')
i = 0
while i < len(JS_Users_lst):
    # f_15JS.write(line_lst[i])
    # f_15JS.write(',')
    for seg in JS_Users_lst[i]:
        f_15JS.write(str(seg))
        f_15JS.write(',')
    f_15JS.write('\n')
    i += 1
f_15JS.close()
print '文件写入完毕...\n'
print 'Users_Short is ...\n'
for ele in User_Short:
    print ele, '\n'
print len(User_Short), '\n'
sys.exit()







