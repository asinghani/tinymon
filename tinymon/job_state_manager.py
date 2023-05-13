"""
job_state_manager.py

JobStateManager tracks all running and completed jobs
"""
from .config import JOBMGR_YAML
import yaml

class JobStateManager:
    def __init__(self):
        try:
            with open(JOBMGR_YAML) as f:
                self.data = yaml.load(f, yaml.Loader)

            self.jobs = self.data["jobs"]
            self.idx = int(self.data["idx"])

        except:
            self.jobs = {}
            self.idx = 1000

    def save(self):
        self.data = {"jobs": self.jobs, "idx": self.idx}

        with open(JOBMGR_YAML, "w+") as f:
            yaml.dump(self.data, f, yaml.Dumper)

    def get_next_jid(self):
        self.idx += 1
        jid = self.idx
        self.save()
        return jid

    def add(self, jid, name, machine, data_dir, results_dir, cmd, pid, start_time):
        self.jobs[jid] = {"id": jid, "name": name, "machine": machine,
                          "pid": pid, "start_cmd": cmd,
                          "data_dir": data_dir, "results_dir": results_dir,
                          "start_time": start_time, "active": True}
        self.save()
        return jid

    def set_stale(self, jid):
        self.jobs[jid]["active"] = False
        self.save()

    def remove(self, jid):
        del self.jobs[jid]
        self.save()

    def get(self, jid):
        return self.jobs.get(jid, None)

    def list(self):
        return self.jobs
