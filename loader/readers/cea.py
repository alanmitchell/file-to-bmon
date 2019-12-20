"""Reader file to parse Chugach Electric Association 15-minute
meter data.
"""
from .base_reader import BaseReader

class Reader(BaseReader):
    
    def read_header(self, fobj, file_name):
        # There are no header lines in the file
        return []

    def parse_line(self, lin):

        # there is one reading per line, fields are separated by commas.
        fields = lin.split(',')
        meter_num, dt_tm_str, kwh = fields[:3]
        meter_mult = float(fields[-1])

        # multiply by 4 to get average kW during 15 minute interval.  
        # Include meter multiplier.
        kw = float(kwh) * 4.0 * meter_mult

        try:
            ts = self.ts_from_date_str(dt_tm_str, '%Y-%m-%d %H:%M:%S')
        except:
            # MOA sends the date in this format
            ts = self.ts_from_date_str(dt_tm_str, '%m/%d/%Y %H:%M')

        # add 7.5 minutes to put timestamp in middle of interval
        ts += 7.5 * 60

        return [(ts, f'cea_{meter_num.strip()}', kw)]
