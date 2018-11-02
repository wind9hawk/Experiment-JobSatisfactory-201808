# coding:utf-8
# 进入到分析系列0.4
# 本模块主要进行一个CERT5.2中用户OS结构中离职用户与其邮件联系人交叉匹配的统计分析

# 大致步骤
# Step-1: 依据用户的LDAP信息和得到的初步邮件联系人信息，得到Part1与Part2的邮件联系人列表；
# Step-2: 将邮件联系人列表与离职关系列表比对，仅考虑前四个行，最后一行数据为不同事业部的离职人数；
# Step-3: 将得到的用户Leave_EMContacts列表数据[user_id, LEC1, LEC2, LEC3, LEC4]进行scale，
# 输出30个Insiders的标准化后的特征

import os,sys
import numpy as np
import sklearn.preprocessing as skp
import copy
import shutil

# 定义一个自动返回恶意场景攻击者名单的函数
def Get_Insiders(RootDir, Number):
    # 父目录
    # 场景编号
    dir = 'r5.2-' + str(Number)
    Insiders = []
    for file in os.listdir(RootDir + '\\' + dir):
        Insiders.append(file[7:-4])
    return Insiders

print '......<<<<<<CERT5.2中用户离职与邮件联系人的关系系列实验>>>>>>......\n\n\n'


print '....<<<<初始化数据源>>>>....\n\n'
# 由LDAP数据生成两个事业部的用户列表
LDAP_Path = os.path.dirname(sys.path[0]) + '\\' + 'LDAP' + '\\' + '2009-12.csv'
f_LDAP = open(LDAP_Path, 'r')
f_LDAP_lst = f_LDAP.readlines()
f_LDAP.close()
# 获取用户的邮件通讯数据（只包括1vs1邮件）
Email_Dir = r'G:\GitHub\Essay-Experiments\CERT5.2-Results\CERT5.2-Users-EmailRecords-0.4'
# 指定分析的主目录
Analyze_Dir = sys.path[0] + '\\' + 'CERT5.2_JS-Risk_Analyze-0.4'
if os.path.exists(Analyze_Dir) == False:
    os.makedirs(Analyze_Dir)
# 指定离职数据源
f_Leave = open(r'CERT5.2-Leave-Relationship.csv', 'r')
f_Leave_lst = f_Leave.readlines()
f_Leave.close()
print '....<<<<初始化数据完毕>>>>....\n\n'


print '....<<<<开始形成CERT5.2的事业部列表，并与离职列表匹配得到新统计特征>>>>....\n\n'
# 事业部列表
CERT52_Part_1 = []
CERT52_Part_2 = []
for line in f_LDAP_lst:
    # employee_name,user_id,email,role,projects,business_unit,functional_unit,department,team,supervisor
    # Hoyt Berk Wiley,HBW0057,Hoyt.Berk.Wiley@dtaa.com,ProjectManager,,1 - Executive,2 - ResearchAndEngineering,1 - ProjectManagement,,Rina Adena Horn
    line_lst = line.strip('\n').strip(',').split(',')
    if line_lst[1] == 'user_id':
        continue
    #print line_lst, '\n'
    if len(line_lst) < 6:
        print '长度小于正常的LDAP数据：\n'
        print line_lst, '\n\n'
        continue
    if line_lst[5] == '1 - Executive':
        CERT52_Part_1.append(line_lst[1])
    if line_lst[5] == '2 - Executive':
        CERT52_Part_2.append(line_lst[1])
print '..<<事业部分割列表统计完毕>>..\n\n'

print '..<<用户匹配特征生成>>..\n\n'
# 遍历事业部1的用户列表，形成其匹配特征
CERT52_Part1_MatchFeats = []
CERT52_Part2_MatchFeats = []
for usr in CERT52_Part_1:
    # 定位其离职用户列表
    Usr_Index = 10000 #一个非常大的数，表明不具有实际意义
    i = 0
    while i < len(f_Leave_lst):
        # CERT5.2 Leave Company Relationships Users for all Users
        # MMK1532,No:
        # Insider_LaidOff_0,
        # Insider_LaidOff_1,WMH1300,JRC1963,BAR1328,RDP1751,DAS1320,HKK0881,CEW1960,ILG0879,DEO1964,SMS0432,VSB1317,
        # Insider_LaidOff_2,CBC1504,JSB0860,KDP1706,FKH0864,RKW1936,BMR0865,SCO1719,ZJN1492,SAF1942,CHP1711,NAO1281,REF1924,JDJ1949,YBH1926,SNK1280,IAJ1729,DCA0857,LKC0405,VAH1292,TMT0851,JIP1503,
        # Insider_LaidOff_3,JAT1218,ADL1898,KSW0708,LAS0256,GWO1660,MIB1265,TCP0380,CDO0684,CDG0770,CLL0306,QSG1150,QAP0266,OCW1127,PKS1187,GER0350,BSS0847,OCD1985,MPF0690,USM0703,RFP1918,FKS1696,CRD0272,AWW0718,EJO0236,ESP1198,MMR1458,JIB1258,ZIE0741,DTB0722,EPG1196,DMP0344,MDS0680,CNM0787,NBL1190,OSS1463,ALT1465,WHG1669,WFV0687,STH0353,RPJ1159,JKB0287,DNJ0740,ELM1123,DXF1662,SCI0778,ISW0738,AYG1697,LMW0837,ICB1890,NTG1667,PCK0271,DHR1157,ZVW1475,BRG0728,HPM0360,ACA1126,KJG1121,JOE1672,UKM0845,KVF1143,DCC1119,JDB1163,NEG0281,FZG0389,MGB1235,KHW0289,VRP0267,CAB1189,JAL0811,AMS1236,ALW0764,CQR1172,EGM1222,AMB0745,MBW1149,WHB1247,XBK0246,ZEH0685,JRB0759,JUP1472,WWW0701,HJO0779,DCV1185,KMO0382,CWW1120,HSN0675,DJH0253,
        # Insider_LaidOff_4,
        line_lst = f_Leave_lst[i].strip('\n').strip(',').split(',')
        if len(line_lst[0]) != 7:
            i += 1
            continue
        if usr not in line_lst[0]:
            i += 1
            continue
        Usr_Index = i
        break
    if Usr_Index == 10000:
        print '离职数据定位失败，退出\n'
        sys.exit()
    leave_lst = [[] for i in range(5)]
    j = 1
    while j < 6:
        for ele in f_Leave_lst[Usr_Index + j].strip('\n').strip(',').split(',')[1:]:
            leave_lst[j - 1].append(ele)
        j += 1
    print usr, '离职列表统计完毕...\n'

    print '..<<开始提取邮件联系人列表>>..\n\n'
    email_contacts = [0.0 for i in range(4)]
    for file in os.listdir(Email_Dir):
        if usr in file and 'feats' in file:
            # 定位到了用户对应的邮件特征表
            shutil.copy(Email_Dir + '\\' + file, Analyze_Dir + '\\' + file)
            f_0 = open(Analyze_Dir + '\\' + file, 'r')
            f_0_lst = f_0.readlines()
            f_0.close()
            # JLF1315,-0.130434782609,10.0,222931.8,0.5,13.0,390778.153846,0.538461538462,
            for feat in f_0_lst:
                feat_lst = feat.strip('\n').strip(',').split(',')
                if feat_lst[0] not in CERT52_Part_1:
                    continue
                k = 0
                while k < 4:
                    if feat_lst[0] in leave_lst[k]:
                        # 该用户是离职的联系人
                        email_contacts[k] += 1
                        break
                    else:
                        k += 1
    #tmp_0 = []
    #tmp_0.append(usr)
    #tmp_0.append(email_contacts)
    CERT52_Part1_MatchFeats.append(email_contacts)
    print '处理完毕： ', usr, email_contacts, '\n\n'
    print usr, '分析完毕\n\n'
print '....<<<<用户离职与联系人匹配特征提取完毕>>>>....\n\n'


print '....<<<<将得到的用户分析结果写入文件>>>>....\n\n'
f_1 = open('0.4-CERT5.2_Part1_Leave-Match-Contacts.csv', 'w')
i = 0
while i < len(CERT52_Part_1):
    f_1.write(CERT52_Part_1[i])
    f_1.write(',')
    for ele in CERT52_Part1_MatchFeats[i]:
        f_1.write(str(ele))
        f_1.write(',')
    f_1.write('\n')
    i += 1
f_1.close()


print '....<<<<将匹配特征标准化输出保存>>>>....\n\n'
f_2 = open('0.4-CERT5.2_Part1_All-LMC_scale.csv', 'w')
CERT52_Part1_MatchFeats_array = np.array(CERT52_Part1_MatchFeats)
CERT52_Part1_MatchFeats = skp.scale(CERT52_Part1_MatchFeats_array)
i = 0
while i < len(CERT52_Part_1):
    f_2.write(CERT52_Part_1[i])
    f_2.write(',')
    for ele in CERT52_Part1_MatchFeats[i]:
        f_2.write(str(ele))
        f_2.write(',')
    f_2.write('\n')
    i += 1
f_1.close()


print '输出场景二的匹配特征...\n\n'
Insiders_2 = Get_Insiders(os.path.dirname(sys.path[0]), 2)
Index1_Insiders_2 = []
for usr in CERT52_Part_1:
    if usr in Insiders_2:
        Index1_Insiders_2.append(CERT52_Part_1.index(usr))
for num in Index1_Insiders_2:
    print CERT52_Part_1[num], ':', CERT52_Part1_MatchFeats[num], '\n'


sys.exit()



























