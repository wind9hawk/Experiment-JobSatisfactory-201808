# coding:utf-8
# 本模块为针对JS_SVM_Predictor.class的对应运行文件

import os,sys
import V08_JS_SVM_Predictor_Class as JSVM_Class

print '......<<<<<<借助SVM的用户JS风险预测器>>>>>>......\n\n\n'

print '....<<<<初始化预测器对象>>>>....\n\n'
Dst_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.8'
Src_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.7'
jsvm_ins = JSVM_Class.JS_SVM_Predictor(Src_Dir, Dst_Dir)
#jsvm_ins.Data_Copy()
#jsvm_ins.Extract_JS_Feats('Train')
jsvm_ins.Build_Predictor(Dst_Dir + '\\' + 'Train_Dir')
