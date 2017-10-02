# coding: utf-8
"""Utils to work with `paramiko` errors.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import errno
import sys

import six

from .. import errors


class _ConvertSSHFSErrors(object):
    """Context manager to convert OSErrors in to FS Errors."""

    FILE_ERRORS = {
        64: errors.RemoteConnectionError,  # ENONET
        errno.ENOENT: errors.ResourceNotFound,
        errno.EFAULT: errors.ResourceNotFound,
        errno.ESRCH: errors.ResourceNotFound,
        errno.ENOTEMPTY: errors.DirectoryNotEmpty,
        errno.EEXIST: errors.FileExists,
        183: errors.DirectoryExists,
        #errno.ENOTDIR: errors.DirectoryExpected,
        errno.ENOTDIR: errors.ResourceNotFound,
        errno.EISDIR: errors.FileExpected,
        errno.EINVAL: errors.FileExpected,
        errno.ENOSPC: errors.InsufficientStorage,
        errno.EPERM: errors.PermissionDenied,
        errno.EACCES: errors.PermissionDenied,
        errno.ENETDOWN: errors.RemoteConnectionError,
        errno.ECONNRESET: errors.RemoteConnectionError,
        errno.ENAMETOOLONG: errors.PathError,
        errno.EOPNOTSUPP: errors.Unsupported,
        errno.ENOSYS: errors.Unsupported,
    }
    #
    DIR_ERRORS = FILE_ERRORS.copy()
    DIR_ERRORS[errno.ENOTDIR] = errors.DirectoryExpected
    DIR_ERRORS[errno.EEXIST] = errors.DirectoryExists
    DIR_ERRORS[errno.EINVAL] = errors.DirectoryExpected

    # if _WINDOWS_PLATFORM:  # pragma: no cover
    #     DIR_ERRORS[13] = errors.DirectoryExpected
    #     DIR_ERRORS[267] = errors.DirectoryExpected
    #     FILE_ERRORS[13] = errors.FileExpected

    def __init__(self, opname, path, directory=False):
        self._opname = opname
        self._path = path
        self._directory = directory

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        ssh_errors = (
            self.DIR_ERRORS
            if self._directory
            else self.FILE_ERRORS
        )

        if exc_type and isinstance(exc_value, EnvironmentError):
            _errno = exc_value.errno
            fserror = ssh_errors.get(_errno, errors.OperationFailed)
            if _errno == errno.EACCES and sys.platform == "win32":
                if getattr(exc_value, 'args', None) == 32:  # pragma: no cover
                    fserror = errors.ResourceLocked
            six.reraise(
                fserror,
                fserror(
                    self._path,
                    exc=exc_value
                ),
                traceback
            )

# Stops linter complaining about invalid class name
convert_sshfs_errors = _ConvertSSHFSErrors
