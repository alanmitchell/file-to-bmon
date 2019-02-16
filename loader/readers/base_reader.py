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

    def load(self):
        # Do a blank line check here, so only sending reader non-blank
        # lines.
        # If a line in the file returns records, remember to add the line
        # to the Completed file.
        # Wrap the parse_line call with try/except, and if an error occurs
        # add the line to the Errors file.
        for fn in glob(self.pattern):

            try:
                # track error lines and successful lines in this file.
                error_ct = 0
                success_ct = 0

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
                        f_err.write(header_str)
                        f_ok.write(header_str)

                        # process each line
                        for lin in fin:
                            lin = lin.strip()
                            if len(lin) == 0:
                                continue
                            try:
                                reads = self.parse_line(lin)
                            except:
                                error_ct += 1
                                print(lin, file=f_err)

            except:
                logging.exception(f'Error processing {fn}')

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
