# coding: utf-8
"""Enums used in `fs.sshfs`.
"""
from __future__ import unicode_literals
from __future__ import absolute_import

import enum


class Platform(object):
    _Unknown = 0
    Windows = 1

    Linux = 10
    BSD = 11
    Darwin = 12

    Unix = frozenset((Linux, BSD, Darwin))
