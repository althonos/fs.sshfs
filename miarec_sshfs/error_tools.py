# coding: utf-8
"""Utils to work with `paramiko` errors.
"""
import errno
import socket
import ssl
from contextlib import contextmanager

from fs import errors

import logging
log = logging.getLogger(__name__)

import typing
if typing.TYPE_CHECKING:
    from .sshfs import SSHFS


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


@contextmanager
def ignore_network_errors(op):
    """Ignore Socket and SSL errors"""
    try:
        yield
    except (ssl.SSLError, socket.error) as error:
        log.info(f"[{op}] Unexpected network error (ignoring): {error}")
        pass   # do nothing


@contextmanager
def convert_sshfs_errors(fs: "SSHFS", path=None, op=None, directory=False):
    """Convert Socket and SSH/SFTP protocol errors into the appropriate FSError types"""

    try:
        yield

    except ssl.SSLError as error:
        log.info('SFTP SSL Socket error: %s' % error)
        raise errors.RemoteConnectionError(
            msg=f"SFTP connection SSL error (host={fs._host}:{fs._port} op={op}): {error}"
        )

    except socket.timeout as error:
        log.info('SFTP Socket timeout error: %s' % error)
        raise errors.RemoteConnectionError(
            msg=f"SFTP operation timed out (host={fs._host}:{fs._port} op={op} path={path})"
        )

    except EOFError as error:    # EOFError is raised when SSH connection is closed by remote side
        log.info('SFTP Unexpected EOF: %s' % error)
        raise errors.RemoteConnectionError(
            msg=f"SFTP lost connection to {fs._host}:{fs._port} op={op} path={path}"
        )

    except OSError as error:   # Generic OSError (it can include socket.error)
        log.info('SFTP error: %s' % error)
        ssh_errors = DIR_ERRORS if directory else FILE_ERRORS
        _errno = error.errno

        fserror = ssh_errors.get(_errno, None)
        if fserror:
            raise fserror(path, exc=error)

        # Anything else, would be a remote connection error.
        # Paramiko returns socket.error for any connection related issues, for example, when socket is closed
        # The `socket.error` is just an alias to `OSError`
        raise errors.RemoteConnectionError(
            msg=f"SFTP lost connection to {fs._host}:{fs._port} op={op} path={path}"
        )
