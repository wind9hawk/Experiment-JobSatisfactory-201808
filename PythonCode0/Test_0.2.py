# coding:utf-8
# Test文件0.2版本

import os,sys
import numpy as np
import sklearn.preprocessing as skp
import sklearn.decomposition as skd
import sklearn.metrics as skm
import copy

# 实验1，分析CERT5.2中用户的邮件联系人与离职用户交叉匹配的结果
Flag_0 = True
if Flag_0 == True:
    Email_Dir_4 = r'G:\GitHub\Essay-Experiments\CERT5.2-Results\CERT5.2-Insiders_2-EmailRecords-0.4'
    Email_Dir_2 = r'G:\GitHub\Essay-Experiments\CERT5.2-Results\CERT5.2-Insiders_2-EmailRecords'

    # 指定要分析的目标用户
    Target_User = 'BYO1846'

    # 数据读入确定
    # 定义存放用户邮件数据的两个列表
    User_Emails_2 = []
    User_Emails_4 = []
    for file in os.listdir(Email_Dir_2):
        # BYO1846-feats.csv
        if 'feats' not in file:
            continue
        if Target_User not in file:
            continue
        else:
            f_0 = open(Email_Dir_2 + '\\' + file, 'r')
            User_Emails_2 = f_0.readlines()
            f_0.close()
            break

    for file in os.listdir(Email_Dir_4):
        # BYO1846-feats.csv
        if 'feats' not in file:
            continue
        if Target_User not in file:
            continue
        else:
            f_0 = open(Email_Dir_4 + '\\' + file, 'r')
            User_Emails_4 = f_0.readlines()
            f_0.close()
            break

    f_1 = open('CERT5.2-Leave-Relationship.csv', 'r')
    Users_Leave = f_1.readlines()
    f_1.close()

    # CERT5.2 Leave Company Relationships Users for all Users
    # MMK1532,No:
    # Insider_LaidOff_0,
    # Insider_LaidOff_1,WMH1300,JRC1963,BAR1328,RDP1751,DAS1320,HKK0881,CEW1960,ILG0879,DEO1964,SMS0432,VSB1317,
    # Insider_LaidOff_2,CBC1504,JSB0860,KDP1706,FKH0864,RKW1936,BMR0865,SCO1719,ZJN1492,SAF1942,CHP1711,NAO1281,REF1924,JDJ1949,YBH1926,SNK1280,IAJ1729,DCA0857,LKC0405,VAH1292,TMT0851,JIP1503,
    # Insider_LaidOff_3,JAT1218,ADL1898,KSW0708,LAS0256,GWO1660,MIB1265,TCP0380,CDO0684,CDG0770,CLL0306,QSG1150,QAP0266,OCW1127,PKS1187,GER0350,BSS0847,OCD1985,MPF0690,USM0703,RFP1918,FKS1696,CRD0272,AWW0718,EJO0236,ESP1198,MMR1458,JIB1258,ZIE0741,DTB0722,EPG1196,DMP0344,MDS0680,CNM0787,NBL1190,OSS1463,ALT1465,WHG1669,WFV0687,STH0353,RPJ1159,JKB0287,DNJ0740,ELM1123,DXF1662,SCI0778,ISW0738,AYG1697,LMW0837,ICB1890,NTG1667,PCK0271,DHR1157,ZVW1475,BRG0728,HPM0360,ACA1126,KJG1121,JOE1672,UKM0845,KVF1143,DCC1119,JDB1163,NEG0281,FZG0389,MGB1235,KHW0289,VRP0267,CAB1189,JAL0811,AMS1236,ALW0764,CQR1172,EGM1222,AMB0745,MBW1149,WHB1247,XBK0246,ZEH0685,JRB0759,JUP1472,WWW0701,HJO0779,DCV1185,KMO0382,CWW1120,HSN0675,DJH0253,
    # Insider_LaidOff_4,RMB1821,FAM0495,WSW1091,SDL0541,CTH1812,JBG1375,LRF0549,JHP1654,NWP1609,JDM0208,HSF1115,FDS1841,NTV1777,GMM1037,MAF0467,ZAD1621,XMG1579,HBH0111,KBC0818,TAG1610,EAL1813,WBP0828,NWH0960,BRM0126,MAR1075,GWH0961,JXH1061,HFF0560,MMB0556,UAM1108,KEW0198,BNS0484,LSM1382,GFM1815,CIM1095,VCF1602,CKP0630,JKM1790,PBC0077,PTV0067,KBC1390,ZHB1104,PTM1432,MGM0539,IHC0561,OJC0930,SIS0042,CIF1430,KLB0918,TRC1838,TNB1616,IVS1411,WDT1634,DHS0204,SLL0193,MTD0971,DDR1649,MFM1400,TTR1792,GWG0497,MCP0611,CTT0639,HMK0653,VVG0624,MIB0203,LLW0179,RAT0514,GKW0043,NAH1366,PLF1030,TPO1049,ICB1354,RRS0056,MJA1784,HMS1658,BYO1846,EJV0094,HIS1394,GCB0118,HXP0976,MZO1066,KRC1348,DPK0954,KJH0475,JJW1785,RBC1624,LVF1626,ITA0159,CKL0652,ZKP0542,LJM1807,KCM0466,KFS1029,PTH0005,CDB1594,NIV1608,LCB1869,WSK1857,IJM0603,ELT1370,SQC1072,TMC0934,GTN1021,FIM0605,ETW0002,KSS1005,LMM0167,MEW0485,GPO1020,OKM1092,XAM0376,HBW0057,MTP1582,ACB0220,JKB1843,SLC1865,VPA0974,ACE1431,LAH0463,
    # NTB0710,No:

    # 首先分析Email与Leave交叉匹配结果

    # 定位Leave数据中的用户
    User_Index = 0
    i = 0
    while i < len(Users_Leave):
        line_lst = Users_Leave[i].strip('\n').strip(',').split(',')
        if Target_User not in line_lst[0]:
            i += 1
            continue
        else:
            User_Index = i
            break
    # 提取目标用户周围的leave用户
    User_LaidOff = [[] for i in range(5)]
    if User_Index == 0:
        print 'Leave文件中没有目标用户...!\n\n'
        sys.exit()
    i = 1
    while i < 6:
        line_lst = Users_Leave[User_Index + i].strip('\n').strip(',').split(',')
        for usr in line_lst[1:]:
            User_LaidOff[i - 1].append(usr)
        i += 1

    Leave_Contacts_2 = [[] for i in range(5)]
    Leave_Contacts_4 = [[] for i in range(5)]

    # 匹配得到Leave Contacts列表
    for line in User_Emails_2:
        line_lst = line.strip('\n').strip(',').split(',')
        print line_lst, '\n'
        # Jayme_C_Cohen,-1.0,0.0,0.0,0.0,1.0,28383.0,0.0,
        # 过滤掉非组织员工
        if len(line_lst[0]) != 7:
            print '联系人非组织员工，跳过...\n'
            #print line_lst, '\n'
            #print line_lst[0], '\n\n'
            continue
        j = 0
        while j < 5:
            if line_lst[0] in User_LaidOff[j]:
                Leave_Contacts_2[j].append(line_lst[0])
                break
            else:
                j += 1

    for line in User_Emails_4:
        line_lst = line.strip('\n').strip(',').split(',')
        # Jayme_C_Cohen,-1.0,0.0,0.0,0.0,1.0,28383.0,0.0,
        # 过滤掉非组织员工
        if len(line_lst[0]) != 7:
            print '联系人非组织员工，跳过...\n\n'
            continue
        j = 0
        while j < 5:
            if line_lst[0] in User_LaidOff[j]:
                Leave_Contacts_4[j].append(line_lst[0])
                break
            else:
                j += 1

    print Target_User, 'Leave Contacts 匹配结果。。。', 'V2', '\n\n'
    j = 0
    while j < 5:
        print j, len(Leave_Contacts_2[j]), '\n'
        for ele in Leave_Contacts_2[j]:
            print ele
        j += 1

    print Target_User, 'Leave Contacts 匹配结果。。。', 'V4', '\n\n'
    j = 0
    while j < 5:
        print j, len(Leave_Contacts_4[j]), '\n'
        for ele in Leave_Contacts_4[j]:
            print ele
        j += 1

    #print User_Emails_2, '\n'
    #print User_Emails_4, '\n'
    #print Users_Leave, '\n'
    print User_LaidOff, '\n'

    print Target_User, 'Leave Contacts 交叉匹配完成...\n\n'
    sys.exit()

