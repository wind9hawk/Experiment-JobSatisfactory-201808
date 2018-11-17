# coding:utf-8

# 本模块用于仅提取CERT5.2中特定的登陆登出数据

# 为了建立用户上下班时间，需要进行统计投票
# 1. 划定几个上班时间段与下班时间段
# 2. 通过统计月度内各个时间段登录/登出次数，投票决定该用户自身的上下班时间（不同职业、不同岗位的人上下班不完全一致）
# 作为函数模块以方便后续调用

import  os, sys
import numpy as np

# 定义一个提取时间的函数，具体到日子
def GetDate(date):
    # like: 01/02/2010 09:03:11
    year = date[6:10]
    month = date[:2]
    #day = date[3:5]
    return year + '-' + month# + '-' + day

# 定义一个从原始大文件中提取各个用户登陆信息的函数
def Extract_Logon_Data(DataSrc, Time_lst, DataDst):
    # DataSrc：用户原始数据路径
    # DataDst: 提取的各个用户登录信息存放目录
    # Time_lst：提取的月度列表，[1_month, 2_month...]
    # DataSrc = r'G:\r5.2\logon.csv'

    print '提取数据来源确认：', DataSrc, '\n'
    print '提取时间范围确认：', Time_lst, '\n'
    print '提取数据输出位置确认： ', DataDst, '\n'

    # 读入数据源
    f_src = open(DataSrc, 'r')
    f_src_lst = f_src.readlines()
    f_src.close()

    # 循环，依次读入数据源每一行
    # 每一行读入，若该行user_id并未分析过，则：
    # 1. 为该用户建立登录列表
    # 2. 以该用户为基准重新遍历全部数据源；
    # 3. 以时间列表作为筛选写入对应记录列表；
    # 4. 完毕后，写入到Dst目录下的用户文件
    # 5. 如果存在该用户，则跳过下一行
    # 继续下一个循环
    # 定义一个分析过的用户列表
    CERT52_Users = []
    line_no = 0
    while line_no < len(f_src_lst):
        # 登录数据格式：
        # ['id', 'date', 'user', 'pc', 'activity']
        # ['{Q4D5-W4HH44UC-5188LWZK}', '01/02/2010 02:24:51', 'JBI1134', 'PC-0168', 'Logon']
        line_lst = f_src_lst[line_no].strip('\n').strip(',').split(',')
        # print line_lst, '\n'
        # sys.exit()
        if line_lst[2] == 'user':
            line_no += 1
            continue
        else:
            if line_lst[2] not in CERT52_Users:
                # 说明遇到一个新用户
                # 为该用户建立单独的数据列表
                # 遍历全部数据源
                CERT52_Users.append(line_lst[2])
                user_logon_lst = [[] for i in range(len(Time_lst))]
                with open(DataSrc) as f:
                    for line_no_0 in f:
                        line_lst_0 = line_no_0.strip('\n').strip(',').split(',')
                        if line_lst_0[2] != line_lst[2]:
                            continue
                        else:
                            date = GetDate(line_lst_0[1])
                            if date not in Time_lst:
                                continue
                            else:
                                user_logon_lst[Time_lst.index(date)].append(line_lst_0[1:])
                print line_lst[2], '数据提取完毕，开始写入文件...\n'
                #for j in range(10):
                #    print user_logon_lst[j], '\n'
                #sys.exit()
                if os.path.exists(DataDst + '\\' + line_lst[2]) == False:
                    os.mkdir(DataDst + '\\' + line_lst[2])
                i = 0
                while i < len(Time_lst):
                    f_1 = open(DataDst + '\\' + line_lst[2] + '\\' + Time_lst[i] + '_csv', 'w')
                    for line_1 in user_logon_lst[i]:
                        if GetDate(line_1[0]) == Time_lst[i]:
                            for ele in line_1:
                                f_1.write(ele)
                                f_1.write(',')
                            f_1.write('\n')
                    print line_lst[2], Time_lst[i], '登录数据写入完毕...\n'
                    f_1.close()
                    i += 1
                line_no += 1
            else:
                line_no += 1
                continue







print '开始提取指定时间范围的用户登录数据...\n\n'
DataSrc = r'G:\r5.2\logon.csv'
DataDst = sys.path[0] + '\\' + r'CERT5.2_Logon-Off_Time_0.6'
if os.path.exists(DataDst) == False:
    os.mkdir(DataDst)
Time_lst = ['2009-12','2010-01']
Extract_Logon_Data(DataSrc, Time_lst, DataDst)