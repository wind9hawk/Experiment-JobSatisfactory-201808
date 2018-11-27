# coding:utf-8
# 本模块主要计算考虑平均出勤表现的综合迟到早退指数LED
# LED = LEC_current + Avg(LEC_i_month)

# 基本算法
# 1. 确定数据源：全部的月份列表，每个月份下的LED指标；
# 2. 依据综合公式计算每个月全新的LED_Values
# 3. 提取均值以及中位数以上用户，输出结果；

# 函数式编程

import os,sys

print '......<<<<<<CERT5.2用户综合出勤率统计分析预测器>>>>>>......\n\n\n'

print '....<<<<确定数据源>>>>.....\n\n'
# 要分析的月份目录：
Dst_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.7'
Months_lst = []
for file in os.listdir(Dst_Dir):
    if os.path.isdir(Dst_Dir + '\\' + file) == True:
        # Months_lst中是纯粹的月份，不包括路径
        Months_lst.append(file)
    else:
        continue

print '....<<<<开始循环计算每个月的综合LED结果>>>....\n\n'
for month in Months_lst:
    month_path = Dst_Dir + '\\' + month


