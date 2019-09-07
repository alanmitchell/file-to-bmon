"""Reader file to parse Golden Valley Electric Association 15-minute
meter data.
"""
from .base_reader import BaseReader

class Reader(BaseReader):
    
    def read_header(self, fobj, file_name):
        # There is one header line
        return [fobj.readline()]

    def parse_line(self, lin):

        # there is one reading per line, fields are separated by commas.
        fields = lin.split(',')
        meter_num, acct, dt_tm_str, kwh = fields[:4]

        # multiply by 4 to get average kW during 15 minute interval
        kw = float(kwh) * 4.0

        ts = self.ts_from_date_str(dt_tm_str, '%Y-%m-%d %H:%M:%S')
        # add 7.5 minutes to put timestamp in middle of interval
        ts += 7.5 * 60

        return [(ts, f'gvea_{meter_num.strip()}', kw)]
