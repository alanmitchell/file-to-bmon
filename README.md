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

## Results of Script Execution

There are a number of results that occur from executing the `process_files.py` script:

* The sensor readings extracted from the set of files targeted by the script
are posted to the designated BMON servers (the target files and BMON servers
are determined in the Configuration file described later).  The readings are transferred
via an HTTP Post method, as described in [this section of the BMON documentation](https://bmon-documentation.readthedocs.io/en/latest/setting-up-sensors-to-post-to-bmon.html#storing-multiple-sensor-readings).  Because
HTTP is used to store the readings, this script can be run from a computer separate
from the computers hosting the BMON applications.
* As the script processes each file, two new files are created--one holding lines from
the original file that were fully processed without errors, and a second file containing
lines from the original file that caused errors during processing.  These two new files
are stored in subdirectories of the directory containing the original files being processed.
The subdirectories are named `completed` and `errors`.  The new files are stored in these
subdirectories using the original file name plus `_ok` and `_err` suffixes.  Files in the
`completed` subdirectory are only retained for a limited amount of time (controlled by
a Configuration parameter), but files in the `errors` subdirectory are stored indefinitely.
These files can be edited and then moved back into the original directory so that processing
can be tried again.
* After processing, the processed file is deleted, since its contents are essentially retained
in the two files in the `completed` and `errors` subdirectories.
* A log file that holds information about each file processed and records processing error
messages is also created and appended to.  It is named `process_files.log` and is stored 
in the `log` subdirectory of the directory holding the configuration file.

## The Configuration File

The Configuration file controls the operation of the script, and the path to the Configuration
file must be provided as the first command line argument when using the script.
There is an example Configuration
file provided [in the repository here](config/config_example.yaml).  The Configuration file uses
[YAML format](https://rollout.io/blog/yaml-tutorial-everything-you-need-get-started/) for
simplicity.  This section describes the contents of the Configuration file.

---

```YAML
sensor_to_bmon_file: /home/cea/meter_db/meters.sqlite
```
The `sensor_to_bmon_file` setting states the path to the file that maps Sensor IDs to BMON servers.
For each Sensor ID read from the files being processed, this mapping file is checked to 
see where the reading should be posted.  BMON servers are identified by the IDs that you
create in the `bmon_servers` section of this Configuration file.  In the sample Configuration
file, you will find two BMON server IDs: `ahfc` and `mssd`.

There are two possible formats for this Sensor ID-to-BMON mapping file.  The file can either
be a SQLite database, and if so, the file must end with the `.sqlite` extension.  If the file
is a SQLite database, the database must have a table named `sensor_target` and that table
must have two string columns: `sensor_id` and `bmon_id`.  Each row of the table maps a
particular Sensor ID to a destination BMON server.

The other possible format for the mapping file is a comma-separated-value (CSV) text file. If
this file format is used, each row of the file should have a Sensor ID and the target BMON ID,
separated by a comma.  The file name must end in the extension `.csv`. Here is an example of
the file contents:

```text
AK9023432, ahfc
AN448234223, mssd
sensor_xyz, ahfc
```

One advantage of using a SQLite database file for this mapping is that a simple SQLite
web-based editing application can be used to maintain the data.  Such an application
is [phpLiteAdmin](https://www.phpliteadmin.org/).

The `sensor_to_bmon_file` file is optional *if* instead you provide a `default_bmon` setting
for each of the file sources defined in the `file_sources` section of this Configuration
file.  If you take this approach, you do not need to provide the `sensor_to_bmon_file` setting
line in the Configuration file.

If a sensor ID is found in one of the processed files that is not provided in the 
`sensor_to_bmon_file` and there is no `default_bmon` setting for the file source, the
line containing the Sensor ID is considered an error, and it is added to the error file.

---

```YAML
logging_level: INFO
```

The `logging_level` setting determines how much information will be put into the application's
log file, `process_files.log`.  The choices for this setting, ranging from the most amount of
information to the least, are `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.  If this setting
is not provided, it defaults to `INFO`.

---

```YAML
file_sources:
  - pattern: /home/alan/chugach/*.csv
    reader: cea
    default_bmon: ahfc
    time_zone: US/Alaska
    file_retention: 3
    chunk_size: 50
  - pattern: /home/alan/mea/*.csv
    reader: mea
```

The `file_sources` key or section in the Configuration file consists of a list of file sets
that will be processed by the script.  The `-` character starts a new list item, describing
a particular set of files and how they should be processed.  In the sample above, there
are two different sets of files that will be processed, because there are two `-` items
indented under the `file_sources` key.

For each set of files, there are a numbers of settings that control the processing of the
files.  First, there are two *required* settings that must be present for each file set:
`pattern` and `reader`.

`pattern` is file pattern compatible with the [Python glob function](https://docs.python.org/3/library/glob.html).
In the example above, the `pattern` for the first file set is `/home/alan/chugach/*.csv`.
This pattern identifies all files withe the `.csv` extension found in the `/home/alan/chugach`
directory.  All of those files will be processed by the script.

The second required setting for each file set is the `reader` setting.  This setting idenfies the
Python Reader module that will be used to parse the file; each different file format requires
a different type of reader module.  There is a subsequent section that explains these Readers in
more detail.  For the example above, the Reader is `cea`, so the script will use the Reader found
in the `cea.py` file in the `loader/readers` directory of this project.  So, the `reader` must
name a Python module (without the `.py` extension) found in the `loader/readers` directory.
The structure of that Reader module is described in a subsequent section.  The `cea` reader in the
example happens to be a Reader that knows how to parse readings from a Chugach Electric
Association 15-minute elecric meter data file. 

---


## Reader Classes for Parsing Files
