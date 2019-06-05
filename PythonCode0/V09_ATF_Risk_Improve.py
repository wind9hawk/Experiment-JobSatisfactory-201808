# coding:utf-8
# 在前期的研究中，得到的最好结果中，对于Insiders_3的召回率可以达到0.9，而最终的FPR约为0.128
# 我们接下来的工作需要进一步分析KMeans+OCSVM分析识别出的300多个用户，从中进一步筛选出真正的高危用户；

import os,sys
import sklearn.preprocessing as skp
import sklearn.decomposition as skd
import numpy as np
import copy
import V09_KMeans_Module

Dst_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.9'
Analyze_Dir = Dst_Dir + '\\' + 'KMeans_OCSVM_Insiders_Predictor'
f_insider_1 = open(Dst_Dir + '\\' + 'Insiders-1_Leave.csv', 'r')
f_insider_2 = open(Dst_Dir + '\\' + 'Insiders-2_Leave.csv', 'r')
f_insider_3 = open(Dst_Dir + '\\' + 'Insiders-3_Leave.csv', 'r')
Insiders_1 = []
Insiders_2 = []
Insiders_3 = []
for line in f_insider_1.readlines():
    line_lst = line.strip('\n').strip(',').split(',')
    #insider_tmp = []
    #insider_tmp.append(line_lst[0])
    #insider_tmp.append(line_lst[1])
    Insiders_1.append(line_lst[0])
    f_insider_1.close()

for line in f_insider_2.readlines():
    line_lst = line.strip('\n').strip(',').split(',')
    Insiders_2.append(line_lst[0])
    f_insider_2.close()

for line in f_insider_3.readlines():
    line_lst = line.strip('\n').strip(',').split(',')
    Insiders_3.append(line_lst[0])
    f_insider_3.close()

# 我们先尝试提取出KMeans+OCSVM中识别的Risk_1阶段用户的ATF特征，在此基础上进一步分析；

# RBN1906,-1,-1,-2.539646441640965,
# user_id, pred, labels, DF
f_Risk = open(Analyze_Dir + '\\' + 'CERT5.2_KMeans_OCSVM_ATF_Predictor_Risk-0.1.csv', 'r')
Risk_1_ATF = [] # 用于存储KMeans+OCSVM阶段的预测结果；（遍历保留最高Recall的OCSVM）
Risk_1_Users = [] # Risk_1用户（去掉了TN Users）
Risk_1_DF = [] # Risk文件的全部内容，数值化变量
Risk_1_Labels = [] # Risk_1中真实的用户标签，Insiders_1/2/3为[+1]，其余为[-1]
for line in f_Risk.readlines():
    line_lst = line.strip('\n').strip(',').split(',')
    if line_lst[1] == '1': # pred
        Risk_1_Users.append(line_lst[0])
        risk_tmp = []
        risk_tmp.append(line_lst[0])
        for ele in line_lst[1:]:
            risk_tmp.append(float(ele))
        Risk_1_DF.append(risk_tmp)
        Risk_1_Labels.append(line_lst[2])  # GT label
    else:
        continue
print Risk_1_Users[0], Risk_1_DF[0], '\n'
f_ATF = open(Analyze_Dir + '\\' + 'CERT5.2_Static_ATF-0.1.csv', 'r')
for line_atf in f_ATF.readlines():
    line_lst = line_atf.strip('\n').strip(',').split(',')
    if line_lst[0] == 'user_id':
        Flag_lst = copy.copy(line_lst)
        continue
    if line_lst[0] in Risk_1_Users:
        atf_tmp = []
        atf_tmp.append(line_lst[0])
        for ele in line_lst[1:]:
            atf_tmp.append(float(ele))
        Risk_1_ATF.append(atf_tmp)

f_Risk.close()
f_ATF.close()
print 'Risk 1 ATF:', len(Risk_1_ATF), Risk_1_ATF[:2], '\n'
f_Risk_1 = open(Analyze_Dir + '\\' + 'KMeans_OCSVM_Risk_1_ATF.csv', 'w')
Flag_lst.insert(1, 'Pred')
Flag_lst.insert(2, 'GT_Label')
Flag_lst.insert(3, 'Decision Function')
for ele in Flag_lst:
    f_Risk_1.write(ele + ',')
f_Risk_1.write('\n')
for line in Risk_1_ATF:
    f_Risk_1.write(line[0] + ',')
    f_Risk_1.write(str(Risk_1_DF[Risk_1_Users.index(line[0])][1]) + ',')
    f_Risk_1.write(str(Risk_1_DF[Risk_1_Users.index(line[0])][2]) + ',')
    f_Risk_1.write(str(Risk_1_DF[Risk_1_Users.index(line[0])][-1]) + ',')
    for ele in line[1:]:
        f_Risk_1.write(str(ele) + ',')

    f_Risk_1.write('\n')
f_Risk_1.close()

# 放弃直接对Risk_1的用户ATF进行KMeans，效果十分不好
# 提取Risk_1_ATF中的LED（出勤指数）
Risk_1_LED = []
Risk_1_ATF_Users = []
for line_atf in Risk_1_ATF:
    Risk_1_ATF_Users.append(line_atf[0])
    led_tmp = []
    # led_tmp.append(line_atf[0])
    led_tmp.append(line_atf[-3] / float(line_atf[-1]))
    led_tmp.append(line_atf[-2] / float(line_atf[-1]))
    led_tmp.append((line_atf[-3] + line_atf[-2]) / float(line_atf[-1]))
    led_tmp.append(line_atf[-1])
    Risk_1_LED.append(led_tmp)
print 'Risk_1_LED is :', Risk_1_LED[:2], '\n'

# 开始提取其中的纯数据部分
Risk_1_LED_MinMax = skp.MinMaxScaler().fit_transform(copy.copy(Risk_1_LED))
Risk_1_LED_Scale = skp.scale(copy.copy(Risk_1_LED))

# 写入Risk_1_ATF_Users中的LED指数，并打印出Insiders的用户
f_Risk_1_LED = open(Analyze_Dir + '\\' + 'CERT5.2_Risk_1_LED.csv', 'w')
j = 0
while j < len(Risk_1_ATF_Users):
    led_w = []
    led_w.append(Risk_1_ATF_Users[j])
    led_w.extend(Risk_1_LED[j])
    led_w.extend(Risk_1_LED_MinMax[j])
    led_w.extend(Risk_1_LED_Scale[j])
    for ele in led_w:
        f_Risk_1_LED.write(str(ele) + ',')
    f_Risk_1_LED.write('\n')
    j += 1
f_Risk_1_LED.close()
print 'Risk_1_LED结果写入完毕..\n'

def Print_Insider_LED(insider_lst, type, risk_1_atf_users, risk_1_led, risk_1_led_minmax, risk_1_led_scale):
    for insider in insider_lst:
        Cnt_Risk_2 = 0.0
        i = 0
        while i < len(risk_1_atf_users):
            if risk_1_atf_users[i] == insider:
                print type, insider, risk_1_led[i], risk_1_led_minmax[i], risk_1_led_scale[i], '\n'
                if risk_1_led_minmax[i][-2] > 0.30:
                    Cnt_Risk_2 += 1
                i += 1
                continue
            else:
                if risk_1_led_minmax[i][-2] > 0.30:
                    Cnt_Risk_2 += 1
                i += 1
                continue
    print 'Risk_2用户个数为:', Cnt_Risk_2, Cnt_Risk_2 / len(Risk_1_Users), Cnt_Risk_2 / 2000, '\n'

Print_Insider_LED(Insiders_1, 'insider_1', Risk_1_ATF_Users, Risk_1_LED, Risk_1_LED_MinMax, Risk_1_LED_Scale)
Print_Insider_LED(Insiders_2, 'insider_2', Risk_1_ATF_Users, Risk_1_LED, Risk_1_LED_MinMax, Risk_1_LED_Scale)
Print_Insider_LED(Insiders_3, 'insider_3', Risk_1_ATF_Users, Risk_1_LED, Risk_1_LED_MinMax, Risk_1_LED_Scale)







