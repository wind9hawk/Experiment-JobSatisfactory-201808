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

# 定义一个函数用来计算用户发送/收到邮件的通信比
def Cal_EmailRatio(X, Y):
    ER_0 = float(X - Y)
    ER_1 = float(X + Y)
    return ER_0 / ER_1


# 见原先的邮件特征模块变成函数调用
def Extract_Email_Feat(user_id, leave_users_month, emails_path, dst_dir, month, have_left_users_month_lst):

    # 提取的邮件特征为截止到当前月month的邮件通信

    print user_id, '......<<<<<<CERT5.2用户邮件通讯9元特征提取开始>>>>>>......\n\n'

    #print '..<<指定原始邮件数据源>>..\n\n'
    # 存放原始的用户邮件通讯记录
    # 该数据源包含全部CERT5.2用户，没有根据离职进行更新
    Email_Dir = r'G:\GitHub\Essay-Experiments\CERT5.2-Results\CERT5.2-Users-EmailRecords'
    # 存放我们提取特征的目录，就在程序目录下
    Email_Feats_Dir = dst_dir + '\\' + 'CERT5.2_Users_EmailFeats-0.7'
    if os.path.exists(Email_Feats_Dir) == False:
        os.makedirs(Email_Feats_Dir)

    print '....<<<<建立用户ID与邮箱名映射字典>>>>.....\n\n'
    f_2009 = open(os.path.dirname(sys.path[0]) + '\\' + 'LDAP' + '\\' + '2009-12.csv', 'r')
    f_2009_lst = f_2009.readlines()
    f_2009.close()
    Email2User_Dic = Email2UserID(f_2009_lst)
    #print Email2User_Dic, '\n'

    #f_user_contacts = open(Email_Feats_Dir + '\\' + user_id + '_email_contacts.csv', 'w')
    #f_0 = open(Email_Feats_Dir + '\\' + user_id + '_leave_efeats.csv', 'w')


    print '....<<<<数据源确定完毕，开始循环分析该用户在该月的邮件特征>>>>....\n\n'

    # 首先建立该用户的特征文件与邮件通讯联系人文件
    for file in os.listdir(Email_Dir):
        Email_Feats_User = []
        # 得到了原始数据目录下所有的文件列表
        # 只读取原始数据文件，like: AAB1302.csv
        if 'feat' in file:
            # print '错误的feat文件..\n'
            continue
        # 确定是否要分析的用户的邮件数据
        # 目录下文件名格式为：CRM0907.csv
        target_user = file[:7]
        if target_user != user_id:
            #print target_user, user_id, '\n'
            # sys.exit()
            continue
            #sys.exit()
        #if target_user not in leave_users_month:
        #    print target_user, '当月未离职，跳过...\n'
        #    continue
        # 为该用户建立特征列表
        email_feat = []
        # 为该用户建立离职邮件联系人列表
        send_users = [] # Target_User发给的离职联系人
        recv_users = [] # target_user接收到离职邮件源
        # 分别建立用户的发送/接收邮件人列表（包括离职与未离职）
        send_users_month = []
        recv_users_month = []
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
        print '读入用户邮件数据示例：', '\n'
        print user_id, f_email_lst[0], '\n'

        for line in f_email_lst:
            line_lst = line.strip('\n').strip(',').split(',')
            #if line_lst[1] != user_id:
            #    print '要分析', user_id, '当前却是：', line_lst[1], '\n'
            #    continue
            # 获取当前邮件时间
            date = GetDate(line_lst[0])
            # 2010-02-12
            date_0 = float(date[:4]) * 10000 + float(date[5:7]) * 100
            date_1 = float(month[:4]) * 10000 + float(month[5:7]) * 100
            # print month, date_0, date_1, '\n'
            #sys.exit()
            if date_0 > date_1:
                print '邮件事件超过分析月份：', date_0, '>', date_1, '\n'
                break
            # 判断是发送邮件还是接收邮件
            # 当前数据格式：date,user,pc,to,cc,bcc,from,activity,size,attachments
            # 作为send邮件，需要同时考虑邮件的收件人to，抄送cc，以及密送bcc
            if line_lst[7] == 'Send':
                # 提取与离职邮件联系人的发送关系
                # user_id_lst中仅统计离职联系人关系
                user_id_lst = []
                for ele in line_lst[3].split(';'):
                    if '@dtaa.com' not in ele:
                        # 非组织雇员
                        # 仅加入到send_users_month中
                        if ele not in send_users_month and len(ele) > 0:
                            send_users_month.append(ele)
                            continue
                    else:
                        # 组织内员工
                        if Email2User_Dic[ele] not in leave_users_month:
                            if Email2User_Dic[ele] not in send_users_month:
                                send_users_month.append(Email2User_Dic[ele])
                                continue
                        else:
                            user_id_lst.append(Email2User_Dic[ele])
                            continue
                for ele in line_lst[4].split(';'):
                    if '@dtaa.com' not in ele:
                        # 非组织雇员
                        # 仅加入到send_users_month中
                        if ele not in send_users_month and len(ele) > 0:
                            send_users_month.append(ele)
                            continue
                    else:
                        # 组织内员工
                        if Email2User_Dic[ele] not in leave_users_month:
                            if Email2User_Dic[ele] not in send_users_month:
                                send_users_month.append(Email2User_Dic[ele])
                                continue
                        else:
                            user_id_lst.append(Email2User_Dic[ele])
                            continue
                for ele in line_lst[5].split(';'):
                    if '@dtaa.com' not in ele:
                        # 非组织雇员
                        # 仅加入到send_users_month中
                        if ele not in send_users_month and len(ele) > 0:
                            send_users_month.append(ele)
                            continue
                    else:
                        # 组织内员工
                        if Email2User_Dic[ele] not in leave_users_month:
                            if Email2User_Dic[ele] not in send_users_month:
                                send_users_month.append(Email2User_Dic[ele])
                                continue
                        else:
                            user_id_lst.append(Email2User_Dic[ele])
                            continue
                # 这是一封发送邮件
                # 对方以前联系过么？
                # 当月的离职邮件联系人send_users/recv_users
                # 当月的非离职邮件联系人：send_users_month/recv_users_month
                for ele in user_id_lst:
                    if len(ele) != 7:
                        # 非组织成员
                        # 无法分析OCEAN信息，故跳过
                        continue
                    if ele not in send_users:
                        # 第一次发邮件
                        # 初始化对应于该收件人的邮件特征
                        send_users.append(ele)
                        cnt_send = 1.0
                        send_days = []
                        send_days.append(date)
                        cnt_size = float(line_lst[8])
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
                        print '第一次联系用户', ele, '初始化特征为： ', send_feat_0, '\n\n'
                        # sys.exit() # 验证通过
                    else:
                        # 已经不是第一次联系该用户了
                        # 需要定位后，更新原始特征数据即可
                        # # 当前数据格式：date,user,pc,to,cc,bcc,from,activity,size,attachments
                        index_0 = send_users.index(ele)
                        send_feat[index_0][0] += 1.0
                        if date not in send_feat[index_0][1]:
                            send_feat[index_0][1].append(date)
                        send_feat[index_0][2] += float(line_lst[8])
                        if len(line_lst) == 10:
                            send_feat[index_0][3] += len(line_lst[9].split(';'))
                        else:
                            send_feat[index_0][3] += 0.0
                        print '再次联系用户', ele, '此时特征为： ', send_feat[index_0], '\n\n'
            else:
                if line_lst[7] == 'Receive':
                    # # # 当前数据格式：date,user,pc,to,cc,bcc,from,activity,size,attachments
                    # 这是一封收到的邮件
                    # 提取用户ID
                    # 需要注意
                    # send行为时目标用户一定在line[6]字段中
                    # receive行为记录中包括目标用户与其他用户都在receiver的情况，即只分析收件人为目标用户的情况
                    print '开始分析用户', target_user, ' 的收取邮件情况...\n'
                    recv_user_id = []
                    # 这里只想验证收件人中是否有目标用户，没有就不用分析该条记录了
                    for ele in line_lst[3].split(';'):
                        if '@dtaa.com' not in ele:
                            # 仅提取离职联系人的邮件通信特征，一般联系人不提取特征
                            continue
                        else:
                            if Email2User_Dic[ele] not in recv_user_id:
                                recv_user_id.append(Email2User_Dic[ele])
                                continue
                    for ele in line_lst[4].split(';'): # cc
                        if '@dtaa.com' not in ele:
                            # 仅提取离职联系人的邮件通信特征，一般联系人不提取特征
                            continue
                        else:
                            if Email2User_Dic[ele] not in recv_user_id:
                                recv_user_id.append(Email2User_Dic[ele])
                                continue
                    for ele in line_lst[5].split(';'): # bcc
                        if '@dtaa.com' not in ele:
                            continue
                        else:
                            if Email2User_Dic[ele] not in recv_user_id:
                                recv_user_id.append(Email2User_Dic[ele])
                                continue
                    if target_user not in recv_user_id:
                        # 默认时邮件名，需要转换成user_id才能和target_user比较
                        print target_user, '邮件收件人中不存在目标用户，不考虑\n'
                        continue
                    # user_id_lst才是我们要提取计算leave_feat的用户列表
                    user_id_lst = []
                    for ele in line_lst[6].split(';'):
                        if '@dtaa.com' not in ele:
                            # 非雇员
                            if ele not in recv_users_month:
                                recv_users_month.append(ele)
                                continue
                        else:
                            if Email2User_Dic[ele] not in leave_users_month:
                                if Email2User_Dic[ele] not in recv_users_month:
                                    recv_users_month.append(Email2User_Dic[ele])
                            else:
                                user_id_lst.append(Email2User_Dic[ele])
                                continue
                            # sys.exit()
                    # 这是一封接收邮件
                    # 对方给自己发过邮件吗？
                    print '接下来要分析的最终发件人列表是： ', user_id_lst, '\n'
                    #print 'line is ',line_lst, '\n'
                    for ele in user_id_lst:
                        if ele not in recv_users:
                            # 第一次收到该人邮件
                            # 初始化对应于该收件人的邮件特征
                            recv_users.append(ele)
                            cnt_recv = 1.0
                            recv_days = []
                            recv_days.append(date)
                            print ele, 'recv_days is ', recv_days, '\n'
                            # sys.exit()
                            cnt_size = float(line_lst[8])
                            if len(line_lst) == 10:
                                cnt_attach = len(line_lst[9].split(';'))
                            else:
                                cnt_attach = 0.0
                            recv_feat_0 = []
                            recv_feat_0.append(cnt_recv)
                            recv_feat_0.append(recv_days)
                            recv_feat_0.append(cnt_size)
                            recv_feat_0.append(cnt_attach)
                            recv_feat.append(recv_feat_0)
                            print '第一次收到用户', ele, '的来新，初始化特征为： ', recv_feat_0, '\n\n'
                            # sys.exit()
                            # sys.exit() # 验证通过
                        else:
                            # 已经不是第一次联系该用户了
                            # 需要定位后，更新原始特征数据即可
                            # # 当前数据格式：date,user,pc,to,cc,bcc,from,activity,size,attachments
                            index_0 = recv_users.index(ele)
                            recv_feat[index_0][0] += 1.0
                            if date not in recv_feat[index_0][1]:
                                recv_feat[index_0][1].append(date)
                            recv_feat[index_0][2] += float(line_lst[8])
                            if len(line_lst) == 10:
                                recv_feat[index_0][3] += len(line_lst[9].split(';'))
                            else:
                                recv_feat[index_0][3] += 0.0
                            print '再次收到用户', ele, '的来信，此时特征为： ', recv_feat[index_0], '\n\n'
                            # sys.exit()
                            # 上述验证以用户AAB为例通过
                            #

        # 在保存结果的同时将该用户的邮件联系人列表保存
        f_user_contacts = open(Email_Feats_Dir + '\\' + user_id + '_email_contacts.csv', 'w')
        f_user_contacts.write('Send Contacts:\n')
        for contact in send_users_month:
            f_user_contacts.write(contact)
            f_user_contacts.write('\n')
        f_user_contacts.write('Recv Contacts:\n')
        for contact in recv_users_month:
            f_user_contacts.write(contact)
            f_user_contacts.write('\n')
        f_user_contacts.close()
        print user_id, month, '邮件联系人列表统计完成..\n\n'


        # target_user的邮件收件人与发件人关系特征已经统计完毕，接下来需要拼接生成需要的特征
        # 依次从send_users，recv_users中交叉匹配，以确定最终的用户特征
        print '开始组合形成', user_id, ' 的邮件行为特征...\n\n'
        # 首先从send_users中匹配
        # 特征构建时，将发送/接收天数的分隔符转换为';'
        for sender in send_users:
            if sender in recv_users:
                # 说明该用户同时具有发送与接收邮件
                # 计算ER比
                # 确定用户对应的发送/接收特征
                send_feat_1 = send_feat[send_users.index(sender)]
                recv_feat_1 = recv_feat[recv_users.index(sender)]
                #print 'send_feat_1 is ', send_feat_1, '\n'
                #print 'recv_feat_1 is ', recv_feat_1, '\n'
                # sys.exit()
                email_feat = []
                er = Cal_EmailRatio(send_feat_1[0], recv_feat_1[0])
                # user_id, er, cnt_send, cnt_send_day, cnt_size, cnt_attach, cnt_recv, cnt_recv_day, cnt_size, cnt_attach
                email_feat.append(sender)
                email_feat.append(er)
                for ele in send_feat_1:
                    email_feat.append(ele)
                for ele in recv_feat_1:
                    email_feat.append(ele)
                #print 'email_feat[7] is ', email_feat[7], '\n'
                #print 'email_feat is ', email_feat, '\n'
                # sys.exit()
                email_feat[4] = email_feat[4] / email_feat[2]
                email_feat[8] = email_feat[8] / email_feat[6]
                #print 'email_feat[3] is :', email_feat[3], '\n'
                email_feat[3] = str(email_feat[3]).replace(',', ';').replace('\'', '')
                email_feat[7] = str(email_feat[7]).replace(',', ';').replace('\'', '')
                # Email_Feats_User.append(email_feat)
                # 这里追加元素应该是email_feat[]。而不应该是line[]
                #email_feat.append(len(email_feat[3].split(';')))
                #email_feat.append(len(email_feat[7].split(';')))
                #print '同时发送接收的邮件联系人', sender, '特征提取完毕, 其邮件特征为：', email_feat, '\n'
                Email_Feats_User.append(email_feat)
                # print '0:', Email_Feats_User, '\n'
                # sys.exit()
            # 再来构造仅发送用户的邮件特征
            else:
                send_feat_1 = send_feat[send_users.index(sender)]
                # recv_feat_1 = recv_feat[recv_users.index(sender)]
                recv_feat_1 = [0,[],0,0]
                email_feat = []
                er = Cal_EmailRatio(send_feat_1[0], recv_feat_1[0])
                #print 'send_users like: ', send_users[:10], '\n'
                #print '仅发送联系人：', sender, '\n'
                #print 'senders中空用户的位置：', send_users.index(sender), '\n'
                #print '对应的发送特征为： ', send_feat_1, '\n'
                #sys.exit()
                email_feat.append(sender)
                email_feat.append(er)
                for ele in send_feat_1:
                    email_feat.append(ele)
                for ele in recv_feat_1:
                    email_feat.append(ele)
                email_feat[4] = email_feat[4] / email_feat[2]
                # email_feat[7] = email_feat[8] / email_feat[6]
                email_feat[3] = str(email_feat[3]).replace(',', ';').replace('\'', '')
                email_feat[7] = str(email_feat[7]).replace(',', ';').replace('\'', '')
                Email_Feats_User.append(email_feat)
                #print '仅发送的邮件联系人', sender, '特征提取完毕, 其邮件特征为：', email_feat, '\n'
                # print '1:', Email_Feats_User, '\n'
        # 最后来考虑仅接收的联系人
        for recver in recv_users:
            if recver in send_users: # 上面已经分析过
                #print '已经分析过同时收发的用户', recver, '跳过...\n\n'
                continue
            else:
                # 仅接收的用户
                # send_feat_1 = send_feat[send_users.index(sender)]
                recv_feat_1 = recv_feat[recv_users.index(recver)]
                send_feat_1 = [0, [], 0, 0]
                email_feat = []
                er = Cal_EmailRatio(send_feat_1[0], recv_feat_1[0])
                email_feat.append(recver)
                email_feat.append(er)
                for ele in send_feat_1:
                    email_feat.append(ele)
                for ele in recv_feat_1:
                    email_feat.append(ele)
                # email_feat[4] = email_feat[4] / email_feat[2]
                email_feat[8] = email_feat[8] / email_feat[6]
                email_feat[3] = str(email_feat[3]).replace(',', ';').replace('\'', '')
                email_feat[7] = str(email_feat[7]).replace(',', ';').replace('\'', '')
                Email_Feats_User.append(email_feat)
                #print '仅发送的邮件联系人', recver, '特征提取完毕, 其邮件特征为：', email_feat, '\n'
        print '目标用户', target_user, '的验证用例显示： 第一个联系人数据： ', '\n'
        print Email_Feats_User, '\n'
        #print Email_Feats_User[1], '\n'
        # sys.exit()


        # 验证通过
        print '....<<<<将得到的用户邮件特征写入到文件>>>>....\n\n'
        f_0 = open(Email_Feats_Dir + '\\' + user_id + '_leave_efeats.csv', 'w')
        # RMB1821,1.0,10.0,[2010-01-13; 2010-01-21; 2010-01-25; 2010-01-26; 2010-01-28; 2010-02-08; 2010-02-09],462898.5,5.0,0,[],0,0,7,1
        # [WMH1300,1.0,2.0,[2010-01-04; 2010-01-30],26533.5,0.0,0,[],0,0,2,1]
        # 第一行应为特征字段说明
        f_0.write('contact_user_id')
        f_0.write(',')
        f_0.write('Email_Ratio')
        f_0.write(',')
        f_0.write('Cnt_Send')
        f_0.write(',')
        f_0.write('Send_Days')
        f_0.write(',')
        f_0.write('Avg_Send_Size')
        f_0.write(',')
        f_0.write('Avg_Send_Attach')
        f_0.write(',')
        f_0.write('Cent_Recv')
        f_0.write(',')
        f_0.write('Recv_Days')
        f_0.write(',')
        f_0.write('Avg_Recv_Size')
        f_0.write(',')
        f_0.write('Avg_Recv_Attach')
        f_0.write(',')
        f_0.write('Cnt_Send_Days')
        f_0.write(',')
        f_0.write('Cnt_Recv_Days')
        f_0.write('\n')
        for line in Email_Feats_User:
            for ele in line:
                f_0.write(str(ele))
                f_0.write(',')
            if len(line[3].strip('[').strip(']')) == 0:
                line.append('0')
            else:
                line.append(len(line[3].strip('[').strip(']').split(';')))
            # 注意！
            # len([].split(';'))的结果永远为1！
            # 因此需要事先判断是否为空！
            f_0.write(str(line[-1]))
            f_0.write(',')
            if len(line[7].strip('[').strip(']')) == 0:
                line.append('0')
            else:
                line.append(len(line[7].strip('[').strip(']').split(';')))
            f_0.write(str(line[-1]))
            f_0.write('\n')
        f_0.close()
        print '写入的邮件特征文件为： user_id is ',user_id, '\n'
        print '....<<<<', target_user, '邮件联系特征文件写入完毕....>>>>\n\n'

        #if user_id == ' AAB1302':
        #    print '调试暂停中止...\n\n'
        #    print user_id, ':', target_user, '\n'
        #    print 'send_users is ', send_users, '\n'
        #    print 'recv_users is ', recv_users, '\n'
        return Email_Feats_User








