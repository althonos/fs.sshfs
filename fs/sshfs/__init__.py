# coding: utf-8
"""Pyfilesystem2 over SSH using paramiko.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from .sshfs import SSHFS

__license__ = "LGPL-2.1+"
__copyright__ = "Copyright (c) 2017 Martin Larralde"
__author__ = "Martin Larralde <martin.larralde@ens-cachan.fr>"
__version__ = 'dev'

# Dynamically get the version of the installed module
try:
    import pkg_resources
    __version__ = pkg_resources.get_distribution(__name__).version
except Exception: # pragma: no cover
    pkg_resources = None
finally:
    del pkg_resources
