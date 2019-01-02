# coding:utf-8
# 通过PCA降维，降33维度的ATF特征处理为制定长度的X的新特征

# 这里的ATF
# 人格特征块（OCEAN+CPBs+JS）：8-->3
# 环境CPB块（Team_CPB + Leader_CPB）: 10-->3
# LCE特征块（14）：9-->3
# 出勤块：3-->1

# ATF特征字段
# user_id,
# （8）O_Score,C_Score,E_Score,A_Score,N_Score,CPB-I,CPB-O,JS_Score,
# （10）Team_CPB-I-mean,Team_CPB-O-mean,Users-less-mean-A,Users-less-mean-A and C,Users-less-mean-C,Users-High-mean-N,Team_CPB-I-median,Team_CPB-O-median,leader-CPB-I,leader-CPB-O,
# dis_ocean,avg_dis_ocean,dis_os,avg_dis_os,email_ratio,cnt_send/recv,cnt_s/r_size,cnt_s/r_attach,cnt_s/r_days,cnt_email_days,
# cnt_late_days,cnt_early_days,month_work_days,

import os,sys
import numpy as np
import sklearn.preprocessing as skp
import sklearn.decomposition as skd


def Extract_ATF_10D(atf_path):
    atf_10D = []
    cert_users = []
    personality_lst = []
    cpbs_lst = []
    lce_lst = []
    workday_lst = []
    f_atf = open(atf_path, 'r')
    f_atf_lst = f_atf.readlines()
    f_atf.close()
    for line in f_atf_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        if line_lst[0] == 'user_id':
            continue
        cert_users.append(line_lst[0])
        per_tmp = []
        print 'personality:', len(line_lst[1:9]), line_lst[1:9], '\n'
        for ele in line_lst[1:8]:
            per_tmp.append(float(ele))
        personality_lst.append(per_tmp)
        print 'cpbs is ', len(line_lst[9:19]), line_lst[9:19], '\n'
        cpbs_tmp = []
        for ele in line_lst[9:19]:
            cpbs_tmp.append(float(ele))
        cpbs_lst.append(cpbs_tmp)
        print 'lce is ', len(line_lst[19:33]), line_lst[19:33], '\n'
        lce_tmp = []
        for ele in line_lst[19:33]:
            lce_tmp.append(float(ele))
        lce_lst.append(lce_tmp)
        print 'workday is', len(line_lst[33:]), line_lst[33:], '\n'
        work_tmp = []
        for ele in line_lst[33:]:
            work_tmp.append(float(ele))
        workday_lst.append(work_tmp)
        # sys.exit()
    print '开始分组做PCA..\n'
    personality_pca = skd.PCA(n_components=3).fit_transform(personality_lst)
    cpbs_pca = skd.PCA(n_components=3).fit_transform(cpbs_lst)
    lce_pca = skd.PCA(n_components=3).fit_transform(lce_lst)
    work_pca = skd.PCA(n_components=1).fit_transform(workday_lst)

    print '重新拼接..\n'
    j = 0
    while j < len(cert_users):
        atf_pca_tmp = []
        atf_pca_tmp.extend(personality_pca[j])
        atf_pca_tmp.extend(cpbs_pca[j])
        atf_pca_tmp.extend(lce_pca[j])
        atf_pca_tmp.extend(work_pca[j])
        atf_10D.append(atf_pca_tmp)
        j += 1
    print 'users is ', len(cert_users), '\n'
    for i in range(5):
        print i, atf_10D[i], '\n'
    return cert_users, atf_10D


print '数据准备..\n'
Dst_Dir = sys.path[0] + '\\' + 'JS-Risks_Analyze-0.9'
# CERT5.2_LaidOff_ATF_0.1.csv
# Insides目录从2010-06到2011-04
for dir in os.listdir(Dst_Dir):
    month_dir = Dst_Dir + '\\' + dir
    if os.path.isdir(month_dir) == True:
        atf_path = month_dir + '\\' + 'CERT5.2_LaidOff_ATF_0.1.csv'
        if os.path.exists(atf_path) == True:
            CERT_Users, ATF_10D_lst = Extract_ATF_10D(atf_path)
            f_ATF_10D = open(month_dir + '\\' + 'CERT5.2_ATF_10D.csv', 'w')
            i = 0
            while i < len(CERT_Users):
                f_ATF_10D.write(CERT_Users[i] + ',')
                for ele in ATF_10D_lst[i]:
                    f_ATF_10D.write(str(ele) + ',')
                f_ATF_10D.write('\n')
                i += 1
            f_ATF_10D.close()
            print dir, 'ATF_10D分析提取完毕..\n'
        else:
            continue
    else:
        continue