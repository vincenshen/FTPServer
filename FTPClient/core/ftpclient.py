# -*- coding:utf-8 -*-
import json
from socket import *
import struct
import os
import hashlib


from FTPClient.conf.settings import HOST, PORT, BUFFER, FAMILY, SOCK
# HOST = "127.0.0.1"
# PORT = 8081
# BUFFER = 1024
# FAMILY = AF_INET
# SOCK = SOCK_STREAM


def auth(func):
    """
    认证装饰器
    :param func:
    :return:
    """
    class Wrapper(object):
        def __init__(self, *args, **kwargs):
            self.client = socket(FAMILY, SOCK)
            self.client.connect((HOST, PORT))
            self.func = func(*args, **kwargs)
            i = 3
            while True:
                username = input("please input username:").strip().encode("utf-8")
                password = input("please input password:").strip().encode("utf-8")
                user_dict = {
                    "cmd": "auth",
                    "username": hashlib.md5(username).hexdigest(),
                    "password": hashlib.md5(password).hexdigest(),
                }
                auth_json = json.dumps(user_dict)
                auth_bytes = auth_json.encode("utf-8")

                self.client.send(struct.pack('i', len(auth_bytes)))
                self.client.send(auth_bytes)
                sign = self.client.recv(BUFFER)
                if sign.decode("utf-8") == str(1):
                    print("Authentication Success!")
                    break
                else:
                    i -= 1
                    print("Authentication failed, you have %s times attempt!" % i)
                if i == 0:
                    exit()

        def __getattr__(self, item):
            return getattr(self.func, item)

    return Wrapper


@auth
class FtpClient(object):
    """
    FTP client基本功能
    """
    def __init__(self):
        self.client = socket(FAMILY, SOCK)
        self.client.connect((HOST, PORT))

    def run(self):
        """
        解析输入命令，并调用对应方法
        :return:
        """
        while True:
            cmds = input('>>: ').strip()
            if not cmds:
                continue
            if len(cmds.split()) == 1:
                cmd, attr = cmds, ""
            else:
                cmd, attr = cmds.split()  # put /a/b/c/a.txt
            if hasattr(self, cmd):
                func = getattr(self, cmd)
                func(attr)
            else:
                print("\033[31mInvalid Command!\033[0m")

    def dir(self, attr):
        """
        查看
        :param attr:
        :return:
        """
        head_dict = {
            "cmd": "dir",
            "attr": attr}
        head_json = json.dumps(head_dict)
        head_bytes = head_json.encode("utf-8")
        self.client.send(struct.pack('i', len(head_bytes)))
        self.client.send(head_bytes)

        package_len = self.client.recv(4)
        package_size = struct.unpack("i", package_len)[0]
        rec_size = 0
        rec_bytes = b''
        while rec_size < package_size:
            res = self.client.recv(BUFFER)
            rec_bytes += res
            rec_size += len(res)

        print(rec_bytes.decode("utf-8"))

    def put(self, attr):
        """
        向FTPServer上传文件
        :param attr:
        :return:
        """
        file_size = os.path.getsize(attr)
        head_dict = {
            'cmd': 'put',
            'file_size': file_size,
            'file_name': attr
        }
        head_json = json.dumps(head_dict)
        head_bytes = head_json.encode('utf-8')
        self.client.send(struct.pack('i', len(head_bytes)))
        self.client.send(head_bytes)

        sign = self.client.recv(BUFFER)

        send_size = 0
        if sign.decode("utf-8") == str(0):
            print("file is exist!")
            return

        progress = self.print_progress(file_size)
        progress.__next__()
        with open(attr, 'rb') as f:
            for line in f:
                self.client.send(line)
                send_size += len(line)
                try:
                    progress.send(len(line))
                except StopIteration as e:
                    print("[100%]")

    def get(self, attr):
        """
        向FTPServer下载文件
        :param attr:
        :return:
        """
        head_dict = {
            'cmd': 'get',
            'file_name': attr
        }
        head_json = json.dumps(head_dict)
        head_bytes = head_json.encode('utf-8')
        self.client.send(struct.pack('i', len(head_bytes)))
        self.client.send(head_bytes)

        sign = self.client.recv(BUFFER)
        if sign.decode("utf-8") == str(0):
            print("file is not exist!")
            return

        head_len = bytes(self.client.recv(4))
        head_size = struct.unpack("i", head_len)[0]
        head_json = bytes.decode(self.client.recv(head_size))
        head_dict = json.loads(head_json)
        file_size = head_dict["file_size"]
        rec_size = 0
        progress = self.print_progress(file_size)
        progress.__next__()
        with open(attr, "wb") as f:
            while rec_size < file_size:
                res = self.client.recv(BUFFER)
                f.write(res)
                rec_size += len(res)
                try:
                    progress.send(len(res))
                except StopIteration as e:
                    print("[100%]")

    def print_progress(self, total):
        received_size = 0
        current_percent = 0
        while received_size < total:
            new_size = yield
            if int((received_size / total) * 100) > current_percent:
                print("#", end="", flush=True)
                current_percent = int((received_size / total) * 100)
            received_size += new_size


def run():
    print("Welcome to FTP world!".center(50, "*"))
    print("初始化用户 [username: alex  password: alex]")
    FtpClient().run()

if __name__ == '__main__':
    client = FtpClient()
    client.run()
