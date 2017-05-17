# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import unittest
import tempfile
import shutil
import time

import six
import paramiko
import docker

import fs.sshfs
import fs.test

from . import utils


# @unittest.skip('OOPS')
# class TestSSHFS(fs.test.FSTestCases, unittest.TestCase):
#
#     @staticmethod
#     def _add_key_to_authorized_keys(key):
#         with open(os.path.expanduser('~/.ssh/authorized_keys'), 'a') as auth_file:
#             auth_file.write("{} {}\n".format(key.get_name(), key.get_base64()))
#
#     @staticmethod
#     def _get_authorized_keys():
#         with open(os.path.expanduser('~/.ssh/authorized_keys'), 'r') as auth_file:
#             return auth_file.readlines()
#
#     @classmethod
#     def setUpClass(cls):
#         cls.rsa_key = paramiko.RSAKey.generate(bits=2048)#, progress_func=show_progress)
#         cls._add_key_to_authorized_keys(cls.rsa_key)
#
#     @classmethod
#     def tearDownClass(cls):
#         keylines = cls._get_authorized_keys()
#         keylines = [l for l in keylines if not l.startswith(cls.rsa_key.get_name())]
#         if keylines: # Write the authorized_keys file without test key
#             with open(os.path.expanduser('~/.ssh/authorized_keys'), 'w') as auth_file:
#                 auth_file.writelines(keylines)
#         else: # Remove the authorized_keys file if there was no other key in it
#             os.remove(os.path.expanduser('~/.ssh/authorized_keys'))
#
#     def make_fs(self):
#         sshfs = fs.sshfs.SSHFS('localhost', pkey=self.rsa_key)
#         tempdir = tempfile.mkdtemp()
#         if six.PY2:
#             tempdir = tempdir.decode('utf-8')
#         subfs = sshfs.opendir(tempdir)
#         subfs.tempdir = tempdir
#         return subfs
#
#     @staticmethod
#     def destroy_fs(fs):
#         fs.close()
#         shutil.rmtree(fs.tempdir)
#         del fs
#
#     # TODO: add tests for SSHFS._chown
#     def test_chown(self):
#         pass
#
#     # TODO: add tests for SSHFS._chmod
#     def test_chmod(self):
#         pass
#
#     # TODO: add tests for SSHFS._utime
#     def test_utime(self):
#         pass


@unittest.skipUnless(utils.CI or utils.DOCKER, "docker service unreachable.")
class TestSSHFSOpener(fs.test.FSTestCases, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = "foo"
        cls.pasw = "pass"
        cls.port = 2222
        cls.docker_client = docker.from_env(version='auto')
        cls.startSFTPserver()

    @classmethod
    def tearDownClass(cls):
        cls.stopSFTPserver()

    @classmethod
    def startSFTPserver(cls):
        cls._sftp_container = cls.docker_client.containers.run(
            "sjourdan/alpine-sshd",
            detach=True, ports={'22/tcp': cls.port},
            environment={'USER': cls.user, 'PASSWORD': cls.pasw},
        )

    @classmethod
    def stopSFTPserver(cls):
        cls._sftp_container.kill()
        cls._sftp_container.remove()

    def make_fs(self):
        return fs.open_fs('ssh://{user}:{pasw}@localhost:{port}/home/{user}'.format(
            user=self.user, pasw=self.pasw, port=self.port,
        ))

    def destroy_fs(self, fs):
        if not fs.isclosed():
            fs.removetree('/')
            fs.close()
        del fs
