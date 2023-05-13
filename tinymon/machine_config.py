"""
machine_config.py

Provides a data structure MachineConfig for maintaining the information
about accessing and logging into a given machine, as well as the utility
method for parsing this information from a config-file
"""
from dataclasses import dataclass
from enum import Enum
from .machine_credentials import CredentialPair

class DirType(Enum):
    LOCAL_DISK = 1
    SHARED_DISK = 2
    AFS = 3

    @classmethod
    def parse(cls, x):
        x = x.lower()
        if x == "local":
            return cls.LOCAL_DISK
        if x == "shared":
            return cls.SHARED_DISK
        if x == "afs":
            return cls.AFS

        assert False, "Directory type must be one of local, shared, or afs"

# Data structure for parsing and maintaining
# user-provided information about a machine, 
# including IPs, login info
@dataclass
class MachineConfig:
    name: str
    host: str # hostname or IP addr
    creds: CredentialPair
    tmpdir: str
    tmpdir_type: DirType
    workdir: str
    workdir_type: DirType

    @classmethod
    def parseconfig(cls, name, cfg, creds):
        assert "host" in cfg, "Machines must have a 'host' parameter for hostname/IP address"

        assert "creds" in cfg, "Machines must have a 'creds' parameter for credentials"
        assert cfg["creds"] in creds, f"Credential pair {cfg['creds']} not found"

        assert "tmpdir" in cfg, "Machines must have a temporary directory specified"
        assert "tmpdir_type" in cfg, "Machines must specify a disk type for the temporary directory"
        tmpdir_type = DirType.parse(cfg["tmpdir_type"])

        assert "workdir" in cfg, "Machines must have a working directory specified"
        assert "workdir_type" in cfg, "Machines must specify a disk type for the working directory"
        workdir_type = DirType.parse(cfg["workdir_type"])

        tmpdir = cfg["tmpdir"].replace(r"{username}", creds[cfg["creds"]].username)
        workdir = cfg["workdir"].replace(r"{username}", creds[cfg["creds"]].username)

        return cls(name, cfg["host"], creds[cfg["creds"]],
                   tmpdir, tmpdir_type, workdir, workdir_type)

    @classmethod
    def parseall(cls, cfg, creds):
        assert len(list(cfg.keys())) == len(set(cfg.keys())), "Machines must all have unique names"
        return {k: cls.parseconfig(k, v, creds) for k, v in cfg.items()}

# Unit-test
if __name__ == "__main__":
    import yaml

    with open("test_data/cmu-machines.yaml") as f:
        data = yaml.load(f, yaml.Loader)

    creds = CredentialPair.parseall(data["credentials"])
    print(MachineConfig.parseall(data["machines"], creds))


