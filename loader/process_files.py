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
from poster.httpPoster2 import HttpPoster, BMSreadConverter

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

    # Make a TimeZone variable for the timezone the data is in
    tz = pytz.timezone(config['time_zone'])

    # Make a dictionary mapping meter numbers to BMON server ID.  This comes from a
    # SQLite database identified in config file.
    db_fn = config['meter_number_db']
    conn = sqlite3.connect(db_fn)
    with conn:
        cur = conn.cursor()
        cur.execute('SELECT meter_number, bmon_id from meters')
        rows = cur.fetchall()
        meter_to_bmon = dict(rows)

except:
    logging.exception('Error in Script Initialization.')
    sys.exit()

# Loop through files to process
for fn in glob.glob(config['meter_files']):

    try:
        # make dictionary keyed on meter number
        # to hold readings
        readings = {}

        # track # of errors
        err_ct = 0

        with open(fn, 'rb') as csvfile:
            for row in csv.reader(csvfile):
                try:
                    meter_num, ts_str, kwh = row[:3]
                    if len(kwh.strip())==0:
                        continue
                    kw = float(kwh) * 4.0    # multiply by 4 to get average kW from kWh

                    # convert timestamp string to Unix Epoch time.
                    dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                    dt_aware = tz.localize(dt)
                    ts = calendar.timegm(dt_aware.utctimetuple())
                    # add 7.5 minutes to put timestamp in middle of interval
                    ts += 7.5 * 60

                    rec = (ts, meter_num, kw)

                    # add to list of readings
                    reading_list =  readings.get(meter_num, [])
                    reading_list.append(rec)
                    readings[meter_num] = reading_list

                except:
                    logging.exception('Error processing %s in %s' % (row, fn))
                    err_ct += 1

        # add readings to correct BMON poster
        for meter_num, reading_list in readings.items():
            if meter_num in meter_to_bmon:
                poster_for_meter = posters[meter_to_bmon[meter_num]]
                poster_for_meter.add_readings(reading_list)
            else:
                logging.error('Meter Number {} not in Meter database.'.format(meter_num))
                err_ct += 1

        # delete meter file if requested and no errors occurred
        if config['delete_after_process'] and err_ct==0:
            os.remove(fn)

    except:
        logging.exception('Error processing %s'  % fn)

# wait until all BMON posters finish their work or stop
# making progress on posting.
for poster in posters.values():
    poster.wait_until_done()
