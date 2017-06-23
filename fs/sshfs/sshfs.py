# coding: utf-8
from __future__ import unicode_literals
from __future__ import absolute_import

import io
import six
import stat
import enum
import socket
import paramiko

from .error_tools import convert_sshfs_errors
from .. import errors
from ..base import FS
from ..info import Info
from ..enums import ResourceType
from ..iotools import RawWrapper
from ..path import basename
from ..permissions import Permissions
from ..osfs import OSFS
from ..mode import Mode


class _SSHFileWrapper(RawWrapper):
    """A file on a remote SSH server.
    """

    def seek(self, offset, whence=0):
        if whence > 2:
            raise ValueError("invalid whence "
                             "({}, should be 0, 1 or 2)".format(whence))
        return self._f.seek(offset, whence)

    def read(self, size=-1):
        size = None if size==-1 else size
        return self._f.read(size)

    def readline(self, size=-1):
        size = None if size==-1 else size
        return self._f.readline(size)

    def truncate(self, size=None):
        size = size or self._f.tell()   # SFTPFile doesn't support
        return self._f.truncate(size)   # truncate without argument

    def readlines(self, hint=-1):
        hint = None if hint==-1 else hint
        return self._f.readlines(hint)

    @staticmethod
    def fileno():
        raise io.UnsupportedOperation('fileno')


class _SSHServerPlatform(enum.Enum):
    _Unknow = 0
    Windows = 1

    Linux = 10
    BSD = 11
    Darwin = 12

    Unix = (Linux, BSD, Darwin)




class SSHFS(FS):
    """A SSH filesystem using SFTP.

    :param str host: A SSH host, e.g. ``shell.openshells.net``.
    :param str user: A username (default is current user username).
    :param str passwd: Password for the server, or ``None`` for
        passwordless / key authentification. If given, it will be
        immediately discared after establishing the connection.
    :param pkey: A private key or a list of private keys to use. If none
        provided, the SSH Agent will be used to look for keys.
    :type pkey: str, list[str] or ``paramiko.PKey``
    :param int port: Port number (default is 22).
    :param int keepalive: The number of second after which a keep-alive
        message will be sent (set to 0 to disable keepalive, default is 10)
    :param bool compress: If the messages should be transfered or not
        (default: False).

    :raises `fs.errors.CreateFailed`: If the server could not be connected to.
    """


    _meta = {
        'case_insensitive': False,
        'invalid_path_chars': '\0',
        'network': True,
        'read_only': False,
        'thread_safe': True,
        'unicode_paths': True,
        'virtual': False,
    }

    @classmethod
    def _make_access_from_stat(cls, stat_result):
        access = {}
        access['permissions'] = Permissions(
            mode=stat_result.st_mode
        ).dump()
        access['gid'] = stat_result.st_gid
        access['uid'] = stat_result.st_uid

        # FIXME: need to extract directly through SSH
        # if not _WINDOWS_PLATFORM:
        #     import grp
        #     import pwd
        #     try:
        #         access['group'] = grp.getgrgid(access['gid']).gr_name
        #     except KeyError:  # pragma: nocover
        #         pass
        #
        #     try:
        #         access['user'] = pwd.getpwuid(access['uid']).pw_name
        #     except KeyError:  # pragma: nocover
        #         pass
        return access

    def __init__(self,
                 host,
                 user=None,
                 passwd=None,
                 pkey=None,
                 timeout=10,
                 port=22,
                 keepalive=10,
                 compress=False,
                 ):
        super(SSHFS, self).__init__()

        try:

            # TODO: add more options
            self._user = user
            self._host = host
            self._port = port
            self._client = client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                host, port, user, passwd, pkey,
                look_for_keys=True if pkey is None else False,
                compress=compress, timeout=timeout
            )

            if keepalive > 0:
                client.get_transport().set_keepalive(keepalive)
            self._sftp = client.open_sftp()
            self._platform = self._guess_platform()

        except (paramiko.ssh_exception.SSHException,            # protocol errors
                paramiko.ssh_exception.NoValidConnectionsError, # connexion errors
                socket.gaierror, socket.timeout) as e:          # TCP errors

            message = "Unable to create filesystem: {}".format(e)
            six.raise_from(errors.CreateFailed(message), e)

    def close(self):
        self._client.close()
        super(SSHFS, self).close()

    def getinfo(self, path, namespaces=None):
        self.check()
        namespaces = namespaces or ()
        _path = self.validatepath(path)

        with convert_sshfs_errors('getinfo', path):
            _stat = self._sftp.lstat(_path)
            return self._make_info(basename(_path), _stat, namespaces)

    def getsyspath(self, path):
        _path = self.validatepath(path)
        return "ssh://{}@{}:{}{}".format(
            self._user, self._host, self._port, _path)

    def listdir(self, path):
        self.check()
        _path = self.validatepath(path)

        _type = self.gettype(_path)
        if _type is not ResourceType.directory:
            raise errors.DirectoryExpected(path)

        with convert_sshfs_errors('listdir', path):
            return self._sftp.listdir(_path)

    def makedir(self, path, permissions=None, recreate=False):
        self.check()
        _permissions = permissions or Permissions(mode=0o755)
        _path = self.validatepath(path)

        try:
            info = self.getinfo(_path)
        except errors.ResourceNotFound:
            with self._lock:
                with convert_sshfs_errors('makedir', path):
                    self._sftp.mkdir(_path, _permissions.mode)
        else:
            if (info.is_dir and not recreate) or info.is_file:
                six.raise_from(errors.DirectoryExists(path), None)

        return self.opendir(path)

    def openbin(self, path, mode='r', buffering=-1, **options):
        """Open a binary file-like object.

        :param str path: A path on the filesystem.
        :param str mode: Mode to open file (must be a valid non-text
          mode). Since this method only opens binary files, the `b` in
          the mode string is implied.
        :param buffering: Buffering policy (-1 to use default
          buffering, 0 to disable buffering, 1 to enable line based
          buffering, or any larger positive integer to indicate buffer size).
        :type buffering: int
        :param options: Keyword parameters for any additional
          information required by the filesystem (if any).
        :rtype: file object

        :raises fs.errors.FileExpected: If the path is not a file.
        :raises fs.errors.FileExists: If the file exists, and
          *exclusive mode* is specified (`x` in the mode).
        :raises fs.errors.ResourceNotFound: If `path` does not exist.

        """
        #
        # Buffering follows the paramiko spec, not the fs one
        # (only difference is that buffering=1 means line based buffering,
        # not an actual buffer size of 1.
        # """
        self.check()
        _path = self.validatepath(path)
        _mode = Mode(mode)
        _mode.validate_bin()

        with self._lock:
            if _mode.exclusive and self.exists(_path):
                raise errors.FileExists(path)
            elif _mode.reading and not _mode.create and not self.exists(_path):
                raise errors.ResourceNotFound(path)
            elif self.isdir(_path):
                raise errors.FileExpected(path)
            with convert_sshfs_errors('openbin', path):
                return _SSHFileWrapper(self._sftp.open(
                    _path,
                    mode=_mode.to_platform_bin(),
                    bufsize=buffering))

    def remove(self, path):
        self.check()
        _path = self.validatepath(path)

        # NB: this will raise ResourceNotFound
        # and as expected by the specifications
        _type = self.gettype(_path)
        if _type is ResourceType.directory:
            raise errors.FileExpected(path)

        with convert_sshfs_errors('remove', path):
            with self._lock:
                self._sftp.remove(_path)

    def removedir(self, path):
        self.check()
        _path = self.validatepath(path)

        # NB: this will raise ResourceNotFound
        # and DirectoryExpected as expected by
        # the specifications
        if not self.isempty(path):
            raise errors.DirectoryNotEmpty(path)

        with convert_sshfs_errors('removedir', path):
            with self._lock:
                self._sftp.rmdir(path)

    def setinfo(self, path, info):
        self.check()
        _path = self.validatepath(path)

        if not self.exists(path):
            raise errors.ResourceNotFound(path)

        access = info.get('access', {})
        details = info.get('details', {})

        with convert_sshfs_errors('setinfo', path):
            if 'accessed' in details or 'modified' in details:
                self._utime(path,
                            details.get("modified"),
                            details.get("accessed"))
            if 'uid' in access or 'gid' in access:
                self._chown(path,
                            access.get('uid'),
                            access.get('gid'))
            if 'permissions' in access:
                self._chmod(path, access['permissions'].mode)

    def _guess_platform(self):

        def exec_command(cmd):
            _, out, err = self._client.exec_command(cmd)
            return out.read().strip() if not err.read().strip() else None

        uname_sys = exec_command("uname -s")
        sysinfo = exec_command("sysinfo")

        if sysinfo is not None and sysinfo:
            return _SSHServerPlatform.Windows

        elif uname_sys is not None:
            if uname_sys.endswith(b"BSD") or uname_sys == b"DragonFly":
                return _SSHServerPlatform.BSD
            elif uname_sys == b"Darwin":
                return _SSHServerPlatform.Darwin
            elif uname_sys == b"Linux":
                return _SSHServerPlatform.Linux

        return _SSHServerPlatform._Unknown

    def _make_info(self, name, stat_result, namespaces):
        info = {
            'basic': {
                'name': name,
                'is_dir': stat.S_ISDIR(stat_result.st_mode)
            }
        }
        if 'details' in namespaces:
            info['details'] = self._make_details_from_stat(stat_result)
        if 'stat' in namespaces:
            info['stat'] = {
                k: getattr(stat_result, k)
                for k in dir(stat_result) if k.startswith('st_')
            }
        if 'access' in namespaces:
            info['access'] = self._make_access_from_stat(stat_result)
        return Info(info)

    def _make_details_from_stat(self, stat_result):
        """Make an info dict from a stat_result object."""
        details = {
            '_write': ['accessed', 'modified'],
            'accessed': stat_result.st_atime,
            'modified': stat_result.st_mtime,
            'size': stat_result.st_size,
            'type': int(OSFS._get_type_from_stat(stat_result)),
        }

        details['created'] = getattr(stat_result, 'st_birthtime', None)
        ctime_key = 'created' if self._platform is _SSHServerPlatform.Windows \
               else 'metadata_changed'
        details[ctime_key] = getattr(stat_result, 'st_ctime', None)
        return details

    def _chmod(self, path, mode):
        self._sftp.chmod(path, mode)

    def _chown(self, path, uid, gid):
        if uid is None or gid is None:
            info = self.getinfo(path, namespaces=('access',))
            uid = uid or info.get('access', 'uid')
            gid = gid or info.get('access', 'gid')
        self._sftp.chown(path, uid, gid)

    def _utime(self, path, modified, accessed):
        if accessed is not None or modified is not None:
            accessed = int(modified if accessed is None else accessed)
            modified = int(accessed if modified is None else modified)
            self._sftp.utime(path, (accessed, modified))
        else:
            self._sftp.utime(path, None)
