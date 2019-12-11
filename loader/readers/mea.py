"""Reader file to parse Matanuska Electric Association 15-minute
meter data that has been saved the BMON mea_data_to_file.py script.
"""
from .base_reader import BaseReader

class Reader(BaseReader):
    
    def read_header(self, fobj, file_name):
        # One header line
        return [fobj.readline()]

    def parse_line(self, lin):

        # there is one reading per line, fields are separated by commas.
        fields = lin.split(',')
        sensor_id, ts, val = fields[:3]
        ts = float(ts)
        val = float(val)

        return [(ts, sensor_id, val)]
