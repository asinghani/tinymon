"""
machine_status.py

Provides a data structure and a utility function for obtaining
status-information about a machine including its hardware specs
and current utilization
"""
from dataclasses import dataclass
from .machine_access import MachineAccess
from .machine_config import DirType

@dataclass
class SysInfo:
    uptime: str

    @classmethod
    def populate(cls, ssh, machine):
        return cls(
            ssh.execute_cmd("uptime -p").strip() \
                .replace("years", "y").replace("months", "mo") \
                .replace("weeks", "w").replace("days", "d") \
                .replace("hours", "h").replace("minutes", "m") \
                .replace("up", "") \
                .replace(" ", "").replace(",", " ").strip()
        )

@dataclass
class CPUInfo:
    cpu_type: str
    cpu_freq: str
    cores: int
    threads: int
    avg_util: int

    @classmethod
    def populate(cls, ssh, machine):
        cpumodel, cpufreq = ssh.execute_cmd("cat /proc/cpuinfo | grep 'model name' | head -n 1") \
                                .strip().split(":")[-1].split("@")

        tpc = int(ssh.execute_cmd("lscpu | grep 'Thread(s) per core'").split(":")[-1].strip())
        cps = int(ssh.execute_cmd("lscpu | grep 'Core(s) per socket'").split(":")[-1].strip())
        soc = int(ssh.execute_cmd("lscpu | grep 'Socket(s)'").split(":")[-1].strip())

        # https://stackoverflow.com/questions/26791240/how-to-get-percentage-of-processor-use-with-bash
        util = float(ssh.execute_cmd("awk -v a=\"$(awk '/cpu /{print $2+$4,$2+$4+$5}' /proc/stat; sleep 1)\" '/cpu /{split(a,b,\" \"); print 100*($2+$4-b[1])/($2+$4+$5-b[2])}'  /proc/stat").strip())
        util = round(util, 1)

        return cls(
            cpumodel.strip(),
            cpufreq.strip(),
            cps*soc,
            cps*soc*tpc,
            util
        )

@dataclass
class MemInfo:
    mem_used: int
    mem_total: int

    @classmethod
    def populate(cls, ssh, machine):
        mem = ssh.execute_cmd("free -m | head -n 2 | tail -n 1").strip().split()

        return cls(
            round(float(mem[2])/1024, 1),
            round(float(mem[1])/1024, 1)
        )

@dataclass
class DiskInfo:
    tmpfs_used: int
    tmpfs_total: int
    workfs_used: int
    workfs_total: int

    @classmethod
    def populate(cls, ssh, machine):
        if machine.tmpdir_type == DirType.AFS:
            df = ssh.execute_cmd(f"fs lq {machine.tmpdir} | tail -n 1").strip().split()
            tmpfs_used = round(float(df[2]) / 1024 / 1024, 1)
            tmpfs_total = round(float(df[1]) / 1024 / 1024, 1)
        else:
            df = ssh.execute_cmd(f"df {machine.tmpdir} | tail -n 1").strip().split()
            tmpfs_used = round(float(df[2]) / 1024 / 1024, 1)
            tmpfs_total = round(float(df[3]) / 1024 / 1024, 1)

        if machine.workdir_type == DirType.AFS:
            df = ssh.execute_cmd(f"fs lq {machine.workdir} | tail -n 1").strip().split()
            workfs_used = round(float(df[2]) / 1024 / 1024, 1)
            workfs_total = round(float(df[1]) / 1024 / 1024, 1)
        else:
            df = ssh.execute_cmd(f"df {machine.workdir} | tail -n 1").strip().split()
            workfs_used = round(float(df[2]) / 1024 / 1024, 1)
            workfs_total = round(float(df[3]) / 1024 / 1024, 1)

        return cls(
            tmpfs_used,
            tmpfs_total,
            workfs_used,
            workfs_total
        )

@dataclass
class MachineStatus:
    sys_info: SysInfo
    cpu_info: CPUInfo
    mem_info: MemInfo
    disk_info: DiskInfo

    @classmethod
    def populate(cls, machine):
        try:
            with MachineAccess(machine) as m:
                out = cls(
                    SysInfo.populate(m, machine),
                    CPUInfo.populate(m, machine),
                    MemInfo.populate(m, machine),
                    DiskInfo.populate(m, machine),
                )

            return out
        except:
            return None

if __name__ == "__main__":
    import yaml
    from .machine_credentials import CredentialPair
    from .machine_config import MachineConfig

    with open("test_data/cmu-machines.yaml") as f:
        data = yaml.load(f, yaml.Loader)

    creds = CredentialPair.parseall(data["credentials"])
    machines = MachineConfig.parseall(data["machines"], creds)

    ## TODO
    print(MachineStatus.populate(machines["finger"]))
