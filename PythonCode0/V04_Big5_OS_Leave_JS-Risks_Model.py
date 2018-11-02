# coding:utf-8
# 本模块在初步实验分析后，判定单纯使用邮件特征不足以确定用户可用的relationship，因此我们
# 转变思路，构造可以表征用户人格与OS结构的特征，进行聚类

import os,sys
import numpy as np
import sklearn.preprocessing as skp
import sklearn.decomposition as skd
import shutil
import copy
import sklearn.metrics as skm

print '......<<<<<<针对CERT5.2用户： 基于Big-5人格特征、OS结构特征以及离职用户特征的JS建模>>>>>>......\n\n'


print '..<<初始化定义函数>>..\n\n'
# 定义一个获取用户LDAP中五个层次总人数的函数
def Cal_LDAP_Counts(user_id, f_ldap_lst):
    # 参数user_id，请过滤掉CEO，其长度小于10
    # 参数f_ldap_lst表示文件readlines()读入的原始数据（2009-12.csv）
    # 由于处理的数据格式提取太麻烦，索性直接重新计算
    # 定义OS结构中的四个层次人员列表：事业部、职能部、部门、团队
    OS_Members = [[] for i in range(5)]
    # 上述五个列表分别是：
    # 0： 同一个团队的成员
    # 1： 同一个部门的不同团队成员
    # 2： 同一个职能部的不同部门的成员
    # 3： 同一个事业部的不同职能部门的成员
    # 4： 不同事业部的成员
    # 提取待分析用户的LDAP信息
    # LDAP数据格式：
    # employee_name,user_id,email,role,projects,business_unit,functional_unit,department,team,supervisor
    for line in f_ldap_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        if line_lst[1] != user_id:
            continue
        else:
            if len(line_lst) < 10:
                # 可能是CEO
                # Anjolie Evangeline Houston,AEH0001,Anjolie.Evangeline.Houston@dtaa.com,ChiefExecutiveOfficer,,,,,,
                return [0,0,0,0,0]
            else:
                # 正常用户
                OS_Src = line_lst[5:9]
                for line in f_ldap_lst:
                    line_lst_0 = line.strip('\n').strip(',').split(',')
                    if len(line_lst_0) < 10:
                        continue
                    OS_Dst = line_lst_0[5:9]
                    if OS_Src == OS_Dst:
                        # 说明在同一个团队
                        OS_Members[0].append(line_lst_0[1])
                        continue
                    else:
                        if OS_Src[:3] == OS_Dst[:3]:
                            # 在同一个部门里
                            OS_Members[1].append(line_lst_0[1])
                            continue
                        else:
                            if OS_Src[:2] == OS_Dst[:2]:
                                # 在同一个职能部里
                                OS_Members[2].append(line_lst_0[1])
                                continue
                            else:
                                if OS_Src[:1] == OS_Dst[:1]:
                                    OS_Members[3].append(line_lst_0[1])
                                    continue
                                else:
                                    OS_Members[4].append(line_lst_0[1])
                                    continue
    return OS_Members

# 定义一个功能函数，由用户LDAP长度与离职用户数据计算其周围的离职比例
def Cal_Leave_Ratio(Leave_lst, LDAP_Length_lst):
    # 参数Leave_lst为所有用户的LDAP的层次化长度，为readlines()格式
    # 参数LDAP_Length_lst为所有用户的离职层次化列表（每个用户为五个小列表的组合）
    for i in range(len(Leave_lst)):
        print i, Leave_lst[i], '\n'
    CERT52_Leave_Ratios = []
    for line in LDAP_Length_lst:
        # line[0]表示用户ID
        # CERT5.2 Leave Company Relationships Users for all Users
        # MMK1532,No:
        # Insider_LaidOff_0,
        # Insider_LaidOff_1,WMH1300,JRC1963,BAR1328,RDP1751,DAS1320,HKK0881,CEW1960,ILG0879,DEO1964,SMS0432,VSB1317,
        # Insider_LaidOff_2,CBC1504,JSB0860,KDP1706,FKH0864,RKW1936,BMR0865,SCO1719,ZJN1492,SAF1942,CHP1711,NAO1281,REF1924,JDJ1949,YBH1926,SNK1280,IAJ1729,DCA0857,LKC0405,VAH1292,TMT0851,JIP1503,
        # Insider_LaidOff_3,JAT1218,ADL1898,KSW0708,LAS0256,GWO1660,MIB1265,TCP0380,CDO0684,CDG0770,CLL0306,QSG1150,QAP0266,OCW1127,PKS1187,GER0350,BSS0847,OCD1985,MPF0690,USM0703,RFP1918,FKS1696,CRD0272,AWW0718,EJO0236,ESP1198,MMR1458,JIB1258,ZIE0741,DTB0722,EPG1196,DMP0344,MDS0680,CNM0787,NBL1190,OSS1463,ALT1465,WHG1669,WFV0687,STH0353,RPJ1159,JKB0287,DNJ0740,ELM1123,DXF1662,SCI0778,ISW0738,AYG1697,LMW0837,ICB1890,NTG1667,PCK0271,DHR1157,ZVW1475,BRG0728,HPM0360,ACA1126,KJG1121,JOE1672,UKM0845,KVF1143,DCC1119,JDB1163,NEG0281,FZG0389,MGB1235,KHW0289,VRP0267,CAB1189,JAL0811,AMS1236,ALW0764,CQR1172,EGM1222,AMB0745,MBW1149,WHB1247,XBK0246,ZEH0685,JRB0759,JUP1472,WWW0701,HJO0779,DCV1185,KMO0382,CWW1120,HSN0675,DJH0253,
        # Insider_LaidOff_4,RMB1821,FAM0495,WSW1091,SDL0541,CTH1812,JBG1375,LRF0549,JHP1654,NWP1609,JDM0208,HSF1115,FDS1841,NTV1777,GMM1037,MAF0467,ZAD1621,XMG1579,HBH0111,KBC0818,TAG1610,EAL1813,WBP0828,NWH0960,BRM0126,MAR1075,GWH0961,JXH1061,HFF0560,MMB0556,UAM1108,KEW0198,BNS0484,LSM1382,GFM1815,CIM1095,VCF1602,CKP0630,JKM1790,PBC0077,PTV0067,KBC1390,ZHB1104,PTM1432,MGM0539,IHC0561,OJC0930,SIS0042,CIF1430,KLB0918,TRC1838,TNB1616,IVS1411,WDT1634,DHS0204,SLL0193,MTD0971,DDR1649,MFM1400,TTR1792,GWG0497,MCP0611,CTT0639,HMK0653,VVG0624,MIB0203,LLW0179,RAT0514,GKW0043,NAH1366,PLF1030,TPO1049,ICB1354,RRS0056,MJA1784,HMS1658,BYO1846,EJV0094,HIS1394,GCB0118,HXP0976,MZO1066,KRC1348,DPK0954,KJH0475,JJW1785,RBC1624,LVF1626,ITA0159,CKL0652,ZKP0542,LJM1807,KCM0466,KFS1029,PTH0005,CDB1594,NIV1608,LCB1869,WSK1857,IJM0603,ELT1370,SQC1072,TMC0934,GTN1021,FIM0605,ETW0002,KSS1005,LMM0167,MEW0485,GPO1020,OKM1092,XAM0376,HBW0057,MTP1582,ACB0220,JKB1843,SLC1865,VPA0974,ACE1431,LAH0463,
        Target_User = line[0]
        i = 0
        while i < len(Leave_lst):
            line_0 = Leave_lst[i].strip('\n').strip(',').split(',')
            if line_0[0] != Target_User:
                i += 1
                continue
            else:
                Leave_Members = [[] for j in range(5)]
                k = 1
                while k < 6:
                    line_1 = Leave_lst[i + k].strip('\n').strip(',').split(',')
                    # print 'line_1:', line_1, '\n'
                    if len(line_1) < 2:
                        # 该层次离职成员为空
                        k += 1
                        continue
                    for ele in line_1[1:]:
                        Leave_Members[k - 1].append(ele)
                    k += 1
                break
        tmp_1 = []
        for i in range(5):
            if line[i + 1] > 0:
                tmp_1.append(float(len(Leave_Members[i])) / line[i + 1] )
            else:
                tmp_1.append(float(len(Leave_Members[i])) / 1.0)
        CERT52_Leave_Ratios.append(tmp_1)
        print Target_User, '离职比例计算完毕...\n'
        print tmp_1, '\n'
    return CERT52_Leave_Ratios


print '....<<<<主体函数开始>>>>....\n\n'


print '....<<<<提取目标用户的LDAP团队成员信息（长度），输出文件并保存>>>>....\n\n'
# 指定数据源
LDAP_Dir = os.path.dirname(sys.path[0]) + '\\' + 'LDAP' + '\\' +'2009-12.csv'
f_LDAP = open(LDAP_Dir, 'r')
f_LDAP_lst = f_LDAP.readlines()
f_LDAP.close()

# 定义CERT5.2全体用户列表
CERT52_Users = []
# 调用函数生成长度特征文件
for line in f_LDAP_lst:
    line_lst = line.strip('\n').strip(',').split(',')
    if len(line_lst) < 10:
        continue
    if line_lst[1] == 'user_id':
        continue
    CERT52_Users.append(line_lst[1])

# 定义一个保存用户OS长度特征的文件
f_OS_Len = open('0.4_CERT5.2_LDAP_Length.csv', 'w')
CERT52_Users_LDAP_Length = []
Count_0 = 0
for usr in CERT52_Users:
    os_len = Cal_LDAP_Counts(usr, f_LDAP_lst)
    tmp_0 = []
    for lst in os_len:
        tmp_0.append(len(lst))
    f_OS_Len.write(usr)
    f_OS_Len.write(',')
    for ele in tmp_0:
        f_OS_Len.write(str(ele))
        f_OS_Len.write(',')
    f_OS_Len.write('\n')
    tmp_0.insert(0,usr)
    CERT52_Users_LDAP_Length.append(tmp_0)
    print Count_0, '..<<', usr, 'OS 长度写入完毕>>...\n\n'
    Count_0 += 1
print '....<<<<CERT5.2用户的LDAP长度信息写入完毕>>>>....\n\n'


print '....<<<<结合离职人员数据计算离职比例>>>>....\n\n'
# 指定离职用户数据源
f_Leave = open('CERT5.2-Leave-Relationship.csv', 'r')
f_Leave_lst = f_Leave.readlines()
f_Leave.close()

CERT52_Leave_Ratios = Cal_Leave_Ratio(f_Leave_lst, CERT52_Users_LDAP_Length)
# 创建保存结果的文件
f_Leave_Ratio = open('0.4_CERT52_Leave_Ratios.csv', 'w')
f_Leave_Ratio_scale = open('0.4_CERT52_Leave_Ratios_scale.csv', 'w')

CERT52_Leave_Ratios_array = np.array(CERT52_Leave_Ratios)
CERT52_Leave_Ratios_scale = skp.scale(CERT52_Leave_Ratios_array)

j = 0
while j < len(CERT52_Users_LDAP_Length):
    f_Leave_Ratio.write(CERT52_Users_LDAP_Length[j][0])
    f_Leave_Ratio.write(',')
    f_Leave_Ratio_scale.write(CERT52_Users_LDAP_Length[j][0])
    f_Leave_Ratio_scale.write(',')
    for ele in CERT52_Leave_Ratios[j]:
        f_Leave_Ratio.write(str(ele))
        f_Leave_Ratio.write(',')
    f_Leave_Ratio.write('\n')
    for ele in CERT52_Leave_Ratios_scale[j]:
        f_Leave_Ratio_scale.write(str(ele))
        f_Leave_Ratio_scale.write(',')
    f_Leave_Ratio_scale.write('\n')
    print '..<<',j, '\t', CERT52_Users_LDAP_Length[j][0],'离职比例计算完毕>>..\n'
    print CERT52_Users_LDAP_Length[j], '\n'
    print CERT52_Leave_Ratios, '\n'
    print CERT52_Leave_Ratios_scale, '\n'
    j += 1
f_Leave_Ratio.close()
f_Leave_Ratio_scale.close()



