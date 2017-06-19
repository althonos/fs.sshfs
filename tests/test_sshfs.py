# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import stat
import time
import unittest
import contextlib
import paramiko
import docker

import fs.test
import fs.errors
import fs.sshfs
from fs.subfs import ClosingSubFS
from fs.permissions import Permissions

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

    def setUp(self):
        super(TestSSHFS, self).setUp()
        self.fs.removetree("/")

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
        fs.close()
        del fs

    def test_chmod(self):
        self.fs.touch("test.txt")
        remote_path = "/home/{}/test/test.txt".format(self.user)

        # Initial permissions
        info = self.fs.getinfo("test.txt", ["access"])
        self.assertEqual(info.permissions.mode, 0o644)
        st = self.fs.delegate_fs()._sftp.stat(remote_path)
        self.assertEqual(stat.S_IMODE(st.st_mode), 0o644)

        # Change permissions with SSHFS._chown
        self.fs.delegate_fs()._chmod(remote_path, 0o744)
        info = self.fs.getinfo("test.txt", ["access"])
        self.assertEqual(info.permissions.mode, 0o744)
        st = self.fs.delegate_fs()._sftp.stat(remote_path)
        self.assertEqual(stat.S_IMODE(st.st_mode), 0o744)

        # Change permissions with SSHFS.setinfo
        self.fs.setinfo("test.txt",
                        {"access": {"permissions": Permissions(mode=0o600)}})
        info = self.fs.getinfo("test.txt", ["access"])
        self.assertEqual(info.permissions.mode, 0o600)
        st = self.fs.delegate_fs()._sftp.stat(remote_path)
        self.assertEqual(stat.S_IMODE(st.st_mode), 0o600)

        with self.assertRaises(fs.errors.PermissionDenied):
            self.fs.delegate_fs().setinfo("/", {
                "access": {"permissions": Permissions(mode=0o777)}
            })

    def test_chown(self):

        self.fs.touch("test.txt")
        remote_path = "/home/{}/test/test.txt".format(self.user)
        info = self.fs.getinfo("test.txt", namespaces=["access"])
        gid, uid = info.get('access', 'uid'), info.get('access', 'gid')

        with utils.mock.patch.object(self.fs.delegate_fs()._sftp, 'chown') as chown:
            self.fs.setinfo("test.txt", {'access': {'uid': None}})
            chown.assert_called_with(remote_path, uid, gid)

            self.fs.setinfo("test.txt", {'access': {'gid': None}})
            chown.assert_called_with(remote_path, uid, gid)

            self.fs.setinfo("test.txt", {'access': {'gid': 8000}})
            chown.assert_called_with(remote_path, uid, 8000)

            self.fs.setinfo("test.txt", {'access': {'uid': 1001, 'gid':1002}})
            chown.assert_called_with(remote_path, 1001, 1002)

    def test_utime(self):

        def get_accessed(f):
            return f.getdetails("test.txt").get('details', 'accessed')
        def get_modified(f):
            return f.getdetails("test.txt").get('details', 'modified')

        self.fs.touch("test.txt")

        self.fs.setinfo("test.txt", {'details': {'accessed': None, 'modified': None}})
        self.assertLessEqual(time.time()-get_accessed(self.fs), 1)
        self.assertLessEqual(time.time()-get_modified(self.fs), 1)

        self.fs.setinfo("test.txt", {'details': {'accessed': 0}})
        self.assertEqual(get_accessed(self.fs), 0)
        self.assertEqual(get_modified(self.fs), 0)

        self.fs.setinfo("test.txt", {'details': {'modified': 100}})
        self.assertEqual(get_accessed(self.fs), 100)
        self.assertEqual(get_modified(self.fs), 100)

        self.fs.setinfo("test.txt", {'details': {'modified': 100, 'accessed': 200}})
        self.assertEqual(get_accessed(self.fs), 200)
        self.assertEqual(get_modified(self.fs), 100)



class TestSSHFSFail(unittest.TestCase):

    def test_unknown_host(self):
        with self.assertRaises(fs.errors.CreateFailed):
            _ = fs.sshfs.SSHFS(host="unexisting-hostname")

    def test_wrong_user(self):
        with self.assertRaises(fs.errors.CreateFailed):
            _ = fs.sshfs.SSHFS(host="localhost", user="nonsensicaluser")


class TestSSHFSWithPassword(TestSSHFS, unittest.TestCase):

    def make_fs(self):
        ssh_fs = fs.open_fs('ssh://{user}:{pasw}@localhost:{port}'.format(
            user=self.user, pasw=self.pasw, port=self.port,
        ))
        ssh_fs.makedir('/home/{}/test'.format(self.user), recreate=True)
        return ssh_fs.opendir('/home/{}/test'.format(self.user), factory=ClosingSubFS)


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
        cls.addKeyToServer()

    def make_fs(self):
        ssh_fs = fs.sshfs.SSHFS('localhost',
            user=self.user, port=self.port, pkey=self.rsa_key
        )
        ssh_fs.makedir('/home/{}/test'.format(self.user), recreate=True)
        return ssh_fs.opendir('/home/{}/test'.format(self.user), factory=ClosingSubFS)
