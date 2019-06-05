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

print '....<<<<第二阶段：确定训练集与测试集范围，并以此训练输出最佳的SVM Predictor>>>>....\n\n'
# 开始构建训练集与测试集，并建立SVM Predictor
# 定义训练器对象
# 2010-01:2010-04训练，2010-05验证；2010-06:2011-05测试
#Train_Obj = JSP01.JS_SVM_Predictor(Dst_Dir, Months_lst[:5], Months_lst[5:])
# 初始化训练JS_Feats与对应的训练集用户标签；
#Train_Obj.Build_TrainSet()
#Train_Obj.Build_ValidateSet()
#Train_Obj.Train_SVM_Predictor()

# 上述通过



sys.exit()








