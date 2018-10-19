# coding: utf-8
from __future__ import unicode_literals
from __future__ import absolute_import

import configparser

import six

from fs.opener.base import Opener
from fs.subfs import ClosingSubFS
from fs.errors import FSError, CreateFailed


class SSHOpener(Opener):
    protocols = ['ssh']

    @staticmethod
    def open_fs(fs_url, parse_result, writeable, create, cwd):
        from ._sshfs import SSHFS
        ssh_host, _, dir_path = parse_result.resource.partition('/')
        ssh_host, _, ssh_port = ssh_host.partition(':')
        ssh_port = int(ssh_port) if ssh_port.isdigit() else 22

        params = configparser.ConfigParser()
        params.read_dict({'sshfs':getattr(parse_result, 'params', {})})

        ssh_fs = SSHFS(
            ssh_host,
            port=ssh_port,
            user=parse_result.username,
            passwd=parse_result.password,
            pkey=params.get('sshfs', 'pkey', fallback=None),
            timeout=params.getint('sshfs', 'timeout', fallback=10),
            keepalive=params.getint('sshfs', 'keepalive', fallback=10),
            compress=params.getboolean('sshfs', 'compress', fallback=False),
            config_path=\
                params.get('sshfs', 'config_path', fallback='~/.ssh/config')
        )

        try:
            if dir_path:
                if create:
                    ssh_fs.makedirs(dir_path, recreate=True)
                return ssh_fs.opendir(dir_path, factory=ClosingSubFS)
            else:
                return ssh_fs
        except Exception as err:
            six.raise_from(CreateFailed, err)
