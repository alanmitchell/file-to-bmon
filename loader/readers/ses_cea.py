"""Reader file to parse Seward Electric Association 15-minute
meter data provided by Chugach Electric.
"""
from .base_reader import BaseReader

class Reader(BaseReader):
    
    def read_header(self, fobj, file_name):
        # There is one header line
        return [fobj.readline()]

    def parse_line(self, lin):

        # there is one reading per line, fields are separated by commas.
        fields = lin.split(',')
        meter_num, dt, tm, _, kw, *rest = fields

        meter_num = meter_num.strip().lower()

        # String versions of the date components
        yr = dt[-2:]
        da = dt[-4:-2]
        mo = '%02d' % int(dt[-6:-4])

        # String versions of the time components
        min = tm[-2:]
        hr = tm[-4:-2]
        if hr == '':
            hr = '0'
        # hr may equal 24, which is invalid.  Convert to 0 and add a day later
        if hr == '24':
            add_a_day = True
            hr = '0'
        else:
            add_a_day = False
        hr = '%02d' % int(hr)

        dt_tm_str = f'20{yr}-{mo}-{da} {hr}:{min}'
        ts = self.ts_from_date_str(dt_tm_str, '%Y-%m-%d %H:%M')
        if add_a_day:
            ts += 24*3600
        # put the timestamp in the middle of the 15 minute interval
        ts -= 7.5 * 60

        kw = float(kw.replace('"', '').replace(',', ''))

        return [(ts, f'ses_{meter_num}', kw)]
