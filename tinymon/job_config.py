"""
job_config.py

Provides a data structure JobConfig for maintaining the information
about a job that can be run on a machine
"""
from dataclasses import dataclass

@dataclass
class JobConfig:
    name: str
    entry_cmd: str
    results_dir_remote: str

    @classmethod
    def parseconfig(cls, cfg):
        assert "name" in cfg, "Jobs must have a 'name' parameter"
        assert "entry_cmd" in cfg, "Jobs must have a 'entry_cmd' parameter"

        return cls(cfg["name"], cfg["entry_cmd"], cfg.get("results_dir_remote", None))

# Unit-test
if __name__ == "__main__":
    import yaml

    with open("test_data/sleep-30.yaml") as f:
        data = yaml.load(f, yaml.Loader)

    print(JobConfig.parseconfig(data))


