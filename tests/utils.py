# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import time
import warnings
import socket, errno

import fs
import semantic_version

try:
    import docker
    docker_client = docker.from_env(version='auto')
except Exception as err:
    warnings.warn("Failed to start Docker client: {}".format(err))
    docker_client = None

try:
    from unittest import mock   # pylint: disable=unused-import
except ImportError:
    import mock                 # pylint: disable=unused-import


def fs_version():
    return semantic_version.Version(fs.__version__)


def startServer(docker_client, user, pasw, port):
    sftp_container = docker_client.containers.run(
        "sjourdan/alpine-sshd", detach=True, remove=True, auto_remove=True,
        ports={'22/tcp': port},
        environment={'USER': user, 'PASSWORD': pasw},
    )
    time.sleep(1)
    return sftp_container


def stopServer(server_container):
    server_container.kill()


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(('localhost', port)) == 0


def find_available_port(begin_port = 2222, end_port=3222):
    """
    Find available port to use for SFTP server.

    This function tries to bind to port in range and return the one 
    that is not in use.
    """

    for port in range(begin_port, end_port):
        if not is_port_in_use(port):
            return port

    raise RuntimeError("Could not find available port in range {begin_port}..{end_port}")
