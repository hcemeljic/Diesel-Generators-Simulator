import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import sqlite3

# The pattern of scanning all files with an .XLS extension.
pattern = '*.XLS'
xls_files = glob.glob(pattern)

# Columns to be converted to float16 format in order to reduce memory load.
float16_cols = ['TOTAL POWER','AVAILABLE POWER','SWBD VOLTAGE','SWBD FREQUENCY','871_200_VO',
                '871_200_HZ','DG1 POWER [kW]','DG1 POWER [%]','DG1 REACTIVE POWER [kWAr]',
                'DG1 REACTIVE POWER [%]','DG1 PHASE FACTOR','DG1 FREQUENCY','DG1 VOLTAGE',
                'DG2 POWER [kW]','DG2 POWER [%]','DG2 REACTIVE POWER [kWAr]',
                'DG2 REACTIVE POWER [%]','DG2 PHASE FACTOR','DG2 FREQUENCY','DG2 VOLTAGE',
                'DG3 POWER [kW]','DG3 POWER [%]','DG3 REACTIVE POWER [kWAr]',
                'DG3 REACTIVE POWER [%]','DG3 PHASE FACTOR','DG3 FREQUENCY',
                'DG3 VOLTAGE','DG4 POWER [kW]','DG4 POWER [%]',
                'DG4 REACTIVE POWER [kWAr]','DG4 REACTIVE POWER [%]',
                'DG4 PHASE FACTOR','DG4 FREQUENCY','DG4 VOLTAGE','DG5 POWER [kW]'	,
                'DG5 POWER [%]','DG5 REACTIVE POWER [kWAr]','DG5 REACTIVE POWER [%]',
                'DG5 PHASE FACTOR','DG5 FREQUENCY','DG5 VOLTAGE','REQUIRED ENGINES','STOP TIMER','START TIMER']

# Connection to SQLite database.
connection = sqlite3.connect('d:/temp/022.sqlite')

# Initial value for last timestamp in an XLS file. This variable will get a new value once the XLS file is read.
last_time = None

# PMS parameters:
start_limit = 85 # Given in [%]
start_time = 15 # Given in [s]
stop_limit = 71 # Given in [%]
stop_time = 1599 # Given in [s]

# Loop for scanning all of the XLS files in the directory, reading through each sheet of an XLS file, creating a Pandas DataFrame,
# converting float64 format to float16 format, converting datetime format to float64 format, finding index or rows that have errors,
# dropping rows with errors, dropping duplicated rows and appending the final DataFrame to an SQLite database.

for i in range(len(xls_files)):
    print('Handling file: ' + str(xls_files[i]))
    sheets = pd.ExcelFile(xls_files[i])
    for sheet in sheets.sheet_names:
        print('Handling sheet: ' + str(sheet))
        xls = pd.DataFrame(pd.read_excel(xls_files[i], sheet_name=sheet, dtype={col: np.float16 for col in float16_cols}))
        xls['Int Time'] = pd.to_datetime(xls['Time']).astype(np.int64)
        error_rows = xls[np.abs(xls['Int Time'] - xls['Int Time'].mean()) > 2 * xls['Int Time'].std()].index.values
        xls = xls.drop(error_rows)
        if last_time is None:
            last_time = xls.loc[xls.index[-1], 'Int Time']
            xls.to_sql('Engine_Room_Database', connection, if_exists='append', index=True)
        else:
            try:
                new_row = xls.index[xls['Int Time'] == last_time]
                xls = xls[new_row[0]+1: -1]
            except:
                pass
            last_time = xls.loc[xls.index[-1], 'Int Time']
            xls.to_sql('Engine_Room_Database', connection, if_exists='append', index=True)


"""
Check for duplicated rows due to inconsistency of timestamps across the original data exports.
Loop prints SQL querries that can be pasted directly in SQLite.
"""
querry11 = 'SELECT "Time" AS TIME FROM Engine_Room_Database'
df = pd.DataFrame(pd.read_sql_query(querry11, connection))
df = df[df.duplicated(keep='first')]

for i in df.index:
    write = 'UPDATE Engine_Room_Database SET duplicates = 1 WHERE ROWID = ' + str(i) + ';'
    print(write)


