# coding:utf-8
# 今日主要工作都在修正以前的程序错误，可谓令人后悔！凡今后编程代码，务必实现模块化+阶段性案例验证，以确保程序结果的准确性

# 本程序主要用于两项工作：
# 1. 从原始的CERT5.2的邮件数据中，分析、梳理邮件联系通讯的特征；
# 2. 形成每个用户一张独特的邮件联系表，该表中应包含以下9个关键特征：
# 2.1 邮件通信比：(X-Y) / (X + Y)，单纯发送关系为1，单纯接收关系为-1，其他为[-1, 1]之间，0表示均衡
# 2.2 发送的邮件总数 + 发送邮件行为的总天数 + 发送的邮件总字数 + 发送邮件带的总附件数
# 2.3 接收的邮件总数 + 接收邮件行为的总天数 + 接收的邮件总字数 + 接收邮件带的总附件书
# 3. 为每个用户输出一张类似的邮件联系特征标，即为我们的本程序目标

import os, sys
import numpy as np
import shutil
import math

# 模块化编程
# 案例阶段性验证

# 定义一个用户ID与邮箱名转换的函数，返回一个映射字典
def Email2UserID(Match_lst):
    # email参数表示要映射的邮箱名（去掉@后面的部分）
    # Match_lst表示原始的用户ID与邮箱名的匹配关系的原始文件行
    # 需要考虑如果联系人不是企业内部的用户，则需要按照原始记录邮件名称
    # 可以使用@dtaa.com来识别雇员与非雇员邮箱
    match_dic = {}
    for line in Match_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        # Data like: employee_name,user_id,email,role,projects,business_unit,functional_unit,department,team,supervisor
        # 因为只考虑user_id与email，不需要考虑LDAP
        match_dic[line_lst[2]] = line_lst[1]
    return match_dic

# 定义一个提取时间的函数，具体到日子
def GetDate(date):
    # like: 01/02/2010 09:03:11
    year = date[6:10]
    month = date[:2]
    day = date[3:5]
    return year + '-' + month + '-' + day


print '......<<<<<<CERT5.2用户邮件通讯9元特征提取开始>>>>>>......\n\n'

print '..<<指定原始邮件数据源>>..\n\n'
# 存放原始的用户邮件通讯记录
Email_Dir = r'G:\GitHub\Essay-Experiments\CERT5.2-Results\CERT5.2-Users-EmailRecords'
# 存放我们提取特征的目录，就在程序目录下
Email_Feats_Dir = sys.path[0] + '\\' + 'CERT5.2_Users_EmailFeats-0.6'
if os.path.exists(Email_Feats_Dir) == False:
    os.makedirs(Email_Feats_Dir)

print '....<<<<建立用户ID与邮箱名映射字典>>>>.....\n\n'
f_2009 = open(os.path.dirname(sys.path[0]) + '\\' + 'LDAP' + '\\' + '2009-12.csv', 'r')
f_2009_lst = f_2009.readlines()
f_2009.close()
Email2User_Dic = Email2UserID(f_2009_lst)
print Email2User_Dic, '\n'


print '....<<<<数据源确定完毕，开始循环分析每个用户的邮件特征>>>>....\n\n'

for file in os.listdir(Email_Dir)[:2]:
    # 得到了原始数据目录下所有的文件列表
    # 只读取原始数据文件，like: AAB1302.csv
    if 'feat' in file:
        print '错误的feat文件..\n'
        continue
    # 确定了要分析的用户ID
    target_user = file[:7]
    # 为该用户建立特征列表
    email_feat = []
    # 为该用户建立邮件联系人列表
    send_users = [] # Target_User发给的联系人
    recv_users = [] # target_user接收到邮件源
    # 分别建立发送与接收子特征
    send_feat = []
    recv_feat = []

    # 邮件数据样例
    # like: 01/02/2010 11:00:02,AAB1302,PC-5565,Ruby.Blair.Alexander@dtaa.com,,,Allen.Ashton.Buckley@dtaa.com,Send,23014,
    # # 当前数据格式：date,user,pc,to,cc,bcc,from,activity,size,attachments
    # 需要判断attachments是否存在，会影响后续位置
    print '读入目标用户', target_user, '邮件数据..\n'
    f_email = open(Email_Dir + '\\' + file, 'r')
    f_email_lst = f_email.readlines()
    f_email.close()

    for line in f_email_lst[:53]:
        line_lst = line.strip('\n').strip(',').split(',')
        # 获取当前邮件时间
        date = GetDate(line_lst[0])
        # 判断是发送邮件还是接收邮件
        if line_lst[7] == 'Send':
            # 提取用户ID
            user_id_lst = []
            for ele in line_lst[3].split(';'):
                if '@dtaa.com' not in ele:
                    # 非雇员
                    user_id_lst.append(ele)
                else:
                    user_id_lst.append(Email2User_Dic[ele])
            # 这是一封发送邮件
            # 对方以前联系过么？
            for user_id in user_id_lst:
                if user_id not in send_users:
                    # 第一次发邮件
                    # 初始化对应于该收件人的邮件特征
                    send_users.append(user_id)
                    cnt_send = 1.0
                    send_days = []
                    send_days.append(date)
                    cnt_size = line_lst[8]
                    if len(line_lst) == 10:
                        cnt_attach = len(line_lst[9].split(';'))
                    else:
                        cnt_attach = 0.0
                    send_feat_0 = []
                    send_feat_0.append(cnt_send)
                    send_feat_0.append(send_days)
                    send_feat_0.append(cnt_size)
                    send_feat_0.append(cnt_attach)
                    send_feat.append(send_feat_0)
                    print '第一次联系用户', user_id, '初始化特征为： ', send_feat_0, '\n\n'
                    # sys.exit() # 验证通过
                else:
                    # 已经不是第一次联系该用户了
                    # 需要定位后，更新原始特征数据即可
                    # # 当前数据格式：date,user,pc,to,cc,bcc,from,activity,size,attachments
                    index_0 = send_users.index(user_id)
                    send_feat[index_0][0] += 1.0
                    if date not in send_feat[index_0][1]:
                        send_feat[index_0][1].append(date)
                    send_feat[index_0][2] += line_lst[8]
                    if len(line_lst) == 10:
                        send_feat[index_0][3] += len(line_lst[9].split(';'))
                    else:
                        send_feat[index_0][3] += 0.0
                    print '再次联系用户', user_id, '此时特征为： ', send_feat[index_0], '\n\n'
        else:
            if line_lst[7] == 'Receive':
                # 这是一封收到的邮件
                continue


