# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import docker
import os

try:
    docker.from_env(version='auto').info()
except Exception:
    DOCKER=False
else:
    DOCKER=True

try:
    from unittest import mock
except ImportError:
    import mock

CI = os.getenv('CI', '').lower() == 'true'
