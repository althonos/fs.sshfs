# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import docker
import os

try:
    docker.from_env().info()
except Exception:
    DOCKER=False
else:
    DOCKER=True
