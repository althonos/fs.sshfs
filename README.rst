fs.sshfs
========

|Source| |PyPI| |Travis| |Codecov| |Codacy| |Format| |License|

.. |Codacy| image:: https://img.shields.io/codacy/grade/9734bea6ec004cc4914a377d9e9f54bd/master.svg?style=flat-square&maxAge=300
   :target: https://www.codacy.com/app/althonos/fs-sshfs/dashboard

.. |Travis| image:: https://img.shields.io/travis/althonos/fs.sshfs/master.svg?style=flat-square&maxAge=300
   :target: https://travis-ci.org/althonos/fs.sshfs/branches

.. |Codecov| image:: https://img.shields.io/codecov/c/github/althonos/fs.sshfs/master.svg?style=flat-square&maxAge=300
   :target: https://codecov.io/gh/althonos/fs.sshfs

.. |PyPI| image:: https://img.shields.io/pypi/v/fs.sshfs.svg?style=flat-square&maxAge=300
   :target: https://pypi.python.org/pypi/fs.sshfs

.. |Format| image:: https://img.shields.io/pypi/format/fs.sshfs.svg?style=flat-square&maxAge=300
   :target: https://pypi.python.org/pypi/fs.sshfs

.. |Versions| image:: https://img.shields.io/pypi/pyversions/fs.sshfs.svg?style=flat-square&maxAge=300
   :target: https://travis-ci.org/althonos/fs.sshfs

.. |License| image:: https://img.shields.io/pypi/l/fs.sshfs.svg?style=flat-square&maxAge=300
   :target: https://choosealicense.com/licenses/lgpl-2.1/

.. |Source| image:: https://img.shields.io/badge/source-GitHub-green.svg?maxAge=300&style=flat-square
   :target: https://github.com/althonos/fs.sshfs


Requirements
------------

+-------------------+-----------------+-------------------+--------------------+
| **fs**            | |PyPI fs|       | |Source fs|       | |License fs|       |
+-------------------+-----------------+-------------------+--------------------+
| **paramiko**      | |PyPI paramiko| | |Source paramiko| | |License paramiko| |
+-------------------+-----------------+-------------------+--------------------+
| **six**           | |PyPI six|      | |Source six|      | |License six|      |
+-------------------+-----------------+-------------------+--------------------+


.. |License six| image:: https://img.shields.io/pypi/l/six.svg?maxAge=300&style=flat-square
   :target: https://choosealicense.com/licenses/mit/

.. |Source six| image:: https://img.shields.io/badge/source-GitHub-green.svg?maxAge=300&style=flat-square
   :target: https://github.com/benjaminp/six

.. |PyPI six| image:: https://img.shields.io/pypi/v/six.svg?maxAge=300&style=flat-square
   :target: https://pypi.python.org/pypi/six

.. |License fs| image:: https://img.shields.io/badge/license-MIT-blue.svg?maxAge=300&style=flat-square
   :target: https://choosealicense.com/licenses/mit/

.. |Source fs| image:: https://img.shields.io/badge/source-GitHub-green.svg?maxAge=300&style=flat-square
   :target: https://github.com/PyFilesystem/pyfilesystem2

.. |PyPI fs| image:: https://img.shields.io/pypi/v/fs.svg?maxAge=300&style=flat-square
   :target: https://pypi.python.org/pypi/fs

.. |License paramiko| image:: https://img.shields.io/pypi/l/paramiko.svg?maxAge=300&style=flat-square
   :target: https://choosealicense.com/licenses/lgpl-2.1/

.. |Source paramiko| image:: https://img.shields.io/badge/source-GitHub-green.svg?maxAge=300&style=flat-square
   :target: https://github.com/paramiko/paramiko

.. |PyPI paramiko| image:: https://img.shields.io/pypi/v/paramiko.svg?maxAge=300&style=flat-square
   :target: https://pypi.python.org/pypi/paramiko


Installation
------------

Install directly from PyPI, using `pip` ::

    pip install fs.sshfs


Usage
-----

Use ``fs.open_fs`` to open a filesystem with an SSH
`FS URL <https://pyfilesystem2.readthedocs.io/en/latest/openers.html>`_:

.. code:: python

   import fs
   my_fs = fs.open_fs("ssh://user:password@host:port/resource")

with the following optional parts:

* ``user``: defaults to the current user
* ``password``: if none provided, passwordless authentification methods are
  used (either using public keys or no authentification to connect to the host)
* ``port``: defaults to the usual SSH port (port 22)
* ``resource``: defaults to the root directory (``"/"``)




For a more granular way of connecting to a SSH server, use the `fs.sshfs.SSHFS`
constructor, which signature is:

.. code:: python

    from fs.sshfs import SSHFS
    my_fs = SSHFS(
      host,            # The name or adress of the SSH server
      user=None,       # an optional username, defaults to the current user
      passwd=None,     # an optional password, not needed if using a public key or
                       #   an SSH server without authentification
      pkey=None,       # a `paramiko.PKey` object, used to connect with a
                       #   specific key (undiscoverable key, etc.)
      timeout=10,      # The timeout of the connection, in seconds
                       #   (None to disable)
      port=22,         # The port to which to connect, default to default SSH port
      keepalive=10,    # The interval of time between keepalive packets, in
                       #    seconds (0 to disable)
      compress=False   # Compress the communications with the server
    )


Once created, the `SSHFS` filesystem behaves like any other filesystem
(see the `Pyfilesystem2 documentation <https://pyfilesystem2.readthedocs.io>`_)
