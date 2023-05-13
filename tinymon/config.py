import os

SELF_DIR = os.path.expanduser("~/.tinymon/")

if not os.path.exists(SELF_DIR): os.mkdir(SELF_DIR)

MACHINES_YAML = os.path.expanduser("~/.tinymon/machines.yaml")
JOBMGR_YAML = os.path.expanduser("~/.tinymon/job_manager.yaml")
