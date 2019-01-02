# coding:utf-8
# 基于用户JS特征的SVM预测器的Main函数
# 1. 整体框架用面向过程的方式编写；
# 2. 核心功能模块采用面向对象的方式构建类对象；
# 3. JS特征提取第一阶段：为2010-01：2011-05每个月建立单独的用户JS特征；
# 4. JS特征：
# 4.1 user_id,
# 4.2 o,c,e,a,n
# 4.3 cpb-i,cpb-o
# 4.4 relation with leave contacts
# 4.4.1 dis_ocean, dis_os
# 4.4.2 cnt_send, cnt_recv
# 4.4.3 cnt_send_size, cnt_recv_size
# 4.4.4 cnt_send_attach, cnt_recv_attach
# 4.4.5 cnt_send_days, cnt_recv_days
# 4.4.6 cnt_email_days

import os,sys

import V09_JS_SVM_Predictor_01 as JSP01

Flag_0 = False
if Flag_0:
    print '....<<<<基于用户JS特征的SVM预测器实验>>>>....\t基于CERT5.2数据集\n\n'
    # JS_Feat提取第一阶段：为2010-01：2011-05的每个月份分别建立完整的JS_Feat/Users_Label
    print '..<<JS_Feat提取第一阶段：为每个月份构建JS_Feat以及Users_Label>>..\n'
    Dst_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.9'
    Months_lst = []
    for month in os.listdir(Dst_Dir):
        if os.path.isdir(Dst_Dir + '\\' + month) == True:
            Months_lst.append(month)
        else:
            continue
    Months_lst.sort()
    print '需要分析的目录为：', Months_lst, '\n'

    # 针对每一个月提取当月的JS_Feats特征
    Extract_JSF_Flag = True
    if Extract_JSF_Flag:
        for month in Months_lst[:]:
            jsp_1 = JSP01.JS_Feats(Dst_Dir, month, Months_lst)
            jsp_1.Extract_JS_Feats()
            del jsp_1

def Extract_Insiders(f_insiders_lst):
    insiders = []
    for line in f_insiders_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        insiders.append(line_lst[0])
    return insiders

Flag_1 = False
if Flag_1:
    # 提取CERT5.2中Insiders_4的用户列表
    # src_dir = r'G:\GitHub\Essay-Experiments\Experiment-JobSatisfactory-201808\r5.2-4'
    dst_dir = r'G:\GitHub\Essay-Experiments\Experiment-JobSatisfactory-201808\PythonCode0\JS-Risks_Analyze-0.9'
    f_src = open(dst_dir + '\\' + 'CERT5.2-Leave-Users_OnDays_0.6.csv', 'r')
    f_1 = open(dst_dir + '\\' + 'Insiders-1_Leave.csv', 'r')
    f_2 = open(dst_dir + '\\' + 'Insiders-2_Leave.csv', 'r')
    f_3 = open(dst_dir + '\\' + 'Insiders-3_Leave.csv', 'r')
    insiders_1 = Extract_Insiders(f_1.readlines())
    insiders_2 = Extract_Insiders(f_2.readlines())
    insiders_3 = Extract_Insiders(f_3.readlines())
    f_1.close()
    f_2.close()
    f_3.close()
    print insiders_1[:5], '\n'
    print insiders_2[:5], '\n'
    print insiders_3[:5], '\n'
    f_dst = open(dst_dir + '\\' + 'CERT5.2-LaidOff-Users_OnDays_0.6.csv', 'w')
    for line in f_src.readlines():
        line_lst = line.strip('\n').strip(',').split(',')
        if len(line_lst) == 1:
            continue
        if line_lst[0] in insiders_1 or line_lst[0] in insiders_2 or line_lst[0] in insiders_3:
            print line_lst[0], 'in insiders\n'
            continue
        else:
            for ele in line_lst:
                f_dst.write(str(ele) + ',')
            f_dst.write('\n')
    f_dst.close()


Flag_2 = True
if Flag_2:
    # 统计下2010-09月份预测结果中，判定为[+1]且DF和中位数大于0.89的用户；
    dst_dir = r'G:\GitHub\Essay-Experiments\Experiment-JobSatisfactory-201808\PythonCode0\JS-Risks_Analyze-0.9\2010-09'
    file = r'2010-09_CERT5.2_ATF_Cross5_OCSVM_DF_MinMax-0.1.csv'
    file_path = dst_dir + '\\' + file
    print file_path, '\n'
    f_4 = open(file_path, 'r')
    f_4_lst = f_4.readlines()
    Cnt_All = len(f_4_lst)
    print f_4_lst[:10], '\n'
    Cnt_Over_Median_P = 0
    Users_Check = []
    for line in f_4_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        if line_lst[-3] == '1' and float(line_lst[-1]) > 0.89:
            Users_Check.append(line_lst[0])
            Cnt_Over_Median_P += 1
    # 此时文件指针已经到了文件末尾，如何readlines()都是空
    #print len(f_4.readlines()), '\n'
    #print f_4.readlines(), '\n'
    #sys.exit()
    print '筛选后用户共有：', Cnt_Over_Median_P, '\t', Cnt_Over_Median_P / float(Cnt_All), '\n'
    f_4.close()


