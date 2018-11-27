# coding:utf-8
# 本模块主要基于用户当月的登录登出体现的出勤特征，来计算其缺勤指数（迟到早退指数）

# 对于涉及到CERT5.2中的Insiders_2的月份开始分析，即从2010-07月开始分析晒黑选结果（第一个离职在2010-08）
# 获取Insiders_2的用户及离职时间列表
# 从2010-07开始读取月份目录——2011-05
# ELV数据：2010-03_Early_Late_Values_Standard.csv
# Over_Mean: 2010-03_Elv_Over_Mean_Standard.csv]
# Over_Median: 2010-03_Elv_Over_Median_Standard.csv
# 假想得到的数据格式：
# month:
# Over_ELV_Mean: user elv, index
# Over_ELV_Median: user elv, index
# insiders, leave_month, insider_elv, index in elv feats,
# True/False Over Mean, True/False Over Median
# 命中：X， 错过：Y


import os,sys


print '......<<<<<<CERT5.2单月ELD数据筛选分析>>>>>>......\n\n\n'

print '....<<<<指定数据源>>>>....\n\n'
Dst_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.7'
Insiders_2 = []
# Insiders-2_Leave.csv
f_Insiders_2 = open(Dst_Dir + '\\' + 'Insiders-2_Leave.csv', 'r')
f_Insiders_2_lst = f_Insiders_2.readlines()
f_Insiders_2.close()
for line in f_Insiders_2_lst:
    line_lst = line.strip('\n').strip(',').split(',')
    tmp_0 = []
    tmp_0.append(line_lst[0])
    tmp_0.append(line_lst[1])
    Insiders_2.append(tmp_0)
print '..<<测试Insiders_2列表>>..\n'
for i in range(5):
    print i, Insiders_2[i], '\n'
# 初始化要分析的月份，因为第一个Insiders_2离职在2010-08，因此从2010-07开始分析
Months_lst = ['2010-07', '2010-08', '2010-09', '2010-10', '2010-11', '2010-12',
              '2011-01', '2011-02', '2011-03', '2011-04', '2011-05']
# 分析2010-07以预测2010-08， 分析2011-04以预测2011-05


print '....<<<<由于所需数据已经提前处理完毕，直接提取数据计算即可>>>>....\n\n'
# 建立一个保存输出结果的文件
f_single_elv = open(Dst_Dir + '\\' + 'CERT5.2_SingleMonth_ELV_Predictor.csv', 'w')
# 定义一个全局计数器，用以统计该单月出勤预测器的效果
Cnt_In_Mean = 0
Cnt_In_Median = 0
Out_Mean_Insiders = []
Out_Median_Insiders = []
# 以Insiders_2为基准进行
for insider in Insiders_2[0:]:
    # insider format: ['VCF1602', '2010-08-20']
    leave_month = insider[1][:7]
    if Months_lst.index(leave_month) - 1 < 0:
        # 说明没有该用户离职前一个月有数据
        continue
    else:
        # 锁定predictor所在文件
        pre_index = Months_lst.index(leave_month) - 1
        pre_month = Months_lst[pre_index]
        pre_month_dir = Dst_Dir + '\\' + pre_month
        # 写入该用户的头信息
        f_single_elv.write(pre_month + '\n')
        # f_single_elv.write(insider[0] + ',' + insider[1] + '\n')
        # 锁定该目录下的三个重要的数据文件：
        # 2010-07_Early_Late_Values_Standard.csv
        # 2010-07_Elv_Over_Mean_Standard.csv
        # 2010-07_Elv_Over_Median_Standard.csv
        for file in os.listdir(pre_month_dir):
            if 'Early_Late_Values_Standard' in file:
                f_elv_values = open(pre_month_dir + '\\' + file, 'r')
                f_elv_lst = f_elv_values.readlines()
                f_elv_values.close()
            if 'Elv_Over_Mean_Standard' in file:
                f_elv_mean = open(pre_month_dir + '\\' + file, 'r')
                f_elv_mean_lst = f_elv_mean.readlines()
                f_elv_mean.close()
            if 'Elv_Over_Median_Standard' in file:
                f_elv_median = open(pre_month_dir + '\\' + file, 'r')
                f_elv_median_lst = f_elv_median.readlines()
                f_elv_median.close()
        print pre_month, '..<<ELV数据源读取完毕>>..\n'
        # 先读取琢磨为的over_mean与over_median数据
        last_mean_index = len(f_elv_mean_lst)
        last_mean_feat = f_elv_mean_lst[-1].strip('\n').strip(',').split(',')
        #print f_elv_mean_lst[-1], '\n'
        #sys.exit()
        f_single_elv.write('Over_ELV_Mean:,' + last_mean_feat[0] + ',' + last_mean_feat[1] + ',' + str(last_mean_index) + '\n')
        last_median_index = len(f_elv_median_lst)
        last_median_feat = f_elv_median_lst[-1].strip('\n').strip(',').split(',')
        f_single_elv.write('Over_ELV_Median:,' + last_median_feat[0] + ',' + last_median_feat[1] + ',' + str(last_median_index) + '\n')

        print '..<<开始写该insider的信息>>..\n'
        f_single_elv.write(insider[0] + ',' + insider[1] + ',')
        # 要写insider的elv及其排序索引
        for line in f_elv_lst:
            line_lst = line.strip('\n').strip(',').split(',')
            if line_lst[0] != insider[0]:
                continue
            else:
                insider_index = f_elv_lst.index(line) + 1
                f_single_elv.write('ELV:,' + line_lst[1] + ',' + str(insider_index) + '\n')
                if insider_index > last_mean_index:
                    f_single_elv.write('Over_Mean:' + ',' + 'False' + '\n')
                    Out_Mean_Insiders.append(insider)
                else:
                    f_single_elv.write('Over_Mean:' + ',' + 'True' + '\n')
                    Cnt_In_Mean += 1
                if insider_index > last_median_index:
                    f_single_elv.write('Over_Median:' + ',' + 'False' + '\n')
                    Out_Median_Insiders.append(insider)
                else:
                    f_single_elv.write('Over_Median:' + ',' + 'True' + '\n')
                    Cnt_In_Median += 1
        print insider, '分析完毕..\n'
        continue

f_single_elv.close()
print '....<<<<CERT5.2场景二用户单月预测出勤分析完毕>>>>....\n\n'
print '..<<统计结果>>..\n'
print '单月预测，Over_Mean命中： ', Cnt_In_Mean, Cnt_In_Mean / float(30), '\n'
print '单月预测，Over_Median命中： ', Cnt_In_Median, Cnt_In_Median / float(30), '\n'
print 'Over_Mean失败用户： \n'
for i in range(30 - Cnt_In_Mean):
    print i, Out_Mean_Insiders[i], '\n'
print 'Over_Median失败用户： \n'
for i in range(30 - Cnt_In_Median):
    print i, Out_Median_Insiders[i], '\n'



sys.exit()







