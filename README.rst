``fs.sshfs``
============

|Source| |PyPI| |Conda| |Travis| |Codecov| |Codacy| |Format| |License|

.. |Codacy| image:: https://img.shields.io/codacy/grade/9734bea6ec004cc4914a377d9e9f54bd/master.svg?style=flat-square&maxAge=300
   :target: https://www.codacy.com/app/althonos/fs.sshfs/dashboard

.. |Travis| image:: https://img.shields.io/travis/althonos/fs.sshfs/master.svg?style=flat-square&maxAge=300
   :target: https://travis-ci.org/althonos/fs.sshfs/branches

.. |Codecov| image:: https://img.shields.io/codecov/c/github/althonos/fs.sshfs/master.svg?style=flat-square&maxAge=300
   :target: https://codecov.io/gh/althonos/fs.sshfs

.. |PyPI| image:: https://img.shields.io/pypi/v/fs.sshfs.svg?style=flat-square&maxAge=300
   :target: https://pypi.python.org/pypi/fs.sshfs

.. |Conda| image:: https://anaconda.org/conda-forge/fs.sshfs/badges/installer/conda.svg
   :target: https://anaconda.org/conda-forge/fs.sshfs

.. |Format| image:: https://img.shields.io/pypi/format/fs.sshfs.svg?style=flat-square&maxAge=300
   :target: https://pypi.python.org/pypi/fs.sshfs

.. |Versions| image:: https://img.shields.io/pypi/pyversions/fs.sshfs.svg?style=flat-square&maxAge=300
   :target: https://travis-ci.org/althonos/fs.sshfs

.. |License| image:: https://img.shields.io/pypi/l/fs.sshfs.svg?style=flat-square&maxAge=300
   :target: https://choosealicense.com/licenses/lgpl-2.1/

.. |Source| image:: https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=300&style=flat-square
   :target: https://github.com/althonos/fs.sshfs



Requirements
------------

+-------------------+-----------------+-------------------+--------------------+
| **pyfilesystem2** | |PyPI fs|       | |Source fs|       | |License fs|       |
+-------------------+-----------------+-------------------+--------------------+
| **six**           | |PyPI six|      | |Source six|      | |License six|      |
+-------------------+-----------------+-------------------+--------------------+
| **paramiko**      | |PyPI paramiko| | |Source paramiko| | |License paramiko| |
+-------------------+-----------------+-------------------+--------------------+


.. |License six| image:: https://img.shields.io/pypi/l/six.svg?maxAge=300&style=flat-square
   :target: https://choosealicense.com/licenses/mit/

.. |Source six| image:: https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=300&style=flat-square
   :target: https://github.com/benjaminp/six

.. |PyPI six| image:: https://img.shields.io/pypi/v/six.svg?maxAge=300&style=flat-square
   :target: https://pypi.python.org/pypi/six

.. |License fs| image:: https://img.shields.io/badge/license-MIT-blue.svg?maxAge=300&style=flat-square
   :target: https://choosealicense.com/licenses/mit/

.. |Source fs| image:: https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=300&style=flat-square
   :target: https://github.com/PyFilesystem/pyfilesystem2

.. |PyPI fs| image:: https://img.shields.io/pypi/v/fs.svg?maxAge=300&style=flat-square
   :target: https://pypi.python.org/pypi/fs

.. |License paramiko| image:: https://img.shields.io/pypi/l/paramiko.svg?maxAge=300&style=flat-square
   :target: https://choosealicense.com/licenses/lgpl-2.1/

.. |Source paramiko| image:: https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=300&style=flat-square
   :target: https://github.com/paramiko/paramiko

.. |PyPI paramiko| image:: https://img.shields.io/pypi/v/paramiko.svg?maxAge=300&style=flat-square
   :target: https://pypi.python.org/pypi/paramiko


Installation
------------

Install directly from PyPI, using `pip <https://pip.pypa.io/>`_ ::

    pip install fs.sshfs


Usage
-----

Opener
''''''

Use ``fs.open_fs`` to open a filesystem with an SSH
`FS URL <https://pyfilesystem2.readthedocs.io/en/latest/openers.html>`_:

.. code:: python

   import fs
   my_fs = fs.open_fs("ssh://[user[:password]@]host[:port]/[directory]")

VThe following URL parameters are supported: ``timeout``, ``keepalive``.


Constructor
'''''''''''

For a more granular way of connecting to an SSH server, use the
``fs.sshfs.SSHFS`` constructor, which signature is:

.. code:: python

    from fs.sshfs import SSHFS
    my_fs = SSHFS(
      host, user=None, paswd=None, pkey=None, timeout=10, port=22,
      keepalive=10, compress=False, config_path='~/.ssh/config'
    )

with each argument explained below:

``host``
  the name or IP address of the SSH server
``user``
  the username to connect with, defaults to the current user.
``passwd``
  an optional password, used to connect directly to the server or to
  decrypt the public key, if any given.
``pkey``
  a `paramiko.PKey <http://docs.paramiko.org/en/2.2/api/keys.html#module-paramiko.pkey>`_
  object, a path, or a list of paths to an SSH key.
``timeout``
  the timeout, in seconds, for networking operations.
``port``
  the port the SSH server is listening on.
``keepalive``
  the interval of time between keepalive packets, in seconds. Set to 0 to disable.
``compress``
  set to ``True`` to compress the communications with the server
``config_path``
  the path to an OpenSSH configuration file.

Additional keyword arguments will be passed to the underlying connection call,
taking precedence over implicitly derived arguments.  Once created, the
``SSHFS`` filesystem behaves like any other filesystem (see the `Pyfilesystem2
documentation <https://pyfilesystem2.readthedocs.io>`_).


Files
'''''

`SSHFS.openbin` has the following extra options that can be passed as keyword arguments
to control the file buffering:

``prefetch``
  enabled by default, use a background thread to prefetch the content of a file 
  opened in reading mode. Does nothing for files in writing mode.
``pipelined``
  enable pipelined mode, avoid waiting for server answer between two uploaded 
  chunks. Does nothing for files in reading mode.



Configuration
-------------

``SSHFS`` are aware of `SSH config files <http://nerderati.com/2011/03/17/simplify-your-life-with-an-ssh-config-file/>`_
and as such, one of the hosts in the configuration file can be provided as the
``host`` argument for the filesystem to connect to the server with the proper
configuration values.



Feedback
--------

Found a bug ? Have an enhancement request ? Head over to the
`GitHub issue tracker <https://github.com/althonos/fs.sshfs/issues>`_ of the
project if you need to report or ask something. If you are filling in on a bug,
please include as much information as you can about the issue, and try to
recreate the same bug in a simple, easily reproductible situation.



See also
--------

* `fs <https://github.com/Pyfilesystem/pyfilesystem2>`_, the core pyfilesystem2 library
* `fs.archive <https://github.com/althonos/fs.archive>`_, enhanced archive filesystems
  for pyfilesystem2
* `fs.smbfs <https://github.com/althonos/fs.smbfs>`_, Pyfilesystem2 over SMB
  using pysmb
