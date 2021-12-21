# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).


## [Unreleased]
[Unreleased]: https://github.com/althonos/fs.sshfs/compare/v1.0.1...HEAD


## [v1.0.1] - 2021-12-21

[v1.0.0]: https://github.com/althonos/fs.sshfs/compare/v1.0.0...v1.0.1

### Fixed
- `SSHFS.move` not supporting the `preserve_time` argument ([#51](https://github.com/althonos/fs.sshfs/issues/51)).


## [v1.0.0] - 2021-01-18

[v1.0.0]: https://github.com/althonos/fs.sshfs/compare/v0.13.1...v1.0.0

### Added
- `SSHFS.upload` (resp. `download`) implementation using `paramiko.SFTP.putfo`
  (resp. `getfo`).
- This changelog file.

### Changed
- Switched from Travis-CI and AppVeyor to GitHub Actions for continuous integration.
- Rewrote `README.rst` in Markdown format.
- Mark the project as *Stable* in `setup.cfg` classifiers.


## [v0.13.1] - 2021-01-18

[v0.13.1]: https://github.com/althonos/fs.sshfs/compare/v0.13.0...v0.13.1

### Fixed
- Make `SSHFile` record the mode it was created with.


## [v0.13.0] - 2021-01-08

[v0.13.0]: https://github.com/althonos/fs.sshfs/compare/v0.12.3...v0.13.0

### Added
- `semantic-version` test requirement.
- `SSHFS.islink` method with behaviour matching `OSFS.islink`.
- Additional documentation of constructor arguments in `SSHFS` docstring.
- Independent timeout for arbitrary SSH commands ([#39](https://github.com/althonos/fs.sshfs/issue/39)).
- Support for passing arbitrary `paramiko.MissingHostKeyPolicy` to `SSHFS`.

### Changed
- `SSHFS.getinfo` now follows symlinks like `OSFS.getinfo`.


## [v0.12.3] - 2020-05-20

[v0.12.3]: https://github.com/althonos/fs.sshfs/compare/v0.12.2...v0.12.3

### Added
- Explicit support for Python 3.8.

### Fixed
- Issue with `SSHFS.close` when exiting while an `SSHFS` instance is still open.


## [v0.12.2] - 2019-11-27

[v0.12.2]: https://github.com/althonos/fs.sshfs/compare/v0.12.1...v0.12.2

### Added
- Dedicated implementation of `SSHFS.scandir` using `paramiko.SFTP.listdir_attr`
  (@jwnimmer-tri [#37](https://github.com/althonos/fs.sshfs/pull/37)).


## [v0.12.1] - 2019-11-16

[v0.12.1]: https://github.com/althonos/fs.sshfs/compare/v0.12.0...v0.12.1

### Fixed
- Assume *unknown* platform is `_exec_command` throws an exception
  (@mrk-its [#35](https://github.com/althonos/fs.sshfs/pull/35)).


## [v0.12.0] - 2019-10-21

[v0.12.0]: https://github.com/althonos/fs.sshfs/compare/v0.11.1...v0.12.0

### Added
- Explicit support for Python 3.7.
- Section documenting the support of `sftp` FS URLs to `README.rst`.
- `support_rename` key to the `SSHFS.getmeta` options.
- `SSHFS.move` implementation using the `paramiko.SFTP.rename` function.

### Fixed
- Typos in `README.rst`
  (@jayvdb [#28](https://github.com/althonos/fs.sshfs/pull/28),
  @timnyborg [#32](https://github.com/althonos/fs.sshfs/pull/32)).


## [v0.11.1] - 2019-07-22

[v0.11.1]: https://github.com/althonos/fs.sshfs/compare/v0.11.0...v0.11.1

### Changed
- Replace `cached-property` dependency with improved `property-cached` fork.


## [v0.11.0] - 2019-05-16

[v0.11.0]: https://github.com/althonos/fs.sshfs/compare/v0.10.2...v0.11.0

### Added
- `prefetch` argument to `SSHFS.openbin` to enable prefetching files when
  they are open in reading mode.


## [v0.10.2] - 2019-02-22

[v0.10.2]: https://github.com/althonos/fs.sshfs/compare/v0.10.1...v0.10.2

### Added
- Explicit support for `fs ~=2.2`.


## [v0.10.1] - 2019-02-11

[v0.10.1]: https://github.com/althonos/fs.sshfs/compare/v0.10.0...v0.10.1

### Added
- Support for passing arbitrary arguments to `paramiko.SSHClient.connect`
  in `SSHFS.__init__` (@paulgessinger [#23](https://github.com/althonos/fs.sshfs/pull/17)).


## [v0.10.0] - 2019-01-05

[v0.10.0]: https://github.com/althonos/fs.sshfs/compare/v0.9.0...v0.10.0

### Changed
- Bumped minimum required `fs` version to `v2.2.0`.

### Fixed
- Explicitly register `SSHOpener` as an opener with `fs.opener.registry.install`
  for cases where the `setuptools` metadata are unavailable and entry points
  cannot be loaded.


## [v0.9.0] - 2018-11-22

[v0.9.0]: https://github.com/althonos/fs.sshfs/compare/v0.8.0...v0.9.0

### Fixed
- Threading issue with `SSHFile` all sharing the same connection, causing
  issues with code working on several files in parallel.
  (@willmcgugan [#17](https://github.com/althonos/fs.sshfs/pull/17))
- `SSHFile` not being writable when opened in exclusive mode.

### Changed
- Dropped support for Python 3.3 and Python 3.4.
- Bumped minimum required `fs` version to `v2.1.0`.
- Cache `SSHFS.locale` and `SSHFS.platform` properties using `cached-property`.
- `SSHFS` now uses the `timeout` argument it received on initialization when
  running an arbitrary command on the remote server.


## [v0.8.0] - 2018-03-07

[v0.8.0]: https://github.com/althonos/fs.sshfs/compare/v0.7.2...v0.8.0

### Fixed
- Catch all exceptions and not just `FSError` in `SSHOpener`.

### Changed
- Make `SSHFile` transfers to be pipelined by default to increase performance.


## [v0.7.2] - 2018-02-23

[v0.7.2]: https://github.com/althonos/fs.sshfs/compare/v0.7.1...v0.7.2

### Changed
- Use `$LANG` instead of `locale` to guess the locale on the remote server.

### Fixed
- `SSHOpener` not using the `create` argument properly.


## [v0.7.1] - 2017-11-08

[v0.7.1]: https://github.com/althonos/fs.sshfs/compare/v0.7.0...v0.7.1

### Fixed
- License file not being packed in source distributions
  (@dougalsutherland [#8](https://github.com/althonos/fs.sshfs/pull/8))


## [v0.7.0] - 2017-10-26

[v0.7.0]: https://github.com/althonos/fs.sshfs/compare/v0.6.1...v0.7.0

### Added
- Public `SSHFile` class in the the `fs.sshfs.file` to expose a file on
  a remote SSH server obtained with `SSHFS.openbin`.
- Support for parameter extraction from FS URLs.
- `backports.configparser` dependency for Python < 3, to allow parsing
  values from FS URLs parameters.

### Changed
- Code used to manage the remote platform compatibility.

### Fixed
- Use `gethostbyname` to the get the adress for an host adress in `SSHFS.__init__`.
- Make `convert_sshfs_errors` inherit from `AbstractContextManager` explicitly.


## [v0.6.1] - 2017-10-02

[v0.6.1]: https://github.com/althonos/fs.sshfs/compare/v0.6.0...v0.6.1

### Fixed
- License file not being packed in wheel distributions.

### Removed
- `enum34` optional dependency, originally required for Python < 3.4.
- Unneeded imports in the `fs.sshfs` submodules.


## [v0.6.0] - 2017-10-01

[v0.6.0]: https://github.com/althonos/fs.sshfs/compare/v0.5.1...v0.6.0

### Fixed
- Test dependencies being unconditionally installed
  (@ReimarBauer [#1](https://github.com/althonos/fs.sshfs/pull/1)).


## [v0.5.2] - 2017-09-18

[v0.5.2]: https://github.com/althonos/fs.sshfs/compare/v0.5.1...v0.5.2

### Added
- Semantic version specifiers to dependencies in `setup.cfg`.


## [v0.5.1] - 2017-09-13

[v0.5.1]: https://github.com/althonos/fs.sshfs/compare/v0.5.0...v0.5.1

### Fixed
- Potential bug occuring with `_SSHFileWrapper.truncate(0)`.
- `seek` and `truncate` methods of `_SSHFileWrapper` returning `None`.


## [v0.5.0] - 2017-08-31

[v0.5.0]: https://github.com/althonos/fs.sshfs/compare/v0.4.0...v0.5.0

### Added
- Missing docstrings to `fs.sshfs` module members.
- `SSFS.geturl` implementation, allowing to retrieve an SSH URL
  for the *download* purpose.
- Allow `SSHFS` to use SSH configuration values (from `~/.ssh/config` for instance)
  if the given host is found in it.

### Changed
- Make tests run against the local version of the code, allowing tests to
  run without having to install the module first.
- Rewrite docstrings in Google style to be consistent with PyFilesystem2
  documentation style.

### Removed
- `SSHFS.getsyspath` implementation.


## [v0.4.0] - 2017-08-17

[v0.4.0]: https://github.com/althonos/fs.sshfs/compare/v0.3.0...v0.4.0

### Added
- Extraction of user/group with `uid`/`gid` if remote platform is Unix.

### Changed
- Switched to `green` to run tests in CI environment.


## [v0.3.0] - 2017-08-05

[v0.3.0]: https://github.com/althonos/fs.sshfs/compare/v0.2.2...v0.3.0

### Changed
- Added opener entry points to `setup.cfg` to be compatible with the new
  plugin architecture for FS URL openers.


## [v0.2.2] - 2017-07-03

[v0.2.2]: https://github.com/althonos/fs.sshfs/compare/v0.2.1...v0.2.2

### Fixed
- Typo in `README.rst`.

### Changed
- Make `setuptools` build version-specific wheels.


## [v0.2.1] - 2017-06-29

[v0.2.1]: https://github.com/althonos/fs.sshfs/compare/v0.2.0...v0.2.1

### Changed
- Use `setup.cfg` to configure the project installation.
- Dynamically load version of the installed package in `fs.sshfs` and
  `fs.opener.sshfs` instead of hardcoding it in a file.

### Fixed
- `nosetests` mistaking base `TestSSHFS` for a test case.
- `nosetests` requiring `rednose` as a setup requirement.
- Typos in `README.rst`.


## [v0.2.0] - 2017-06-26

[v0.2.0]: https://github.com/althonos/fs.sshfs/compare/v0.1.0...v0.2.0

### Added
- Heuristic to guess the server platform using either `uname` or `sysinfo`.

### Changed
- Use custom function to extract `info` and `details` from `status` results
  instead of using the builtin `OSFS` one.
- Use plain enums instead of `enum.Flag` to record the server platform.

### Fixed
- Invalid license classifiers in project metadata.


## [v0.1.0] - 2017-06-22

[v0.1.0]: https://github.com/althonos/fs.sshfs/compare/2d28534...v0.1.0

Initial release.
