"""Script to test a file Reader class.  Takes a Reader module
name and a path to a test file containing sensor readings, then
prints out the header rows, and prints out the first 3 rows of 
parsed readings.

Example Usage:

    python3 test_reader.py gvea /home/user12/data/testfile.csv
"""

import sys
import importlib

reader_module = sys.argv[1].strip()
test_file_path = sys.argv[2].strip()

# get readers directory in path
sys.path.insert(0, '../loader')

# Dynamically import the module containing the reader class
mod = importlib.import_module(f'readers.{reader_module}')
reader_obj = mod.Reader('', [])

# Open the test data file
fin = open(test_file_path)

print('Header Rows:')
header_str = ''.join(reader_obj.read_header(fin, test_file_path))
print(header_str)

# Print first three rows of data, parsed into sensor readings
print('Parsed Data Rows:')
for i in range(3):
    print(reader_obj.parse_line(fin.readline()))

