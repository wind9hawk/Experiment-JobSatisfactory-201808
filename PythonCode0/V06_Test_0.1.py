# coding:utf-8

# 本测试模块用户实验系列6的分析研究

import os, sys
import numpy as np
import sklearn.preprocessing as skp
import sklearn.decomposition as skd
import sklearn.metrics as skm
import shutil

# 实验一：
# 研究CERT5.2中跳槽内部用户周围离职用户的时间关系
# 分析源来自离职用户数据以及用户关系的离职数据
# 生成结果应当是：
# user_id, leave time,
# relation_0, user_1, leave_1, user_2, leave_2...\n
# relation_4, ...

# 首先读入场景二的攻击者列表
Insiders_2_Dir = os.path.dirname(sys.path[0]) + '\\' + 'r5.2-2'
Insiders_2_lst = []
for file in os.listdir(Insiders_2_Dir):
    Insiders_2_lst.append(file[7:-4])

# 定义一个函数，给定用户ID与离职信息表，返回其离职时间
def Search_LeaveTime(user_id, f_leave_lst):
    Flag_Exist = 'No'
    for line in f_leave_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        if line_lst[0] != user_id:
            continue
        else:
            return line_lst[1]
    return Flag_Exist

Flag_0 = True # 实验开关
if Flag_0:
    print '....<<<<实验一：离职用户的时间线分析>>>>....\n\n'
    print '..<<读入数据源>>..\n\n'
    # 离职用户数据（有哪些离职用户）
    f_leave = open('CERT5.2-Leave-Users.csv', 'r')
    # 该文件数据样例：
    # Laid off Users in CERT5.2 from 2009-12 to 2011-05
    # RMB1821,2010-02,Rose Maisie Blackwell,RMB1821,Rose.Maisie.Blackwell@dtaa.com,Salesman,,1 - Executive,5 - SalesAndMarketing,2 - Sales,5 - RegionalSales,Donna Erin Black
    f_leave_lst = f_leave.readlines()
    f_leave.close()

    # 读入离职关系数据，即目标用户多层次OS中离职用户列表
    f_lr = open('CERT5.2-Leave-Relationship.csv', 'r')
    f_lr_lst = f_lr.readlines()
    f_lr.close()

    # 数据分析步骤
    # 1. 从攻击者用户列表中顺序选择一个攻击者Insiders；
    # 2. 首先查阅f_leave_lst得到其离职时间；（判断是否离职）
    # 3. 查阅该用户的lr关系，顺序读取五个层次列表，并依次查阅列表中用户的离职时间
    # 最终输出的结果形式为：
    # [user_id, leave time]
    # [leave 0 cluster: user_1, leave_1, user-2， leave_2...]
    # 然后写入文件：
    # 先写如目标用户与离职时间
    # 然后是分行写入用户与离职时间

    f_lr = open('CERT5.2_Insiders_Leave_TimeRelation.csv', 'w')
    # 存储最终的用户与离职时间特征
    # 总共目标用户+五个层次=6个列表
    Users_Leave_TR = []

    # 先将目标用户写入
    for usr in Insiders_2_lst[:]:
        user_leave_tr = [[] for i in range(6)]
        for line in f_leave_lst:
            line_lst = line.strip('\n').strip(',').split(',')
            if line_lst[0] == usr:
                user_leave_tr[0].append(usr)
                user_leave_tr[0].append(line_lst[1])
                print line_lst[1], '\n'
                # sys.exit()
                print usr, '自身离职时间确定...\n\n'
            else:
                continue

        i = 0
        while i < len(f_lr_lst):
            line_lst = f_lr_lst[i].strip('\n').strip(',').split(',')
            # print 'line_lst is ', line_lst, '\n'
            # Leave Relation文件数据样例
            # CERT5.2 Leave Company Relationships Users for all Users
            # MMK1532,No:
            # Insider_LaidOff_0,
            # Insider_LaidOff_1,WMH1300,JRC1963,BAR1328,RDP1751,DAS1320,HKK0881,CEW1960,ILG0879,DEO1964,SMS0432,VSB1317,
            # Insider_LaidOff_2,CBC1504,JSB0860,KDP1706,FKH0864,RKW1936,BMR0865,SCO1719,ZJN1492,SAF1942,CHP1711,NAO1281,REF1924,JDJ1949,YBH1926,SNK1280,IAJ1729,DCA0857,LKC0405,VAH1292,TMT0851,JIP1503,
            # Insider_LaidOff_3,JAT1218,ADL1898,KSW0708,LAS0256,GWO1660,MIB1265,TCP0380,CDO0684,CDG0770,CLL0306,QSG1150,QAP0266,OCW1127,PKS1187,GER0350,BSS0847,OCD1985,MPF0690,USM0703,RFP1918,FKS1696,CRD0272,AWW0718,EJO0236,ESP1198,MMR1458,JIB1258,ZIE0741,DTB0722,EPG1196,DMP0344,MDS0680,CNM0787,NBL1190,OSS1463,ALT1465,WHG1669,WFV0687,STH0353,RPJ1159,JKB0287,DNJ0740,ELM1123,DXF1662,SCI0778,ISW0738,AYG1697,LMW0837,ICB1890,NTG1667,PCK0271,DHR1157,ZVW1475,BRG0728,HPM0360,ACA1126,KJG1121,JOE1672,UKM0845,KVF1143,DCC1119,JDB1163,NEG0281,FZG0389,MGB1235,KHW0289,VRP0267,CAB1189,JAL0811,AMS1236,ALW0764,CQR1172,EGM1222,AMB0745,MBW1149,WHB1247,XBK0246,ZEH0685,JRB0759,JUP1472,WWW0701,HJO0779,DCV1185,KMO0382,CWW1120,HSN0675,DJH0253,
            # Insider_LaidOff_4,RMB1821,FAM0495,WSW1091,SDL0541,CTH1812,JBG1375,LRF0549,JHP1654,NWP1609,JDM0208,HSF1115,FDS1841,NTV1777,GMM1037,MAF0467,ZAD1621,XMG1579,HBH0111,KBC0818,TAG1610,EAL1813,WBP0828,NWH0960,BRM0126,MAR1075,GWH0961,JXH1061,HFF0560,MMB0556,UAM1108,KEW0198,BNS0484,LSM1382,GFM1815,CIM1095,VCF1602,CKP0630,JKM1790,PBC0077,PTV0067,KBC1390,ZHB1104,PTM1432,MGM0539,IHC0561,OJC0930,SIS0042,CIF1430,KLB0918,TRC1838,TNB1616,IVS1411,WDT1634,DHS0204,SLL0193,MTD0971,DDR1649,MFM1400,TTR1792,GWG0497,MCP0611,CTT0639,HMK0653,VVG0624,MIB0203,LLW0179,RAT0514,GKW0043,NAH1366,PLF1030,TPO1049,ICB1354,RRS0056,MJA1784,HMS1658,BYO1846,EJV0094,HIS1394,GCB0118,HXP0976,MZO1066,KRC1348,DPK0954,KJH0475,JJW1785,RBC1624,LVF1626,ITA0159,CKL0652,ZKP0542,LJM1807,KCM0466,KFS1029,PTH0005,CDB1594,NIV1608,LCB1869,WSK1857,IJM0603,ELT1370,SQC1072,TMC0934,GTN1021,FIM0605,ETW0002,KSS1005,LMM0167,MEW0485,GPO1020,OKM1092,XAM0376,HBW0057,MTP1582,ACB0220,JKB1843,SLC1865,VPA0974,ACE1431,LAH0463,
            # NTB0710,No:
            if len(line_lst) < 2:
                i += 1
                continue
            if usr == line_lst[0]:
                j = 1
                while j < 6:
                    for lusr in f_lr_lst[i + j].strip('\n').strip(',').split(','):
                        if 'LaidOff' in lusr:
                            continue
                        lusr_ltime = Search_LeaveTime(lusr, f_leave_lst)
                        user_leave_tr[j].append(lusr)
                        user_leave_tr[j].append(lusr_ltime)
                    j += 1
                break
            else:
                i += 1
                continue

            # 输出一下得到的新离职时间列表
        for i in range(len(user_leave_tr)):
            print i, user_leave_tr[i], '\n'
        Users_Leave_TR.append(user_leave_tr)

    # 将所有用户的离职时间线写入文件
    for usr in Users_Leave_TR:
        print 'User is ', usr, '\n'
        f_lr.write('User:')
        f_lr.write(',')
        # 每个Usr都是一个6维度的符合列表
        for line in usr:
            print 'line is ', line, '\n'
            f_lr.write('line:')
            f_lr.write(',')
            for ele in line:
                f_lr.write(ele)
                f_lr.write(',')
            f_lr.write('\n')
    f_lr.close()
    print '文件写入完毕...\n\n'

    sys.exit()

