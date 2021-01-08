# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import stat
import sys
import time
import uuid
import unittest

import paramiko.ssh_exception

import fs.path
import fs.test
import fs.errors
from fs.sshfs import SSHFS
from fs.subfs import ClosingSubFS
from fs.permissions import Permissions

from . import utils


@unittest.skipIf(utils.docker_client is None, "docker service unreachable.")
class TestSSHFS(fs.test.FSTestCases, unittest.TestCase):

    user = "user"
    pasw = "pass"
    port = 2222

    @classmethod
    def setUpClass(cls):
        super(TestSSHFS, cls).setUpClass()
        cls.sftp_container = utils.startServer(
            utils.docker_client, cls.user, cls.pasw, cls.port)

    @classmethod
    def tearDownClass(cls):
        utils.stopServer(cls.sftp_container)
        super(TestSSHFS, cls).tearDownClass()

    @staticmethod
    def destroy_fs(fs):
        fs.close()
        del fs

    def make_fs(self):
        self.ssh_fs = SSHFS('localhost', self.user, self.pasw, port=self.port)
        self.test_folder = fs.path.join('/home', self.user, uuid.uuid4().hex)
        self.ssh_fs.makedir(self.test_folder, recreate=True)
        return self.ssh_fs.opendir(self.test_folder, factory=ClosingSubFS)

    @unittest.skipIf(sys.version_info[:2] == (3, 4), 'hangs in Python 3.4')
    def test_download_0(self):
        super(TestSSHFS, self).test_download_0()

    @unittest.skipIf(sys.version_info[:2] == (3, 4), 'hangs in Python 3.4')
    def test_download_1(self):
        super(TestSSHFS, self).test_download_1()

    @unittest.skipIf(sys.version_info[:2] == (3, 4), 'hangs in Python 3.4')
    def test_download_2(self):
        super(TestSSHFS, self).test_download_2()

    @unittest.skipIf(sys.version_info[:2] == (3, 4), 'hangs in Python 3.4')
    def test_download_4(self):
        super(TestSSHFS, self).test_download_4()

    @unittest.skipIf(sys.version_info[:2] == (3, 4), 'hangs in Python 3.4')
    def test_upload_0(self):
        super(TestSSHFS, self).test_upload_0()

    @unittest.skipIf(sys.version_info[:2] == (3, 4), 'hangs in Python 3.4')
    def test_upload_1(self):
        super(TestSSHFS, self).test_upload_1()

    @unittest.skipIf(sys.version_info[:2] == (3, 4), 'hangs in Python 3.4')
    def test_upload_2(self):
        super(TestSSHFS, self).test_upload_2()

    @unittest.skipIf(sys.version_info[:2] == (3, 4), 'hangs in Python 3.4')
    def test_upload_4(self):
        super(TestSSHFS, self).test_upload_4()

    def test_chmod(self):
        self.fs.touch("test.txt")
        remote_path = fs.path.join(self.test_folder, "test.txt")

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
        remote_path = fs.path.join(self.test_folder, "test.txt")
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

    def test_exec_command_exception(self):
        ssh = self.fs.delegate_fs()
        # make sure to invalidate the cache
        ssh.platform
        del ssh.platform
        # pretend we get an error while the platform is guessed
        with utils.mock.patch.object(
            ssh,
            '_exec_command',
            side_effect=paramiko.ssh_exception.SSHException()
        ) as _exec_command:
            self.assertEquals(ssh.platform, "unknown")
            if sys.version_info[:2] != (3,5):
                _exec_command.assert_called()

    def test_utime(self):

        def get_accessed(f):
            return f.getdetails("test.txt").get('details', 'accessed')
        def get_modified(f):
            return f.getdetails("test.txt").get('details', 'modified')

        self.fs.touch("test.txt")

        self.fs.setinfo("test.txt", {'details': {'accessed': None, 'modified': None}})
        self.assertLessEqual(time.time()-get_accessed(self.fs), 2)
        self.assertLessEqual(time.time()-get_modified(self.fs), 2)

        self.fs.setinfo("test.txt", {'details': {'accessed': 0}})
        self.assertEqual(get_accessed(self.fs), 0)
        self.assertEqual(get_modified(self.fs), 0)

        self.fs.setinfo("test.txt", {'details': {'modified': 100}})
        self.assertEqual(get_accessed(self.fs), 100)
        self.assertEqual(get_modified(self.fs), 100)

        self.fs.setinfo("test.txt", {'details': {'modified': 100, 'accessed': 200}})
        self.assertEqual(get_accessed(self.fs), 200)
        self.assertEqual(get_modified(self.fs), 100)

    def test_symlinks(self):
        with self.fs.openbin("foo", "wb") as f:
            f.write(b"foobar")

        self.fs.delegate_fs()._sftp.symlink(
            fs.path.join(self.test_folder, "foo"),
            fs.path.join(self.test_folder, "bar")
        )

        # os.symlink(self._get_real_path("foo"), self._get_real_path("bar"))
        self.assertFalse(self.fs.islink("foo"))
        self.assertFalse(self.fs.getinfo("foo", namespaces=["link"]).is_link)
        self.assertTrue(self.fs.islink("bar"))
        self.assertTrue(self.fs.getinfo("bar", namespaces=["link"]).is_link)

        foo_info = self.fs.getinfo("foo", namespaces=["link", "lstat"])
        self.assertIn("link", foo_info.raw)
        self.assertIn("lstat", foo_info.raw)
        self.assertEqual(foo_info.get("link", "target"), None)
        self.assertEqual(foo_info.target, foo_info.raw["link"]["target"])
        bar_info = self.fs.getinfo("bar", namespaces=["link", "lstat"])
        self.assertIn("link", bar_info.raw)
        self.assertIn("lstat", bar_info.raw)
