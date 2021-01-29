# coding: utf-8
"""Pyfilesystem2 over SSH using paramiko.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from .sshfs import SSHFS

__license__ = "LGPLv2+"
__copyright__ = "Copyright (c) 2017-2021 Martin Larralde"
__author__ = "Martin Larralde <martin.larralde@embl.de>"
__version__ = (
    __import__("pkg_resources")
    .resource_string(__name__, "_version.txt")
    .strip()
    .decode("ascii")
)
