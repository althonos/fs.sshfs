from ._base import Opener
from ._registry import registry
from ..subfs import ClosingSubFS

@registry.install
class SSHOpener(Opener):
    protocols = ['ssh']

    @staticmethod
    def open_fs(fs_url, parse_result, writeable, create, cwd):
        from ..sshfs import SSHFS
        ssh_host, _, dir_path = parse_result.resource.partition('/')
        ssh_host, _, ssh_port = ssh_host.partition(':')
        ssh_port = int(ssh_port) if ssh_port.isdigit() else 22
        ssh_fs = SSHFS(
            ssh_host,
            port=ssh_port,
            user=parse_result.username,
            passwd=parse_result.password,
        )

        if dir_path: # pragma: no cover
            return ssh_fs.opendir(dir_path, factory=ClosingSubFS)
        else:
            return ssh_fs
