# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import re
import time
import collections

import fs

try:
    import docker
    docker_client = docker.from_env(version='auto')
except Exception:
    docker_client = None

try:
    from unittest import mock   # pylint: disable=unused-import
except ImportError:
    import mock                 # pylint: disable=unused-import


def fs_version():
    version_info = collections.namedtuple(
        'version_info', 'major minor micro releaselevel serial'
    )
    match = re.match(r'v?(\d+)\.(\d+)\.(\d+)(\D+)?(\d+)?', fs.__version__)
    major = int(match.group(1))
    minor = int(match.group(2))
    micro = int(match.group(3))
    level = match.group(4)
    serial = None if match.group(5) is None else int(match.group(5))
    return version_info(major, minor, micro, level, serial)


def startServer(docker_client, user, pasw, port):
    sftp_container = docker_client.containers.run(
        "sjourdan/alpine-sshd", detach=True, ports={'22/tcp': port},
        environment={'USER': user, 'PASSWORD': pasw},
    )
    time.sleep(1)
    return sftp_container


def stopServer(server_container):
    server_container.kill()
    server_container.remove()
