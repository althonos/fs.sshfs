# coding: utf-8
"""Implementation of `SSHFS`.
"""
from __future__ import unicode_literals
from __future__ import absolute_import

import itertools
import os
import stat
import socket
import sys

import six
import paramiko
from property_cached import threaded_cached_property as cached_property

from .. import errors
from ..base import FS
from ..info import Info
from ..enums import ResourceType
from ..path import basename, dirname
from ..permissions import Permissions
from ..osfs import OSFS
from ..mode import Mode

from .file import SSHFile
from .error_tools import convert_sshfs_errors


class SSHFS(FS):
    """A SSH filesystem using SFTP.

    Arguments:
        host (str): A SSH host or IP adress, e.g. ``shell.openshells.net``
            or ``127.0.0.1``.
        user (str): the username to connect with (defaults to the current
            user). If ``None`` is given, the SSH configuration file will be
            used if available.
        passwd (str): Password for the server, or ``None`` for passwordless
            authentification. If given, it will be discarded immediately after
            establishing the connection.
        pkey (paramiko.PKey): A private key or a list of private key  to use.
            If ``None`` is supplied, the SSH Agent will be used to look for
            keys.
        timeout (int): The timeout to use when connecting to the SSH server, in
            seconds (defaults to 10).
        port (int): Port number the SSH server is listening on (defaults to 22,
            the usual SSH port).
        keepalive (int): The number of seconds after which a keep-alive message
            is sent (set to 0 to disable keepalive, default is 10).
        compress (bool): Set to ``True`` to compress the messages (disabled by
            default).
        config_path (str): The path to a SSH configuration file to use while
            establishing connection. Defaults to ``~/.ssh/config``, the path
            to the default OpenSSH client configuration file.
        exec_timeout (int): The timeout to use when executing arbitrary
            commands on the SSH server. Defaults to the value of ``timeout``.
        policy (paramiko.MissingHostKeyPolicy): The policy to use to resolve
            missing host keys. Defaults to ``None``, which will create a
            `paramiko.AutoAddPolicy` instance.

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
        'supports_rename': True,
        'thread_safe': sys.version_info[:2] > (3, 4),
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

    def __init__(
            self,
            host,
            user=None,
            passwd=None,
            pkey=None,
            timeout=10,
            port=22,
            keepalive=10,
            compress=False,
            config_path='~/.ssh/config',
            exec_timeout=None,
            policy=None,
            **kwargs
    ):  # noqa: D102
        super(SSHFS, self).__init__()

        # Attempt to get a configuration for the given host
        ssh_config = self._get_ssh_config(config_path)
        config = ssh_config.lookup(host)
        pkey = config.get('identityfile') or pkey
        # Extract the given info
        pkey, keyfile = (pkey, None) \
            if isinstance(pkey, paramiko.PKey) else (None, pkey)
        self._user = user = user or config.get('user')
        self._host = host = config.get('hostname')
        self._port = port = int(config.get('port', port))
        self._client = client = paramiko.SSHClient()
        self._timeout = timeout
        self._exec_timeout = timeout if exec_timeout is None else exec_timeout

        _policy = paramiko.AutoAddPolicy() if policy is None else policy

        try:
            # TODO: add more options
            client.load_system_host_keys()
            client.set_missing_host_key_policy(_policy)
            argdict = {
                "pkey": pkey,
                "key_filename": keyfile,
                "look_for_keys": True if (pkey and keyfile) is None else False,
                "compress": compress,
                "timeout": timeout
            }

            argdict.update(kwargs)

            client.connect(
                socket.gethostbyname(host), port, user, passwd,
                **argdict
            )

            if keepalive > 0:
                client.get_transport().set_keepalive(keepalive)
            self._sftp = client.open_sftp()

        except (paramiko.ssh_exception.SSHException,            # protocol errors
                paramiko.ssh_exception.NoValidConnectionsError,  # connexion errors
                socket.gaierror, socket.timeout) as e:          # TCP errors

            message = "Unable to create filesystem: {}".format(e)
            raise errors.CreateFailed(message)

    if six.PY2:

        def close(self):  # noqa: D102
            self._client.close()
            super(SSHFS, self).close()

    else:

        def close(self): # noqa: D102
            self._client.close()
            super().close()

    def getinfo(self, path, namespaces=None):  # noqa: D102
        self.check()
        namespaces = namespaces or ()
        _path = self.validatepath(path)

        with convert_sshfs_errors('getinfo', path):
            _stat = self._sftp.stat(_path)
            info = self._make_raw_info(basename(_path), _stat, namespaces)

            if "lstat" in namespaces or "link" in namespaces:
                _lstat = self._sftp.lstat(_path)
            if "lstat" in namespaces:
                info["lstat"] = {
                    k: getattr(_lstat, k)
                    for k in dir(_lstat)
                    if k.startswith("st_")
                }
            if "link" in namespaces:
                if OSFS._get_type_from_stat(_lstat) == ResourceType.symlink:
                    target = self._sftp.readlink(_path)
                    info["link"] = {"target": target}
                else:
                    info["link"] = {"target": None}

            return Info(info)

    def geturl(self, path, purpose='download'):  # noqa: D102
        _path = self.validatepath(path)
        if purpose != 'download':
            raise errors.NoURL(path, purpose)
        return "ssh://{}@{}:{}{}".format(
            self._user, self._host, self._port, _path)

    def islink(self, path):  # noqa: D102
        return self.getinfo(path, namespaces=["link"]).is_link

    def listdir(self, path):  # noqa: D102
        self.check()
        _path = self.validatepath(path)

        _type = self.gettype(_path)
        if _type is not ResourceType.directory:
            raise errors.DirectoryExpected(path)

        with convert_sshfs_errors('listdir', path):
            return self._sftp.listdir(_path)

    def scandir(self, path, namespaces=None, page=None):  # noqa: D102
        self.check()
        _path = self.validatepath(path)
        _namespaces = namespaces or ()
        start, stop = page or (None, None)
        try:
            with convert_sshfs_errors('scandir', path, directory=True):
                # We can't use listdir_iter here because it doesn't support
                # concurrent iteration over multiple directories, which can
                # happen during a search="depth" walk.
                listing = self._sftp.listdir_attr(_path)
                for _stat in itertools.islice(listing, start, stop):
                    yield Info(self._make_raw_info(_stat.filename, _stat, _namespaces))
        except errors.ResourceNotFound:
            # When given a bad path to listdir, the sftp client raises IOError
            # with an errno of ENOENT no matter if the path was missing or was
            # the wrong type (e.g., a file).  For the fs API, we need to figure
            # out if it was supposed to be ENOTDIR instead of ENOENT.
            if self.isfile(_path):
                six.raise_from(errors.DirectoryExpected(path), None)
            raise

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

    def move(self, src_path, dst_path, overwrite=False, preserve_time=False):
        info_ns = ("basic", "details") if preserve_time else ("basic",)

        self.check()
        _src_path = self.validatepath(src_path)
        _dst_path = self.validatepath(dst_path)

        with self._lock:
            # check src exists and is a file
            src_info = self.getinfo(_src_path, namespaces=info_ns)
            if src_info.is_dir:
                raise errors.FileExpected(src_path)
            # check dst is not a dir and can be created
            if self.isdir(_dst_path):
                raise errors.FileExpected(dst_path)
            if not self.isdir(dirname(_dst_path)):
                raise errors.ResourceNotFound(dirname(dst_path))
            # check dst does not exist or remove it
            if self.isfile(_dst_path):
                if not overwrite:
                    raise errors.DestinationExists(dst_path)
                with convert_sshfs_errors('move', dst_path):
                    self._sftp.remove(_dst_path)
            # rename the file through SFTP's 'RENAME'
            self._sftp.rename(_src_path, _dst_path)
            # preserve times if required
            if preserve_time:
                self._utime(
                    _path,
                    src_info.raw["details"]["modified"],
                    src_info.raw["details"]["accessed"],
                )

    def openbin(self, path, mode='r', buffering=-1, **options):  # noqa: D102
        """Open a binary file-like object.

        Arguments:
            path (str): A path on the filesystem.
            mode (str): Mode to open the file (must be a valid, non-text mode).
                Since this method only opens binary files, the ``b`` in the
                mode is implied.
            buffering (int): the buffering policy (-1 to use default buffering,
                0 to disable completely, 1 to enable line based buffering, or
                any larger positive integer for a custom buffer size).

        Keyword Arguments:
            pipelined (bool): Set the transfer in pipelined mode (should
                improve transfer speed). Defaults to ``True``.
            prefetch (bool): Use background threading to prefetch the file
                content when opened in reading mode. Disable in case of
                threading issues. Defaults to ``True``.

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
            if _mode.exclusive:
                if self.exists(_path):
                    raise errors.FileExists(path)
                else:
                    _mode = Mode(''.join(set(mode.replace('x', 'w'))))
            elif not _mode.create and not self.exists(_path):
                raise errors.ResourceNotFound(path)
            elif self.isdir(_path):
                raise errors.FileExpected(path)
            with convert_sshfs_errors('openbin', path):
                _sftp = self._client.open_sftp()
                handle = _sftp.open(
                    _path,
                    mode=_mode.to_platform_bin(),
                    bufsize=buffering
                )
                handle.set_pipelined(options.get("pipelined", True))
                if options.get("prefetch", True):
                    if _mode.reading and not _mode.writing:
                        handle.prefetch(self.getsize(_path))
                return SSHFile(handle, _mode.to_platform_bin())

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
        if not self.isempty(_path):
            raise errors.DirectoryNotEmpty(path)

        with convert_sshfs_errors('removedir', path):
            with self._lock:
                self._sftp.rmdir(_path)

    def setinfo(self, path, info):  # noqa: D102
        self.check()
        _path = self.validatepath(path)

        if not self.exists(path):
            raise errors.ResourceNotFound(path)

        access = info.get('access', {})
        details = info.get('details', {})

        with convert_sshfs_errors('setinfo', path):
            if 'accessed' in details or 'modified' in details:
                self._utime(_path,
                            details.get("modified"),
                            details.get("accessed"))
            if 'uid' in access or 'gid' in access:
                self._chown(_path,
                            access.get('uid'),
                            access.get('gid'))
            if 'permissions' in access:
                self._chmod(_path, access['permissions'].mode)

    def download(self, path, file, chunk_size=None, callback=None, **options):
        """Copy a file from the filesystem to a file-like object.

        This method uses the underlying `paramiko.SFTP.getfo` method, which
        should be more efficient than manually opening and reading from a
        file.

        Arguments:
            path (str): Path to a resource.
            file (file-like): A file-like object open for writing in
                binary mode.
            chunk_size (int, optional): Ignored, kept for compatibility
                with the `fs.base.FS.download` signature.
            callback (callable, optional): An optional callback function
                (form: ``func(int, int)``) that accepts the bytes transferred
                so far and the total bytes to be transferred. Passed
                transparently to `~paramiko.SFTP.getfo`.

        Note that the file object ``file`` will *not* be closed by this
        method. Take care to close it after this method completes
        (ideally with a context manager).

        Example:
            >>> with open('starwars.mov', 'wb') as write_file:
            ...     my_fs.download('/movies/starwars.mov', write_file)

        """
        _path = self.validatepath(path)
        with self._lock:
            if not self.exists(_path):
                raise errors.ResourceNotFound(path)
            elif self.isdir(_path):
                raise errors.FileExpected(path)
            with convert_sshfs_errors('download', path):
                self._sftp.getfo(_path, file, callback=callback)

    def upload(self, path, file, chunk_size=None, callback=None, file_size=None, confirm=True, **options):
        """Set a file to the contents of a binary file object.

        This method uses the underlying `paramiko.SFTP.putfo` method, which
        should be more efficient than manually opening and writing to a file.

        Arguments:
            path (str): A path on the filesystem.
            file (io.IOBase): A file object open for reading in
                binary mode.
            chunk_size (int, optional): Ignored, kept for compatibility
                with the `fs.base.FS.download` signature.
            callback (callable, optional): An optional callback function
                (form: ``func(int, int)``) that accepts the bytes transferred
                so far and the total bytes to be transferred. Passed
                transparently to `~paramiko.SFTP.put`.
            file_size (int, optional): An optional size parameter, passed
                to ``callback``. If `None` is given, uses ``0``.
            confirm (bool): If `True` (the default), do a ``stat()`` call
                once finished to confirm the size of the uploaded file.

        Raises:
            fs.errors.ResourceNotFound: If a parent directory of
                ``path`` does not exist.

        Note that the file object ``file`` will *not* be closed by this
        method. Take care to close it after this method completes
        (ideally with a context manager).

        Example:
            >>> with open('~/movies/starwars.mov', 'rb') as read_file:
            ...     my_fs.upload('starwars.mov', read_file)

        """
        _path = self.validatepath(path)
        with self._lock:
            if not self.exists(dirname(_path)):
                raise errors.ResourceNotFound(path)
            elif self.isdir(_path):
                raise errors.FileExpected(path)
            with convert_sshfs_errors('upload', path):
                self._sftp.putfo(
                    file,
                    _path,
                    file_size=file_size,
                    callback=callback,
                    confirm=confirm
                )

    @cached_property
    def platform(self):
        """The platform the server is running on.

        Returns:
            str: the platform of the remote server, as in `sys.platform`.
        """
        try:
            uname_sys = self._exec_command("uname -s")
            sysinfo = self._exec_command("sysinfo")
        except paramiko.ssh_exception.SSHException:
            return "unknown"
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

    @cached_property
    def locale(self):
        """The locale the server is running on.

        Returns:
            str: the locale of the remote server if detected, or `None`.
        """
        if self.platform in ("linux", "darwin", "freebsd"):
            locale = self._exec_command('echo $LANG')
            if locale is not None:
                return locale.split(b'.')[-1].decode('ascii').lower()
        return None

    def _exec_command(self, cmd):
        """Run a command on the remote SSH server.

        Returns:
            bytes: the output of the command, if it didn't fail
            None: if the error pipe of the command was not empty
        """
        _, out, err = self._client.exec_command(cmd, timeout=self._exec_timeout)
        return out.read().strip() if not err.read().strip() else None

    def _make_raw_info(self, name, stat_result, namespaces):
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
        return info

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
        ctime_key = 'created' if self.platform == "win32" else 'metadata_changed'
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
            accessed = float(modified if accessed is None else accessed)
            modified = float(accessed if modified is None else modified)
            self._sftp.utime(path, (accessed, modified))
        else:
            self._sftp.utime(path, None)
