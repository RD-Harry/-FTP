"""
ftp文件服务端
多线程并发
只要涉及到短时间内多次发送数据，就要注意粘包
"""
import pymysql
from threading import *
from socket import *
import sys
import time
import os

# from threading import Thread


ADDR = ('localhost', 8888)
ftpfile = "/home/tarena/PycharmProjects/pycharm/200lines-perday/8.23/ftpfile/"
# 注意最后面对额斜杠，拼接的时候没有/不是正确的路径
#get_data_from_service(user='root', spassword='123456', db='service')


class FTPServer(Thread):
    def __init__(self, connfd):
        super().__init__()  # 调用父类的初始化方法
        self.connfd = connfd

    def do_list(self):
        file_list = os.listdir(ftpfile)  # 把文件夹里面的文件名字返回一个列表
        if not file_list:
            self.connfd.send('文件库为空'.encode())
            return  # 为空就跳出
        else:
            self.connfd.send(b'OK')
            time.sleep(0.1)
        # 发送name list
        files = '\n'.join(file_list)  # 用\n去拼接
        self.connfd.send(files.encode())

    def do_get(self, filename):
        try:  # 判断文件是否能打开
            f = open(ftpfile + filename, 'rb')
        except Exception as e:
            self.connfd.send('文件不存在'.encode())
            return
        else:
            self.connfd.send(b"OK")
            time.sleep(0.1)  # 防止粘包
        # 发送文件内容

        while True:
            data = f.read(1024)
            if not data:
                time.sleep(0.1)
                self.connfd.send(b'##')

                break
            self.connfd.send(data)
        f.close()

    def do_put(self, filename):
        # a = 0
        f = open(ftpfile + filename, 'wb')
        if os.path.exists(ftpfile + filename):
            # a += 1
            f = open(ftpfile + filename, 'wb')
            self.connfd.send('有同名文件'.encode())

            # f = open(ftpfile + filename + a, 'wb')
            # return

            # else:
            self.connfd.send(b'OK')

            while True:
                data = self.connfd.recv(1024)
                if data == b'##':
                    break
                f.write(data)
        f.close()

    # 重写run方法
    def run(self):
        # 接收客户端请求
        while True:
            data = self.connfd.recv(1024).decode()
            print(data)
            if not data or data == 'Q':
                return
            elif data == 'L':

                self.do_list()
            elif data[0] == 'G':
                filename = data.split(' ')[-1]
                self.do_get(filename)

                self.connfd.recv(1024)

            elif data[0] == 'P':
                filename = data.split(' ')[-1]
                self.do_put(filename)
            elif data[0] == 'D':
                filename = data.split(' ')[-1]
                self.do_delete(filename)

            elif data[0] == 'R':
                #print(data)
                #get_data_from_service(user='root', password='123456', db='service')
                #data = self.connfd.recv(1024).decode()
                name=data.split(' ')[1]

                password =data.split(' ')[2]
                print(name,password)

                self.insert_data_to_service(name,password)
            elif data[0] == 'E':
                # print(data)
                # get_data_from_service(user='root', password='123456', db='service')

                name1 = data.split(' ')[1]
                password1 = data.split(' ')[2]
                print(name1,password1)
                self.get_data_from_service(name1,password1)

    def insert_data_to_service(self, name, password):
        # 连接数据库
        db = pymysql.connect(host='localhost',  # 连接本机的话可以不写
                             port=3306,  # 连接本机可以不写,注意是整形
                             user='root',
                             password='123456',
                             database='service',
                             charset='utf8')  # 指程序和数据库交互的时候用的是UTF8，
        # 不写的话无法插入中文，数据库已经是utf8也要写

        # 生成游标（油表对象用于执行sql语句，获取执行结果）
        cur = db.cursor()
        try:
            sql = "insert into userinfo (name,password) values (%s,%s);"
            # name = '常安'
            # password = 123456
            print(sql)
            print(name)
            print(password)
            cur.execute(sql, [name, password])  # 游标调用，将sql语句传进来
            # 若没有到close就一只在缓冲区没有立即生效
            # 用commit立即生效
            db.commit()  # 提交到数据库执行

            # 执行sql语句
            # print(cur)
        except Exception as e:
            db.rollback()  # 万一写有问题就数据回滚
            # 回滚commit()，用于当commit（）出错时恢复到原来状态
        cur.close()  # 关闭游标
        db.close()  # 关闭连接
        # 关闭游标和数据库
        self.connfd.send(('注册成功').encode())

    def get_data_from_service(self, name1, password1):
        """
        判断用户是否已经存在
        :param user: 用户名
        :param password: 密码
        :param db: 数据库
        :param host: 地址
        :param port: 端口
        :return:
        """

        db = pymysql.connect(host='localhost',  # 连接本机的话可以不写
                             port=3306,  # 连接本机可以不写,注意是整形
                             user='root',
                             password='123456',
                             database='service',
                             charset='utf8')  # 指程序和数据库交互的时候用的是UTF8，
        # 不写的话无法插入中文，数据库已经是utf8也要写

        # 生成游标（油表对象用于执行sql语句，获取执行结果）
        cur = db.cursor()
        sql = "select password from userinfo where name =%s;"
        # res = cursor.execute(sql,name1)
        # # print(res)
        # df = pd.read_sql(sql=sql, con=conn)
        # print(df)
        cur.execute(sql, name1)
        one=cur.fetchone()
        #print(one[0])
        cur.close()
        db.close()
        if one == None:
            self.connfd.send(('登录失败').encode())
            return
        elif one[0]==password1 :
            self.connfd.send(("登录成功").encode())





    def do_delete(self, filename):
        file_list = os.listdir(ftpfile)
        for i in file_list:
            if i == filename:
                os.remove(ftpfile + filename)
                self.connfd.send('删除成功'.encode())


def main():
    s = socket()
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(ADDR)
    s.listen(2)
    print("listen from 8888...")

    while True:
        try:

            c, addr = s.accept()
            print("connect from :", addr)
        except  KeyboardInterrupt:
            s.close()
            sys.exit('服务端退出')
        except Exception as e:
            print(e)
            continue

        t = FTPServer(c)  # 传入c的目的t.c.send()/t.c.recv()，创建一个自定义线程对象
        t.setDaemon(True)  # 在没有用户连接后就会自动离开
        t.start()  # 会自动找run方法


# 如果直接运行当前文件，则执行下面语句；
# 如果当前文件当做模块导入其他文件则不执行
if __name__ == '__main__':
    main()
