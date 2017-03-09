# -*- coding:utf-8 -*-

import os
import sys

BASE_DIR = os.path.normcase(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            os.path.pardir,
                            os.path.pardir))

sys.path.append(BASE_DIR)


from FTPClient.core import ftpclient


if __name__ == '__main__':
    ftpclient.run()