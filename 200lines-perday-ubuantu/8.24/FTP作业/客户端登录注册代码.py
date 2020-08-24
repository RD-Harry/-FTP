"""
ftp 文件客户端
"""

#服务器地址
ADDR = ('localhost',8888)
from socket import *
import os,sys
import time
class FTPClient:
    #每一个通过此类创建的对象都会有一个sockfd属性
    def __init__(self,sockfd):
        self.sockfd = sockfd
    def do_list(self):
        self.sockfd.send(b'L')
        data = self.sockfd.recv(1024).decode()
        if data =='OK':
            data = self.sockfd.recv(1024*1024)
            print(data.decode())
        else:
            print(data)
    def do_quit(self):
        self.sockfd.send(b'Q')
        self.sockfd.close()
        sys.exit('客户端退出')
        # 下载

    def do_get(self, filename):
        # 发送下载请求
        self.sockfd.send(("G " + filename).encode())
        data = self.sockfd.recv(128).decode()  # 准备接收文件内容
        if data == 'OK':  # 准备接受文件内容
            f = open(filename, 'wb')
            while True:
                data = self.sockfd.recv(1024)
                if data == b"##":
                    break
                f.write(data)
            f.close()
        else:
            print(data)

    def do_put(self, filename):
        f = open(filename, 'rb')
        filename = filename.split('/')[-1]

        self.sockfd.send(('P ' + filename).encode())

        data = self.sockfd.recv(128).decode()

        if data == 'OK':
            while True:
                data = f.read(1024)
                if not data:
                    time.sleep(0.1)
                    self.sockfd.send(b'##')
                    break
                self.sockfd.send(data)
            f.close()
        else:
            print(data)

    def do_delete(self, filename):
        self.sockfd.send(('D ' + filename).encode())
        data = self.sockfd.recv (1024)
        print(data.decode())



    def do_regist(self):
        """
        注册功能
        :return:
        """
        while True:
            self.name = input('name:')
            self.password = input('password:')
            self.confirm_password = input('confirm password:')
            person = (self.name,self.password)
            if self.password == self.confirm_password:


                print(person)
                self.sockfd.send(('R ' + self.name +' ' +self.password).encode())
                time.sleep(0.1)
                data = self.sockfd.recv(1024)
                print(data.decode())
                return self.name,self.password
            else:
                print('两次密码不一致，请重新输入')
                continue


    def do_login(self):
        self.name = input('请输入姓名:')
        self.password = input('请输入密码:')

        self.sockfd.send(('E '+self.name +' ' +self.password).encode())
        data =self.sockfd.recv(1024)
        print(data.decode())
        # if data.decode() =='登录失败':
        #     continue
        if data.decode()[-1]=='败':
            print('请重新登录')
            return
        self.do_choice()






    def do_choice(self):
        s = socket()
        try:
            s.connect(ADDR)
        except Exception as e:
            print(e)
            return
        ftp = FTPClient(s)
        while True:
            print('\n菜单')
            print('list')
            print('get')
            print('put')
            print('quit')
            print('delete')
            print('=========')
            try:

                cmd = input('>>>')
                #print(cmd[:3])
            except KeyboardInterrupt:
                ftp.do_quit()
            except:
                continue
            if cmd.strip() == 'list':
                ftp.do_list()
            elif cmd.strip() == 'quit':
                ftp.do_quit()
            elif cmd[:3] == 'get':
                filename = cmd.split(' ')[-1]
                ftp.do_get(filename)
            elif cmd[:3] == 'put':
                filename = cmd.split(' ')[-1]
                ftp.do_put(filename)
            elif cmd[:6] == 'delete':
                #print(cmd[:6])
                # print('shanchu')
                filename = cmd.split(' ')[-1]
                ftp.do_delete(filename)
            else:
                print('请输入正确命令')
def main():
    s=socket()
    try:
        s.connect(ADDR)
    except Exception as e:
        print(e)
        return
    ftp = FTPClient(s)



    while True:
        print('\n欢迎访问')
        print('①登录')
        print('②注册新用户')
        print('=========')
        try:

            msg = input("请输入你的选择: ")
            #choice = cmd
            #print(choice)
        except KeyboardInterrupt :
            ftp.do_quit()

        except:
            continue
        if msg == '1':
            ftp.do_login()
        elif msg == '2':
            ftp.do_regist()
        else:
            print('请输入正确命令')







if __name__ == "__main__":
        main()