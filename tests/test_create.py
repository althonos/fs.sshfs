# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import uuid
import unittest
import tempfile

import docker
import paramiko

import fs.errors
from fs.sshfs import SSHFS

from . import utils


class TestCreateFailed(unittest.TestCase):

    def test_unknown_host(self):
        self.assertRaises(
            fs.errors.CreateFailed, SSHFS, 'unexisting-hostname', timeout=1)

    def test_unknown_user(self):
        self.assertRaises(
            fs.errors.CreateFailed, SSHFS, 'localhost', 'baduser', timeout=1)


class TestCreate(unittest.TestCase):

    user = "user"
    pasw = "pass"
    port = 2223

    @classmethod
    def setUpClass(cls):
        cls.sftp_container = utils.startServer(
            utils.docker_client, cls.user, cls.pasw, cls.port)

    @classmethod
    def tearDownClass(cls):
        utils.stopServer(cls.sftp_container)

    @classmethod
    def addKeyToServer(cls, pkey):
        with paramiko.SSHClient() as client:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect('localhost', cls.port, cls.user, cls.pasw)
            with client.open_sftp() as sftp:
                if not '.ssh' in sftp.listdir('/home/{}'.format(cls.user)):
                    sftp.mkdir('/home/{}/.ssh'.format(cls.user))
                with sftp.open('/home/{}/.ssh/authorized_keys'.format(cls.user), 'w') as f:
                    f.write("{} {}\n".format(
                        pkey.get_name(), pkey.get_base64()).encode('utf-8'))

    def setUp(self):
        # Generate an RSA key and add it to the server
        self.rsa_key = rsa_key = paramiko.RSAKey.generate(bits=512)
        self.addKeyToServer(rsa_key)
        # Write the key to a file
        key_fd, self.key_file = tempfile.mkstemp()
        os.close(key_fd)
        rsa_key.write_private_key_file(self.key_file)
        #with open(key_fd, 'w+') as key_handle:
        # Create an empty config file
        config_fd, self.config_file = tempfile.mkstemp()

    def tearDown(self):
        os.remove(self.key_file)
        os.remove(self.config_file)

    def assertFunctional(self, ssh_fs):
        test_folder = '/home/{}/{}'.format(self.user, uuid.uuid4().hex)
        ssh_fs.makedir(test_folder)
        with ssh_fs.opendir(test_folder) as test_fs:

            test_fs.makedirs('foo/bär/baz')
            test_fs.settext('foo/test.txt', 'this is a test.')

            self.assertFalse(test_fs.getinfo('foo/test.txt').is_dir)
            self.assertTrue(test_fs.getinfo('foo/bär').is_dir)
            self.assertEqual(sorted(test_fs.listdir('foo')), ['bär', 'test.txt'])

            self.assertRaises(fs.errors.ResourceNotFound, test_fs.remove, 'dog')
            test_fs.move('foo/test.txt', 'foo/bär/test.txt')
            self.assertFalse(test_fs.exists('foo/test.txt'))
            self.assertTrue(test_fs.exists('foo/bär/test.txt'))
            self.assertEqual(test_fs.gettext('foo/bär/test.txt'), 'this is a test.')

            self.assertRaises(fs.errors.DirectoryNotEmpty, test_fs.removedir, 'foo/bär')
            test_fs.removedir('foo/bär/baz')
            self.assertFalse(test_fs.exists('foo/bär/baz'))



        ssh_fs.close()

    def test_password(self):
        ssh_fs = SSHFS('localhost', self.user, self.pasw, port=self.port)
        self.assertFunctional(ssh_fs)

    def test_publickey(self):
        ssh_fs = SSHFS('localhost', self.user, port=self.port, pkey=self.rsa_key)
        self.assertFunctional(ssh_fs)

    def test_publickey_file(self):
        ssh_fs = SSHFS('localhost', self.user, port=self.port, pkey=self.key_file)
        self.assertFunctional(ssh_fs)

    def test_sshconfig(self):
        with open(self.config_file, 'w') as conf:
            conf.writelines([
                "Host             test_host\n",
                "  User           {}\n".format(self.user),
                "  Hostname       localhost\n",
                "  Port           {}\n".format(self.port),
                "  IdentityFile   {}\n".format(self.key_file),
                "  IdentitiesOnly yes\n"
            ])
        ssh_fs = SSHFS('test_host', config_path=self.config_file)
        self.assertFunctional(ssh_fs)

    def test_sshconfig_override(self):
        with open(self.config_file, 'w') as conf:
            conf.writelines([
                "Host             test_host\n",
                "  Hostname       localhost\n",
                "  User           no_one\n",
                "  Port           {}\n".format(self.port),
                "  IdentityFile   {}\n".format(self.key_file),
                "  IdentitiesOnly yes\n"
            ])
        ssh_fs = SSHFS('test_host', self.user, config_path=self.config_file)
        self.assertFunctional(ssh_fs)

    def test_sshconfig_notfound(self):
        ssh_fs = SSHFS('localhost', self.user, self.pasw, port=self.port, config_path='zzzz')
        self.assertFunctional(ssh_fs)
