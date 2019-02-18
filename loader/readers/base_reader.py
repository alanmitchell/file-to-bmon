from pathlib import Path
from datetime import datetime
import logging
import time
import calendar
from glob import glob

import pytz

class BaseReader:
    
    def __init__(self, **kw):

        # Store all of the keyword arguments as object attributes
        for ky, val in kw.items():
            setattr(self, ky, val)

        # Change the string timezone into a timezone object
        self.time_zone = pytz.timezone(self.time_zone)

        # save the directory where the files are located as a Path
        self.file_dir = Path(self.pattern).parent

        # create subdirectories under file source to hold completed readings
        # and error readings.
        (self.file_dir / 'completed').mkdir(exist_ok=True)
        (self.file_dir / 'errors').mkdir(exist_ok=True)
        (self.file_dir / 'debug').mkdir(exist_ok=True)

        # *** TO DO *** Clean out old files in completed

    def load(self):
        # Do a blank line check here, so only sending reader non-blank
        # lines.
        # If a line in the file returns records, remember to add the line
        # to the Completed file.
        # Wrap the parse_line call with try/except, and if an error occurs
        # add the line to the Errors file.

        # Create list buffers for the poster object to accumulate records 
        # before posting.
        rd_buffer = {}
        for id, _ in self.posters:
            rd_buffer[id] = []

        def post_buffer(min_post_size=1):
            """Posts the readings in the reading buffers if the reading count
            exceeds 'min_post_size'.  Also resets buffer if records are posted.
            """
            for bmon, buf in rd_buffer.items:
                if len(buf) >= min_post_size:
                    with open(self.file_dir / 'debug' / f'{bmon}.txt', 'a') as fout:
                        print('\n'.join(buf), file = fout)
                    rd_buffer[bmon] = []  # reset buffer

        # Get default BMON ID.
        if hasattr(self, 'default_bmon')
            default_bmon = self.default_bmon
        else:
            default_bmon = None

        for fn in glob(self.pattern):

            # track error lines and successful lines in this file.
            error_ct = 0
            success_ct = 0

            try:

                with open(fn) as fin:

                    # get the header lines from the file, and also reassemble into
                    # a string.
                    header_lines = self.read_header(fin, fn)
                    header_str = '/n'.join(header_lines)

                    # Make Paths for both error lines and completed lines
                    f_path = Path(fn)
                    f_err_path = self.file_dir / 'errors' / (f_path.stem + '_err' + f_path.suffix)
                    f_ok_path = self.file_dir / 'completed' / (f_path.stem + '_ok' + f_path.suffix)

                    with open(f_err_path, 'w') as f_err, open(f_ok_path, 'w') as f_ok:
                        
                        # Write the header lines into each file
                        print(header_str, file=f_err)
                        print(header_str, file=f_ok)

                        # process each line
                        for lin in fin:
                            lin = lin.strip()
                            if len(lin) == 0:
                                continue

                            try:
                                reads = self.parse_line(lin)
                                err_in_line = False
                                for ts, sensor_id, val in reads:
                                    # Add the reading to the appropriate BMON buffer
                                    the_bmon = self.id_to_bmon.get(sensor_id, default_bmon)
                                    if the_bmon:
                                        rd_buffer[the_bmon].append( (ts, sensor_id, val) )
                                    else:
                                        # there is no BMON destination for this reading, so register
                                        # it as an error.
                                        err_in_line = True

                                # put the line into the appropriate output file, depending on whether
                                # it had an error or not.
                                if err_in_line:
                                    print(lin, file=f_err)
                                    error_ct += 1
                                else:
                                    print(lin, file=f_ok)
                                    success_ct += 1

                                # Check to see if any of the buffers have enough records to send
                                # to the poster.
                                post_buffer(self.chunk_size)

                            except:
                                error_ct += 1
                                print(lin, file=f_err)

            except:
                logging.exception(f'Error processing {fn}')

            logging.info(f'Processed {fn}: {success_ct} successful lines, {error_ct} error lines.')


        # Send remaining readings to BMON poster
        post_buffer()

    def add_to_error_file(self, lin):
        # Add the bad row to the the errors file.
        # *** FINISH ME ***
        # Track error count here also.
        print(lin)
        pass

    def ts_from_date_str(self, date_time_str, fmt):
        """Converts a date/time string to a Unix Epoch time.
        'date_time_str' is the date/time string, and 'fmt' is the strptime
        format string. 
        """
        # convert timestamp string to Unix Epoch time.
        dt = datetime.strptime(date_time_str, fmt)
        dt_aware = self.time_zone.localize(dt)
        return calendar.timegm(dt_aware.utctimetuple())
