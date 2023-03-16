from datetime import datetime
import getpass

import os.path

import pandas as pd

import DPS

rebuildCache = True

# If you want to hardcode username and password in the script, do it here and comment out the prompt below
LDAP_USER = ''
LDAP_PASS = ''

# No hardcoded values, so prompt user
LDAP_USER = input('LDAP username: ')
LDAP_PASS = getpass.getpass(prompt='LDAP password: ')

startdate = '2023055'
enddate = '2023064'

# Convert to a DateTime
start = datetime.strptime(startdate, '%Y%j')
end = datetime.strptime(enddate, '%Y%j')

hkcriteria=[
    DPS.MD_PROD_SDC + "=SOC",
    DPS.MD_CREATION_DATE + '>' + DPS.getEASTime(start),
    DPS.MD_CREATION_DATE + '<' + DPS.getEASTime(end)
    ]

criteria=[
    DPS.MD_PROD_SDC + "=SOC",
    DPS.MD_CREATION_DATE + '>' + DPS.getEASTime(start)
    ]

visOutput =  {
    'dpd': DPS.CL_LE1_VIS_FRAME, 
    'criteria': criteria, 
    'fields': [DPS.MD_CREATION_DATE, DPS.MD_LE1_OBSMODE, DPS.MD_LE1_CALBLOCK, DPS.MD_LE1_VIS_DATAFILE],
    'filter': None
    }

nispOutput = {
    'dpd': DPS.CL_LE1_NISP_FRAME, 
    'criteria': criteria, 
    'fields': [DPS.MD_CREATION_DATE, DPS.MD_LE1_OBSMODE, DPS.MD_LE1_CALBLOCK, DPS.MD_LE1_NISP_DATAFILE],
    'filter': None
    }

hkProdOutput = {
    'dpd': DPS.CL_LE1_HKTM, 
    'criteria': hkcriteria, 
    'fields': [DPS.MD_CREATION_DATE, DPS.MD_DATASET, DPS.MD_HKPROD_FROMDATE, DPS.MD_HKPROD_TODATE, DPS.MD_HKPROD_FILENAMES],
    'filter': DPS.toPandas(DPS.MD_DATASET) + "=='TEST'"  # Filter the dataframe
    }

qlaOutput = {
    'dpd': DPS.CL_LE1_QLAREP, 
    'criteria': criteria, 
    'fields': [DPS.MD_CREATION_DATE, DPS.MD_QLAREP_FILENAME],
    'filter': None
    }

rawHkOutput = {
    'dpd': DPS.CL_LE1_RAWHK, 
    'criteria': criteria, 
    'fields': [DPS.MD_CREATION_DATE, DPS.MD_RAWHK_FILENAME],
    'filter': None
    }

rawSciOutput = {
    'dpd': DPS.CL_LE1_RAWSCI, 
    'criteria': criteria, 
    'fields': [DPS.MD_CREATION_DATE, DPS.MD_RAWSCI_FILENAME],
    'filter': None
    }

allData = [visOutput, nispOutput, hkProdOutput, qlaOutput, rawHkOutput, rawSciOutput]
# allData = [rawSciOutput]

for data in allData:
    filename = 'sovt2_' + data['dpd'] + '.csv'

    # Re-query the DPS if the output CSV does not exist, or on request
    if rebuildCache or not os.path.isfile(filename):
        DPS.queryToFile(filename, data['dpd'], data['criteria'], data['fields'], LDAP_USER, LDAP_PASS)

    # Read data into a dataframe
    data['frame'] = pd.read_csv(filename)

    # Here we just want to count the rows, using a pandas query filter if specified
    if data['filter'] is None:
        print(data['dpd'] + ' rows: ' + str(len(data['frame'].index)))
    else:
        filtered = data['frame'].query(data['filter'])
        print(data['dpd'] + ' rows: ' + str(len(filtered)))
