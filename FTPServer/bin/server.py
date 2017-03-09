# -*- coding:utf-8 -*-
import os
import sys
from socketserver import ThreadingTCPServer
from FTPClient.conf.settings import HOST, PORT

BASE_DIR = os.path.normcase(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            os.path.pardir,
                            os.path.pardir))
sys.path.append(BASE_DIR)


from FTPServer.core import ftpserver


if __name__ == '__main__':

    tcp_Server = ThreadingTCPServer((HOST, PORT), ftpserver.FTPServer)
    tcp_Server.allow_reuse_address = True
    tcp_Server.serve_forever()
