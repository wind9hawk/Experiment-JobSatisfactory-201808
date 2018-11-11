# coding:utf-8

# 由于之前分析CERT5.2中leave_relationship的时候没有考虑具体到离职的日期，结果导致
# 在分析部分用户离职关系时，会受到其离职后的离职用户的影响
# 如比较用户A与B两个用户的离职用户关联，可能用户A在离职前的三个月离职关联增长迅速；而B并未离职或者离职晚于A，导致其绝对数量值高于A，出现误差

# 为了避免上述问题，我们重新计算提取CERT5.2中所有用户的离职关联，其中，以用户自身的离职日期未标准，只考虑在此之前的离职用户

# 依据的数据文件
# 1. CERT5.2-Leave-Relationship.csv
# 2. CERT5.2-Leave-Users_OnDays_0.6.csv


import os,sys

# 定义一个日期比较函数
def Cmp_Date(A, B):
    # 2010-02-25
    # 判断日期A是否比B更近
    year_a = A[:4]
    month_a = A[5:7]
    day_a = A[8:]
    year_b = B[:4]
    month_b = B[5:7]
    day_b = B[8:]
    if year_a > year_b:
        return True
    else:
        if year_a < year_b:
            return False
        else:
            if month_a > month_b:
                return True
            else:
                if month_a < month_b:
                    return False
                else:
                    if day_a > day_b:
                        return True
                    else:
                        return False


# 定义一个函数用于比较符合列表中是否存在某个元素
def Exist_In_MultiLst(A, X, Y):
    # A = [a_lst, b_lst]
    # 要判断元素X是否在A[:, Y]中
    tmp_2 = []
    for ele in A:
        tmp_2.append(ele[Y])
    if X in tmp_2:
        return A[tmp_2.index(X)][1]
    else:
        return False

print '......<<<<<考虑日期天数的离职关系表更新>>>>>>......\n\n'

# 定义所有离职用户及其离职时间
# 数据样例
# Laid off Users in CERT5.2 from 2009-12 to 2011-05
# RMB1821,2010-02-09,Rose Maisie Blackwell,RMB1821,Rose.Maisie.Blackwell@dtaa.com,Salesman,,1 - Executive,5 - SalesAndMarketing,2 - Sales,5 - RegionalSales,Donna Erin Black
CERT52_Leave_Users = []
f_leave = open('CERT5.2-Leave-Users_OnDays_0.6.csv', 'r')
f_leave_lst = f_leave.readlines()
f_leave.close()
for line in f_leave_lst:
    line_lst = line.strip('\n').strip(',').split(',')
    if len(line_lst) < 2:
        continue
    tmp_0 = []
    tmp_0.append(line_lst[0])
    tmp_0.append(line_lst[1])
    CERT52_Leave_Users.append(tmp_0)
print '....<<<<CERT5.2中离职用户表建立完毕>>>>....\n\n'
print '输出样例：\n'
for i in range(5):
    print i, CERT52_Leave_Users[i], '\n'


print '....<<<<开始更新离职关系表>>>>....\n\n'

# 读入原始离职表
f_leave_rs_0 = open('CERT5.2-Leave-Relationship.csv', 'r')
f_leave_rs_0_lst = f_leave_rs_0.readlines()
f_leave_rs_0.close()
# 定义一个存放所有用户原始离职关系的列表
CERT52_Users_Leave_Relationship = []
i = 0
while i < len(f_leave_rs_0_lst):
    line_lst = f_leave_rs_0_lst[i].strip('\n').strip(',').split(',')
    # 数据样例
    # CERT5.2 Leave Company Relationships Users for all Users
    # MMK1532,No:
    # Insider_LaidOff_0,
    # Insider_LaidOff_1,WMH1300,JRC1963,BAR1328,RDP1751,DAS1320,HKK0881,CEW1960,ILG0879,DEO1964,SMS0432,VSB1317,
    # Insider_LaidOff_2,CBC1504,JSB0860,KDP1706,FKH0864,RKW1936,BMR0865,SCO1719,ZJN1492,SAF1942,CHP1711,NAO1281,REF1924,JDJ1949,YBH1926,SNK1280,IAJ1729,DCA0857,LKC0405,VAH1292,TMT0851,JIP1503,
    # Insider_LaidOff_3,JAT1218,ADL1898,KSW0708,LAS0256,GWO1660,MIB1265,TCP0380,CDO0684,CDG0770,CLL0306,QSG1150,QAP0266,OCW1127,PKS1187,GER0350,BSS0847,OCD1985,MPF0690,USM0703,RFP1918,FKS1696,CRD0272,AWW0718,EJO0236,ESP1198,MMR1458,JIB1258,ZIE0741,DTB0722,EPG1196,DMP0344,MDS0680,CNM0787,NBL1190,OSS1463,ALT1465,WHG1669,WFV0687,STH0353,RPJ1159,JKB0287,DNJ0740,ELM1123,DXF1662,SCI0778,ISW0738,AYG1697,LMW0837,ICB1890,NTG1667,PCK0271,DHR1157,ZVW1475,BRG0728,HPM0360,ACA1126,KJG1121,JOE1672,UKM0845,KVF1143,DCC1119,JDB1163,NEG0281,FZG0389,MGB1235,KHW0289,VRP0267,CAB1189,JAL0811,AMS1236,ALW0764,CQR1172,EGM1222,AMB0745,MBW1149,WHB1247,XBK0246,ZEH0685,JRB0759,JUP1472,WWW0701,HJO0779,DCV1185,KMO0382,CWW1120,HSN0675,DJH0253,
    # Insider_LaidOff_4,RMB1821,FAM0495,WSW1091,SDL0541,CTH1812,JBG1375,LRF0549,JHP1654,NWP1609,JDM0208,HSF1115,FDS1841,NTV1777,GMM1037,MAF0467,ZAD1621,XMG1579,HBH0111,KBC0818,TAG1610,EAL1813,WBP0828,NWH0960,BRM0126,MAR1075,GWH0961,JXH1061,HFF0560,MMB0556,UAM1108,KEW0198,BNS0484,LSM1382,GFM1815,CIM1095,VCF1602,CKP0630,JKM1790,PBC0077,PTV0067,KBC1390,ZHB1104,PTM1432,MGM0539,IHC0561,OJC0930,SIS0042,CIF1430,KLB0918,TRC1838,TNB1616,IVS1411,WDT1634,DHS0204,SLL0193,MTD0971,DDR1649,MFM1400,TTR1792,GWG0497,MCP0611,CTT0639,HMK0653,VVG0624,MIB0203,LLW0179,RAT0514,GKW0043,NAH1366,PLF1030,TPO1049,ICB1354,RRS0056,MJA1784,HMS1658,BYO1846,EJV0094,HIS1394,GCB0118,HXP0976,MZO1066,KRC1348,DPK0954,KJH0475,JJW1785,RBC1624,LVF1626,ITA0159,CKL0652,ZKP0542,LJM1807,KCM0466,KFS1029,PTH0005,CDB1594,NIV1608,LCB1869,WSK1857,IJM0603,ELT1370,SQC1072,TMC0934,GTN1021,FIM0605,ETW0002,KSS1005,LMM0167,MEW0485,GPO1020,OKM1092,XAM0376,HBW0057,MTP1582,ACB0220,JKB1843,SLC1865,VPA0974,ACE1431,LAH0463,
    # NTB0710,No:
    # 首先需要确定用户开始
    if len(line_lst) < 2:
        i += 1
        continue
    if len(line_lst[0]) == 7:
        print '开始分析 ', i, line_lst[0], ':', line_lst[1].strip(':'), '\n'
        tmp_1 = [[] for j in range(6)] # 如果使用i，后面的变量会发生变化
        user_0 = f_leave_rs_0_lst[i].strip('\n').strip(',').split(',')[0]
        tmp_1[0].append(user_0)
        if f_leave_rs_0_lst[i].strip('\n').strip(',').split(',')[1].strip(':') != 'No':
            tmp_1[0].append(Exist_In_MultiLst(CERT52_Leave_Users, user_0, 0))
        else:
            tmp_1[0].append('All Job Time')

        j = 1
        while j < 6:
            #print i+j, f_leave_rs_0_lst[i + j], '\n'
            for ele in f_leave_rs_0_lst[i + j].strip('\n').strip(',').split(','):
                #if 'LaidOff' not in ele:
                tmp_1[j].append(ele.strip(':'))
            #print j, 'tmp_1[j] is ', tmp_1[j], '\n'
            j += 1
        CERT52_Users_Leave_Relationship.append(tmp_1)
        i += 1
    else:
        i += 1
        continue
print '....<<<<读取原始离职关系列表完毕>>>>....\n\n'
for line in CERT52_Users_Leave_Relationship[:10]:
    for ele in line:
        print ele, '\n'
#sys.exit()


print '....<<<<开始进行过滤>>>>....\n\n'
# 定义一个存放过滤掉的时间晚离职的用户列表
Late_Leave_Users = []
i = 0
while i < len(CERT52_Users_Leave_Relationship):
    # line[0][0]表示user_id
    # line[0][1]表示该用户离职时间，'No'表示全职
    # [[],[],[],[],[].[]]
    if CERT52_Users_Leave_Relationship[i][0][1].strip(':') != 'All Job Time':
        late_leave = []
        late_leave.append(CERT52_Users_Leave_Relationship[i][0][0])
        late_leave.append(Exist_In_MultiLst(CERT52_Leave_Users, CERT52_Users_Leave_Relationship[i][0][0], 0))
    else:
        late_leave = []
        late_leave.append(CERT52_Users_Leave_Relationship[i][0][0])
        late_leave.append('All Job Time')
    # late_leave.append(':')
    print '过滤前：\n'
    #for j in range(1):
    #    for ele in CERT52_Users_Leave_Relationship[j]:
    #        print j, '层次长度为：', len(ele) - 1, ele, '\n'
    # sys.exit()
    if CERT52_Users_Leave_Relationship[i][0][1].strip(':') == 'All Job Time':
        # 说明该用户全职
        # 即只需要提出2011-05的离职用户即可，因为我们默认使用1 to N-1来分析第N个月
        deadline_date = '2011-06-01'
    else:
        #print 'CERT52_Users_Leave_Relationship[i][0][0] is \n'
        #print CERT52_Users_Leave_Relationship[i][0][0], ':', CERT52_Users_Leave_Relationship[i][0][1], '\n'
        deadline_date = Exist_In_MultiLst(CERT52_Leave_Users,CERT52_Users_Leave_Relationship[i][0][0], 0)
        # sys.exit()
    for sub_gp in CERT52_Users_Leave_Relationship[i][1:]:
        for l_user in sub_gp:
            if 'LaidOff' in l_user:
                print l_user, '标题，跳过..\n\n'
                continue
            else:
                # 用户l_user的离职时间
                date_l_user = Exist_In_MultiLst(CERT52_Leave_Users, l_user, 0)
                print 'date_l_user is ', date_l_user, '\n'
                # sys.exit()
                # 上述该用户的离职时间
                # 与deadline比较，只有小于deadline才可以
                if date_l_user == False:
                    print l_user, '该用户非离职..\n\n'
                    sys.exit()
                if Cmp_Date(deadline_date, date_l_user) == False:
                    # 该时间比目标用户离职晚，过滤掉
                    tmp_2= []
                    tmp_2.append(l_user)
                    tmp_2.append(date_l_user)
                    late_leave.append(tmp_2)
                    sub_gp.remove(l_user)
                else:
                    continue
    print '过滤后：\n'
    for j in range(1):
        for ele in CERT52_Users_Leave_Relationship[j]:
            print j, '层次长度为：', len(ele) - 1, ele, '\n'
    Late_Leave_Users.append(late_leave)
    i += 1


print '过滤掉的用户为： \n'
t = 0
for line in Late_Leave_Users:
    if len(line) == 2:
        Late_Leave_Users.remove(line)
        # print '移除：', line, '\n'
    else:
        print t+1, '过滤的用户为： ', line, '\n'
        t += 1


print '....<<<<接下来要将过滤的离职用户关联写入文件>>>>....\n\n'
# 计划写入两个文件
# 一个文件保存新的CERT5.2离职用户关系列表
# 一个文件保存过滤掉的原本考虑的用户离职关系
f_New_Leave = open('CERT5.2_Leave_Relationship_Order.csv-0.6', 'w')
for line in CERT52_Users_Leave_Relationship:
    # [[],[],[],[],[],[]]
    for sub_gp in line:
        for ele in sub_gp:
            f_New_Leave.write(ele)
            f_New_Leave.write(',')
        f_New_Leave.write('\n')
f_New_Leave.close()

f_Filter_Users = open('CERT5.2_Leave_Relationship_Filter.csv-0.6', 'w')
for line in Late_Leave_Users:
    # line数据格式样例为：
    # ['BSS0847', '2010-05-14', ['GER0350', '2010-05-14'], ['HBH0111', '2010-05-27']]
    f_Filter_Users.write(line[0])
    f_Filter_Users.write(',')
    f_Filter_Users.write(line[1])
    f_Filter_Users.write(',')
    for ele in line[2:]:
        f_Filter_Users.write(ele[0])
        f_Filter_Users.write(':')
        f_Filter_Users.write(ele[1])
        f_Filter_Users.write(',')
    f_Filter_Users.write('\n')
f_Filter_Users.close()









