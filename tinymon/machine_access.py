"""
machine_access.py

Provides a wrapper around an SSH client which takes a MachineConfig and
runs the provided commands, retrieving their results. Session must be
closed after all commands have been executed.

MachineAccess also implements context-manager, which can assist in cleanup
when using it in error-prone situations.
"""
import subprocess
from .machine_config import MachineConfig
from .machine_credentials import MachineAuthMode
import time
import tarfile
import tempfile
from pwn import *
context.log_level = "error"

class MachineAccess:
    def __init__(self, cfg):
        self.cfg = cfg
        self.sess = None

    def login(self):
        if self.sess:
            return

        if self.cfg.creds.authmode == MachineAuthMode.PASSWORD:
            self.sess = ssh(host=self.cfg.host, user=self.cfg.creds.username, password=self.cfg.creds.password)
        else:
            self.sess = ssh(host=self.cfg.host, user=self.cfg.creds.username, keyfile=self.cfg.creds.sshkey)

    def execute_cmd(self, cmd, timeout=5):
        assert self.sess, "SSH must be connected to execute commands"

        p = self.sess.process(cmd, shell=True)

        start = time.time()
        while time.time() - start < timeout:
            if p.poll() is not None: break

        if p.poll() is None:
            p.kill()
            p.close()

        assert p.poll() is not None, f"Command '{cmd}' on machine '{self.cfg.name}' timed out"
        assert p.poll() == 0, f"Command '{cmd}' on machine '{self.cfg.name}' failed with error code {p.poll()}"

        return p.recvall().decode()

    def execute_with_nohup(self, cmd, cwd):
        # no neeed for nohup, handled it with pwntools python backend
        p = self.sess.process(["sh", "-c", "cd {cwd}; " + cmd + " > nohup.out"], cwd=cwd)

        # let the process start before disconnecting
        time.sleep(10)
        return p.pid

    def run_to_end(self, cmd):
        return self.sess.run_to_end(cmd)

    def pull_file(self, remote, local):
        assert self.sess, "SSH must be connected to pull files"
        self.sess.download_file(remote, local)

    def pull_dir(self, remote, local):
        assert self.sess, "SSH must be connected to pull files"
        self.sess.download_dir(remote, local)

    def push_file(self, local, remote):
        assert self.sess, "SSH must be connected to push files"
        self.sess.upload_file(local, remote)

    def push_dir(self, local, remote):
        assert self.sess, "SSH must be connected to push files"
        self._upload_dir(local, remote)

    # https://github.com/arthaud/python3-pwntools/blob/7519197918/pwnlib/tubes/ssh.py
    def _upload_dir(self, local, remote):
        local = os.path.expanduser(local)
        basename = os.path.basename(local)

        if not os.path.isdir(local):
            print("%r is not a directory" % local)
            sys.exit(1)

        msg = "Uploading %r to %r" % (basename, remote)
        with self.sess.waitfor(msg) as w:
            # Generate a tarfile with everything inside of it
            local_tar = tempfile.mktemp()
            with tarfile.open(local_tar, 'w:gz') as tar:
                tar.add(local, basename)

            # Upload and extract it
            with context.local(log_level='error'):
                remote_tar = self.sess.mktemp('--suffix=.tar.gz')
                if not isinstance(remote_tar, str): remote_tar = remote_tar.decode()
                self.sess.upload_file(local_tar, remote_tar)

                untar = self.sess.run('cd %s && tar -xzf %s' % (sh_string(remote), sh_string(remote_tar)))
                message = untar.recvrepeat(2)

                if untar.wait() != 0:
                    print("Could not untar %r on the remote end\n%s" % (remote_tar, message))
                    sys.exit(1)

    def logout(self):
        if self.sess is None:
            return

        self.sess.close()
        self.sess = None

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()

if __name__ == "__main__":
    import yaml
    from .machine_credentials import CredentialPair

    with open("test_data/cmu-machines.yaml") as f:
        data = yaml.load(f, yaml.Loader)

    creds = CredentialPair.parseall(data["credentials"])
    machines = MachineConfig.parseall(data["machines"], creds)

    ## TODO
    with MachineAccess(machines["finger"]) as m:
        print(repr(m.execute_cmd("ls -1")))
        print(repr(m.execute_cmd("pwd")))
        print(repr(m.execute_cmd("hostname")))
