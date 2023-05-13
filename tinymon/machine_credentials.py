"""
machine_credentials.py

Provides a data structure CredentialPair for maintaining a credential-pair
to use to log into a machine, as well as the utility method for parsing
a credential pair from the config-file
"""
from dataclasses import dataclass
from enum import Enum
import subprocess

class MachineAuthMode(Enum):
    PASSWORD = 1
    SSH_KEY = 2

@dataclass
class CredentialPair:
    authmode: MachineAuthMode
    username: str
    password: str # password (for non-key-based auth)
    sshkey: str # path to SSH priv key on local machine

    @classmethod
    def parseconfig(cls, cfg):
        assert "password_cmd" in cfg or "password" in cfg or "sshkey" in cfg, \
                "Must provide authentication credentials in the form of a password or SSH key in each credential pair"

        assert "username" in cfg, "Must provide a username in each credential pair"

        if "sshkey" in cfg:
            return cls(MachineAuthMode.SSH_KEY, cfg["username"], None, cfg["sshkey"])

        if "password" in cfg:
            password = cfg["password"]

        if "password_cmd" in cfg:
            password = subprocess.check_output(["sh", "-c", cfg["password_cmd"]]).decode()

            # some password managers will append a newline
            if password[-1] == "\n": password = password[:-1]

        return cls(MachineAuthMode.PASSWORD, cfg["username"], password, None)

    @classmethod
    def parseall(cls, cfg):
        assert len(list(cfg.keys())) == len(set(cfg.keys())), "Credential pairs must all have unique names"
        return {k: cls.parseconfig(v) for k, v in cfg.items()}

# Unit-test
if __name__ == "__main__":
    import yaml

    with open("test_data/cmu-machines.yaml") as f:
        data = yaml.load(f, yaml.Loader)

    data = data["credentials"]
    print(CredentialPair.parseall(data))


