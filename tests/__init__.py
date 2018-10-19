# coding: utf-8
from __future__ import unicode_literals
from __future__ import absolute_import

import fs
import os
import pkg_resources


# Add additional openers to the entry points
pkg_resources.get_entry_map('fs', 'fs.opener')['ssh'] = \
    pkg_resources.EntryPoint.parse(
        'ssh = sshfs.opener:SSHOpener',
        dist=pkg_resources.get_distribution('fs')
    )
