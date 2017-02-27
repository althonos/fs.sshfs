# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import fs.sshfs
import fs.test
import unittest

class TestSSHFS(fs.test.FSTestCases, unittest.TestCase):

    def make_fs(self):
        return fs.sshfs.SSHFS()

    def destroy_fs(self, fs):
        fs.close()
        del fs

    
