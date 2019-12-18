#!/usr/bin/env python3.7
"""Script to add sensor reading data from files into BMON systems.
"""

import glob
import logging
from pathlib import Path
import os
import csv
import sys
from datetime import datetime
import importlib
import calendar
import sqlite3

import yaml
import pytz

import logging_setup
from poster.httpPoster import HttpPoster, BMSreadConverter

# configuration file name, 1st command line argument
config_fn = sys.argv[1]

# get path to folder where config file is.  This folder
# is used to store logs and other files.
config_folder = Path(config_fn).parent

# Make sure there are log and posters directories underneath config file
(config_folder / 'log').mkdir(exist_ok=True)
(config_folder / 'posters').mkdir(exist_ok=True)

# ----- Setup Exception/Debug Logging for the Application

# Log file for the application.
log_file = config_folder / 'log' / 'process_files.log'
logging_setup.configure_logging(log_file)

# -------------------

try:
    # load configuration file describing general operation of this script
    # and the files to be loaded.
    config = yaml.load(open(config_fn))

except:
    logging.exception('Error in Reading Configuration File.')
    sys.exit()

try:
    # set the log level. Because we are setting this on the logger, it will apply
    # to all handlers (unless maybe you set a specific level on a handler?).
    # defaults to INFO if no entry or a bad entry in the config file.
    if 'logging_level' in config:
        logging.root.setLevel(getattr(logging, config['logging_level'].upper(), logging.INFO))
    else:
        logging.root.setLevel(logging.INFO)
    logging.info('Started file processing.')

    # start BMON posters and put in a dictionary
    posters = {}
    poster_folder = config_folder / 'posters'
    for id, bmon_info in config['bmon_servers'].items():
        posters[id] = HttpPoster(bmon_info['url'],
                                 reading_converter=BMSreadConverter(bmon_info['store_key']),
                                 post_q_filename=poster_folder / ('%s_postQ.sqlite' % id),
                                 post_thread_count=1,
                                 post_time_file=poster_folder / ('%s_last_post_time' % id)
                                )

    # Make a dictionary mapping sensor IDs to BMON server IDs.  The file name 
    # comes from the config file and is either a SQLite database (if the file
    # extension is .sqlite) or a CSV file (if the file extension is .csv).
    # If no file is specified, then presumably every file source will have a 
    # default bmon location.
    if 'sensor_to_bmon_file' in config:
        id_to_bmon_fn = Path(config['sensor_to_bmon_file'])
        if id_to_bmon_fn.suffix.lower() == '.sqlite':
            conn = sqlite3.connect(id_to_bmon_fn)
            with conn:
                cur = conn.cursor()
                cur.execute('SELECT sensor_id, bmon_id from sensor_target')
                rows = cur.fetchall()
                id_to_bmon = dict(rows)

        elif id_to_bmon_fn.suffix.lower() ==  '.csv':
            id_to_bmon = {}
            with open(id_to_bmon_fn) as csvfile:
                filereader = csv.reader(csvfile)
                for row in filereader:
                    if len(row) != 2:
                        continue
                    id_to_bmon[row[0].strip()] = row[1].strip()

        else:
            raise TypeError('Invalid extension for configuration file.')

    else:
        # No mapping file so use empty dictionary.
        id_to_bmon = {}

except:
    logging.exception('Error in Script Initialization.')
    sys.exit()

# Loop through file sources
for src in config['file_sources']:

    try:
        # Extract the reader to use with this set of files and then
        # delete it from the dictionary
        reader_name = src['reader']
        del src['reader']

        # Dynamically import the module containing the reader class
        mod = importlib.import_module(f'readers.{reader_name}')

        # Determine Dry-Run status.  If setting is not present, then not
        # a dry run.
        if 'dry_run' in config:
            dry_run = config['dry_run']
        else:
            dry_run = False
        
        # develop a dictionary of the constructor parameters for the
        # reader class, some of which come from the config file.
        reader_params = {
            'id_to_bmon': id_to_bmon,
            'posters': posters,
            'dry_run': dry_run,
        }
        reader_params.update(src)

        # pass parameters as keyword arguments to the Reader class within
        # the imported module.
        reader_obj = mod.Reader(**reader_params)
        reader_obj.load()     # process the files

    except:
        logging.exception(f'Error processing {src["pattern"]}')

# wait until all BMON posters finish their work or stop
# making progress on posting.
for poster in posters.values():
    poster.wait_until_done()
