"""Script to convert all Excel XLSX files in a directory
into CSV files.  After successful conversion, the XLSX file
is deleted.

The script expects one command line argument: the folder that
holds the XLSX files to convert.

Example Usage:

    python3 xlsx_to_csv.py /home/user1/excelfiles

This script is used with Golden Valley Electric 15 minute electric
meter readings files.
"""
import sys
from path import Path
from xlsx2csv import Xlsx2csv

# get the first command line argument which is the path the folder
# holding the xlsx files.
xlsx_folder = sys.argv[1]

# Loop through all XLSX files in that folder, convert and delete
# the orginal if the conversion was successful.
for p_xlsx in Path(xlsx_folder).glob('*.xlsx'):
    p_csv = p_xlsx.with_suffix('.csv')
    try:
        Xlsx2csv(p_xlsx, outputencoding="utf-8").convert(p_csv)
        if p_csv.exists():
            p_xlsx.unlink()
    except:
        print(f'Error processing {p_xlsx}.')
