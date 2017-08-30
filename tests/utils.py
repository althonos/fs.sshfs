# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import time

try:
    import docker
    docker_client = docker.from_env(version='auto')
except Exception:
    docker_client = None

try:
    from unittest import mock   # pylint: disable=unused-import
except ImportError:
    import mock                 # pylint: disable=unused-import


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
