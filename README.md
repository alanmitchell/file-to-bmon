# file-to-bmon
Loads sensor reading data located in files into the BMON Building Monitoring system.  Uses Python 3.6+.

## *NOT COMPLETE YET -- DO NOT USE*

## Introduction

This script is used to load sensor readings stored in a set of text files
into the [BMON Building Monitoring System](https://github.com/alanmitchell/bmon).  The
script was initially developed to load files of electric meter 15-minute data that were
periodically FTP'd to a server.  The script was scheduled to run
as a CRON job, and each time it ran, it would load any new files that appeared through 
the FTP process.

The script is designed with the following features:

* Multiple different directories of files can be processed with one execution
of the script.
* Files of different formats can be accommodated. Each file format requires a 
"Reader" Python class, which is used to interpret the contents of the file and parse
out the sensor readings.  These Python classes are relatively simple to write and
are discussed further below.
* Script execution is controlled by a [YAML](https://rollout.io/blog/yaml-tutorial-everything-you-need-get-started/)
configuration file. More details on the configuration file contents later.
* The script can send sensor readings to different BMON servers.  The user provides
a mapping file or database that indicates which BMON server should be the target
of each sensor reading (based on the ID of that sensor reading). 

## Example Usage

The script requires Python 3.6 or greater to excecute and requires one command
line argument, which is the path to the configuration file.
Here is example usage of the script:

```bash
python /home/ahfc/file-to-bmon/loader/process_files.py /home/ahfc/cea-config/cea.yaml
```

`/home/ahfc/file-to-bmon/loader/process_files.py` is the path to the main script for this
project, which is located in the `loader` subdirectory of this project.  
In the example above, `/home/ahfc/cea-config/cea.yaml`
is the path to the YAML configuration file, created by the user, that will control 
execution of the script.

## Documentation

Here is documentation about script use, configuration and installation:

* [Results of Script Execution and How to Configure Script](docs/script_docs.md)
* [Sample Installation and Use of the Script on the AHFC Webfaction Server](docs/install_docs.md)
