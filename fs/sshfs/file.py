# coding: utf-8
"""Implementation of `SSHFile`.
"""
from __future__ import unicode_literals
from __future__ import absolute_import

import io

from ..iotools import RawWrapper


class SSHFile(RawWrapper):
    """A file on a remote SSH server.
    """

    def seek(self, offset, whence=0):  # noqa: D102
        if whence > 2:
            raise ValueError("invalid whence "
                             "({}, should be 0, 1 or 2)".format(whence))
        self._f.seek(offset, whence)
        return self.tell()

    def read(self, size=-1):  # noqa: D102
        size = None if size==-1 else size
        return self._f.read(size)

    def readline(self, size=-1):  # noqa: D102
        size = None if size==-1 else size
        return self._f.readline(size)

    def truncate(self, size=None):  # noqa: D102
        size = size if size is not None else self._f.tell()  # SFTPFile doesn't support
        self._f.truncate(size)                               # truncate without argument
        return size

    def readlines(self, hint=-1):  # noqa: D102
        hint = None if hint==-1 else hint
        return self._f.readlines(hint)

    @staticmethod
    def fileno():  # noqa: D102
        raise io.UnsupportedOperation('fileno')
