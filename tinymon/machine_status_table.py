"""
machine_status_table.py

Display the information on all of the running machines
"""
from .table_display import display_table

def display_machine_list(machines):
    col_names = ["Name", "Host", "Username"]
    rows = []
    for name, info in machines.items():
        rows.append([
            name,
            info.host,
            info.creds.username
        ])

    display_table("Machine List", col_names, rows)

def display_machines(machines):
    col_names = ["Name", "Uptime", "Cores", "Freq", "CPU %", "RAM", "Temp FS", "Working FS"]
    rows = []
    for name, info in machines.items():
        if info is None:
            rows.append([name, "Unknown"] + ["" for _ in range(len(col_names)-2)])
        else:
            rows.append([
                name,
                info.sys_info.uptime,
                f"{info.cpu_info.cores}C/{info.cpu_info.threads}T",
                info.cpu_info.cpu_freq,
                str(info.cpu_info.avg_util)+"%",
                f"{info.mem_info.mem_used}G/{info.mem_info.mem_total}G",
                f"{info.disk_info.tmpfs_used}G/{info.disk_info.tmpfs_total}G",
                f"{info.disk_info.workfs_used}G/{info.disk_info.workfs_total}G",
            ])

    display_table("Machine Statuses", col_names, rows)

if __name__ == "__main__":
    import yaml
    from .machine_credentials import CredentialPair
    from .machine_config import MachineConfig
    from .machine_status import MachineStatus

    with open("test_data/cmu-machines.yaml") as f:
        data = yaml.load(f, yaml.Loader)

    creds = CredentialPair.parseall(data["credentials"])
    machines = MachineConfig.parseall(data["machines"], creds)
    statuses = {k: MachineStatus.populate(v) for k, v in machines.items()}

    display_machines(statuses)

