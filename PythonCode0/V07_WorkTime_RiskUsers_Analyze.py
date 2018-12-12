# coding:utf-8
# 时间紧迫，务必一次成功
# 1.统计每个月中用户的迟到与早退天，计算所占该月工作天的比例
# 2.计算每个用户每个月迟到早退比例之和，然后该月所有用户MinMax；
# 3.取该月中高于均值/高于中位数的一半用户，组成WorkTime_RiskUsers，保存
# 4.检查每个月份中，Insiders_2用户如果存在，则其所处位置是否位于前一半（或者更少）？

import os,sys
import numpy as np
import sklearn.preprocessing as skp

print '....<<<<指定数据源>>>>....\n\n'
# 月份目录
Dst_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.7'
# 场景二攻击者列表
Insiders_2 = []
Insiders2_Path = Dst_Dir + '\\' + 'Insiders-2_Leave.csv'
f_Insiders_2 = open(Insiders2_Path, 'r')
f_Insiders_2_lst = f_Insiders_2.readlines()
f_Insiders_2.close()
for line in f_Insiders_2_lst:
    line_lst = line.strip('\n').strip(',').split(',')
    Insiders_2.append(line_lst[0])

print '....<<<<开始逐月份分析>>>>....\n\n'
# 统计该月份所有用户的缺勤程度
# 选取一半
# 保存到文件
# 检查场景二用户在其中的位置

print '..<<计算每个月份的用户的缺勤程度>>..\n'
for file in os.listdir(Dst_Dir)[:-2]:
    file_path = Dst_Dir + '\\' + file
    if os.path.isdir(file_path) == False:
        continue
    #if '2010-11' in file:
    #    break
    else:
        # 月份目录
        for file_0 in os.listdir(file_path):
            # 目标文件：2010-01_early_late_feats.csv
            if 'early_late_team_feats.csv' not in file_0:
                continue
            else:
                f_early_late = open(file_path + '\\' + file_0, 'r')
                f_early_late_lst = f_early_late.readlines()
                f_early_late.close()
                # early_late数据格式：
                # JBI1134,6.5,19.0,6.0,0.0,25,
                users_month = []
                el_month = []
                for line in f_early_late_lst:
                    line_lst = line.strip('\n').strip(',').split(',')
                    if line_lst[0] == 'user_id':
                        continue
                    if line_lst[0] not in users_month:
                        users_month.append(line_lst[0])
                    tmp_0 = []
                    if len(line_lst) < 6:
                        continue
                    print 'line is ', line, '\n'
                    tmp_0.append(float(line_lst[3]) / float(line_lst[5]))
                    tmp_0.append(float(line_lst[4]) / float(line_lst[5]))
                    el_month.append(tmp_0)
                print file, '用户出勤情况比例提取完毕...\n'
                el_month_minmax = skp.MinMaxScaler().fit_transform(el_month)
                for i in range(5):
                    print i, el_month_minmax[i], '\n'

                print '组成该月用户的缺勤指数\n'
                elv_lst = []
                i = 0
                while i < len(el_month):
                    tmp_1 = []
                    tmp_1.append(users_month[i])
                    print el_month_minmax[i][0], el_month_minmax[i][1], '\n'
                    tmp_1.append(el_month_minmax[i][0] + el_month_minmax[i][1])
                    print 'tmp_1 is ', tmp_1, '\n'
                    i += 1
                    elv_lst.append(tmp_1)
                for i in range(5):
                    print i, elv_lst[i], '\n'
                    print i, type(elv_lst[i][1]), '\n'
                # sys.exit()

                print '排序保存得到的Early_Late_Value数据\n'
                f_el_value = open(file_path + '\\' + file + '_Early_Late_Values_Team.csv', 'w')
                elv_order_lst = sorted(elv_lst, key=lambda t:t[1], reverse=True)
                for ele in elv_order_lst:
                    for ele_0 in ele:
                        f_el_value.write(str(ele_0))
                        f_el_value.write(',')
                    f_el_value.write('\n')
                f_el_value.close()
                # sys.exit()
                # 从每个月份的elv_order_lst中，自动选取elv高于均值/中位数的用户作为LJS_Risk的用户保存输出
                # 首先计算均值与中位数
                elv_values = []
                for ele in elv_order_lst:
                    elv_values.append(ele[1])
                elv_values_array = np.array(elv_values)
                elv_mean = np.mean(elv_values_array)
                elv_median = np.median(elv_values_array)
                print '均值为： ', elv_mean, '中位数为： ', elv_median, '\n'
                # 开始计算高于均值的用户列表
                f_elv_Over_mean = open(file_path + '\\' + file + '_Elv_Over_Mean_Team.csv', 'w')
                f_elv_Over_median = open(file_path + '\\' + file + '_Elv_Over_Median_Team.csv', 'w')

                Over_Mean = 0
                Over_Median = 0
                j = 0
                while j < len(elv_order_lst):
                    if elv_order_lst[j][1] > elv_mean:
                        f_elv_Over_mean.write(elv_order_lst[j][0])
                        f_elv_Over_mean.write(',')
                        f_elv_Over_mean.write(str(elv_order_lst[j][1]))
                        f_elv_Over_mean.write('\n')
                        j += 1
                        continue
                    else:
                        Over_Mean = j + 1
                        j += 1
                        continue

                j = 0
                while j < len(elv_order_lst):
                    if elv_order_lst[j][1] > elv_median:
                        f_elv_Over_median.write(elv_order_lst[j][0])
                        f_elv_Over_median.write(',')
                        f_elv_Over_median.write(str(elv_order_lst[j][1]))
                        f_elv_Over_median.write('\n')
                        j += 1
                        continue
                    else:
                        Over_Median = j + 1
                        j += 1
                        continue
                f_elv_Over_mean.close()
                f_elv_Over_median.close()

                # 统计场景2的攻击者在elv_order_lst中的位置
                f_insiders2_elv = open(file_path + '\\' + file + '_Insiders_2_ELV_Team.csv', 'w')
                j = 0
                while j < len(elv_order_lst):
                    if elv_order_lst[j][0] in Insiders_2:
                        f_insiders2_elv.write(elv_order_lst[j][0])
                        f_insiders2_elv.write(',')
                        f_insiders2_elv.write(str(elv_order_lst[j][1]))
                        f_insiders2_elv.write(',')
                        f_insiders2_elv.write(str(j + 1))
                        f_insiders2_elv.write('\n')
                        j += 1
                    else:
                        j += 1
                f_insiders2_elv.close()
                print file, '....<<<<Early_Late_Value分析完毕>>>>....\n\n'

                # sys.exit()

