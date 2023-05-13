import sys, shutil
import yaml
from tqdm import tqdm
from termcolor import colored, cprint
from .config import *
from .machine_credentials import CredentialPair
from .machine_config import MachineConfig
from .machine_status import MachineStatus
from .job_config import JobConfig
from .job_state_manager import JobStateManager
from .job_manager import *
from .machine_status_table import display_machine_list, display_machines

def usage():
    print("Usage:")
    print("  tinymon machine list   :  list all available machines")
    print("  tinymon machine status :  get status of all available machines")
    print("  tinymon job list  :  list all currently-active jobs")
    print("  tinymon job start (job yaml) (machine) [arg1=val1] [arg2=val2] ...  :  start the job specified in the YAML file")
    print("  tinymon job status (id) :  get the status of a specific job")
    print("  tinymon job retrieve (id) (destination dir) :  pull results from a specific job")
    print("  tinymon job logs (id)  :  get logs from a specific job")
    print("  tinymon job kill (id)  :  forcibly terminate a specific job")
    sys.exit(1)

def main():
    if len(sys.argv) < 3:
        usage()

    if not os.path.exists(MACHINES_YAML):
        print("machines.yaml not found. Populating with example file.")
        shutil.copy(os.path.join(os.path.dirname(__file__), "example.yaml"), MACHINES_YAML)

    with open(MACHINES_YAML) as f:
        machines = yaml.load(f, yaml.Loader)

    if machines.get("is_template", False):
        print(f"Please populate {MACHINES_YAML} with information on your available machines.")
        sys.exit(1)

    creds = CredentialPair.parseall(machines["credentials"])
    machines = MachineConfig.parseall(machines["machines"], creds)
    jm = JobStateManager()

    if sys.argv[1] == "machine":
        if sys.argv[2] == "list":
            display_machine_list(machines)

        elif sys.argv[2] == "status":
            print("Retrieving machine statuses. This may take a while.")
            statuses = {}
            for k, v in tqdm(machines.items()):
                statuses[k] = MachineStatus.populate(v)

            display_machines(statuses)

        else:
            print(f"Invalid subcommand '{sys.argv[1]} {sys.argv[2]}'")
            usage()

    elif sys.argv[1] == "job":
        if sys.argv[2] == "list":
            job_list(jm)

        elif sys.argv[2] == "start":
            try:
                yamlfile = sys.argv[3]
            except:
                print("Usage: tinymon start (job yaml) (machine) [arg1=val1] [arg2=val2]")
                sys.exit(1)

            try:
                machine = sys.argv[4]
            except:
                print("Usage: tinymon start (job yaml) (machine) [arg1=val1] [arg2=val2]")
                sys.exit(1)

            args = {}
            for x in sys.argv[5:]:
                x = x.split("=")
                if len(x) == 1:
                    print(f"Invalid argument {x}. Must be in 'arg=val' style key-value pairs")
                    sys.exit(1)

                args[x[0]] = "=".join(x[1:])

            job_start(machines, jm, machine, yamlfile, args)

        elif sys.argv[2] == "status":
            try:
                jid = int(sys.argv[3])
            except:
                print("Usage: tinymon status (id)")
                print("Specified job ID must be numeric")
                sys.exit(1)

            job_check(machines, jid, jm)

        elif sys.argv[2] == "retrieve":
            try:
                jid = int(sys.argv[3])
            except:
                print("Usage: tinymon retrieve (id) (destination dir)")
                print("Specified job ID must be numeric")
                sys.exit(1)

            try:
                dest = sys.argv[4]
            except:
                print("Usage: tinymon retrieve (id) (destination dir)")
                sys.exit(1)

            job_retrieve(machines, jid, jm, dest)

        elif sys.argv[2] == "logs":
            try:
                jid = int(sys.argv[3])
            except:
                print("Usage: tinymon logs (id)")
                print("Specified job ID must be numeric")
                sys.exit(1)

            job_log(machines, jid, jm)

        elif sys.argv[2] == "kill":
            try:
                jid = int(sys.argv[3])
            except:
                print("Usage: tinymon kill (id)")
                print("Specified job ID must be numeric")
                sys.exit(1)

            job_kill(machines, jid, jm)

        else:
            print(f"Invalid subcommand '{sys.argv[1]} {sys.argv[2]}'")
            usage()

    else:
        print(f"Invalid command '{sys.argv[1]}'")
        usage()

if __name__ == "__main__":
    main()
