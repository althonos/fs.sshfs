# `miarec_sshfs` SFTP filesystem for PyFilesystem2

This is a fork of [fs.sshfs](https://github.com/althonos/fs.sshfs) project, with modifications that are required for our needs.

[![Actions](https://img.shields.io/github/actions/workflow/status/miarec/miarec_sshfs/test.yml?branch=master&logo=github&style=flat-square&maxAge=300)](https://github.com/miarec/miarec_sshfs/actions)
[![License](https://img.shields.io/pypi/l/fs.sshfs.svg?logo=gnu&style=flat-square&maxAge=36000)](https://choosealicense.com/licenses/lgpl-2.1/)


## Requirements

| **PyFilesystem2** | [![PyPI fs](https://img.shields.io/pypi/v/fs.svg?maxAge=300&style=flat-square)](https://pypi.python.org/pypi/fs) | [![Source fs](https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=36000&style=flat-square)](https://github.com/PyFilesystem/pyfilesystem2) | [![License fs](https://img.shields.io/pypi/l/fs.svg?maxAge=36000&style=flat-square)](https://choosealicense.com/licenses/mit/) |
|:-|:-|:-|:-|
| **six** | [![PyPI six](https://img.shields.io/pypi/v/six.svg?maxAge=300&style=flat-square)](https://pypi.python.org/pypi/six) | [![Source six]( https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=36000&style=flat-square )]( https://github.com/benjaminp/six) | [![License six](https://img.shields.io/pypi/l/six.svg?maxAge=36000&style=flat-square)](https://choosealicense.com/licenses/mit/) |
| **paramiko** | [![PyPI paramiko](https://img.shields.io/pypi/v/paramiko.svg?maxAge=300&style=flat-square)](https://pypi.python.org/pypi/paramiko) | [![Source paramiko]( https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=36000&style=flat-square )]( https://github.com/paramiko/paramiko) | [![License paramiko](https://img.shields.io/pypi/l/paramiko.svg?maxAge=36000&style=flat-square)](https://choosealicense.com/licenses/lgpl-2.1/) |
| **property-cached** | [![PyPI property](https://img.shields.io/pypi/v/property-cached.svg?maxAge=300&style=flat-square)](https://pypi.python.org/pypi/property-cached) | [![Source property]( https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=36000&style=flat-square )](https://github.com/althonos/property-cached) | [![License property]( https://img.shields.io/pypi/l/property-cached.svg?maxAge=36000&style=flat-square )]( https://choosealicense.com/licenses/bsd-3-clause/) |

`miarec_sshfs` supports Python versions 3.6+ 

## Notable differences to `fs.sshfs`

1. Loading of configuration from SSH Config files (`~/.ssh/config`) is removed due to potential security issues, 
when this component used in SaaS project. 
 
2. Automatic loading of SSH keys from SSH Agent is forbidden due to potential security issues, when this components
is used in SaaS project.
 
3. The opener protocol prefixes are `mssh://` and `msftp://` (instead of the original `ssh://` and `sftp://`)

4. URL is forbidden due to potential leak of SFTP credentials via url.

## Installation

Install from GitHub, using [pip](https://pip.pypa.io/):

```console
$ pip install git+https://github.com/miarec/miarec_sshfs@master
```

## Usage

To connect to an SSH server, use the `fs.sshfs.SSHFS` constructor, which signature is:

```python
from miarec_sshfs import SSHFS
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


## Testing

Automated unit tests are run on [GitHub Actions](https://github.com/miarec/miarec_sshfs/actions)

To run the tests locally, do the following.

Install Docker on local machine.

Create activate python virtual environment:

    python -m vevn venv
    source venv\bin\activate

Install the project and test dependencies:

    pip install -e ".[test]"

Run tests:

    pytest -v


## Feedback

Found a bug ? Have an enhancement request ? Head over to the [GitHub
issue tracker](https://github.com/miarec/miarec_sshfs/issues) of the
project if you need to report or ask something. If you are filling in on
a bug, please include as much information as you can about the issue,
and try to recreate the same bug in a simple, easily reproductible
situation.


## Credits

`miarec_ssfs` is developed and maintained by [MiaRec](https://www.miarec.com)

Original code (`fs.sshfs`) was developed by:
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

