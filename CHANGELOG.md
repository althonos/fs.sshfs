# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).


## [v2024.1.3] - 2024-01-15

[v2024.1.3]: https://github.com/miarec/miarec_sshfs/compare/v2024.1.2...v2024.1.3

### Changes

- Bump up version to resolve GitHub Actions workflow issues


## [v2024.1.2] - 2024-01-13

[v2024.1.2]: https://github.com/miarec/miarec_sshfs/compare/v2024.1.0...v2024.1.2

### Changed

- For security reasons, do not load SSH configuration from local `~/.ssh/config`.
- For security reasons, do not load SSH private keys from local system `~/.ssh`.
- For security reasons, do not load SSH private keys from SSH Agent.
- Disable by default a prefetch of files in background thread because a client may not need to read a whole file.
- Use protocol prefixes `msftp://` and `mssh://` instead of originals `sftp://` and `ssh://` respectively.
- Fix bug in `move()` when `preferve_time` is `True`.
- By default, do not run any shell commands (like `uname -s`) because some SFTP servers forbid a shell and close forcibly a network connection when the client attemps to run shell commands.
- Add `use_posix_rename` optional parameter to use a more efficient POSIX RENAME command rather than RENAME.
- Fix issue with SSH connection is being closed while `SSHFile` object is stil using it. This occurs because garbage collector may destroy the parent SSHFS object (and the underlying SSH connection) because `SSHFile` objects are not referencing the parent object directly.
- Fix connection leakage when `SSHFile` is opened directly rather than using context manager.



## [v2024.1.0] - 2024-01-05

[v2024.1.0]: https://github.com/miarec/miarec_sshfs/compare/v1.0.2...v2024.1.0

### Changed

- Forked from [fs.sshfs](https://github.com/althonos/fs.sshfs) version 1.0.2
- Rename project from `fs.sshfs` to `miarec_sshfs`


## [v1.0.2] - 2023-08-17

The latest release of the original (forked) [fs.sshfs](https://github.com/althonos/fs.sshfs) repo
