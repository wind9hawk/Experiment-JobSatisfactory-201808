# coding:utf-8
# 例行：含有控制开关的测试模块文件
import sys,os
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import math
import copy
# 测试1
# 第一次实验发现BYO846的JS_Risk计算为0，怀疑单纯考虑一个friends群簇没有离职人员命中
Flag_0 = False
if Flag_0:
    f_laidoff = open(r'CERT5.2-Leave-Relationship.csv', 'r')
    f_cluster_friends = open(sys.path[0] + '\\' + 'CERT5.2_EmailContactFeats-0.1' + '\\' + 'SIS0042_KMeans_Clusters.csv', 'r')
    f_laidoff_lst = f_laidoff.readlines()
    f_cluster_friends_lst = f_cluster_friends.readlines()
    f_laidoff.close()
    f_cluster_friends.close()

    # Cluster_Friends数据格式
    # Cluster0
    # Carol_Copeland,Juarez.Isaac,Lane-Kylie,Lawrence-Stuart,ACS951,RIK0629,CKM0939,KJH0475,Nora_Blevins,OWS0279,BLC1263,Ochoa-Albert,Myra.M.Morrow,Jackson.B.Moody,PDH1180,CZK1473,JJF1167,HBO999,Ashely_H_Nguyen,Bryant-Upton,ZVW1475,BRM0126,ZWS0755,Justine.R.Skinner,AAC683,ZHB7,IAH5891,Carol_Gomez,Melissa.Q.Short,Vivian_Douglas,SRC586,Aileen_Munoz,Abra_M_Campos,PWB1739,QZH57,DJP73,Florence_N_Lawson,QKB1893,Butler-Kadeem,KNH588,Myra_M_Morrow,BDM178,BTR1410,TCP0380,XAB588,Chastity_Bonner,Carol_S_Copeland,Zena_A_Duncan,CLD1435,SRP1576,BHO3872,Mcgee_Kirestin,IJM621,MAF1623,ARM0805,HBO3,IJM748,Vanna-Fowler,KRC0098,LKM19,Hilda_Moran,YBD1929,BSD1735,Blair_Elvis,HAC1527,SJP1023,SEO0946,Laura_A_Bowman,RKF0080,Aileen_R_Munoz,KLG0576,KBC1390,CWM0618,Ivory_Mejia,BAR1640,Lacota.H.Livingston,Kirestin-Mcgee,MGC0646,Bruce.G.Kelley,Deirdre_Clayton,KJA0347,ZWS866,BCG37,SJA57,HTH1001,INW1064,LIJ1581,DAR0139,CEG1467,Webb-Lenore,Willa_Bullock,LHD1750,Cash-Christopher,YLH0423,LTB0308,CLF1981,IAJ1729,Charde.L.Farmer,Ulric.B.Juarez,JDS115,OTB0008,ISK0116,DDS1090,Cynthia_Blanchard,Moana.A.Weiss,KRC0842,RPJ1159,Gwendolyn_Eaton,Adam.C.Haney,Hall.L.Gay,ICH1810,HBW0683,JAW1429,DHR4378,ZUR99,OLM1747,Oneill-Bernard,DTB0722,RCD0299,Eve_Powell,QEL1515,YNC1336,TCA1183,RJM1,DAL0795,ASH0458,Jayme_Mcguire,YSH1997,ERM1590,Nora.A.Booth,RLF0472,CIM735,Odette_Richardson,Lara_C_Rich,Cummings-Matthew,Tamekah.C.Cochran,AUH0138,Blair-Tarik,AGB0447,NLC1113,AJR817,PJB0886,HRT0984,RAV0088,Neil_Dickerson,JEC1427,CEB1879,ACT1903,GRB56,EMM0641,YEG1439,YWF1562,INC0091,FAD1863,Brock.B.Weaver,GTF1464,TSJ0655,JGM1269,OFA1415,FWT1586,BCR0747,CHL0953,JIT0356,KVP1424,XAW13,XRS0498,Tana_Curry,Florence.N.Lawson,KVC522,Maggie-Keith,Ashely_Wilkerson,KMO0382,Shannon_Quin,IAM6518,AGB0901,TAK0501,DCC1119,CAB1189,BCA1517,Tamekah.W.Brady,KHG0205,MNE1698,Vera_Luna,ABL1229,HRR1154,Moreno-Ann,Teagan.Abbott,Celeste_Bright,Frost_Taylor,Morgan_Dixon,Ariel.L.Barr,Nevada.H.Hood,KJM1303,CPW1,CBD1128,JAC0721,EYM2474,TCC0311,MMM1655,SDH1854,DXB1791,GGH991,HNR0874,Bell.S.Willis,ARF0719,
    # Cluster1
    # Macy_Patterson,WAS1823,HMC1847,ESM1828,GRB1842,XKB1829,YDM1822,Haney-Aaron,CBW1826,Chiquita_Burns,Micah-King,HDA364,Rose.M.Blackwell,Donna_Black,YDM6,Ava_Hebert,Jonathan_Buck,Fatima_Santana,WAS1,William.O.Sykes,GRB3,WCR1830,Hannah_M_Callahan,NRR1835,Hammond-Nelle,ONB1833,MUP1819,JKB1843,HDA1824,ACH1831,MPK1844,Rebekah_Santos,WLH1827,TRC1838,NJV1818,DEB1767,Jemima-Pratt,Eugenia.S.Mercado,RMV1820,GFV1837,WOS1834,ACH1840,RSS1825,NZH1839,CCB1836,BGF1845,WCR66,Carly_B_Witt,Roman-Nelle,Olympia.N.Bonner,WLH7557,RMV674,Belle_Frost,JBP1832,
    # Cluster2
    # FDS1841,RMB1821,Germane_Velez,Vasquez-Noah,XKB1,Curry-Tana,Puckett-Regan,Salazar-Jordan,YVJ641,BAG995,Orr_Arthur,Keelie.I.Sargent,MIC54,CLN0061,HBP0009,Osborn-Jeanette,GCH0470,DOR0935,HYA23,ENB1617,JKC1522,Baker-Thaddeus,CLG236,Morgan_A_Fowler,YLR1188,CBN45,Small_Christopher,Ferris-Horton,KVC1487,AAC0904,HMD1505,MES0966,Gilbert-Christopher,PAP72,HXP0976,Cassady.R.Daniels,AJS1408,ZAR0235,RNC1295,HJB0858,NFH0677,HBP9842,DZA0195,Shelly.L.May,Hasad.S.Knowles,DJC0137,Combs-Louis,CTK0406,DSB0530,TTG0460,DOT0144,YNO0103,Camden-Powell,Stuart.Keefe,CKB0245,UMB0310,HTM1498,Cortez-Harding,KUB1569,Jaden.A.Waters,JJS0013,JJA1164,ERB0104,CTP0071,SWC1392,Alma_S_Carpenter,Sawyer-Marcia,Ulla.M.Henry,Madaline_Tillman,PEM0277,DLM2,CEM1385,Mara_Farrell,MAB1340,YIN0342,ROB6,JBI25,RMK1771,SFJ0856,HTM57,TAB0519,HBP1076,VCM0992,RDB0546,RRC0891,PHG1778,CAG1416,DPC367,MYB0686,AEG0962,JRB0759,WPL0086,CCW5426,GPS29,Jael.I.Griffith,DEC1939,RDW1710,SJC1563,GCE1147,Wesley-Fletcher,WWW0701,UAB0534,Althea_M_Berger,Alice_Callahan,TDC1086,DZH1867,Sage.E.Ortega,Bree_Mcclure,Darryl_J_Hays,BDB1111,JAC1275,ABM0890,Burt_Giselle,Conrad-Gannon,Conner-Clayton,BRM1080,WAH1774,MSK0117,BWC0509,HLH9961,Finley-Lynn,BDP0096,ROB0477,Brenda_P_Allison,SJA0635,Ursa_S_Wood,DDK0995,Aphrodite_Macias,JMW0038,Brenda_O_Carver,CPL0439,ZEP0543,Oliver-Declan,EZB0925,MVM0092,Chavez-Sylvester,ZOF1559,GMB0400,UMB0322,GCD0194,ACB1087,CSE0417,AAW0952,MDR1497,IBR0131,EOG0433,FAJ1122,ENB4947,WDS1286,Jane-Buchanan,BEM1501,
    # Cluster3
    # Tatyana_A_Johnston,Tana_P_Orr,Indigo_Christensen,Lara.Y.Lopez,OJC0930,Jane.A.Griffin,Wong-Flynn,IKB0691,DLM1699,JQS1350,DJT1534,DES1617,
    # Cluster4
    # DLH0679,JBI1134,Colon-Upton,DEM0018,
    Cluster_Friends = [[] for i in range(5)]
    line = f_cluster_friends_lst[1].strip('\n').strip(',').split(',')
    for ele in line:
        Cluster_Friends[0].append(ele)
    line = f_cluster_friends_lst[3].strip('\n').strip(',').split(',')
    for ele in line:
        Cluster_Friends[1].append(ele)
    line = f_cluster_friends_lst[5].strip('\n').strip(',').split(',')
    for ele in line:
        Cluster_Friends[2].append(ele)
    line = f_cluster_friends_lst[7].strip('\n').strip(',').split(',')
    for ele in line:
        Cluster_Friends[3].append(ele)
    #line = f_cluster_friends_lst[9].strip('\n').strip(',').split(',')
    #for ele in line:
    #    Cluster_Friends[4].append(ele)

    # 离职关系数据格式
    # BYO1846,2010-12:
    # Insider_LaidOff_0,RMB1821,FDS1841,
    # Insider_LaidOff_1,NWP1609,ZAD1621,TAG1610,MAR1075,JXH1061,LSM1382,KBC1390,IVS1411,MFM1400,CTT0639,MZO1066,
    # Insider_LaidOff_2,WSW1091,JHP1654,JDM0208,HSF1115,UAM1108,CIM1095,ZHB1104,PTM1432,WDT1634,DHS0204,DDR1649,HMK0653,HMS1658,
    # Insider_LaidOff_3,FAM0495,SDL0541,CTH1812,JBG1375,LRF0549,NTV1777,GMM1037,MAF0467,XMG1579,HBH0111,KBC0818,EAL1813,WBP0828,NWH0960,BRM0126,GWH0961,HFF0560,MMB0556,BNS0484,CKP0630,JKM1790,PTV0067,MGM0539,OJC0930,KLB0918,MTD0971,TTR1792,MCP0611,VVG0624,LLW0179,RAT0514,NAH1366,PLF1030,TPO1049,RRS0056,MJA1784,EJV0094,GCB0118,
    # Insider_LaidOff_4,JAT1218,ADL1898,KSW0708,WMH1300,LAS0256,GWO1660,MIB1265,TCP0380,CBC1504,JSB0860,CDO0684,KDP1706,CDG0770,FKH0864,CLL0306,JRC1963,QSG1150,QAP0266,BAR1328,OCW1127,PKS1187,GER0350,BSS0847,OCD1985,USM0703,RKW1936,RFP1918,RDP1751,FKS1696,BMR0865,AWW0718,EJO0236,HKK0881,ESP1198,MMR1458,JIB1258,SCO1719,ZJN1492,ZIE0741,DTB0722,CEW1960,ILG0879,DMP0344,DEO1964,CNM0787,NBL1190,ALT1465,WHG1669,SMS0432,WFV0687,STH0353,RPJ1159,JKB0287,ELM1123,DXF1662,NAO1281,SCI0778,AYG1697,LMW0837,ICB1890,NTG1667,PCK0271,DHR1157,ZVW1475,BRG0728,HPM0360,KJG1121,JOE1672,UKM0845,KVF1143,
    LaidOff = [[] for i in range(5)]
    i = 0
    while i < len(f_laidoff_lst):
        line_lst = f_laidoff_lst[i].strip('\n').strip(',').split(',')
        if len(line_lst) == 2 and ':' in line_lst[1] and 'GWG0497' in line_lst[0]:
            # 定位到用户在第i行
            line_users = f_laidoff_lst[i + 1].strip('\n').strip(',').split(',')
            j = 1
            while j < len(line_users):
                LaidOff[0].append(line_users[j])
                j += 1
            line_users = f_laidoff_lst[i + 2].strip('\n').strip(',').split(',')
            j = 1
            while j < len(line_users):
                LaidOff[1].append(line_users[j])
                j += 1
            line_users = f_laidoff_lst[i + 3].strip('\n').strip(',').split(',')
            j = 1
            while j < len(line_users):
                LaidOff[2].append(line_users[j])
                j += 1
            line_users = f_laidoff_lst[i + 4].strip('\n').strip(',').split(',')
            j = 1
            while j < len(line_users):
                LaidOff[3].append(line_users[j])
                j += 1
            line_users = f_laidoff_lst[i + 5].strip('\n').strip(',').split(',')
            j = 1
            while j < len(line_users):
                LaidOff[4].append(line_users[j])
                j += 1
            break
        else:
            i += 1
            continue
    print 'LaidOff user is :','\n'
    for i in range(len(LaidOff)):
        print LaidOff[i], '\n'
    print 'Friends is ', '\n'
    for i in range(len(Cluster_Friends)):
        print Cluster_Friends[i], '\n'

    print '....<<<<验证离职人员是否在好友关系里>>>>....\n\n'
    LaidOff_Friends = [[] for i in range(5)]
    i = 0
    while i < 5:
        for usr in LaidOff[i]:
            j = 0
            while j < len(Cluster_Friends):
                if usr in Cluster_Friends[j]:
                    LaidOff_Friends[i].append(usr)
                    break
                else:
                    j += 1
                    continue
            continue
        i += 1
        continue
    print 'LaidOff Friends is \n'
    for i in range(len(LaidOff_Friends)):
        print i, LaidOff_Friends[i], '\n'
    sys.exit()

Flag_1 = False
# 验证下python中函数调用的函数参数的引用情况
# 函数调用改变了原始参数！
if Flag_1 == True:
    a = range(20)
    def Sort_List(a, k):
        if k/2 == 0:
          turn = k/2
        else:
           turn = k/2 + 1
        new_lst = []
        i = 0
        while i < turn:
            new_lst.append(max(a))
            a.remove(max(a))
            i += 1
        return new_lst
    b = Sort_List(a,5)
    print 'b, is ', b, '\n'
    print 'a is ', a, '\n'


# 本测试代码用于验证0.2版本的JS_Risk的准确度
# 通过对计算得到的JS_Risk进行排序，从而得到最高的用户，显示出所有场景二的30个用户所处的位置
Flag_2 = True
if Flag_2 == True:
    f_js_risk = open('CERT5.2_JS-Risks-Leave-0.2.csv', 'r')
    f_js_risk_lst = f_js_risk.readlines()
    f_js_risk.close()
    # 场景二用户的ID名单
    Insiders_2 = []
    Insiders_2_Dir = os.path.dirname(sys.path[0]) + '\\' + 'r5.2-2'
    for usr in os.listdir(Insiders_2_Dir):
        Insiders_2.append(usr[7:-4])
    print 'CERT5.2中Insiders_2的列表有...\n'
    for usr in Insiders_2:
        print usr, '\n'


    print '..<<开始依据2000个用户的JS_Risk进行排序>>..\n\n'
    # 定义需要排序的用户与对应的JS_Risk列表
    Users_JS_Risks = []
    for line in f_js_risk_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        if len(line_lst) != 2:
            print line_lst, '非规范数据...\n'
            continue
        # print line, line_lst, '\n'
        if line_lst[0] == 'NoMathc':
            print 'NoMatch...\n\n'
            continue
        tmp_0 = []
        tmp_0.append(line_lst[0])
        tmp_0.append(float(line_lst[1]))
        Users_JS_Risks.append(tmp_0)
    Users_JS_Risks_Sort = sorted(Users_JS_Risks, key=lambda a:a[1], reverse=True)

    f_0 = open('CERT5.2_JS-Risk_Sort-0.1.csv', 'w')
    i = 0
    while i < len(Users_JS_Risks_Sort):
        if Users_JS_Risks_Sort[i][0] in Insiders_2:
            print 'Insider_2: ', i, ' : ', Users_JS_Risks_Sort[i][0], ':', Users_JS_Risks_Sort[i][1], '\n'
            f_0.write(Users_JS_Risks_Sort[i][0])
            f_0.write(',')
            f_0.write(str(Users_JS_Risks_Sort[i][1]))
            f_0.write('\n')
            i += 1
        else:
            f_0.write(Users_JS_Risks_Sort[i][0])
            f_0.write(',')
            f_0.write(str(Users_JS_Risks_Sort[i][1]))
            f_0.write('\n')
            i += 1
            continue

    print '..<<Insider_2的JS_Risk分析完毕（0.2版本）>>..\n\n'
    sys.exit()



print '....<<<<本部分分析30个跳槽用户离职邮件关系情况>>>>....\n\n'
Flag_3 = False
if Flag_3 == True:
    # 获得30个跳槽用户的用户列表
    Insiders_2 = []
    Insiders_2_Dir = os.path.dirname(sys.path[0]) + '\\' + 'r5.2-2'
    for usr in os.listdir(Insiders_2_Dir):
        Insiders_2.append(usr[7:-4])
    print 'CERT5.2中Insiders_2的列表有...\n'
    for usr in Insiders_2:
        print usr, '\n'
    # 接下来分析其离职邮件联系人
    f_test_3 = open('CERT5.2_Insiders-2_LeaveContacts_NonSingle.csv', 'w')
    Dir_Path = sys.path[0] + '\\' + 'CERT5.2_EmailContactFeats-0.2'
    for file in os.listdir(Dir_Path):
        # AAB1302Leave_Contacts.csv
        if file[:7] in Insiders_2:
            # 说明是跳槽用户
            # 继续分析其包含离职邮件联系人的文件
            Flag_Exist_Nonsignle = False
            if 'Leave_Contacts' in file:
                f_tmp = open(Dir_Path + '\\' + file, 'r')
                f_tmp_lst = f_tmp.readlines()
                f_tmp.close()
                for line in f_tmp_lst:
                    line_lst = line.strip('\n').strip(',').split(',')
                    if len(line_lst) < 2:
                        f_test_3.write(line_lst[0])
                        f_test_3.write('\n')
                        continue
                    if float(line_lst[1]) > 0 and float(line_lst[1]) < 1:
                        Flag_Exist_Nonsignle = True
                        for ele in line_lst:
                            f_test_3.write(ele)
                            f_test_3.write(',')
                        f_test_3.write('\n')
                    else:
                        continue
                if Flag_Exist_Nonsignle == False:
                    print '不存在正常通信的离职邮件联系人。。', file[:7], '\n'
            else:
                continue
    print '包含30个跳槽用户的离职邮件联系人文件提取完毕...\n'
    f_test_3.close()
    print '....<<<<本部分分析30个跳槽用户离职邮件关系情况。。。分析完毕...>>>>....\n\n'
    sys.exit()
