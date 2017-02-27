# coding: utf-8
from __future__ import unicode_literals
from __future__ import absolute_import

from fs.base import FS


class SSHFS(FS):

    _meta = {
        'case_insensitive': False,
        'invalid_path_chars': '\0',
        'network': True,
        'read_only': False,
        'thread_safe': True,
        'unicode_paths': True,
        'virtual': False,
    }

    def __init__(self,
                 host,
                 user='anonymous',
                 passwd='',
                 acct='',
                 timeout=10,
                 port=22):
        super(FTPFS, self).__init__()


    def getinfo():
        pass

    def listdir():
        pass

    def makedir():
        pass

    def openbin():
        pass

    def remove():
        pass

    def removedir():
        pass

    def setinfo():
        pass
