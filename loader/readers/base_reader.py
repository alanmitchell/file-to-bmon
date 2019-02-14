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
        print(self.ts_from_date_str('2019-02-14 11:05:00', '%Y-%m-%d %H:%M:%S'))
        print(time.time())

    def ts_from_date_str(self, date_time_str, fmt):
        """Converts a date/time string to a Unix Epoch time.
        'date_time_str' is the date/time string, and 'fmt' is the strptime
        format string. 
        """
        # convert timestamp string to Unix Epoch time.
        dt = datetime.strptime(date_time_str, fmt)
        dt_aware = self.time_zone.localize(dt)
        return calendar.timegm(dt_aware.utctimetuple())
