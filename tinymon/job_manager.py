"""
job_manager.py

Provides functions to handle starting and stopping jobs
"""
from .job_instance import JobInstance
from .job_config import JobConfig
from .machine_access import MachineAccess
from .table_display import display_table
from datetime import datetime
import sys, os
import time
import yaml

def job_start(machines, jm, machine_name, jobfile, args):
    print(f"Loading job from file {jobfile}")
    jid = jm.get_next_jid()

    with open(jobfile) as f:
        data = yaml.load(f, yaml.Loader)

    jobdir = os.path.dirname(jobfile)

    job_config = JobConfig.parseconfig(data)

    if machine_name not in machines:
        print(f"Error: unknown machine {machine_name}")
        sys.exit(1)

    print(f"Starting job {job_config.name} on machine {machine_name}")

    machine = machines[machine_name]

    job_inst = JobInstance(job_config, machine, jid, args)

    with MachineAccess(machine) as m:
        assert m.run_to_end("mkdir -p "+job_inst.get_jobdir())[1] == 0, "Failed to create working directory"
        assert m.run_to_end("mkdir -p "+job_inst.get_tmpdir())[1] == 0, "Failed to create temp directory"
        assert m.run_to_end("mkdir -p "+job_inst.get_data_dir())[1] == 0, "Failed to create src directory"

        m.push_dir(jobdir, job_inst.get_data_dir())
        dirname = jobdir
        while dirname.endswith("/"): dirname = dirname[:-1]
        dirname = dirname.split("/")[-1]

        cmd = job_inst.get_entry_cmd()
        print(f"Starting with command: {cmd}")

        data_dir = os.path.join(job_inst.get_data_dir(), dirname)

        pid = m.execute_with_nohup(cmd, data_dir)
        print(f"Job started with job ID {jid} and PID {pid}")

    jm.add(jid, job_config.name, machine_name,
           data_dir, job_inst.get_results_dir(), cmd, pid, time.time())

    return jid

def job_kill(machines, jid, jm):
    state = jm.get(jid)
    assert state is not None, f"Job ID {jid} doesn't exist"
    assert state["active"], f"Job ID {jid} has completed already"

    machine = machines[state["machine"]]
    pid = int(state["pid"])

    with MachineAccess(machine) as m:
        assert m.run_to_end(f"kill -9 {pid}")[1] == 0, "Failed to kill the process"

    print(f"Successfully killed job ID {jid} of job {state['name']} on machine {state['machine']}")
    jm.remove(jid)

def job_log(machines, jid, jm):
    state = jm.get(jid)
    assert state is not None, f"Job ID {jid} doesn't exist"

    print(f"Retrieving logs for job ID {jid}")
    print()
    print("="*80)

    machine = machines[state["machine"]]
    pid = int(state["pid"])

    with MachineAccess(machine) as m:
        print(os.path.join(state["data_dir"], "nohup.out"))
        m.pull_file(os.path.join(state["data_dir"], "nohup.out"), "/tmp/_nohup.out")

    with open("/tmp/_nohup.out") as f:
        print(f.read())

    print("="*80)

def job_check(machines, jid, jm):
    state = jm.get(jid)
    assert state is not None, f"Job ID {jid} doesn't exist"
    assert state["active"], f"Job ID {jid} has completed already"

    print(f"Checking status of job ID {jid}")

    machine = machines[state["machine"]]
    pid = int(state["pid"])

    with MachineAccess(machine) as m:
        is_running = (m.run_to_end(f"ps -p {pid}")[1] == 0)

        if not is_running:
            m.pull_file(os.path.join(state["data_dir"], "nohup.out"), "/tmp/_nohup.out")

    if is_running:
        print(f"Job ID {jid} is running")
    else:
        print("="*80)
        with open("/tmp/_nohup.out") as f:
            print(f.read())
        print("="*80)

        print(f"Job ID {jid} has completed")

        if state["results_dir"] is not None:
            print(f"Use the 'retrieve' command to pull the results of the job")

        jm.set_stale(jid)

    return is_running

def job_retrieve(machines, jid, jm, outdir):
    state = jm.get(jid)
    assert state is not None, f"Job ID {jid} doesn't exist"
    assert not state["active"], f"Job ID {jid} is still running"
    assert state["results_dir"] is not None, f"Job ID {jid} does not have a results directory specified"

    print(f"Retrieving results from job ID {jid}")

    machine = machines[state["machine"]]
    pid = int(state["pid"])

    with MachineAccess(machine) as m:
        m.pull_dir(state["results_dir"], outdir)

    print(f"Saved results to {outdir}")

def job_list(jm):
    col_names = ["Job ID", "Name", "Machine", "Running Time"]
    rows = []

    for jid, job in jm.list().items():
        if not job["active"]: continue

        td = datetime.now() - datetime.fromtimestamp(int(job["start_time"]))

        if td.days > 0:
            td = "{:d}d {:d}h {:d}m {:d}s".format(td.days, td.seconds // 3600, td.seconds // 60 % 60, td.seconds % 60)
        elif td.seconds > 3600:
            td = "{:d}h {:d}m {:d}s".format(td.seconds // 3600, td.seconds // 60 % 60, td.seconds % 60)
        else:
            td = "{:d}m {:d}s".format(td.seconds // 60 % 60, td.seconds % 60)

        rows.append([
            str(jid),
            job["name"],
            job["machine"],
            td
        ])

    if len(rows) == 0:
        print("No currently-running jobs")
    else:
        display_table("Running Job List", col_names, rows)

if __name__ == "__main__":
    from .machine_credentials import CredentialPair
    from .machine_config import MachineConfig
    from .machine_status import MachineStatus
    from .job_config import JobConfig
    from .job_state_manager import JobStateManager

    with open("test_data/cmu-machines.yaml") as f:
        data = yaml.load(f, yaml.Loader)

    creds = CredentialPair.parseall(data["credentials"])
    machines = MachineConfig.parseall(data["machines"], creds)

    jm = JobStateManager()

    print(machines["finger"])
    jid = job_start(machines, jm, "finger", "test_data/sleep-5.yaml", {})
    job_list(jm)
    time.sleep(1)
    job_check(machines, jid, jm)
    time.sleep(6)
    job_check(machines, jid, jm)

    try: os.system("rm -r /tmp/example-data-out")
    except: pass

    job_retrieve(machines, jid, jm, "/tmp/example-data-out")
