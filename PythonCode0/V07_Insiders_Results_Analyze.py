# coding:utf-8
# 本模块主要依据JSR的预测结果，对于CERT5.2的预测结果进行分析

# 首先是对于JSR预测系统的，全月份，场景123的Insiders的预测结果：
# 我们将按照场景分别统计三个场景的内部攻击者的JSR预测结果，大体格式为：
# 1行： insider_id, leave_time
# 2行： 2010-02, True(in High-Risk Predictor) or False
# 2.1 行： 2010-02， 本月的leave_feats
# 2.2 行： 2010-02， 本月JSR/截止到本月的累积JSR

import os,sys

def Extract_Insiders_Leave(Scene_No, Dst_Dir):
    # Scene_No: 索引0-1-2
    # Dst_Dir: Insiders_Leave所在目录
    Insiders_File = ['Insiders-1_Leave.csv','Insiders-2_Leave.csv','Insiders-3_Leave.csv']
    Insiders_lst = []
    f_Insiders = open(Dst_Dir + '\\' + Insiders_File[Scene_No], 'r')
    f_Insiders_lst = f_Insiders.readlines()
    f_Insiders.close()
    for line in f_Insiders_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        tmp_0 = []
        tmp_0.append(line_lst[0])
        tmp_0.append(line_lst[1])
        Insiders_lst.append(tmp_0)
    return Insiders_lst

def Extract_Statistical_Feats(Insiders_Leave, No, Dst_Dir):
    # 内部攻击者列表：Insiders_Leave
    # 分析输出目录：Dst_Dir = sys.path[0] + '\\' + '\JS-Risks_Analyze-0.7'
    f_insiders_jsr = open(Dst_Dir + '\\' + 'Insiders_' + str(No) + '_JSR_lst.csv', 'w')
    for user_line in Insiders_Leave[:]:
        f_insiders_jsr.write(user_line[0])
        f_insiders_jsr.write(',')
        f_insiders_jsr.write(user_line[1])
        f_insiders_jsr.write(',')

        # 开始仔细分析每个月份的JSR
        for dir in os.listdir(Dst_Dir):
            # 使用os.path.isfile/isdir判断是否是文件或者目录，必须使用全路径
            #print 'dir is ', Dst_Dir + '\\' + dir, '\n'
            #print os.path.isfile(Dst_Dir + '\\' + dir), '\n'
            if os.path.isfile(Dst_Dir + '\\' + dir)  == True:
                continue
            # 我们只分析目录
            # Current_Month_Leave_JSR.csv
            # Accumulated_Months_JSR.csv
            current_jsr_path = Dst_Dir + '\\' + dir + '\\' + 'Current_Month_Leave_JSR.csv'
            accu_jsr_path = Dst_Dir + '\\' + dir + '\\' + 'Accumulated_Months_JSR.csv'
            if os.path.exists(current_jsr_path) == False:
                # 该月份没有JSR分析，跳过
                continue
            f_current_jsr = open(current_jsr_path, 'r')
            f_current_jsr_lst = f_current_jsr.readlines()
            f_current_jsr.close()
            for jsr_line in f_current_jsr_lst:
                jsr_line_lst = jsr_line.strip('\n').strip(',').split(',')
                if jsr_line_lst[0] != user_line[0]:
                    #print dir, ':', jsr_line_lst[0], '!=', user_line[0], '\n'
                    continue
                else:
                    #print dir, ':', user_line[0], '=====', jsr_line_lst[0], '\n'
                    # sys.exit()
                    print '写入dir: ', dir, '\n'
                    f_insiders_jsr.write(dir)
                    f_insiders_jsr.write(',')
                    f_insiders_jsr.write('current:')
                    f_insiders_jsr.write(jsr_line_lst[1])
                    f_insiders_jsr.write(',')
                    break
            f_accu_jsr = open(accu_jsr_path, 'r')
            f_accu_jsr_lst = f_accu_jsr.readlines()
            f_accu_jsr.close()
            for jsr_line in f_accu_jsr_lst:
                jsr_line_lst = jsr_line.strip('\n').strip(',').split(',')
                if jsr_line_lst[0] != user_line[0]:
                    continue
                else:
                    f_insiders_jsr.write(dir)
                    f_insiders_jsr.write(',')
                    f_insiders_jsr.write('accu:')
                    f_insiders_jsr.write(':')
                    f_insiders_jsr.write(jsr_line_lst[1])
                    f_insiders_jsr.write('\n')

            # 尝试将该用户当月的RLV特征也写入
            print dir, user_line[0], '尝试写入RLV特征...\n'
            rlv_dir = Dst_Dir + '\\' + dir + '\\' + 'CERT5.2_Users_EmailFeats-0.7'
            rlv_path = rlv_dir + '\\' + user_line[0] + '_leave_efeats.csv'
            print os.path.exists(rlv_path), '\n'
            if os.path.exists(rlv_path) == True:
                # 当存在rlv特征时，打开写入
                f_rlv_user = open(rlv_path, 'r')
                f_rlv_lst = f_rlv_user.readlines()
                f_rlv_user.close()
                if len(f_rlv_lst) < 2:
                    continue
                else:
                    for rlv_line in f_rlv_lst:
                        rlv_line_lst = rlv_line.strip('\n').strip(',').split(',')
                        print rlv_line_lst, '\n'
                        # sys.exit()
                        if len(rlv_line_lst) < 2:
                            continue
                        else:
                            for ele in rlv_line_lst:
                                f_insiders_jsr.write(ele)
                                f_insiders_jsr.write(',')
                            f_insiders_jsr.write('\n')
        print user_line[0], 'JSR分析完毕...\n\n'
    f_insiders_jsr.close()




Flag_0 = True
if Flag_0 == True:
    print '....<<<<统计分析三个场景内部攻击者的JSR预测器效果>>>>....\n\n'

    print '..<<指定数据分析源>>..\n\n'
    Dst_Dir = sys.path[0] + '\\' + '\JS-Risks_Analyze-0.7'
    # 攻击者列表
    # Insiders_x_Leave Data like:
    # KEW0198,2010-07-29,
    Insiders_1_Leave = Extract_Insiders_Leave(0, Dst_Dir)
    Insiders_2_Leave = Extract_Insiders_Leave(1, Dst_Dir)
    Insiders_3_Leave = Extract_Insiders_Leave(2, Dst_Dir)
    print Insiders_1_Leave[:2], '\n'
    print Insiders_2_Leave[:2], '\n'
    print Insiders_3_Leave[:2], '\n'
    # 验证通过

    # 当月的，存在离职邮件关联的用户的JSR：Current_Month_Leave_JSR.csv
    # 当月的，考虑之前累积JSR：Accumulated_Months_JSR.csv
    Extract_Statistical_Feats(Insiders_2_Leave, 2, Dst_Dir)





    sys.exit()





