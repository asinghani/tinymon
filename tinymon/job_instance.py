"""
job_instance.py

Provides a data structure JobInstance for maintaining
information about a single invocation of a job
"""
from dataclasses import dataclass
from .job_config import JobConfig
from .machine_config import MachineConfig
import os

@dataclass
class JobInstance:
    config: JobConfig
    machine: MachineConfig
    jid: int
    args: dict

    def get_jobdir(self):
        return os.path.join(self.machine.workdir, f"run-{self.jid}-work/")

    def get_tmpdir(self):
        return os.path.join(self.machine.tmpdir, f"run-{self.jid}-tmp/")

    def get_data_dir(self):
        return os.path.join(self.machine.workdir, f"run-{self.jid}-src/")

    def get_results_dir(self):
        if self.config.results_dir_remote:
            return self.config.results_dir_remote.replace(r"{tmpdir}", self.get_tmpdir())\
                                            .replace(r"{workdir}", self.get_jobdir())
        else:
            return None

    def get_entry_cmd(self):
        cmd = self.config.entry_cmd.replace(r"{tmpdir}", self.get_tmpdir())\
                               .replace(r"{workdir}", self.get_jobdir())

        cmd = cmd.format(**self.args)
        return cmd


# Unit-test
if __name__ == "__main__":
    import yaml

    with open("test_data/sleep-30.yaml") as f:
        data = yaml.load(f, yaml.Loader)

    print(JobConfig.parseconfig(data))


