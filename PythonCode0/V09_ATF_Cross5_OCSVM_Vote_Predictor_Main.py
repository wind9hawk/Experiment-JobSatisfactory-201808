# coding:utf-8
# 对应于 ATF_Cross5_OCSVM_Vote_Predictor的Main函数

import os,sys
import V09_ATF_Cross5_OCSVM_Vote_Predictor
import V09_ATF_Cross5_OCSVM_Vote_Insiders_Predictor as Cross5_Insiders

from sklearn import svm
# clf = svm.OneClassSVM(kernel='rbf', tol=0.01, nu=0.35)
# print clf, '\n'

# sys.exit()

print '....<<<<基于5折多OCSVM投票的攻击倾向分析预测器>>>>....\n\n'

print '..<<环境数据准备>>..\n'
Dst_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.9'
Months_lst = []
for file in os.listdir(Dst_Dir):
    if os.path.isdir(Dst_Dir + '\\' + file) == True:
        if 'Dir' not in file:
            Months_lst.append(file)
    else:
        continue
print '总月份为： ', Months_lst, '\n'

# 注意，输入类的月份为N, N+1，不要超出2011-05
# # Insides目录从2010-06到2011-04：[5:-1]
for month in Months_lst[7:8]: # 2010-08:2010-09  [7:8]实验分析用
    next_month = Months_lst[Months_lst.index(month) + 1]
    atf_predictor = Cross5_Insiders.ATF_Cross5_OCSVM_Vote_Predictor(Dst_Dir, month, next_month)
    atf_predictor.Split_Cross5_Index()
    atf_predictor.Map_Index2Feat()
    atf_predictor.Train_5_OCSVMs()
    atf_predictor.Run_Predictor()
