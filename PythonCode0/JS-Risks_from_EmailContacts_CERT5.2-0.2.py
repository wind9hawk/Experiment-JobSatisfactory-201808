# coding:utf-8
# 本模块脚本主要功能是定量计算用户邮件联系的亲密度（RelationLevel, RL），然后与目标用户周围的离职列表对比，计算出其相应的JS_Risks
# 鉴于已经有0.1版本作为基础，0.2版本只修改计算所有用户RelationLevel以及最终JS_Risks的部分即可



import numpy as np
import KMeans_Module
from sklearn.cluster import KMeans
import os,sys
import shutil
from sklearn.preprocessing import MinMaxScaler
import math
# b_lst = a_lst (浅复制，同一个内存对象)
# c_lst = copy.copy(a_lst)  (深复制，不同的内存对象，相互独立)
import copy # 列表深复制

# 定义一个群簇中心点的定性指标计算函数
def Cal_RelationLevel(sr, s1, s2, s3, r1, r2, r3):
    # RL = math.log10(1 + (1 - abs(sr)) * (s1 * s2 + r1 * r2) * (s1 * s3 + r1 * r3))
    # 为了打开单纯发送与接收的开关，尝试将对数变量的乘法因素变为加法（或者修正EM为 [2 - abs(sr)]）
    # RL = math.log10(1 + (1 - abs(sr)) + (s1 * s2 + r1 * r2) + (s1 * s3 + r1 * r3))
    # sr = float((s1 - r1) / (s1 + r1))
    # RL = math.log(1 + (1 - abs(sr)) + (s1 * s2 + r1 * r2) + (s1 * s3 + r1 * r3), math.e)
    RL = math.log(1 + math.pow(math.exp(abs(0.5 - sr)), -1) + (s1 * s2 + r1 * r2) + (s1 * s3 + r1 * r3), math.e)
    return RL

print '....<<<<CERT5.2用户邮件联系特征数据定位准备开始>>>>....\n\n'
# 首先需要指定几个文件夹目录
# 存放邮件统计7元组特征的文件目录：
# 2000个普通用户的邮件统计7元组特征文件目录：
CERT52_Users_EmailFeats_Dir = r'G:\GitHub\Essay-Experiments\CERT5.2-Results\CERT5.2-Users-EmailRecords'
# 由于邮件feats文件名称类似[BYO1846-feats.csv]，因此，需要在上述目录下过滤掉邮件记录
# 将上述所有要分析的用户的邮件联系人七元组特征拷贝到程序目录下
EmailFeats_Dir = sys.path[0] + '\\' + r'CERT5.2_EmailContactFeats-0.2'
if os.path.exists(EmailFeats_Dir) == False:
    os.makedirs(EmailFeats_Dir)
# 之后所有的数据分析就在[CERT5.2_EmailContactFeats-1030]目录下进行即可
print '....<<<<CERT5.2用户邮件联系特征数据定位完毕>>>>....\n\n'



print '....<<<<将Insiders与Users的邮件通讯特征文件导入到既定的CERT5.2_EmailContactFeats目录下>>>>....\n\n'
print '..<<导入CERT5.2全部用户Users邮件通讯特征文件>>..\n\n'
for file in os.listdir(CERT52_Users_EmailFeats_Dir):
    if 'feat' not in file:
        continue
    else:
        # 这是需要的用户邮件通讯特征文件
        # 利用shutil库的copy命令实现文件的复制
        shutil.copy(CERT52_Users_EmailFeats_Dir + '\\' + file, EmailFeats_Dir)
        print 'Users: ', file, '复制到目标目录，完毕...\n'
print '....<<<<将Insiders与Users的邮件通讯特征文件导入到既定的CERT5.2_EmailContactFeats目录下，完毕>>>>....\n\n'



print '....<<<<开始就每个用户的邮件通讯特征依次进行计算每个用户的RelationLevle，并最终交叉匹配计算JS_Risk计算>>>>....\n\n'
# 邮件联系特征数据样例
# BYO1846-feats.csv
# Macy_Patterson,0.472222222222,17.0,362672.941176,0.411764705882,36.0,104119.388889,0.138888888889,
# Carol_Copeland,-1.0,5.0,285675.2,0.2,0.0,0.0,0.0,
# WAS1823,1.0,47.0,157937.87234,0.148936170213,47.0,118080.361702,0.170212765957,
# 定义一个存放所有用户ID顺序的列表
CERT52_Users = []
# 打开离职人员关系文件
#f_laidoff = open(r'CERT5.2-LaidOff_Relationship.csv', 'r')
f_laidoff = open(r'CERT5.2-Leave-Relationship.csv', 'r')
f_lo_lst = f_laidoff.readlines()
f_laidoff.close()
# 初始化最终的用户JS_Risk列表
JS_Risk = []
# 初始化建立一个用于记录所有用户JS_Risk数据的文件CERT5.2_JS_Risks.csv
f_JS_Risks = open('CERT5.2_JS-Risks-Leave-0.2.csv', 'w')
f_JS_Risks.write('JS_Risks for CERT5.2\n')
for file in os.listdir(EmailFeats_Dir)[:]:
    if 'feats' not in file:
        continue
    # 用于分析指定用户的过滤
    #if 'SIS0042' not in file:
    #   continue
    CERT52_Users.append(file[0:7])
    # 读取该文件，并提取出单独的通讯用户列表以及通讯特征
    print '..<<提取', file[0:7], ' 的邮件通讯列表及其通讯特征>>..\n\n'
    # 存储该用户的邮件通讯用户顺序
    user_contacts = []
    # 存储该用户的数组化邮件通讯特征列表
    user_contacts_feats = []
    f_0 = open(EmailFeats_Dir + '\\' + file, 'r')
    f_0_lst = f_0.readlines()
    f_0.close()
    for line in f_0_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        if len(line_lst) < 2:
            continue
        # 如果邮件名不是企业规范名称，不分析，跳过
        if len(line_lst[0]) != 7:
            continue
        user_contacts.append(line_lst[0])
        tmp_0 = []
        for ele in line_lst[1:]:
            tmp_0.append(float(ele))
        user_contacts_feats.append(tmp_0)
    user_contacts_feats = MinMaxScaler().fit_transform(user_contacts_feats)
    print '..<<', file[0:7], '邮件通讯特征读取完毕>>..\n\n'



    # 提取得到了目标用户的邮件通讯列表user_contacts以及对应的通讯7元组特征user_contacts_feats
    # 开始计算该用户的所有通讯用户的RelationLevel，保存在user_rl_lst中
    print '..<<开始计算', file[:7], ' 所有邮件通讯用户的RelationLevel>>..\n\n'
    # 初始化该用户的RL列表，依次存放到user_rl_lst中，并写入到对应的文件中保存
    user_rl_lst = []
    f_user_rl = open(EmailFeats_Dir + '\\' + file[:7] + '_Email_RelationLevel.csv', 'w')
    for feat in user_contacts_feats:
        rl = Cal_RelationLevel(feat[0], feat[1], feat[2], feat[3], feat[4], feat[5], feat[6])
        user_rl_lst.append(rl)
    print file[:7], 'RelationLevel计算完毕...\n\n'
    # 开始写入到文件中保存起来
    k = 0
    while k < len(user_rl_lst):
        f_user_rl.write(user_contacts[k])
        f_user_rl.write(',')
        f_user_rl.write(str(user_rl_lst[k]))
        f_user_rl.write('\n')
        k += 1
    f_user_rl.close()
    print file[:7], ' RelationshipLevel文件写作完毕...\n\n'
    print '..<<开始计算', file[:7], ' 所有邮件通讯用户的RelationLevle计算完毕>>..\n\n'



    print '..<<开始计算',file[:7], ' JS_Risk>>..\n\n'
    # 开始结合离职人员数据计算该用户的JS_Risk
    # 离职人员数据格式：CERT5.2-LaidOff_Relationship.csv
    # MTD0971,2010-10:
    # Insider_LaidOff_0,NWH0960,GWH0961,
    # Insider_LaidOff_1,FAM0495,BNS0484,GWG0497,
    # Insider_LaidOff_2,SDL0541,LRF0549,NTV1777,HBH0111,BRM0126,HFF0560,MMB0556,PTV0067,MGM0539,OJC0930,
    # Insider_LaidOff_3,RMB1821,WSW1091,CTH1812,JBG1375,JHP1654,NWP1609,JDM0208,HSF1115,FDS1841,GMM1037,MAF0467,ZAD1621,XMG1579,KBC0818,TAG1610,EAL1813,WBP0828,MAR1075,JXH1061,UAM1108,LSM1382,CIM1095,CKP0630,JKM1790,ZHB1104,PTM1432,CIF1430,KLB0918,TNB1616,IVS1411,DHS0204,DDR1649,MFM1400,TTR1792,
    # Insider_LaidOff_4,JAT1218,ADL1898,KSW0708,WMH1300,LAS0256,GWO1660,MIB1265,TCP0380,CBC1504,JSB0860,CDO0684,KDP1706,CDG0770,FKH0864,CLL0306,JRC1963,QSG1150,QAP0266,BAR1328,OCW1127,PKS1187,GER0350,BSS0847,OCD1985,USM0703,RKW1936,RFP1918,RDP1751,FKS1696,BMR0865,AWW0718,EJO0236,HKK0881,ESP1198,MMR1458,JIB1258,SCO1719,ZJN1492,ZIE0741,DTB0722,CEW1960,ILG0879,DMP0344,DEO1964,CNM0787,NBL1190,ALT1465,WHG1669,SMS0432,WFV0687,STH0353,RPJ1159,JKB0287,ELM1123,
    # NHB1529,No:
    #　直接分析本目录下的离职人员数据，从中找到对应用户的信息
    # 初始化一个tmp_1变量以免if语句落空报错
    tmp_1 = ['NoMathc', 'NoMatch']
    # 定义一个文件用来保存目标用户离职与邮件通讯匹配的用户列表，按照层级保存
    f_1 = open(EmailFeats_Dir + '\\' + file[:7] + 'Leave_Contacts.csv', 'w')
    leave_contacts_lst = [[] for i in range(5)]
    j = 0
    while j < len(f_lo_lst):
        line_lst = f_lo_lst[j].strip('\n').strip(',').split(',')
        # 首先需要定位目标用户的离职人员关系数据位置
        if file[:7] not in line_lst[0]:
            j += 1
            continue
        else:
            # 此时第j行正好时目标用户
            JS_Risk_LaidOff_Friends = [[0.0] for i in range(5)]
            # N个关系层级，1/N为级差，这里N为5，故而选择0.2
            Weight_Level = [[float((5 - i)/5.0)] for i in range(5)]
            # q表示五个组织层次，p表示每个层次中的用户坐标
            q = 0
            while q < 5:
                # 分别分析每个层级中离职的friends个数
                p = 1
                while p < len((f_lo_lst[j + q + 1]).strip('\n').strip(',').split(',')):
                    f_lo_line = f_lo_lst[j + q + 1].strip('\n').strip(',').split(',')
                    if f_lo_line[p] in user_contacts:
                        JS_Risk_LaidOff_Friends[q][0] += user_rl_lst[user_contacts.index(f_lo_line[p])]
                        tmp_2 = []
                        tmp_2.append(f_lo_line[p])
                        tmp_2.append(user_contacts_feats[user_contacts.index(f_lo_line[p])])
                        tmp_2.append(user_rl_lst[user_contacts.index(f_lo_line[p])])
                        leave_contacts_lst[q].append(tmp_2)
                        p += 1
                        continue
                    else:
                        p += 1
                        continue
                q += 1
                continue
            js_risk = 0.0
            n = 0
            while n < 5:
                print n, ':', JS_Risk_LaidOff_Friends[n][0], ' * ', Weight_Level[n][0], '\n'
                js_risk += JS_Risk_LaidOff_Friends[n][0] * Weight_Level[n][0]
                print n, ' js_risk is ', js_risk, '\n'
                n += 1
            tmp_1 = []
            tmp_1.append(file[0:7])
            tmp_1.append(js_risk)
            JS_Risk.append(tmp_1)
            print '\n....<<<<',file[0:7], 'JS_Risk is ', js_risk, '>>>>.....\n\n'
            break
    f_JS_Risks.write(tmp_1[0])
    f_JS_Risks.write(',')
    f_JS_Risks.write(str(tmp_1[1]))
    f_JS_Risks.write('\n')

    print '将用户Leave与Email Contacts匹配结果写入到文件中...\n\n'
    f_1.write(file[:7])
    f_1.write('\n')
    m = 0
    while m < 5:
        #f_1.write(file[:7])
        #f_1.write('\n')
        f_1.write('Cluster' + str(m) + '\n')
        for usr in leave_contacts_lst[m]:
            f_1.write(usr[0])
            f_1.write(',')
            print usr, '\n'
            print usr[1], '\n'
            for ele in usr[1]:
                f_1.write(str(ele))
                f_1.write(',')
            f_1.write(str(usr[2]))
            f_1.write('\n')
        m += 1
    f_1.close()
    print '用户Leave与Email Contacts匹配结果写入完成....\n\n'




print '....<<<<将Insiders与Users的邮件通讯特征文件导入到既定的CERT5.2_EmailContactFeats目录下，完毕>>>>....\n\n'




sys.exit()
