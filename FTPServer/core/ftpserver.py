# -*- coding:utf-8 -*-

from socketserver import ThreadingTCPServer, BaseRequestHandler
import struct
import subprocess
import json
import os
import hashlib
import shelve

from FTPClient.conf.settings import HOST, PORT, BUFFER, FAMILY, SOCK, ROOT_DIR


class FTPServer(BaseRequestHandler):

    def handle(self):

        while True:
            print("connect from:", self.client_address)
            head_len = self.request.recv(4)
            if not head_len: break
            head_size = struct.unpack("i", head_len)[0]

            head_json = bytes.decode(self.request.recv(head_size))
            head_dict = json.loads(head_json)
            if hasattr(self, head_dict["cmd"]):
                func = getattr(self, head_dict["cmd"])
                func(head_dict)

    def auth(self, head_dict):
        if not os.path.isfile("../db/userlist.dir"):
            username = hashlib.md5(b"alex").hexdigest()
            password = hashlib.md5(b"alex").hexdigest()
            print("初始化用户alex")
            user = shelve.open("../db/userlist")
            user[username] = password
            user.close()
            print("初始化alex完成")

        username = head_dict["username"]
        password = head_dict["password"]
        user = shelve.open("../db/userlist")
        if user[username] == password:
            self.request.send(b"1")
        else:
            self.request.send(b"0")

    def dir(self, head_dict):
        """
        查看文件列表
        :param head_dict:
        :return:
        """
        cmd_list = [head_dict["cmd"], head_dict["attr"], ROOT_DIR]
        res = subprocess.Popen(" ".join(cmd_list), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        err = res.stderr.read()
        if err:
            back_msg = err
        else:
            back_msg = res.stdout.read()
        self.request.send(struct.pack("i", len(back_msg)))
        self.request.send(back_msg)

    def put(self, head_dict):
        """
        接收文件
        :param head_dict:
        :return:
        """
        file_name = head_dict["file_name"]
        file_size = head_dict["file_size"]

        if os.path.isfile("%s/%s" % (ROOT_DIR, file_name)):
            self.request.send(b"0")
            return
        else:
            self.request.send(b"1")

        rec_size = 0
        with open("%s/%s" % (ROOT_DIR, file_name), "wb") as f:
            while rec_size < file_size:
                res = self.request.recv(BUFFER)
                f.write(res)
                rec_size += len(res)

    def get(self, cmd_dict):
        """
        发送文件
        :param cmd_dict:
        :return:
        """
        file_name = cmd_dict["file_name"]
        file_size = os.path.getsize("%s/%s" % (ROOT_DIR, file_name))

        if os.path.isfile("%s/%s" % (ROOT_DIR, file_name)):
            self.request.send(b"1")
        else:
            self.request.send(b"0")
            return

        head_dict = {
            'file_size': file_size,
        }
        head_json = json.dumps(head_dict)
        head_bytes = head_json.encode('utf-8')

        self.request.send(struct.pack('i', len(head_bytes)))
        self.request.send(head_bytes)

        with open("%s/%s" % (ROOT_DIR, file_name), 'rb') as f:
            for line in f:
                self.request.send(line)


if __name__ == '__main__':

    tcp_Server = ThreadingTCPServer(("127.0.0.1", 8081), FTPServer)
    tcp_Server.allow_reuse_address = True
    tcp_Server.serve_forever()

