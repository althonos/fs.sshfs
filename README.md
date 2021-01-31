# `fs.sshfs` [![star me](https://img.shields.io/github/stars/althonos/fs.sshfs.svg?style=social&maxAge=3600&label=Star)](https://github.com/althonos/fs.sshfs/stargazers)

[![Source](https://img.shields.io/badge/source-GitHub-303030.svg?logo=git&maxAge=36000&style=flat-square)](https://github.com/althonos/fs.sshfs)
[![PyPI](https://img.shields.io/pypi/v/fs.sshfs.svg?logo=pypi&style=flat-square&maxAge=3600)](https://pypi.python.org/pypi/fs.sshfs)
[![Conda](https://img.shields.io/conda/vn/conda-forge/fs.sshfs?logo=anaconda&style=flat-square&maxAge=3600)](https://anaconda.org/conda-forge/fs.sshfs)
[![Actions](https://img.shields.io/github/workflow/status/althonos/fs.sshfs/Test/master?logo=github&style=flat-square&maxAge=300)](https://github.com/althonos/fs.sshfs/actions)
[![Codecov](https://img.shields.io/codecov/c/github/althonos/fs.sshfs/master.svg?logo=codecov&style=flat-square&maxAge=300)](https://codecov.io/gh/althonos/fs.sshfs)
[![Codacy](https://img.shields.io/codacy/grade/9734bea6ec004cc4914a377d9e9f54bd/master.svg?logo=codacy&style=flat-square&maxAge=300)](https://www.codacy.com/app/althonos/fs.sshfs/dashboard)
[![License](https://img.shields.io/pypi/l/fs.sshfs.svg?logo=gnu&style=flat-square&maxAge=36000)](https://choosealicense.com/licenses/lgpl-2.1/)
[![Versions](https://img.shields.io/pypi/pyversions/fs.sshfs.svg?logo=python&style=flat-square&maxAge=300)](https://pypi.org/project/fs.sshfs)
[![Format](https://img.shields.io/pypi/format/fs.sshfs.svg?style=flat-square&maxAge=300)](https://pypi.org/project/fs.sshfs)
[![GitHub issues](https://img.shields.io/github/issues/althonos/fs.sshfs.svg?style=flat-square&maxAge=600)](https://github.com/althonos/fs.sshfs/issues)
[![Downloads](https://img.shields.io/badge/dynamic/json?style=flat-square&color=303f9f&maxAge=86400&label=downloads&query=%24.total_downloads&url=https%3A%2F%2Fapi.pepy.tech%2Fapi%2Fprojects%2Ffs.sshfs)](https://pepy.tech/project/fs.sshfs)
[![Changelog](https://img.shields.io/badge/keep%20a-changelog-8A0707.svg?maxAge=2678400&style=flat-square)](https://github.com/althonos/fs.sshfs/blob/master/CHANGELOG.md)


## Requirements

| **PyFilesystem2** | [![PyPI fs](https://img.shields.io/pypi/v/fs.svg?maxAge=300&style=flat-square)](https://pypi.python.org/pypi/fs) | [![Source fs](https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=36000&style=flat-square)](https://github.com/PyFilesystem/pyfilesystem2) | [![License fs](https://img.shields.io/pypi/l/fs.svg?maxAge=36000&style=flat-square)](https://choosealicense.com/licenses/mit/) |
|:-|:-|:-|:-|
| **six** | [![PyPI six](https://img.shields.io/pypi/v/six.svg?maxAge=300&style=flat-square)](https://pypi.python.org/pypi/six) | [![Source six]( https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=36000&style=flat-square )]( https://github.com/benjaminp/six) | [![License six](https://img.shields.io/pypi/l/six.svg?maxAge=36000&style=flat-square)](https://choosealicense.com/licenses/mit/) |
| **paramiko** | [![PyPI paramiko](https://img.shields.io/pypi/v/paramiko.svg?maxAge=300&style=flat-square)](https://pypi.python.org/pypi/paramiko) | [![Source paramiko]( https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=36000&style=flat-square )]( https://github.com/paramiko/paramiko) | [![License paramiko](https://img.shields.io/pypi/l/paramiko.svg?maxAge=36000&style=flat-square)](https://choosealicense.com/licenses/lgpl-2.1/) |
| **property-cached** | [![PyPI property](https://img.shields.io/pypi/v/property-cached.svg?maxAge=300&style=flat-square)](https://pypi.python.org/pypi/property-cached) | [![Source property]( https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=36000&style=flat-square )](https://github.com/althonos/property-cached) | [![License property]( https://img.shields.io/pypi/l/property-cached.svg?maxAge=36000&style=flat-square )]( https://choosealicense.com/licenses/bsd-3-clause/) |

`fs.sshfs` supports all Python versions supported by PyFilesystem2:
Python 2.7, and Python 3.5 onwards. Code should still be compatible with
Python 3.4, but not tested anymore.


## Installation

Install directly from PyPI, using [pip](https://pip.pypa.io/):

```console
$ pip install fs.sshfs
```

There is also a [`conda-forge` package](https://conda-forge.org/) available:

```console
$ conda install -c conda-forge fs.sshfs
```


## Usage

### Opener

Use `fs.open_fs` to open a filesystem with an SSH
[FS URL](https://docs.pyfilesystem.org/en/latest/openers.html):

```python
import fs
my_fs = fs.open_fs("ssh://[user[:password]@]host[:port]/[directory]")
```

The `sftp` scheme can be used as an alias for the `ssh` scheme in the FS
URL. Additional argument can be passed to the `SSHFS` constructor as
percent-encoded URL parameters (excepted `policy`). See section below
for a list of all supported arguments.

### Constructor

For a more granular way of connecting to an SSH server, use the
`fs.sshfs.SSHFS` constructor, which signature is:

```python
from fs.sshfs import SSHFS
my_fs = SSHFS(
  host, user=None, passwd=None, pkey=None, timeout=10, port=22,
  keepalive=10, compress=False, config_path='~/.ssh/config'
)
```

with each argument explained below:

- `host`: the name or IP address of the SSH server
- `user`: the username to connect with, defaults to the current user.
- `passwd`: an optional password, used to connect directly to the server or
  to decrypt the public key, if any given.
- `pkey`: a [`paramiko.PKey`](http://docs.paramiko.org/en/stable/api/keys.html#paramiko.pkey.PKey)
  object, a path, or a list of paths to an SSH key.
- `timeout`: the timeout, in seconds, for networking operations.
- `port`: the port the SSH server is listening on.
- `keepalive`: the interval of time between *keepalive* packets, in seconds.
  Set to 0 to disable.
- `compress`: set to `True` to compress the communications with the server.
- `config_path`: the path to an OpenSSH configuration file.
- `exec_timeout`: the timeout, in seconds, for arbitrary SSH commands on
  the server.
- `policy`: a
  [`paramiko.MissingHostKeyPolicy`](http://docs.paramiko.org/en/stable/api/client.html#paramiko.client.MissingHostKeyPolicy)
  instance, or `None` to use
  [`paramiko.AutoAddPolicy`](http://docs.paramiko.org/en/stable/api/client.html#paramiko.client.AutoAddPolicy).

Additional keyword arguments will be passed to the underlying
[`paramiko.SSHClient.connect`](http://docs.paramiko.org/en/stable/api/client.html#paramiko.client.SSHClient.connect)
call, taking precedence over implicitly derived arguments. Once created, the `SSHFS` filesystem behaves like any
other filesystem (see the [PyFilesystem2 documentation](https://pyfilesystem2.readthedocs.io)).

### Files

`SSHFS.openbin` has the following extra options that can be passed as
keyword arguments to control the file buffering:

- `prefetch`: enabled by default, use a background thread to prefetch the content
  of a file opened in reading mode. Does nothing for files in writing mode.
- `pipelined`: enable pipelined mode, avoid waiting for server answer between
  two uploaded chunks. Does nothing for files in reading mode.


## Configuration

`SSHFS` are aware of [SSH config
files](http://nerderati.com/2011/03/17/simplify-your-life-with-an-ssh-config-file/)
and as such, one of the hosts in the configuration file can be provided
as the `host` argument for the filesystem to connect to the server with
the proper configuration values.


## Feedback

Found a bug ? Have an enhancement request ? Head over to the [GitHub
issue tracker](https://github.com/althonos/fs.sshfs/issues) of the
project if you need to report or ask something. If you are filling in on
a bug, please include as much information as you can about the issue,
and try to recreate the same bug in a simple, easily reproductible
situation.


## Credits

`fs.sshfs` is developped and maintainted by:
- [Martin Larralde](https://github.com/althonos)

The following people contributed to `fs.sshfs`:
- [Reimar Bauer](https://github.com/ReimarBauer)
- [Paul Gessinger](https://github.com/paulgessinger)
- [Mariusz Kryński](https://github.com/mrk-its)
- [Will McGugan](https://github.com/willmcgugan)
- [Jeremy Nimmer](https://github.com/jwnimmer-tri)
- [Tim Nyborg](https://github.com/timnyborg)
- [Danica J. Sutherland](https://github.com/djsutherland)
- [John Vandenberg](https://github.com/jayvdb)

This project obviously owes a lot to the PyFilesystem2 project and
[all its contributors](https://github.com/PyFilesystem/pyfilesystem2/blob/master/CONTRIBUTORS.md).

## See also

-   [fs](https://github.com/Pyfilesystem/pyfilesystem2), the core
    PyFilesystem2 library
-   [fs.archive](https://github.com/althonos/fs.archive), enhanced
    archive filesystems for PyFilesystem2
-   [fs.smbfs](https://github.com/althonos/fs.smbfs), PyFilesystem2 over
    SMB using pysmb
