# file-to-bmon
Loads sensor reading data located in files into the BMON Building Monitoring system.  Uses python 3.6+.

## Introduction

This script is used to load a set of files containing sensor reading data into
the [BMON Building Monitoring System](https://github.com/alanmitchell/bmon).  The
script was initially developed to load electric meter 15-minute data that was
periodically FTP'd to a server.  The `file-to-bmon` script was scheduled to run
as a CRON job, and it would load any new files that appeared through the FTP process.

The script is designed with following features:

* Multiple different directories of files can be processed with one execution
of the script.
* Files of different formats can be accommodated. Each file format requires a 
"Reader" Python class, which is used to interpret the contents of the file and parse
out the sensor readings.  These Python classes are relatively simple to write and
are discussed further below.
* Script execution is controlled by a [YAML](https://rollout.io/blog/yaml-tutorial-everything-you-need-get-started/)
configuration file. More details on the configuration file contents later.

The script reequires Python 3.6 or greater to excecute and requires one command
line argument, which is the path to the configuration file.
Here is example usage of the script:

```bash
python /home/ahfc/file-to-bmon/loader/process_files.py /home/ahfc/cea-config/cea.yaml
```

The `process_files.py` is the script that should be executed, and it is located in the
`loader` subdirectory of this project.  In the example above, `/home/ahfc/cea-config/cea.yaml`
is the path to the YAML configuration file that will control execution of the script.

## Results of Script Execution

## The Configuration File

## Reader Classes for Parsing Files
