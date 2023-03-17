from datetime import datetime
import getpass

import os.path

import pandas as pd

import DPS

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

df = DPS.queryToFrame(visOutput['dpd'], visOutput['criteria'], visOutput['fields'], LDAP_USER, LDAP_PASS)
print(visOutput['dpd'] + ' rows: ' + str(len(df)))
