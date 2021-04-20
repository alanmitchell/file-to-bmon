"""Script to convert Alaska Village Electric Coop XML meter files to CSV files.  
After successful conversion, the XML file is moved into a 'xml-completed'
subdirectory.  The converted CSV files are left in the base directory. 
Error and info log information is put into the 'xmlcsv-log'
subdirectory.

The script expects one command line argument: the folder that
holds the XML files to convert.

Example Usage:

    python3 avec_xml_to_csv.py /home/user1/avec-files

"""
import sys
from pathlib import Path
import shutil
import csv
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET
import logging
import logging.handlers

def parse_xml_file(fn):
    """Parses one XML file with the full path of 'fn' and returns a list of
    readings, each reading being a tuple of the form: 
        (meter serial number, UNIX timestamp, avereage kW in interval)
    Timestamps are placed at the middle of the time interval.
    """
    # create element tree object
    tree = ET.parse(fn)

    # get root element
    root = tree.getroot()

    # create empty list for readings
    readings = []

    for meter_readings in root.findall('./MeterReadings'):
        try:
            meter = meter_readings.find('./Meter')
            meter_sn = meter.attrib['SerialNumber'].strip()
            tz_offset_mins = float(meter.attrib['TimeZoneOffset'])   # minutes
            for interval_data in meter_readings.findall('./IntervalData'):
                interval_spec = interval_data.find('./IntervalSpec')
                interval = float(interval_spec.attrib['Interval'])
                # determine the multiplier to convert kWh in the interval to average
                # kW.
                kw_mult = 60.0 / interval
                direction = interval_spec.attrib['Direction']   # ** To be Addressed later
                for rdg in interval_data.findall('./Reading'):
                    try:
                        kw = kw_mult * float(rdg.attrib['RawReading'])
                        ts_str = rdg.attrib['TimeStamp']
                        ts_dt = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
                        ts_dt += timedelta(minutes=tz_offset_mins)  # convert to UTC
                        ts_dt = ts_dt.replace(tzinfo=timezone.utc)
                        ts = ts_dt.timestamp() + interval / 2.0 * 60.0   # make timestamp in middle of interval
                        readings.append( (meter_sn, ts, kw) )

                    except:
                        logging.exception('Error processing a reading.')

        except:
            logging.exception('Error processing a meter.')
    
    return readings

if __name__ == '__main__':

    # get the base directory to process
    base_path = Path(sys.argv[1])

    # create the directory for the completed XML files
    xml_completed_path = (base_path / 'xml-completed')
    xml_completed_path.mkdir(exist_ok=True)

    # Setup logging for application
    log_file_dir = (base_path / 'xmlcsv-log')
    log_file_dir.mkdir(exist_ok=True)
    log_file_path = log_file_dir / 'xmlcsv.log'

    # create a rotating file handler
    fh = logging.handlers.RotatingFileHandler(log_file_path, maxBytes=200000, backupCount=5)

    # create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    fh.setFormatter(formatter)

    # create a handler that will print to console as well.
    console_h = logging.StreamHandler()
    console_h.setFormatter(formatter)

    # add the handlers to the logger
    logging.root.addHandler(fh)
    logging.root.addHandler(console_h)

    logging.root.setLevel(logging.INFO)

    # Process all of the XML files in the base directory.
    for xml_file in base_path.glob('*.xml'):
        try:
            readings = parse_xml_file(xml_file)
            if len(readings):
                csv_file_name = xml_file.with_suffix('.csv')
                with open(csv_file_name, 'w', newline='') as csvfile:
                    csvwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                    for rdg in readings:
                        csvwriter.writerow(rdg)

                logging.info(f'{len(readings)} readings from {xml_file} converted.')

            else:
                logging.info(f'No readings present in {xml_file}.')

            # copy completed XML file to completed directory and then delete
            shutil.copyfile(xml_file, xml_completed_path / xml_file.name)
            xml_file.unlink()

        except:
            logging.exception(f'Error processing {xml_file}')
