# coding:utf-8
# 经过反复的假设与实验验证，这次我们采取Team决定的上下班时间
# 1. 用户守时多于不守时：统计2010-01月份用户的出勤表现，依据频繁高低选择出现最多的时间窗口作为上下班时间
# （之前的工作，V07_CERT5.2_Users_WorkOn-Off_Time_Oneself.csv）
# 2. 团队守时多于不守时：基于LDAPUsers数据，进一步以Team为单位计算出单位的WorkTime，然后反映射到用户身上，得到
# V07_CERT5.2_Users_WorkOn-Off_Time_Team.csv

import os,sys

print '....<<<<依据Team表现确定用户的上下班时间>>>>....\n\n'

print '..<<确定数据源>>..\n'

Dst_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.7'
# 2010-01月份个人出勤表现得到的上下班时间
WorkTime_Oneself_Path = Dst_Dir + '\\' + 'V07_CERT5.2_Users_WorkOn-Off_Time_Oneself.csv'
# CERT5.2的LDAP数据
LDAP_Users_Path = sys.path[0] + '\\' + 'CERT5.2-LDAPUsers.csv'
# 读入内容行列表
f_WorkTime_Oneself = open(WorkTime_Oneself_Path, 'r')
f_WT_Oneself_lst = f_WorkTime_Oneself.readlines()
f_WorkTime_Oneself.close()
#
f_LDAP_Users = open(LDAP_Users_Path, 'r')
f_LDAP_Users_lst = f_LDAP_Users.readlines()
f_LDAP_Users.close()

print '..<<开始计算LDAP中每个Team的上下班时间，并保存>>..\n'
# 本步骤的目标：
# Team_No,WorkOn:8.5,WorkOff:17.0
# LDAP数据格式
# CERT5.2 LDAP Users
# 143
# ['': '': '': ''],ETW0002,
# ['1 - Executive': '': '': ''],NJC0003,PTH0005,
# ['1 - Executive': '1 - Adminstration': '': ''],BBB0012,CWC0006,
#
# 定义Team_WorkTime保存的文件
f_Team_WorkTime = open(Dst_Dir + '\\' + 'V07_CERT5.2_Team_WorkTime.csv', 'w')
# 定义最终要保存的Team时间列表
Team_WorkTime_lst = []
for line in f_LDAP_Users_lst:
    # 每行代表一个Team名称及其成员
    line_lst = line.strip('\n').strip(',').split(',')
    if len(line_lst) < 2:
        continue
    team_time = []
    team_time.append(line_lst[0])
    # 开始逐个用户统计上下班频率最高的时间
    team_workon_time = []
    team_workon_counts = []
    team_workoff_time = []
    team_workoff_counts = []
    for user in line_lst[1:]:
        # 逐个循环匹配到该用户的上下班时间
        for line_time in f_WT_Oneself_lst:
            # data like: # Team_No,WorkOn:8.5,WorkOff:17.0
            line_time_lst = line_time.strip('\n').strip(',').split(',')
            if line_time_lst[0] == user:
                if line_time_lst[1][7:] not in team_workon_time:
                    team_workon_time.append(line_time_lst[1][7:])
                    team_workon_counts.append(1)
                else:
                    team_workon_counts[team_workon_time.index(line_time_lst[1][7:])] += 1
                if line_time_lst[2][8:] not in team_workoff_time:
                    team_workoff_time.append(line_time_lst[2][8:])
                    team_workoff_counts.append(1)
                else:
                    team_workoff_counts[team_workoff_time.index(line_time_lst[2][8:])] += 1
                print line_lst[0], ':', user, '上下班时期采点完毕..\n'
                print team_workon_time, team_workon_counts, '\n'
                print team_workoff_time, team_workoff_counts, '\n'
                break
            else:
                continue
    # 若极端情况出现，即同一个组中，出现多个最常出现的上下班时间，则我们这时候依据最好人假设，选取最常出现的最晚上班与最早下班时间
    if team_workon_counts.count(max(team_workon_counts)) == 1:
        team_workon = team_workon_time[team_workon_counts.index(max(team_workon_counts))]
    else:
        team_workon_tmp = []
        i = 0
        while i < len(team_workon_counts):
            if team_workon_counts[i] == max(team_workon_counts):
                team_workon_tmp.append(team_workon_time[i])
                i += 1
                continue
            else:
                i += 1
                continue
        team_workon = max(team_workon_tmp)
    if team_workoff_counts.count(max(team_workoff_counts)) == 1:
        team_workoff = team_workoff_time[team_workoff_counts.index(max(team_workoff_counts))]
    else:
        team_workoff_tmp = []
        j = 0
        while j < len(team_workoff_counts):
            if team_workoff_counts[j] == max(team_workoff_counts):
                team_workoff_tmp.append(team_workoff_time[j])
                j += 1
                continue
            else:
                j += 1
                continue
        team_workoff = min(team_workoff_tmp)
    team_time.append(team_workon)
    team_time.append(team_workoff)
    for ele in team_time:
        f_Team_WorkTime.write(str(ele))
        f_Team_WorkTime.write(',')
    f_Team_WorkTime.write('\n')
f_Team_WorkTime.close()
print '..<<Team WorkTime统计完毕>>..\n'

print '..<<接着依据上述结果，计算得到每个用户的上下班时间（基于Team）>>..\n'
# 定义Team_WorkTime文件
f_Team_WorkTime = open(Dst_Dir + '\\' + 'V07_CERT5.2_Team_WorkTime.csv', 'r')
f_Team_WT_lst = f_Team_WorkTime.readlines()
f_Team_WorkTime.close()

# 定义一个保存的CERT5.2用户上下班文件
f_Users_WorkTime = open(Dst_Dir + '\\' + 'V07_CERT5.2_Users_WorkOn-Off_Time_Team.csv', 'w')
CERT52_Users_WorkTime = []
for line in f_LDAP_Users_lst:
    # data like:
    # CERT5.2 LDAP Users
    # 143
    # ['': '': '': ''],ETW0002,
    # ['1 - Executive': '': '': ''],NJC0003,PTH0005,
    # ['1 - Executive': '1 - Adminstration': '': ''],BBB0012,CWC0006,
    line_lst = line.strip('\n').strip(',').split(',')
    if len(line_lst) < 2:
        continue
    for line_worktime in f_Team_WT_lst:
        line_wt = line_worktime.strip('\n').strip(',').split(',')
        if line_wt[0] == line_lst[0]:
            workon_time = line_wt[1]
            workoff_time = line_wt[2]
    for user in line_lst[1:]:
        user_wt = []
        user_wt.append(user)
        user_wt.append(workon_time)
        user_wt.append(workoff_time)
        CERT52_Users_WorkTime.append(user_wt)
CERT52_Users_WorkTime_Sort = sorted(CERT52_Users_WorkTime)
for i in range(10):
    print i, CERT52_Users_WorkTime_Sort[i], '\n'
# sys.exit()
for line in CERT52_Users_WorkTime_Sort:
    f_Users_WorkTime.write(line[0])
    f_Users_WorkTime.write(',')
    f_Users_WorkTime.write('WorkOn:' + str(line[1]))
    f_Users_WorkTime.write(',')
    f_Users_WorkTime.write('WorkOff:' + str(line[2]))
    f_Users_WorkTime.write('\n')
f_Users_WorkTime.close()

sys.exit()





