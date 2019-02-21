# file-to-bmon
Loads sensor reading data located in files into the BMON Building Monitoring system.  Uses python 3.6+.

## Introduction

This script is used to load sensor readings stored in a set of text files
into the [BMON Building Monitoring System](https://github.com/alanmitchell/bmon).  The
script was initially developed to load files of electric meter 15-minute data that were
periodically FTP'd to a server.  The `file-to-bmon` script was scheduled to run
as a CRON job, and it would load any new files that appeared through the FTP process.

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

## Results of Script Execution

There are a number of results from executing the `process_files.py` script:

* The sensor readings extracted from the set of files targeted by the script
are posted to the designated BMON servers (the target files and BMON servers
are determined in the Configuration file described later).  The readings are stored
via an HTTP Post method, as described in [this section of the BMON documentation](https://bmon-documentation.readthedocs.io/en/latest/setting-up-sensors-to-post-to-bmon.html#storing-multiple-sensor-readings).  Because
HTTP is used to store the readings, this script can be run from a computer separate
from the computers hosting the BMON application.
* As the script processes each file, two new files are created--one holding lines in
the original file that were fully processed without errors, and second file containing
lines from the original file that caused errors during processing.  These two new files
are stored in subdirectories of the directory containing the original files being processed.
The subdirectories are named `completed` and `errors`.  The new files are stored in these
subdirectories using the original file name plus `_ok` and `_err` suffixes.  Files in the
`completed` subdirectory are only retained for a limited amount of time (controlled by
a Configuration parameter), but files in the `errors` subdirectory are stored indefinitely.
These files can be edited and then moved back into the original directory so that processing
can be retried.
* After processing, the processed file is deleted, since its contents are essentially retained
in the two files in the `completed` and `errors` subdirectories.
* A log file that holds information about each file processed and records processing error
messages is created.  It is named `process_files.log` and is stored in the `log` subdirectory
of the directory holding the configuration file.

## The Configuration File

## Reader Classes for Parsing Files
