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
    # defaults to INFO if a bad entry in the config file.
    logging.root.setLevel(getattr(logging, config['logging_level'].upper(), 20))
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

    os._exit(0)

    # Make a dictionary mapping sensor IDs to BMON server IDs.  The file name 
    # comes from the config file and is either a SQLite database (if the file
    # extension is .sqlite) or a CSV file (if the file extension is .csv).
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
                id_to_bmon[row[0].strip()] = row[1].strip()

    else:
        raise TypeError('Invalid extension for configuration file.')

except:
    logging.exception('Error in Script Initialization.')
    sys.exit()

# Loop through file sources
for src in config['file_sources']:
    # create subdirectories under file source to hold completed readings
    # and error readings.
    file_pattern = Path(src['pattern'])
    (file_pattern.parent / 'completed').mkdir(exist_ok=True)
    (file_pattern.parent / 'errors').mkdir(exist_ok=True)

    # Loop through files to process
    for fn in glob.glob(src['pattern']):
        pass

# wait until all BMON posters finish their work or stop
# making progress on posting.
for poster in posters.values():
    poster.wait_until_done()
