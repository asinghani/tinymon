# tinymon

A lightweight utility for monitoring and running jobs across a variety of servers. As opposed to similar tools, `tinymon` does not require any dependencies to be installed on the target server, and runs entirely in Python on the user's local machine.

## Installation

To install `tinymon`:

```
git clone https://github.com/asinghani/tinymon
cd tinymon
pip3 install -e .
```

This will also install all of `tinymon`'s dependencies, namely:

- `pyyaml` - Used for parsing the YAML config file format
- `pwntools` - Used for remotely connecting to servers via SSH
- `termcolor` - Used for formatting program output
- `tqdm` - Used for showing progress bars

## Getting Started

`tinymon` includes an example hash-cracking program which can be used to demonstrate its capabilities. Start by installing and running `tinymon`. This will create a `.tinymon` directory in your home dir, which contains an example configuration YAML file.

See `test_data/cmu-machines.yaml` for an example of the machine specification format, or see the "File Formats" section for a detailed explanation of the YAML file format.

If you are at Carnegie Mellon University, simply copy `test_data/cmu-machines.yaml` to `~/.tinymon/machines.yaml` and add your Andrew ID username and password into the designated fields.

1. Get a list of all loaded machines:

```
$ tinymon machine list
Machine List

| Name         | Host                     | Username |
|--------------|--------------------------|----------|
| cmu-linux-15 | linux-15.andrew.cmu.edu  | asinghan |
| cmu-linux-16 | linux-16.andrew.cmu.edu  | asinghan |
| cmu-linux-17 | linux-17.andrew.cmu.edu  | asinghan |
| cmu-linux-18 | linux-18.andrew.cmu.edu  | asinghan |
| cmu-ghc40    | ghc40.ghc.andrew.cmu.edu | asinghan |
```

2. Pull status information from all machines:

```
$ tinymon machine status
Retrieving machine statuses. This may take a while.
100%|███████████████████████████████████████████████| 5/5 [00:18<00:00,  3.79s/it]
Machine Statuses

| Name         | Uptime  | Cores | Freq    | CPU % | RAM        | Temp FS       | Working FS |
|--------------|---------|-------|---------|-------|------------|---------------|------------|
| cmu-linux-15 | 16h 55m | 4C/4T | 2.60GHz | 0.0%  | 0.6G/31.4G | 0.0G/18.5G    | 1.5G/1.9G  |
| cmu-linux-16 | 16h 55m | 4C/4T | 2.60GHz | 1.0%  | 0.6G/31.4G | 0.0G/18.5G    | 1.5G/1.9G  |
| cmu-linux-17 | 16h 55m | 4C/4T | 2.60GHz | 5.0%  | 0.7G/31.4G | 0.0G/18.5G    | 1.5G/1.9G  |
| cmu-linux-18 | 16h 56m | 4C/4T | 2.60GHz | 0.7%  | 0.7G/31.4G | 0.0G/18.5G    | 1.5G/1.9G  |
```

3. Start the example "hashcrack" (which cracks a password from its hash) job onto one of the machines, with the hash of "123456" as the provided hash

```
$ tinymon job start test_data/hashcrack.yaml cmu-linux-15 tgt_hash=8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92
Loading job from file test_data/hashcrack.yaml
Starting job hashcrack on machine cmu-linux-15
Starting with command: python3 hashcrack.py 8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92 "/afs/andrew.cmu.edu/usr/asinghan/run-1063-work//crack.txt"
Job started with job ID 1063 and PID 93687
```

4. Check the job status table to see the job listed there

```
Running Job List

| Job ID | Name      | Machine      | Running Time |
|--------|-----------|--------------|--------------|
| 1063   | hashcrack | cmu-linux-15 | 0m 19s       |
```

5. Check the job status and get its logs:

```
$ tinymon job status 1063
Checking status of job ID 1063
================================================================================
progress = 1.0%
progress = 2.0%
progress = 3.0%
progress = 4.0%
progress = 5.0%
progress = 6.0%
progress = 7.0%
progress = 8.0%
progress = 9.0%
progress = 10.0%
progress = 11.0%
progress = 12.0%
FOUND 123456

================================================================================
Job ID 1063 has completed
Use the 'retrieve' command to pull the results of the job
```

6. Retrieve the job results and read them:

```
$ tinymon job retrieve 1063 /tmp/test-out
Retrieving results from job ID 1063
Saved results to /tmp/test-out

$ ls /tmp/test-out/
crack.txt

$ cat /tmp/test-out/crack.txt
FOUND = 123456
```

## Usage

```
tinymon machine list   :  list all available machines
tinymon machine status :  get status of all available machines
tinymon job list  :  list all currently-active jobs
tinymon job start (job yaml) (machine) [arg1=val1] [arg2=val2] ...  :  start the job specified in the YAML file
tinymon job status (id) :  get the status of a specific job
tinymon job retrieve (id) (destination dir) :  pull results from a specific job
tinymon job logs (id)  :  get logs from a specific job
tinymon job kill (id)  :  forcibly terminate a specific job
```

## File Formats

Example `machines.yaml` file:

```
credentials:
  EXAMPLE1:
    username: (username)
    password: (password)
  EXAMPLE2:
    username: (username)
    password_cmd: (command that outputs password, i.e. from password manager)
  EXAMPLE3:
    username: (username)
    sshkey: (path to SSH private key)

machines:
  MACHINE-NAME:
    host: (machine hostname or IP)
    creds: (one of the credential-pair names, as above)
    tmpdir: (path to temporary directory)
    tmpdir_type: (local, shared, or afs)
    workdir: (path to work directory)
    workdir_type: (local, shared, or afs)
```

Example job YAML file:

```
name: JOB_NAME
results_dir_remote: "{workdir}/"
entry_cmd: python3 hashcrack.py {tgt_hash} "{workdir}/crack.txt"
```

Note that `{tmpdir}` and `{workdir}` will be auto-substituted with a fresh directory created for each invocation of the job (these will be subdirectories of the machine's own tmpdir/workdir, but in a directory marked with the job ID). Other substituted parameters (i.e. `{tgt_hash}` above) can be provided on the command-line during an invocation to `tinymon start`.

## Code Structure

- config.py - Specifies the config-file locations
- job_config.py - Parses and handles the configuration for a job to run
- job_instance.py - An instance of a specific job, ready to run
- job_manager.py - Handles running, tracking, and stopping jobs
- job_state_manager.py - Persistently tracks jobs across invocations of the program
- machine_access.py - SSH access to machines and running programs
- machine_config.py - Access and job-running information about machines
- machine_credentials.py - Credentials/login information about machines
- machine_status.py - Retrieve the status of a machine
- machine_status_table.py - Render the machines status as a talbe
- table_display.py - Utility for rendering tables
- tinymon.py - Main entry-point, handles command-line commands and error checking


## License

MIT
