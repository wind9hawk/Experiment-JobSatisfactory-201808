# coding:utf-8
# 这是一个邮件过滤程序
# 过滤的目标有两个：
# 1. 由于我们分析的是反映亲密关系的邮件通讯，因此需要过滤掉群发性质的工作通知邮件，即只关注一个收件人的邮件；
# 2. 为每个用户建立一个最终的邮件通讯特征表，该表中应当具有七元基本特征：
# 2.1 信息发送接收比例；
# 2.2 发送邮件总数；
# 2.3 发送邮件字数平均大小；
# 2.4 发送邮件平均附件个数；
# 2.5 接收邮件总数；
# 2.6 接收邮件字数平均大小；
# 2.7 接收邮件平均附件个数；

# 基本步骤
# Step-1: 为每一个用户而言，统计其需要分析的所有邮件文件路径列表；
# Step-2： 依次遍历读入所有的邮件数据，聚合成该用户的一个单一邮件文件Email-UserID.csv
# Step-3： 针对读入的邮件数据文件，对于每个通讯用户进行遍历：
# Step-3.1: 如果收件人超过1个，则跳过；
# Step-3.2： 如果是要比对的用户邮件通讯，记录六元特征，最后计算通讯发送接收比；
# Step-4. 将得到的用户七元特征写入到CERT5.2-Insider_2-Email7Features.csv

import os,sys




print '......<<<<<<首先建立CERT5.2数据集中用户ID与邮件的对应关系>>>>>......\n\n'
# G:\GitHub\Essay-Experiments\Experiment-JobSatisfactory-201808\LDAP
# employee_name,user_id,email,role,projects,business_unit,functional_unit,department,team,supervisor
# Maisie Maggy Kline,MMK1532,Maisie.Maggy.Kline@dtaa.com
LDAPPath = os.path.dirname(sys.path[0]) + '\\' + 'LDAP' + '\\' + '2009-12.csv'
User2Email = [] # 用于存放提取的user_id, user_name, email_name信息
Users = [] # 用于存放与User2Email顺序一致的user_name列表，以供后续比较检索索引号
f = open(LDAPPath, 'r')
f_lst = f.readlines()
f.close()
for line in f_lst:
    line_lst = line.strip('\n').strip(',').split(',')
    if line_lst[1] == 'user_id':
        continue
    index_0 = line_lst[2].index('@')  # 邮箱地址中@符号的位置
    Users.append(line_lst[2][:index_0])
    user2email = []
    user2email.append(line_lst[1])
    user2email.append(line_lst[0])
    user2email.append(line_lst[2][:index_0])
    # 最后记录的对应表是 [MMK1532,Maisie Maggy Kline,Maisie.Maggy.Kline]
    # 之所以如此，是因为邮箱@后的地址可以根据是否在单位内部改变，而姓名是不变的
    User2Email.append(user2email)
print '用户ID与邮箱对应关系提取完毕...\t', len(User2Email), '\n'
for i in range(10):
    print User2Email[i], '\n'
print '......<<<<<<CERT5.2数据集中用户ID与邮件的对应关系建立完毕>>>>>......\n\n'
#sys.exit()




print '......<<<<<<分析CERT5.2特定用户的邮件通信数据，并生成7元邮件统计特征>>>>>>......\n\n'


# 指定用户邮件数据根目录
RootDir = r'G:\GitHub\Essay-Experiments\CERT5.2-Results'
UsersDir = RootDir + '\\' + 'CERT5.2-Insider_2-Records'
EmailDir = RootDir + '\\' + 'CERT5.2-Insiders_2-EmailRecords'

for user in os.listdir(UsersDir)[:]:
    print '....<<<<<首先读取', user, ' 的所有邮件通讯数据>>>>....\n\n'
    if os.path.exists(EmailDir) == False:
        os.makedirs(EmailDir)
    f_eml = open(EmailDir + '\\' + user + '.csv', 'w') # 用来存储user的所有邮件通信记录
    f_eml_feats = open(EmailDir + '\\' + user + '-feats.csv', 'w') # 用来存储该用户的通讯特征
    f_eml_lst = []
    for month in os.listdir(UsersDir + '\\' + user):
        for day in os.listdir(UsersDir + '\\' + user + '\\' + month):
            EmailPath = UsersDir + '\\' + user + '\\' + month + '\\' + day + '\\' + 'Email.csv'
            if os.path.exists(EmailPath) == False:  # 没有email文件则跳过
                continue
            f_eml_tmp = open(EmailPath, 'r')
            # 01/04/2010 08:03:00,BYO1846,PC-8402,Germane_Velez@bellsouth.net;Olympia.N.Bonner@cox.net,Jemima-Pratt@msn.com;Buffy_Ortiz@bellsouth.net,,Hannah_M_Callahan@msn.com,Receive,17835,,
            # 01/04/2010 08:03:00,BYO1846,PC-8402,Rebekah_Santos@verizon.net;Buffy_Ortiz@bellsouth.net,,,Eugenia.S.Mercado@juno.com,Receive,36078,,
            f_eml_tmp_lst = f_eml_tmp.readlines()
            f_eml_tmp.close()

            for line in f_eml_tmp_lst:
                line_lst = line.strip('\n').strip(',').split(',')
                # 源数据格式：id,date,user,pc,to,cc,bcc,from,activity,size,attachments,content
                # 当前数据格式：date,user,pc,to,cc,bcc,from,activity,size,attachments
                # line_tmp = []
                #for ele in line_lst:
                #    line_tmp.append(ele)
                f_eml_lst.append(line_lst)
            print user, day, 'Email读入完毕..\n'
            continue
        print user, month, 'Email读入完毕...\n\n'
        continue
    for i in range(20):
        print f_eml_lst[i], '\n'
    print '邮件内容写入到文件...\n\n'
    for line in f_eml_lst:
        for ele in line:
            f_eml.write(ele)
            f_eml.write(',')
        f_eml.write('\n')
    f_eml.close()
    #sys.exit()

    print '......<<<<<<开始准备提取计算想要的用户邮件7元特征>>>>>>......\n\n'
    print '首先统计用户的有效邮件通信列表...\n'

    # 基本步骤
    # 争取一次遍历，即完成邮件通讯行为的特征提取工作
    # 为发送与接收邮件分别建立用户列表与对应的邮件特征：通讯发送接收比，发送邮件数量，平均大小，平均附件个数以及接收邮件的类似三元特征
    Send_Users = [] ## 成对的 用户列表与对应的通讯行为特征
    Send_Feats = []
    Recv_Users = []
    Recv_Feats = []

    print '....<<<<一次遍历，全部特征提取完毕>>>>....\n\n'
    for line in f_eml_lst:
        # 已经是字符串列表了，不需要再分割转换一次
        # 源数据格式：id,date,user,pc,to,cc,bcc,from,activity,size,attachments,content
        # 当前数据格式：date,user,pc,to,cc,bcc,from,activity,size,attachments
        # 首先判断用户是否已经建立了对应的列表
        # 区分发送与接收
        # 首先过滤掉群发邮件与群收邮件
        if len(line[3].split(';')) > 1 or len(line[6].split(';')) > 1:
            print '群发/群收邮件，跳过...\n'
            continue
        if line[-2] == 'Send':
            # 04/07/2010 13:52:21,HMS1658,PC-2691,Hasad.Jason.Leon@dtaa.com,,,Hedda.Melissa.Slater@dtaa.com,Send,23957,,
            # 对于HMS1658而言，其没有附件属性，因而总体个数小于标准，send标志在[-2]位置
            # 06/04/2010 12:56:28,HMS1658,PC-2691,Melinda.Hilary.Mercer@dtaa.com,,,Hedda.Melissa.Slater@dtaa.com,Send,40710,,
            # 先判断用户是否已存在列表中，即对应的feat是否已建立？
            SendTo = line[3][:line[3].index('@')]
            if SendTo not in Send_Users:
                Send_Users.append(SendTo)
                # 建立其发送特征
                Send_Sum = 1.0
                Send_Avg_Size = float(line[-1])
                Send_Avg_Attach = 0.0
                send_feat = []
                send_feat.append(SendTo)
                send_feat.append(Send_Sum)
                send_feat.append(Send_Avg_Size)
                send_feat.append(Send_Avg_Attach)
                Send_Feats.append(send_feat)
                continue
            else:
                # 说明之前已经初始化针对该用户的发送特征，接下来需要更新部分特征参数
                # 定位
                Index_sender = Send_Users.index(SendTo)
                # 所以找到了要更新的Send_Feats中的位置
                Send_Feats[Index_sender][1] += 1.0
                Send_Feats[Index_sender][2] += float(line[-1])
                Send_Feats[Index_sender][3] += 0
        # 类似的建立对饮的Receive
        if line[-2] == 'Receive':
            # 先判断用户是否已存在列表中，即对应的feat是否已建立？
            RecvFrom = line[6][:line[6].index('@')]
            if RecvFrom not in Recv_Users:
                Recv_Users.append(RecvFrom)
                # 建立其接收特征
                Recv_Sum = 1.0
                Recv_Avg_Size = float(line[-1])
                Recv_Avg_Attach = 0.0
                recv_feat = []
                recv_feat.append(RecvFrom)
                recv_feat.append(Recv_Sum)
                recv_feat.append(Recv_Avg_Size)
                recv_feat.append(Recv_Avg_Attach)
                Recv_Feats.append(recv_feat)
                print user, 'receive email from ', RecvFrom, '分析完毕...\n\n'
                continue
            else:
                # 说明之前已经初始化针对该用户的接收特征，接下来需要更新部分特征参数
                # 定位
                Index_recv = Recv_Users.index(RecvFrom)
                # 所以找到了要更新的Recv_Feats中的位置
                Recv_Feats[Index_recv][1] += 1.0
                Recv_Feats[Index_recv][2] += float(line[-1])
                Recv_Feats[Index_recv][3] += 0.0
                print user, 'receive email from ', RecvFrom, '分析完毕...\n\n'
                continue
        if line[-3] == 'Send':
            # 04/07/2010 13:52:21,HMS1658,PC-2691,Hasad.Jason.Leon@dtaa.com,,,Hedda.Melissa.Slater@dtaa.com,Send,23957,,
            # 对于HMS1658而言，其没有附件属性，因而总体个数小于标准，send标志在[-2]位置
            # 06/04/2010 12:56:28,HMS1658,PC-2691,Melinda.Hilary.Mercer@dtaa.com,,,Hedda.Melissa.Slater@dtaa.com,Send,40710,,
            # 先判断用户是否已存在列表中，即对应的feat是否已建立？
            SendTo = line[3][:line[3].index('@')]
            if SendTo not in Send_Users:
                Send_Users.append(SendTo)
                # 建立其发送特征
                Send_Sum = 1.0
                Send_Avg_Size = float(line[-2])
                Send_Avg_Attach = float(len(line[-1].split(';')))
                send_feat = []
                send_feat.append(SendTo)
                send_feat.append(Send_Sum)
                send_feat.append(Send_Avg_Size)
                send_feat.append(Send_Avg_Attach)
                Send_Feats.append(send_feat)
                continue
            else:
                # 说明之前已经初始化针对该用户的发送特征，接下来需要更新部分特征参数
                # 定位
                Index_sender = Send_Users.index(SendTo)
                # 所以找到了要更新的Send_Feats中的位置
                Send_Feats[Index_sender][1] += 1.0
                Send_Feats[Index_sender][2] += float(line[-2])
                Send_Feats[Index_sender][3] += float(len(line[-1].split(';')))
        # 类似的建立对饮的Receive
        if line[-3] == 'Receive':
            # 先判断用户是否已存在列表中，即对应的feat是否已建立？
            RecvFrom = line[6][:line[6].index('@')]
            if RecvFrom not in Recv_Users:
                Recv_Users.append(RecvFrom)
                # 建立其接收特征
                Recv_Sum = 1.0
                Recv_Avg_Size = float(line[-2])
                Recv_Avg_Attach = float(len(line[-1].split(';')))
                recv_feat = []
                recv_feat.append(RecvFrom)
                recv_feat.append(Recv_Sum)
                recv_feat.append(Recv_Avg_Size)
                recv_feat.append(Recv_Avg_Attach)
                Recv_Feats.append(recv_feat)
                print user, 'receive email from ', RecvFrom, '分析完毕...\n\n'
                continue
            else:
                # 说明之前已经初始化针对该用户的接收特征，接下来需要更新部分特征参数
                # 定位
                Index_recv = Recv_Users.index(RecvFrom)
                # 所以找到了要更新的Recv_Feats中的位置
                Recv_Feats[Index_recv][1] += 1.0
                Recv_Feats[Index_recv][2] += float(line[-2])
                Recv_Feats[Index_recv][3] += float(len(line[-1].split(';')))
                print user, 'receive email from ', RecvFrom, '分析完毕...\n\n'
                continue
    print user, '发送邮件与接收邮件分析完毕...\n'
    print '发送邮件统计示例...\n'
    print len(Send_Feats), len(Send_Users), '\n'
    for i in range(5):
        print Send_Feats[i], '\n'
    print '接收邮件统计示例...\n'
    print len(Recv_Feats), len(Recv_Users), '\n'
    for i in range(5):
        print Recv_Feats[i], '\n'

    print '....<<<<开始比较发送与接收列表，并形成最终的用户邮件通讯行为特征>>>>....\n\n'
    Email_Feats = []
    for user in Send_Users:
        if user in Recv_Users:
            print user, '同时有通信往来...\n'
            # 按照send汇集成一个完整的邮件特征
            send_feat_0 = Send_Feats[Send_Users.index(user)]
            recv_feat_0 = Recv_Feats[Recv_Users.index(user)]
            email_feat = []
            email_feat.append(send_feat_0[0])
            # 邮件发送与接收通信比计算
            # 新的公式为(X-Y)/(X+Y)，取代原有的X/Y形式
            #email_feat.append(float(send_feat_0[1] / recv_feat_0[1]))
            X = float(send_feat_0[1])
            Y = float(recv_feat_0[1])
            email_feat.append((X-Y)/(X+Y))
            email_feat.append(float(send_feat_0[1]))
            email_feat.append(float(send_feat_0[2] / send_feat_0[1]))
            email_feat.append(float(send_feat_0[3] / send_feat_0[1]))
            email_feat.append(float(recv_feat_0[1]))
            email_feat.append(float(recv_feat_0[2] / recv_feat_0[1]))
            email_feat.append(float(recv_feat_0[3] / recv_feat_0[1]))
            Email_Feats.append(email_feat)
            print user, 'email feat 分析完毕..\t', email_feat, '\n'
            Recv_Feats.remove(Recv_Feats[Recv_Users.index(user)])
            Recv_Users.remove(Recv_Users[Recv_Users.index(user)])
            continue
        else:
            print '只有发送行为，没有接收..\n'
            send_feat_0 = Send_Feats[Send_Users.index(user)]
            # recv_feat_0 = Recv_Feats[Recv_Users.index(user)]
            email_feat = []
            email_feat.append(send_feat_0[0])
            # email_feat.append(float(-1))  # -1表示只有发送没有对应的接收
            X = float(send_feat_0[1])
            Y = 0.0
            email_feat.append((X-Y)/(X+Y))
            email_feat.append(float(send_feat_0[1]))
            email_feat.append(float(send_feat_0[2] / send_feat_0[1]))
            email_feat.append(float(send_feat_0[3] / send_feat_0[1]))
            email_feat.append(float(0))
            email_feat.append(float(0))
            email_feat.append(float(0))
            Email_Feats.append(email_feat)
            continue
    for user in Recv_Users:
        # 剩下的都是没有Send行为的
        #send_feat_0 = Send_Feats[Send_Users.index(user)]
        recv_feat_0 = Recv_Feats[Recv_Users.index(user)]
        email_feat = []
        email_feat.append(recv_feat_0[0])
        # email_feat.append(float(0))  # 0表示只有接收没有发送
        X = 0.0
        Y = float(recv_feat_0[1])
        email_feat.append((X - Y) / (X + Y))
        email_feat.append(float(0))
        email_feat.append(float(0))
        email_feat.append(float(0))
        email_feat.append(float(recv_feat_0[1]))
        email_feat.append(float(recv_feat_0[2] / recv_feat_0[1]))
        email_feat.append(float(recv_feat_0[3] / recv_feat_0[1]))
        Email_Feats.append(email_feat)
        continue
    print user, '最终的邮件通讯行为记录为： ', len(Email_Feats), '\n'
    for i in range(int(len(Email_Feats) * 0.1)):
        print Email_Feats[i], '\n'
    for line in Email_Feats:
        if line[0] in Users:
            f_eml_feats.write(User2Email[Users.index(line[0])][0])
        else:
            f_eml_feats.write(line[0]) #说明与非单位员工通信
        f_eml_feats.write(',')
        i = 1
        while i < len(line):
            f_eml_feats.write(str(line[i]))
            f_eml_feats.write(',')
            i += 1
        f_eml_feats.write('\n')
        print line, '写入完毕...\n'
    f_eml.close()
    f_eml_feats.close()











