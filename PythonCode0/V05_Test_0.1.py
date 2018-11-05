# coding:utf-8

# V0.5实验的配对测试脚本

import numpy as np
import os,sys


# 测试1
# 查看关系特征聚类后得到的群簇中，离职用户的个数以及比例；
f_Leave_relations = open(sys.path[0] + '\\' + 'CERT5.2-Leave-Relationship.csv', 'r')
f_leave_lst = f_Leave_relations.readlines()
f_Leave_relations.close()
Relation_Feats_Dir = 'G:\GitHub\Essay-Experiments\Experiment-JobSatisfactory-201808\PythonCode0\CERT5.2_Big5_OS_Relationship_v0.5'
Insiders_2_Dir = os.path.dirname(sys.path[0]) + '\\' + 'r5.2-2'
Insiders_2_lst = []
for file in os.listdir(Insiders_2_Dir):
    Insiders_2_lst.append(file[7:-4])



Flag_0 = True

Insiders_2_Clusters = [[] for i in range(len(Insiders_2_lst))]
Insiders_2_Leave_Users = []
if Flag_0:
    for usr in Insiders_2_lst[:]:
        for file in os.listdir(Relation_Feats_Dir):
            if usr in file and 'Cluster' in file:
                # 定位到了该用户的群簇文件
                f_0 = open(Relation_Feats_Dir + '\\' + file, 'r')
                f_0_lst = f_0.readlines()
                f_0.close()
                tmp_0 = []
                for line in f_0_lst:
                    line_lst = line.strip('\n').strip(',').split(',')
                    # Cluster文件数据样例
                    # Cluster_0
                    # TAG1610,ASB0658,CAH0595,HSG1585,DWR1387,BCB1715,UTM0493,WBK1077,KGL0178,EBG1553,PAG0429,RFC1991,MME1034,MHP1377,RAS0197,JJH0862,GUT1619,CAP0471,AAW0952,WCO0020,AAC1489,AIH0814,KRC1348,MGS1944,ACB0220,ACW0078,BKL0545,AFW1639,GNG1026,ROA0482,PAM0867,NRH0510,LCB1869,HGG0535,VMD0850,HBR1528,AEM0113,MUW0570,DJH0895,HAE0105,AEO1116,SDL0541,MRH0407,ILJ0929,JFC0075,FKS0069,MAM1293,DDM1065,ACH1011,CIS1542,MMO0531,NGB1625,CHP1711,RDB0546,LPL0420,WSK1857,TIH0573,ALM1768,LPS1875,TLW1555,KST1643,UMB0108,IEH0412,SEL1062,SNO0033,MAW1397,EOG0433,IKW0174,HDW1779,CDG0551,ATD0517,DKC0053,KPM0579,KLW1789,ADH1016,RLM1578,KRS0172,SWM1653,ALH0506,DSB0530,KCG1615,EAG0633,CCK1540,HKR1291,DBB1004,MGT0898,HSK0479,CBC1504,MSM1800,ILH1650,NAO1281,RSM1426,GPS0970,GSB0173,FWB1999,BPA0095,BZC1806,KAG0566,ASC1297,CSE0417,HWR1573,HJA1954,AOC1283,JVH1575,RBH0661,HMS1658,SJA0635,BKB0669,JAC1275,ISD1866,EAP0107,LSO1783,JCV0994,IMC0133,SNK1280,JIG1593,AME1364,SGN0146,ELT1370,HJB0858,MJF1646,WYG0599,BUE1561,DJC0137,OHA1516,MXM0184,DVM1290,GRR1428,AJD1612,PMB1928,GKW0043,CRM0880,RPM0125,SJC1563,JHR1580,LSH0464,NRM1656,KIF0951,ASR0150,ZHB1104,EHJ1339,HDH1384,NKF1871,WDS1286,DAD1438,SKV0041,YJB0171,CHW0919,NKT1510,EYM0896,ZAD1621,BDP0096,JUL0610,ICP1063,CLM1538,SQC1296,MLC0141,MBK1726,YCC0119,CTB0923,CRD0987,RJG0511,MCL1953,ILH1564,UAB0534,RWJ1403,JCC0016,MDR0572,JNR1592,GNV1082,FMH1018,LSB1588,GCC1659,LVF1626,RVJ0046,TCF0559,BPK1731,KVV0871,SIV1287,HWS0101,ADG0619,AAW0914,GTC0081,MVM0092,EBD1636,JJL1722,KDP1706,MEC0212,SZN1421,UCM1572,JAG0861,MJW1758,CGS0647,RJM0634,LKP1714,CDB1594,EPB0893,WCW1013,CMB0824,
                    # Cluster_1
                    if len(line_lst) == 1:
                        continue
                    if usr in line_lst:
                        for ele in line_lst:
                            if ele != usr:
                                tmp_0.append(ele)
                # 保存的群簇中，第一个用户为目标用户本身
                Insiders_2_Clusters.append(tmp_0.insert(0, usr))
                break
            else:
                continue
        print 'Insiders_2 关系群簇聚类完毕...\n\n'

        print '形成Insiders_2的离职关系列表...\n\n'
        for line in f_leave_lst:
            line_lst = line.strip('\n').strip(',').split(',')
        # 数据样例
        # CERT5.2 Leave Company Relationships Users for all Users
        # MMK1532,No:
        # Insider_LaidOff_0,
        # Insider_LaidOff_1,WMH1300,JRC1963,BAR1328,RDP1751,DAS1320,HKK0881,CEW1960,ILG0879,DEO1964,SMS0432,VSB1317,
        # Insider_LaidOff_2,CBC1504,JSB0860,KDP1706,FKH0864,RKW1936,BMR0865,SCO1719,ZJN1492,SAF1942,CHP1711,NAO1281,REF1924,JDJ1949,YBH1926,SNK1280,IAJ1729,DCA0857,LKC0405,VAH1292,TMT0851,JIP1503,
        # Insider_LaidOff_3,JAT1218,ADL1898,KSW0708,LAS0256,GWO1660,MIB1265,TCP0380,CDO0684,CDG0770,CLL0306,QSG1150,QAP0266,OCW1127,PKS1187,GER0350,BSS0847,OCD1985,MPF0690,USM0703,RFP1918,FKS1696,CRD0272,AWW0718,EJO0236,ESP1198,MMR1458,JIB1258,ZIE0741,DTB0722,EPG1196,DMP0344,MDS0680,CNM0787,NBL1190,OSS1463,ALT1465,WHG1669,WFV0687,STH0353,RPJ1159,JKB0287,DNJ0740,ELM1123,DXF1662,SCI0778,ISW0738,AYG1697,LMW0837,ICB1890,NTG1667,PCK0271,DHR1157,ZVW1475,BRG0728,HPM0360,ACA1126,KJG1121,JOE1672,UKM0845,KVF1143,DCC1119,JDB1163,NEG0281,FZG0389,MGB1235,KHW0289,VRP0267,CAB1189,JAL0811,AMS1236,ALW0764,CQR1172,EGM1222,AMB0745,MBW1149,WHB1247,XBK0246,ZEH0685,JRB0759,JUP1472,WWW0701,HJO0779,DCV1185,KMO0382,CWW1120,HSN0675,DJH0253,
        # Insider_LaidOff_4,RMB1821,FAM0495,WSW1091,SDL0541,CTH1812,JBG1375,LRF0549,JHP1654,NWP1609,JDM0208,HSF1115,FDS1841,NTV1777,GMM1037,MAF0467,ZAD1621,XMG1579,HBH0111,KBC0818,TAG1610,EAL1813,WBP0828,NWH0960,BRM0126,MAR1075,GWH0961,JXH1061,HFF0560,MMB0556,UAM1108,KEW0198,BNS0484,LSM1382,GFM1815,CIM1095,VCF1602,CKP0630,JKM1790,PBC0077,PTV0067,KBC1390,ZHB1104,PTM1432,MGM0539,IHC0561,OJC0930,SIS0042,CIF1430,KLB0918,TRC1838,TNB1616,IVS1411,WDT1634,DHS0204,SLL0193,MTD0971,DDR1649,MFM1400,TTR1792,GWG0497,MCP0611,CTT0639,HMK0653,VVG0624,MIB0203,LLW0179,RAT0514,GKW0043,NAH1366,PLF1030,TPO1049,ICB1354,RRS0056,MJA1784,HMS1658,BYO1846,EJV0094,HIS1394,GCB0118,HXP0976,MZO1066,KRC1348,DPK0954,KJH0475,JJW1785,RBC1624,LVF1626,ITA0159,CKL0652,ZKP0542,LJM1807,KCM0466,KFS1029,PTH0005,CDB1594,NIV1608,LCB1869,WSK1857,IJM0603,ELT1370,SQC1072,TMC0934,GTN1021,FIM0605,ETW0002,KSS1005,LMM0167,MEW0485,GPO1020,OKM1092,XAM0376,HBW0057,MTP1582,ACB0220,JKB1843,SLC1865,VPA0974,ACE1431,LAH0463,
            if line_lst[0] == usr:
                User_Index = f_leave_lst.index(line)
                break
            else:
                continue
        print 'tmp_0 is ', tmp_0, '\n'
        print 'User_Index验证： ', f_leave_lst[User_Index], '\n'
        tmp_1 = []
        j = 1
        while j < 6:
            line_0 = f_leave_lst[User_Index + j].strip('\n').strip(',').split(',')
            print 'ling_0 is ', line_0, '\n'
            for ele in line_0[1:]:
                if ele in tmp_0[1:]:
                    tmp_1.append(ele)
            j += 1
        print 'tmo_1 is ', tmp_1, '\n'
        tmp_2 = []
        tmp_2.append(len(tmp_1))
        for ele in tmp_1:
            tmp_2.append(ele)
        print 'tmp_2 is ', tmp_2, '\n'
        Insiders_2_Leave_Users.append(tmp_2)
    print 'Insiders_2_Leave_Users is ', Insiders_2_Leave_Users, '\n'
    k = 0
    while k < len(Insiders_2_lst):
        print k, Insiders_2_lst[k], '\n'
        print len(Insiders_2_Leave_Users[k]) - 1, '\n'
        print Insiders_2_Leave_Users[k], '\n'
        k += 1




