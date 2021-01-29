# coding: utf-8
from __future__ import unicode_literals
from __future__ import absolute_import

import configparser

import six

from .base import Opener
from .registry import registry
from ..subfs import ClosingSubFS
from ..errors import FSError, CreateFailed

__license__ = "LGPLv2+"
__copyright__ = "Copyright (c) 2017-2021 Martin Larralde"
__author__ = "Martin Larralde <martin.larralde@embl.de>"
__version__ = __version__ = (
    __import__("pkg_resources")
    .resource_string("fs.sshfs", "_version.txt")
    .strip()
    .decode("ascii")
)


class SSHOpener(Opener):
    protocols = ['ssh']

    @staticmethod
    def open_fs(fs_url, parse_result, writeable, create, cwd):
        from ..sshfs import SSHFS
        ssh_host, _, dir_path = parse_result.resource.partition('/')
        ssh_host, _, ssh_port = ssh_host.partition(':')
        ssh_port = int(ssh_port) if ssh_port.isdigit() else 22

        params = configparser.ConfigParser()
        params.read_dict({'sshfs':getattr(parse_result, 'params', {})})

        ssh_fs = SSHFS(
            ssh_host,
            user=parse_result.username,
            passwd=parse_result.password,
            pkey=params.get('sshfs', 'pkey', fallback=None),
            timeout=params.getint('sshfs', 'timeout', fallback=10),
            port=ssh_port,
            keepalive=params.getint('sshfs', 'keepalive', fallback=10),
            compress=params.getboolean('sshfs', 'compress', fallback=False),
            config_path=\
                params.get('sshfs', 'config_path', fallback='~/.ssh/config'),
            exec_timeout=params.getint('sshfs', 'timeout', fallback=None),
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


registry.install(SSHOpener)
