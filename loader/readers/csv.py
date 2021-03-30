"""Reader file to parse CCHRC CSV files"""
from .base_reader import BaseReader

class Reader(BaseReader):
    
    def read_header(self, fobj, file_name):
        # One header line
        return [fobj.readline()]

    def parse_line(self, lin):

        # there is one reading per line, fields are separated by commas.
        fields = lin.split(',')
        dt_tm, sensor_id, value = fields[:3]

        return [(float(dt_tm), sensor_id, float(value))]
