# Editing and Adding Sensor-to-BMON Mapping Relationships for AHFC Script

Each sensor read by the file-to-bmon script needs to be sent to a paricular BMON
server.  To determine which BMON server should be the destination for a
particular sensor, a SQLite, CSV text file, or Google Sheets spreadsheet
is used to map Sensor IDs to
BMON IDs. The BMON IDs are established in the YAML Configuration file for
the script.  Also, a default BMON ID can be provided for a file source, and
any sensors not in the mapping file will be sent to that server.

For the Alaska Housing Finance Corporation (AHFC) file-to-bmon script, a
Google Sheets spreadsheet named "sensor_to_bmon" is used to do the mapping.
This spreadsheet was created by Alan Mitchell but shared with Tyler Boyes 
at AHFC.
