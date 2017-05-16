# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import paramiko
import os


def is_reachable(hostname, port=22, username=None, password=None):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname, port, username, password)
    except (paramiko.ssh_exception.SSHException, paramiko.ssh_exception.NoValidConnectionsError):
        return False
    else:
        return True

SSH_SERVICE_REACHABLE = is_reachable(
        'localhost',
        os.getenv('FS_SSHFS_PORT'),
        os.getenv('FS_SSHFS_USER'),
        os.getenv('FS_SSHFS_PASS'),
)
