# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import unittest
import tempfile
import shutil

import six
import paramiko

import fs.sshfs
import fs.test



class TestSSHFS(fs.test.FSTestCases, unittest.TestCase):

    @staticmethod
    def _add_key_to_authorized_keys(key):
        with open(os.path.expanduser('~/.ssh/authorized_keys'), 'a') as auth_file:
            auth_file.write("{} {}\n".format(key.get_name(), key.get_base64()))

    @staticmethod
    def _get_authorized_keys():
        with open(os.path.expanduser('~/.ssh/authorized_keys'), 'r') as auth_file:
            return auth_file.readlines()

    @classmethod
    def setUpClass(cls):
        rsa_key_filename = 'test_key'
        cls.rsa_key = paramiko.RSAKey.generate(bits=2048)#, progress_func=show_progress)
        cls._add_key_to_authorized_keys(cls.rsa_key)

    @classmethod
    def tearDownClass(cls):
        keylines = cls._get_authorized_keys()
        keylines = [l for l in keylines if not l.startswith(cls.rsa_key.get_name())]
        if keylines: # Write the authorized_keys file without test key
            with open(os.path.expanduser('~/.ssh/authorized_keys'), 'w') as auth_file:
                auth_file.writelines(keylines)
        else: # Remove the authorized_keys file if there was no other key in it
            os.remove(os.path.expanduser('~/.ssh/authorized_keys'))

    def make_fs(self):
        sshfs = fs.sshfs.SSHFS('localhost', pkey=self.rsa_key)
        tempdir = tempfile.mkdtemp()
        if six.PY2:
            tempdir = tempdir.decode('utf-8')
        subfs = sshfs.opendir(tempdir)
        subfs.tempdir = tempdir
        return subfs

    def destroy_fs(self, fs):
        fs.close()
        shutil.rmtree(fs.tempdir)
        del fs
