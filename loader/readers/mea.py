from .base_reader import BaseReader

class Reader(BaseReader):
    
    def read_header(self, fobj, file_path):
        print('Reading Header in cea')
        header_lines = []
        return header_lines

    def parse_line(self, lin):
        readings = []
        return readings
