# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import uuid
import unittest
import tempfile

import paramiko

import fs.errors
import fs.path
from miarec_sshfs import SSHFS

from . import utils


class TestCreateFailed(unittest.TestCase):

    def test_unknown_host(self):
        self.assertRaises(
            fs.errors.CreateFailed, SSHFS, 'unexisting-hostname', timeout=1)

    def test_unknown_user(self):
        self.assertRaises(
            fs.errors.CreateFailed, SSHFS, 'localhost', 'baduser', timeout=1)


@unittest.skipIf(utils.docker_client is None, "docker service unreachable.")
class TestOpener(unittest.TestCase):

    user = "user"
    pasw = "pass"
    port = 2223

    @classmethod
    def setUpClass(cls):
        cls.port = utils.find_available_port(begin_port=cls.port)
        cls.sftp_container = utils.startServer(
            utils.docker_client, cls.user, cls.pasw, cls.port)

    @classmethod
    def tearDownClass(cls):
        utils.stopServer(cls.sftp_container)

    @classmethod
    def addKeyToServer(cls, pkey):
        with paramiko.SSHClient() as client:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect('localhost', cls.port, cls.user, cls.pasw, allow_agent=False, look_for_keys=False)
            with client.open_sftp() as sftp:
                if not '.ssh' in sftp.listdir('/home/{}'.format(cls.user)):
                    sftp.mkdir('/home/{}/.ssh'.format(cls.user))
                with sftp.open('/home/{}/.ssh/authorized_keys'.format(cls.user), 'w') as f:
                    f.write("{} {}\n".format(
                        pkey.get_name(), pkey.get_base64()).encode('utf-8'))

    def setUp(self):
        # Generate an ECDSA key and add it to the server
        self.key = paramiko.ECDSAKey.generate()
        self.addKeyToServer(self.key)
        # Write the key to a file
        key_fd, self.key_file = tempfile.mkstemp()
        os.close(key_fd)
        self.key.write_private_key_file(self.key_file)
        #with open(key_fd, 'w+') as key_handle:
        # Create an empty config file
        config_fd, self.config_file = tempfile.mkstemp()
        os.close(config_fd)

    def tearDown(self):
        os.remove(self.key_file)
        #try:
        os.remove(self.config_file)
        #except:
            #pass   # On Windows the file could be still opened by other process

    def assertFunctional(self, ssh_fs):
        test_folder = '/home/{}/{}'.format(self.user, uuid.uuid4().hex)
        ssh_fs.makedir(test_folder)
        with ssh_fs.opendir(test_folder) as test_fs:

            test_fs.makedirs('foo/bär/baz')
            test_fs.writetext('foo/test.txt', 'this is a test.')

            self.assertFalse(test_fs.getinfo('foo/test.txt').is_dir)
            self.assertTrue(test_fs.getinfo('foo/bär').is_dir)
            self.assertEqual(sorted(test_fs.listdir('foo')), ['bär', 'test.txt'])

            self.assertRaises(fs.errors.ResourceNotFound, test_fs.remove, 'dog')
            test_fs.move('foo/test.txt', 'foo/bär/test.txt')
            self.assertFalse(test_fs.exists('foo/test.txt'))
            self.assertTrue(test_fs.exists('foo/bär/test.txt'))
            self.assertEqual(test_fs.readtext('foo/bär/test.txt'), 'this is a test.')

            self.assertRaises(fs.errors.DirectoryNotEmpty, test_fs.removedir, 'foo/bär')
            test_fs.removedir('foo/bär/baz')
            self.assertFalse(test_fs.exists('foo/bär/baz'))

        ssh_fs.close()

    def test_password(self):
        ssh_fs = SSHFS('localhost', self.user, self.pasw, port=self.port)
        self.assertFunctional(ssh_fs)

    def test_publickey(self):
        ssh_fs = SSHFS('localhost', self.user, port=self.port, pkey=self.key)
        self.assertFunctional(ssh_fs)

    def test_publickey_file(self):
        ssh_fs = SSHFS('localhost', self.user, port=self.port, pkey=self.key_file)
        self.assertFunctional(ssh_fs)

    def test_create_passwd(self):
        directory = fs.path.join("home", self.user, "test_pwd", "directory")
        base = "mssh://{}:{}@localhost:{}".format(self.user, self.pasw, self.port)
        url = "{}/{}".format(base, directory)

        # Make sure unexisting directory raises `CreateFailed`
        with self.assertRaises(fs.errors.CreateFailed):
            ssh_fs = fs.open_fs(url)

        # Open with `create` and try touching a file
        with fs.open_fs(url, create=True) as ssh_fs:
            ssh_fs.touch("foo")

        # Open the base filesystem and check the subdirectory exists
        with fs.open_fs(base) as ssh_fs:
            self.assertTrue(ssh_fs.isdir(directory))
            self.assertTrue(ssh_fs.isfile(fs.path.join(directory, "foo")))

        # Open without `create` and check the file exists
        with fs.open_fs(url) as ssh_fs:
            self.assertTrue(ssh_fs.isfile("foo"))

        # Open with create and check this does fail
        with fs.open_fs(url, create=True) as ssh_fs:
            self.assertTrue(ssh_fs.isfile("foo"))

    def test_create_pkey(self):

        directory = fs.path.join("home", self.user, "test_pkey", "directory")
        base = "mssh://{}@localhost:{}".format(self.user, self.port)
        root_url = "{}?pkey={}".format(base, self.key_file)
        url = "{}/{}?pkey={}".format(base, directory, self.key_file)

        # Make sure unexisting directory raises `CreateFailed`
        with self.assertRaises(fs.errors.CreateFailed):
            ssh_fs = fs.open_fs(url)

        # Open with `create` and try touching a file
        with fs.open_fs(url, create=True) as ssh_fs:
            ssh_fs.touch("foo")

        # Open the base filesystem and check the subdirectory exists
        with fs.open_fs(root_url) as ssh_fs:
            self.assertTrue(ssh_fs.isdir(directory))
            self.assertTrue(ssh_fs.isfile(fs.path.join(directory, "foo")))

        # Open without `create` and check the file exists
        with fs.open_fs(url) as ssh_fs:
            self.assertTrue(ssh_fs.isfile("foo"))

        # Open with create and check this does fail
        with fs.open_fs(url, create=True) as ssh_fs:
            self.assertTrue(ssh_fs.isfile("foo"))

