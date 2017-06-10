# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import time
import unittest
import contextlib
import paramiko
import docker


import fs.sshfs
import fs.test

from . import utils


@unittest.skipUnless(utils.CI or utils.DOCKER, "docker service unreachable.")
class TestSSHFS(fs.test.FSTestCases):

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
        time.sleep(0.5)

    @classmethod
    def stopSFTPserver(cls):
        cls._sftp_container.kill()
        cls._sftp_container.remove()

    @staticmethod
    def destroy_fs(fs):
        if not fs.isclosed():
            fs.removetree('/')
            fs.close()
        del fs


class TestSSHFSWithPassword(TestSSHFS, unittest.TestCase):

    def make_fs(self):
        return fs.open_fs('ssh://{user}:{pasw}@localhost:{port}/home/{user}'.format(
            user=self.user, pasw=self.pasw, port=self.port,
        ))


class TestSSHFSWithKey(TestSSHFS, unittest.TestCase):

    @classmethod
    def makeRSAKey(cls):
        cls.rsa_key = paramiko.RSAKey.generate(bits=2048)

    @classmethod
    def addKeyToServer(cls):
        with contextlib.closing(paramiko.SSHClient()) as client:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect('localhost', cls.port, cls.user, cls.pasw)
            with contextlib.closing(client.open_sftp()) as sftp:
                sftp.mkdir('/home/{}/.ssh'.format(cls.user))
                with sftp.open('/home/{}/.ssh/authorized_keys'.format(cls.user), 'w') as f:
                    f.write("{} {}\n".format(
                        cls.rsa_key.get_name(), cls.rsa_key.get_base64()
                    ).encode('utf-8'))

    @classmethod
    def setUpClass(cls):
        super(TestSSHFSWithKey, cls).setUpClass()
        cls.makeRSAKey()

    def make_fs(self):
        self.addKeyToServer()
        ssh_fs = fs.sshfs.SSHFS('localhost',
            user=self.user, port=self.port, pkey=self.rsa_key
        )
        sub_fs = ssh_fs.opendir('/home/{}'.format(self.user))
        sub_fs.removetree('/')
        return sub_fs
