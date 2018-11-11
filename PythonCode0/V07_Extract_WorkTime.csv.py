# coding:utf-8
# 本脚本用于针对CERT5.2的用户数据，生成我们认为i的该用户的上下班时间（确定值）

# 基本思路：
# 1. 建立一个通用的时间窗口列表，上班时间窗口开始自早上6：00.终止于早上9：30；下班时间列表起始分别为下午16：00与晚上19：30,
# 并且以0.5小时为一个时间窗口长度；
# 2. 针对每个用户，统计该用户在2010-01这个月中，所有的登录/登出时间位于的时间窗口的次数；
# 3. 最后选择次数最多的时间窗口的上下限作为上下班时间；
# 4. 更多管理员之类的统计，6：00之前的登入以及19：30之后的登出都不再考虑

import os,sys


# 定义一个提取小时、分钟的函数
def Extract_HourMinute(date):
    # 01/02/2010 06:35:00
    hour = date[11:13]
    minute = date[14:16]
    return hour, minute, float(hour) + float(minute) / 60

# 定义一个自动提取上下班时间确定的函数
def Extract_WorkTime(user, f_logon_lst):
    # f_logon_lst为用户user在2010-01的登录登出数据
    print '为用户 ', user, '建立上下班时间窗口字典..\n\n'
    # 上班时间窗口从早上6点开始，到早上9点半结束，一共5个时间窗口，分别是：
    # 6：01-6：30；6：31-7：00；7：01-7：30；7：31-8：00；8：01-8：30；8：31-9：00；9：01-9：30
    # 下班时间窗口分别为
    # 下午16：00-16：29； 16：30-16：59；17：00-17：29；17：30-17：59；18：00-18：29；18：30-18：59；19：00-19：29
    WorkOn = []
    i = 0
    while i < 7:
        start = 6.5 + 0.5 * i
        tmp_0 = []
        tmp_0.append(start)
        tmp_0.append(0.0)
        WorkOn.append(tmp_0)
        i += 1
    print 'WorkOn 初始化为： ', WorkOn, '\n'
    WorkOff = []
    i = 0
    while i < 7:
        start = 16 + 0.5 * i
        tmp_0 = []
        tmp_0.append(start)
        tmp_0.append(0.0)
        WorkOff.append(tmp_0)
        i += 1
    print user, '上下班原始时间窗口字典初始化完毕..\n'

    print '开始具体统计上下班时间段特征..\n'
    for line in f_logon_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        #     # 登录数据格式：
        #     # 01/02/2010 06:35:00,HMI1448,PC-9352,Logon,
        #     # 01/02/2010 11:02:11,HMI1448,PC-9352,Logon,
        #     # 01/02/2010 16:47:00,HMI1448,PC-9352,Logoff,
        if line_lst[3] == 'Logon':
            hour, minute, time_value = Extract_HourMinute(line_lst[0])
            j = 1
            while j < len(WorkOn):
                if time_value <= WorkOn[j - 1][0]:
                    WorkOn[j - 1][1] += 1.0
                    break
                if time_value > WorkOn[j - 1][0] and time_value <= WorkOn[j][0]:
                    WorkOn[j][1] += 1.0
                    break
                else:
                    j += 1
                    continue
        if line_lst[3] == 'Logoff':
            #print 'Logoff case is ', line_lst, '\n'
            hour, minute, time_value = Extract_HourMinute(line_lst[0])
            #print hour, minute, time_value, '\n'
            j = len(WorkOff) - 1
            while j >= 0:
                if time_value >= WorkOff[j][0]:
                    WorkOff[j][1] += 1.0
                    break
                if time_value >= WorkOff[j - 1][0] and time_value < WorkOff[j][0]:
                    WorkOff[j - 1][1] += 1.0
                    break
                else:
                    j -= 1
                    continue
    print 'in Function WorkOff is like: ', WorkOff, '\n'
    # sys.exit()
    return WorkOn, WorkOff

# 定义一个函数从先期得到的WorkOn/WorkOff中筛选出次数最多的时间
def Decide_WorkOnOff_Time(WorkOn, WorkOff):
    WorkOn_Order = sorted(WorkOn, key=lambda t:t[1], reverse=True)
    WorkOff_Order = sorted(WorkOff, key=lambda t:t[1], reverse=True)
    return WorkOn_Order[0], WorkOff_Order[0]


print '......<<<<<<开始确定CERT5.2中用户的上下班时间>>>>>>.....\n\n'


print '....<<<<准备数据源>>>>....\n\n'
Logon_Dir = sys.path[0] + '\\' + 'CERT5.2_Logon-Off_Time_0.6'

if os.path.exists(sys.path[0] + '\\' + 'JS-Risks_Analyze-0.7') == False:
    os.mkdir(sys.path[0] + '\\' + 'JS-Risks_Analyze-0.7')
Dst_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.7'

f_WorkTime = open(Dst_Dir + '\\' + 'V07_CERT5.2_Users_WorkOn-Off_Time.csv', 'w')

# 定义最终输出的用户上下班时间
# [user_id, WorkOn_Time. WorkOff_Time]
CERT52_Users_WorkTime = []

print '....<<<<开始循环遍历登录文件，确定用户上下班时间>>>>....\n\n'
# Logon_Dir\user_id\2010-01_csv
# G:\GitHub\Essay-Experiments\Experiment-JobSatisfactory-201808\PythonCode0\CERT5.2_Logon-Off_Time_0.6
print os.listdir(Logon_Dir), '\n'
for user in os.listdir(Logon_Dir)[:]:
    user_dir = Logon_Dir + '\\' + user
    for file in os.listdir(user_dir):
        if '2010-01' not in file:
            continue
        else:
            #print file, '\n'
            #sys.exit()
            f_logon = open(user_dir + '\\' + file)
            f_logon_lst = f_logon.readlines()
            f_logon.close()
            print user, '2010-01:登录登出数据读入完毕...\n'
            # 调用自动筛选WorkOn/WorkOff Time的函数
            WorkOn, WorkOff = Extract_WorkTime(user, f_logon_lst)
            print 'WorkOn is like: ', WorkOn, '\n'
            print 'WorkOff is like: ', WorkOff, '\n'

            # 开始筛选出出现次数最多的作为WorkOn/WorkOff 时间
            # 调用函数
            WorkOn_0, WorkOff_0 = Decide_WorkOnOff_Time(WorkOn, WorkOff)
            print WorkOn_0, WorkOff_0, '\n'
            WorkOn_Time = WorkOn_0[0]
            WorkOff_Time = WorkOff_0[0]

            f_WorkTime.write(user)
            f_WorkTime.write(',')
            f_WorkTime.write('WorkOn:')
            f_WorkTime.write(str(WorkOn_Time))
            f_WorkTime.write('WorkOff:')
            f_WorkTime.write(str(WorkOff_Time))
            f_WorkTime.write('\n')

