# coding:utf-8
# 本模块负责将日期转换为礼拜几
# 需要提供：
# 年度月份的总天数
# 开始计算日期天数是礼拜几

import os,sys

def Transfor_Date_2_Weekdays(date):
    # date: 2010-01-02
    # 静态数据
    # 一年有 12个月，其中：
    #
    # 一月，三月，五月，七月，八月，十月，十二月都有31天。
    #
    # 四月，六月，九月，十一月都是30天。
    cnt_10year_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    cnt_11year_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


    start_weekday_10 = 4  # 2010-01-01是礼拜五
    start_year_10 = 2010
    start_month_10 = 1
    start_day_10 = 1
    start_weekday_11 = 5 # 2011-01-01是礼拜六
    start_year_11 = 2011
    start_month_11 = 1
    start_day_11 = 1


    # 分析输入的日期对应的礼拜几
    year = float(date[:4])
    month = float(date[5:7])
    day = float(date[8:])

    cnt_days = 0 #相对于对应年的1月1日的偏移
    if year == 2010:
        print cnt_10year_days, '\n'
        j = 0
        while j < month - 1:
            cnt_days += cnt_10year_days[j]
            j += 1
            continue
        cnt_days += day
        cnt_days -= 1 # 减去1月1日自身一天
        print date, 'is from 2010-01-01', cnt_days, '天\n'
        print cnt_days % 7, '\n'
        print start_weekday_10, '\n'
        weekday = (start_weekday_10 + cnt_days) % 7 + 1
        print date, 'response to weekday is ', weekday, '\n'
        return weekday
    if year == 2011:
        # 需要以2011-01-01为起点
        j = 0
        while j < month - 1:
            cnt_days += cnt_11year_days[j]
            j += 1
            continue
        cnt_days += day
        cnt_days -= 1 # 减去自身一天
        print date, 'is from 2011-01-01', cnt_days, '天\n'
        print cnt_days % 7, '\n'
        print start_weekday_11, '\n'
        weekday = (start_weekday_11 + cnt_days) % 7 + 1
        print date, 'response to weekday is ', weekday, '\n'
        return weekday


# 提取Insiders的函数
def Extract_Insiders():
    dst_dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.9'
    # Insiders-1_Leave.csv
    # data like: KEW0198,2010-07-29,
    insiders_1_lst = []
    insiders_2_lst = []
    insiders_3_lst = []
    for file in os.listdir(dst_dir):
        if 'Insiders-1_Leave' in file:
            f_1 = open(dst_dir + '\\' + file, 'r')
            for line_1 in f_1.readlines():
                line_lst = line_1.strip('\n').strip(',').split(',')
                insiders_1_lst.append(line_lst[0])
            f_1.close()
            print 'Insiders_1名单提取完毕..\n'
        if 'Insiders-2_Leave' in file:
            f_2 = open(dst_dir + '\\' + file, 'r')
            for line_2 in f_2.readlines():
                line_lst = line_2.strip('\n').strip(',').split(',')
                insiders_2_lst.append(line_lst[0])
            f_2.close()
            print 'Insiders_1名单提取完毕..\n'
        if 'Insiders-3_Leave' in file:
            f_3 = open(dst_dir + '\\' + file, 'r')
            for line_3 in f_3.readlines():
                line_lst = line_3.strip('\n').strip(',').split(',')
                insiders_3_lst.append(line_lst[0])
            f_3.close()
            print 'Insiders_1名单提取完毕..\n'
    return insiders_1_lst, insiders_2_lst, insiders_3_lst

# Transfor_Date_2_Weekdays('2010-02-26') 验证通过

# 系统分析CERT5.2所有离开用户的离开礼拜几
# 1. 针对离开用户得到其礼拜几离开的信息
# 2. 计算CERT5.2中所有用户关联的离开用户的礼拜几，区分出礼拜一、礼拜二、--礼拜六、天以及礼拜一+礼拜二/礼拜三-礼拜六
# 3. user_id, lc_Monday, lc_Tuesday, lc_Wedesday, lc_Thursday, lc_Friday, lc_Saturday, lc_Sunday
# 4. cnt_lc_(Monday+Tuesday), cnt_lc_(Back_Week)

weekday = Transfor_Date_2_Weekdays('2010-02-28')
weekday = Transfor_Date_2_Weekdays('2010-05-19')
weekday = Transfor_Date_2_Weekdays('2011-09-12')

sys.exit()
Dst_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.9'
f_r_lu = open(Dst_Dir + '\\' + 'CERT5.2-Leave-Users_OnDays_0.6.csv', 'r')
f_w_luw = open(Dst_Dir + '\\' + 'CERT5.2-Leave-Users_OnWeekDays_0.6.csv', 'w')

Cnt_Leave_Weekdays = []
for line in f_r_lu.readlines():
    line_lst = line.strip('\n').strip(',').split(',')
    if len(line_lst) < 3:
        continue
    weekday = Transfor_Date_2_Weekdays(line_lst[1])
    Cnt_Leave_Weekdays.append(weekday)
    line_lst.insert(2, str(weekday))
    for ele in line_lst:
        f_w_luw.write(str(ele) + ',')
    f_w_luw.write('\n')
f_r_lu.close()
f_w_luw.close()

for i in range(8):
    if i == 0 or i == 8:
        continue
    else:
        print i, Cnt_Leave_Weekdays.count(i), '\t'

# 在上述工作完成后，继续进一步统计2000个CERT5.2中用户的Leave_Weekdays特征
# psychometric-5.2.csv
# CERT5.2-Leave-Users_OnWeekDays_0.9.csv
# CERT5.2_Users_LeaveContacts_EmailFeats.csv

CERT52_Users = []
f_psy = open(Dst_Dir + '\\' + 'psychometric-5.2.csv', 'r')
for line_psy in f_psy.readlines():
    line_lst = line_psy.strip('\n').strip(',').split(',')
    # employee_name,user_id,O,C,E,A,N
    # Maisie Maggy Kline,MMK1532,17,17,16,22,28
    if line_lst[1] == 'user_id':
        continue
    CERT52_Users.append(line_lst[1])
f_psy.close()

Leave_Weekdays = []
Leave_Users = []
f_lw = open(Dst_Dir + '\\' + 'CERT5.2-Leave-Users_OnWeekDays_0.9.csv', 'r')
for line_lw in f_lw.readlines():
    line_lst = line_lw.strip('\n').strip(',').split(',')
    tmp_lw = []
    tmp_lw.append(line_lst[0])
    tmp_lw.append(float(line_lst[2]))
    Leave_Users.append(line_lst[0])
    Leave_Weekdays.append(tmp_lw)
f_lw.close()

f_lc = open(Dst_Dir + '\\' + 'CERT5.2_Users_LeaveContacts_EmailFeats.csv', 'r')
f_lwd = open(Dst_Dir + '\\' + 'CERT5.2_Users_LeaveContacts_Weekdays.csv', 'w')
CERT52_Users_WithLC = []
# <<MMK1532_start>>:2011-06-30
# 2010-02:
# WMH1300,1.0,1.0,[2010-01-25],38275.0,0.0,0,[],0,0,1,0,
# 2010-03:
# MIB1265,1.0,1.0,[2010-03-05],26650.0,0.0,0,[],0,0,1,0,
# 2010-04:
# 2010-05:
# 2010-06:
# <<MMK1532_end>>
CERT52_Users_Leave_Weekdays = []
f_lc_lst = f_lc.readlines()
for line in f_lc_lst[:]:
    line_lst = line.strip('\n').strip(',').split(',')
    if len(line_lst) == 1 and '_start>>' in line_lst[0]:
        # 用户LC记录的起点
        user = line_lst[0][2:9]
        CERT52_Users_WithLC.append(user)
        user_lwd_feat = [0.0 for i in range(9)]
        i = f_lc_lst.index(line) + 1
        while i < len(f_lc_lst):
            line_new = f_lc_lst[i].strip('\n').strip(',').split(',')
            if len(line_new) == 1 and '-' in line_new[0]:
                i += 1
                continue
            if len(line_new) == 1 and '_end>>' in line_new[0]:
                break
            index_leave = Leave_Users.index(line_new[0])
            weekday = Leave_Weekdays[index_leave][1]
            user_lwd_feat[int(weekday) - 1] += 1
            i += 1
            continue
        tmp_lw = []
        tmp_lw.append(user)
        for ele in user_lwd_feat:
            tmp_lw.append(ele)
        tmp_lw[-2] = user_lwd_feat[0] + user_lwd_feat[1]
        tmp_lw[-1] = user_lwd_feat[2] + user_lwd_feat[3] + user_lwd_feat[4]
        CERT52_Users_Leave_Weekdays.append(tmp_lw)
        print user, 'Leaver Weekdays统计完毕', tmp_lw, '\n'

for line in CERT52_Users_Leave_Weekdays:
    for ele in line:
        f_lwd.write(str(ele) + ',')
    f_lwd.write('\n')
f_lwd.close()

Insiders_1, Insiders_2, Insiders_3 = Extract_Insiders()
CERT52_Users_Leave_Weekdays_Sort_1Half = sorted(CERT52_Users_Leave_Weekdays, key=lambda t:t[-1], reverse=True)
for insider in Insiders_2:
    for line in CERT52_Users_Leave_Weekdays_Sort_1Half:
        if insider == line[0]:
            print insider, CERT52_Users_Leave_Weekdays_Sort_1Half.index(line), '\n'










