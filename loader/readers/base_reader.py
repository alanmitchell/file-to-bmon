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

        # Clean out old files in completed directory
        max_age = self.file_retention * 24. * 3600.    # seconds
        for f_path in (self.file_dir / 'completed').glob('*'):
            if time.time() - f_path.stat().st_mtime > max_age:
                f_path.unlink()

    def load(self):

        # Create list buffers for the poster object to accumulate records 
        # before posting.
        rd_buffer = {}
        for bmon_id, _ in self.posters.items():
            rd_buffer[bmon_id] = []

        def post_buffer(min_post_size=1):
            """Posts the readings in the reading buffers if the reading count
            exceeds 'min_post_size'.  Also resets buffer if records are posted.
            """
            for bmon_id, buf in rd_buffer.items():
                if len(buf) >= min_post_size:
                    with open(self.file_dir / 'debug' / f'{bmon_id}.txt', 'a') as fout:
                        for rd in buf:
                            print(rd, file=fout)
                    rd_buffer[bmon_id] = []  # reset buffer

        # Get default BMON ID, if not present, set to None.
        if hasattr(self, 'default_bmon'):
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
                        if header_str.strip():
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
                                    bmon_id = self.id_to_bmon.get(sensor_id, default_bmon)
                                    if bmon_id:
                                        rd_buffer[bmon_id].append( (ts, sensor_id, val) )
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

                    # if the error and success files have nothing in them, remove them.
                    if f_err_path.stat().st_size == 0:
                        f_err_path.unlink()
                    if f_ok_path.stat().st_size == 0:
                        f_ok_path.unlink()


            except:
                logging.exception(f'Error processing {fn}')

            logging.info(f'Processed {fn}: {success_ct} successful lines, {error_ct} error lines.')
            
            # delete the processed file
            Path(fn).unlink()

        # Send remaining readings to BMON poster
        post_buffer()

    def ts_from_date_str(self, date_time_str, fmt):
        """Converts a date/time string to a Unix Epoch time.
        'date_time_str' is the date/time string, and 'fmt' is the strptime
        format string. 
        """
        # convert timestamp string to Unix Epoch time.
        dt = datetime.strptime(date_time_str, fmt)
        dt_aware = self.time_zone.localize(dt)
        return calendar.timegm(dt_aware.utctimetuple())

    def read_header(self, fobj, file_path):
        """This method must be overridden by the Reader subclass.  'fobj' is a file object
        opened for reading of the file being loaded. 'file_path' is a pathlib.Path
        object pointing at the file. 
        This method should return a list of lines (strings, no line termination) that 
        are the header lines in the file.
        """
        raise TypeError('The read_header() method must be implemented in the Reader sublclass.')

    def parse_line(self, lin):
        """This method must be overridden by the Reader subclass. 'lin' is a line from the
        file being loaded, stripped of leading and trailing whitespace.  This method must
        return a list of three-tuples, each tuple being one sensor reading.  The format
        of the three-tuple is (Unix Epoch timestamp, sensor ID, reading value).  If no readings
        are present in the line, return an empty list.  Do not catch any errors that occur
        during processing of the line, as the calling routine will handle the errors.
        """
        raise TypeError('The parse_line() method must be implemented in the Reader sublclass.')
