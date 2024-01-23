# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import unittest

import fs
from semantic_version import Version

from . import utils


@unittest.skipIf(utils.fs_version() < Version("2.0.10"), "FS URL params not supported.")
class TestFSURL(unittest.TestCase):

    user = "user"
    pasw = "pass"
    port = 3222

    @classmethod
    def setUpClass(cls):
        # Find a port, which is for sure doesn't have SFTP server listening to
        cls.port = utils.find_available_port(begin_port=cls.port, end_port=cls.port+1000)

    def test_timeout(self):
        with utils.mock.patch('miarec_sshfs.SSHFS', utils.mock.MagicMock()) as magic:
            fs.open_fs(f'mssh://user:pass@localhost:{self.port}/?timeout=1')
            self.assertEqual(magic.call_args[-1]['timeout'], 1)
            fs.open_fs(f'mssh://user:pass@localhost:{self.port}/?compress=1&timeout=5')
            self.assertEqual(magic.call_args[-1]['timeout'], 5)

    def test_compress(self):
        with utils.mock.patch('miarec_sshfs.SSHFS', utils.mock.MagicMock()) as magic:
            fs.open_fs(f'mssh://user:pass@localhost:{self.port}/?compress=true')
            self.assertEqual(magic.call_args[-1]['compress'], True)
            fs.open_fs(f'mssh://user:pass@localhost:{self.port}/?timeout=5&compress=1')
            self.assertEqual(magic.call_args[-1]['compress'], True)
            fs.open_fs(f'mssh://user:pass@localhost:{self.port}/?timeout=5&compress=0')
            self.assertEqual(magic.call_args[-1]['compress'], False)
