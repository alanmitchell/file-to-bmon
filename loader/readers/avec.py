"""Reader file to parse Alaska Village Electric Cooperative meter files.
These CSV files are produced by the tools/avec_xml_to_csv.py script, which
converts the raw XML meter files from AVEC into CSV files.
"""
from .base_reader import BaseReader

class Reader(BaseReader):
    
    def read_header(self, fobj, file_name):
        # There are no header lines in the file
        return []

    def parse_line(self, lin):

        # there is one reading per line, fields are separated by commas.
        meter_sn, ts, kw = lin.split(',')
        ts = float(ts)
        kw = float(kw)

        return [(ts, f'avec_{meter_sn.strip()}', kw)]
