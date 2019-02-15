from pathlib import Path
from datetime import datetime
import time
import calendar

import pytz

class BaseReader:
    
    def __init__(self, **kw):

        # Store all of the keyword arguments as object attributes
        for ky, val in kw.items():
            setattr(self, ky, val)

        # Change the string timezone into a timezone object
        self.time_zone = pytz.timezone(self.time_zone)

        # create subdirectories under file source to hold completed readings
        # and error readings.
        file_pattern = Path(self.pattern)
        (file_pattern.parent / 'completed').mkdir(exist_ok=True)
        (file_pattern.parent / 'errors').mkdir(exist_ok=True)

    def load(self):
        print('loading')
        # Do a blank line check here, so only sending reader non-blank
        # lines.
        # If a line in the file returns records, remember to add the line
        # to the Completed file.
        # Wrap the parse_line call with try/except, and if an error occurs
        # add the line to the Errors file.

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
