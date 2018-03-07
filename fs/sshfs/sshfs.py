# coding: utf-8
"""Implementation of `SSHFS`.
"""
from __future__ import unicode_literals
from __future__ import absolute_import

import io
import os
import stat
import socket

import six
import paramiko

from .. import errors
from ..base import FS
from ..info import Info
from ..enums import ResourceType
from ..iotools import RawWrapper
from ..path import basename
from ..permissions import Permissions
from ..osfs import OSFS
from ..mode import Mode

from .file import SSHFile
from .error_tools import convert_sshfs_errors


class SSHFS(FS):
    """A SSH filesystem using SFTP.

    Arguments:
        host (str): a SSH host or IP adress, e.g. ``shell.openshells.net``
        user (str): the username to connect with (defaults to the current user)
        passwd (str): Password for the server, or ``None`` for passwordless
            authentification. If given, it will be discarded immediately after
            establishing the connection.
        pkey (paramiko.PKey): a private key or a list of private key  to use.
            If ``None`` is supplied, the SSH Agent will be used to look for
            keys.
        port (int): Port number (defaults to 22).
        keepalive (int): the number of seconds after which a keep-alive message
            is sent (set to 0 to disable keepalive, default is 10).
        compress (bool): set to ``True`` to compress the messages (disable by
            default).

    Raises:
        fs.errors.CreateFailed: when the filesystem could not be created. The
            source exception is stored as the ``exc`` attribute of the
            ``CreateFailed`` error.
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

    @staticmethod
    def _get_ssh_config(config_path='~/.ssh/config'):
        """Extract the configuration located at ``config_path``.

        Returns:
            paramiko.SSHConfig: the configuration instance.
        """
        ssh_config = paramiko.SSHConfig()
        try:
            with open(os.path.realpath(os.path.expanduser(config_path))) as f:
                ssh_config.parse(f)
        except IOError:
            pass
        return ssh_config


    def __init__(self, host, user=None, passwd=None, pkey=None, timeout=10,
                 port=22, keepalive=10, compress=False,
                 config_path='~/.ssh/config'):  # noqa: D102
        super(SSHFS, self).__init__()

        # Attempt to get a configuration for the given host
        ssh_config = self._get_ssh_config(config_path)
        config = ssh_config.lookup(host)
        pkey = config.get('identityfile') or pkey
        # Extract the given info
        pkey, keyfile= (pkey, None) \
            if isinstance(pkey, paramiko.PKey) else (None, pkey)
        self._user = user = user or config.get('user')
        self._host = host = config.get('hostname')
        self._port = port = int(config.get('port', port))
        self._client = client = paramiko.SSHClient()
        self._locale = None

        try:

            # TODO: add more options
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                socket.gethostbyname(host), port, user, passwd,
                pkey=pkey, key_filename=keyfile,
                look_for_keys=True if (pkey and keyfile) is None else False,
                compress=compress, timeout=timeout
            )

            if keepalive > 0:
                client.get_transport().set_keepalive(keepalive)
            self._sftp = client.open_sftp()
            self._platform = None

        except (paramiko.ssh_exception.SSHException,            # protocol errors
                paramiko.ssh_exception.NoValidConnectionsError, # connexion errors
                socket.gaierror, socket.timeout) as e:          # TCP errors

            message = "Unable to create filesystem: {}".format(e)
            raise errors.CreateFailed(message)

    def close(self):  # noqa: D102
        self._client.close()
        super(SSHFS, self).close()

    def getinfo(self, path, namespaces=None):  # noqa: D102
        self.check()
        namespaces = namespaces or ()
        _path = self.validatepath(path)

        with convert_sshfs_errors('getinfo', path):
            _stat = self._sftp.lstat(_path)
            return self._make_info(basename(_path), _stat, namespaces)

    def geturl(self, path, purpose='download'):  # noqa: D102
        _path = self.validatepath(path)
        if purpose != 'download':
            raise errors.NoURL(path, purpose)
        return "ssh://{}@{}:{}{}".format(
            self._user, self._host, self._port, _path)

    def listdir(self, path):  # noqa: D102
        self.check()
        _path = self.validatepath(path)

        _type = self.gettype(_path)
        if _type is not ResourceType.directory:
            raise errors.DirectoryExpected(path)

        with convert_sshfs_errors('listdir', path):
            return self._sftp.listdir(_path)

    def makedir(self, path, permissions=None, recreate=False):  # noqa: D102
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

    def openbin(self, path, mode='r', buffering=-1, **options):  # noqa: D102
        """Open a binary file-like object.

        Arguments:
            path (str): A path on the filesystem.
            mode (str): Mode to open the file (must be a valid, non-text mode).
                Since this method only opens binary files, the ``b`` in the mode
                is implied.
            buffering (int): the buffering policy (-1 to use default buffering,
                0 to disable completely, 1 to enable line based buffering, or
                any larger positive integer for a custom buffer size).

        Keyword Arguments:
            pipelined (bool): Set the transfer in pipelined mode (should
                improve transfer speed). Defaults to ``True``.

        Raises:
            fs.errors.FileExpected: if the path if not a file.
            fs.errors.FileExists: if the file already exists and
                *exclusive mode* is specified (``x`` in the mode).
            fs.errors.ResourceNotFound: if the path does not exist.

        Returns:
            io.IOBase: a file handle.
        """
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
                handle = self._sftp.open(
                    _path,
                    mode=_mode.to_platform_bin(),
                    bufsize=buffering
                )
                handle.set_pipelined(options.get("pipelined", True))
                return SSHFile(handle)

    def remove(self, path):  # noqa: D102
        self.check()
        _path = self.validatepath(path)

        # NB: this will raise ResourceNotFound
        # as expected by the specifications
        if self.getinfo(_path).is_dir:
            raise errors.FileExpected(path)

        with convert_sshfs_errors('remove', path):
            with self._lock:
                self._sftp.remove(_path)

    def removedir(self, path):  # noqa: D102
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

    def setinfo(self, path, info):  # noqa: D102
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

    @property
    def platform(self):
        """The platform the server is running on.

        Returns:
            fs.sshfs.enums.Platform: the platform of the remote server.
        """
        if self._platform is None:
            self._platform = self._guess_platform()
        return self._platform

    @property
    def locale(self):
        """The locale the server is running on.

        Returns:
            str: the locale of the remote server.
        """
        if self._locale is None:
            self._locale = self._guess_locale()
        return self._locale

    def _exec_command(self, cmd):
        """Run a command on the remote SSH server.

        Returns:
            bytes: the output of the command, if it didn't fail
            None: if the error pipe of the command was not empty
        """
        _, out, err = self._client.exec_command(cmd)
        return out.read().strip() if not err.read().strip() else None

    def _guess_platform(self):
        """Guess the platform of the remove server.

        Returns:
            fs.sshfs.enums.Platform: the guessed platform.
        """
        uname_sys = self._exec_command("uname -s")
        sysinfo = self._exec_command("sysinfo")
        if uname_sys is not None:
            if uname_sys == b"FreeBSD":
                return "freebsd"
            elif uname_sys == b"Darwin":
                return "darwin"
            elif uname_sys == b"Linux":
                return "linux"
            elif uname_sys.startswith(b"CYGWIN"):
                return "cygwin"
        elif sysinfo is not None and sysinfo:
            return "win32"
        return "unknown"

    def _guess_locale(self):
        """Guess the locale of the remote server.

        Returns:
            str: the guessed locale.
        """
        if self.platform in ("linux", "darwin", "freebsd"):
            locale = self._exec_command('echo $LANG')
            if locale is not None:
                return locale.split(b'.')[-1].decode('ascii').lower()
        return None

    def _make_info(self, name, stat_result, namespaces):
        """Create an `Info` object from a stat result.
        """
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
        """Make a *details* dictionnary from a stat result.
        """
        details = {
            '_write': ['accessed', 'modified'],
            'accessed': stat_result.st_atime,
            'modified': stat_result.st_mtime,
            'size': stat_result.st_size,
            'type': int(OSFS._get_type_from_stat(stat_result)),
        }

        details['created'] = getattr(stat_result, 'st_birthtime', None)
        ctime_key = 'created' if self.platform=="win32" else 'metadata_changed'
        details[ctime_key] = getattr(stat_result, 'st_ctime', None)
        return details

    def _make_access_from_stat(self, stat_result):
        """Make an *access* dictionnary from a stat result.
        """
        access = {}
        access['permissions'] = Permissions(mode=stat_result.st_mode).dump()
        access['gid'] = stat_result.st_gid
        access['uid'] = stat_result.st_uid

        if self.platform in ("linux", "darwin", "freebsd"):
            def entry_name(db, _id):
                entry = self._exec_command('getent {} {}'.format(db, _id))
                name = next(iter(entry.split(b':')))
                return name.decode(self.locale or 'utf-8')
            access['group'] = entry_name('group', access['gid'])
            access['user'] = entry_name('passwd', access['uid'])

        return access

    def _chmod(self, path, mode):
        """Change the *mode* of a resource.
        """
        self._sftp.chmod(path, mode)

    def _chown(self, path, uid, gid):
        """Change the *owner* of a resource.
        """
        if uid is None or gid is None:
            info = self.getinfo(path, namespaces=('access',))
            uid = uid or info.get('access', 'uid')
            gid = gid or info.get('access', 'gid')
        self._sftp.chown(path, uid, gid)

    def _utime(self, path, modified, accessed):
        """Set the *accessed* and *modified* times of a resource.
        """
        if accessed is not None or modified is not None:
            accessed = int(modified if accessed is None else accessed)
            modified = int(accessed if modified is None else modified)
            self._sftp.utime(path, (accessed, modified))
        else:
            self._sftp.utime(path, None)
