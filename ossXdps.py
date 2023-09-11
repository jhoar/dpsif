import datetime as dt
from datetime import date
from datetime import timedelta

import os.path

import pandas as pd

import DPS
import OSS

LDAP_USER = 'jhoar'
LDAP_PASS = 'J4nn4k4r!01'

rebuildCache = True

ossFile = "OSS_icr_SOVT2_94H_v13_short.xml"

from datetime import datetime
startdate = '2023060'
start = datetime.strptime(startdate, '%Y%j')

criteria=[
    DPS.MD_PROD_SDC + "=SOC",
    DPS.MD_CREATION_DATE + '>' + DPS.getEASTime(start)
    ]

# Ask for:
# Observing Mode & VIS Data file
visOutput = [DPS.MD_LE1_OBSMODE, DPS.MD_LE1_PLANNINGID, DPS.MD_CREATION_DATE, 'Data.VisSequence', DPS.MD_LE1_VIS_DATAFILE]
nispOutput = [DPS.MD_LE1_OBSMODE, DPS.MD_LE1_PLANNINGID, DPS.MD_CREATION_DATE, 'Data.ExposureConfiguration.InstrumentConfiguration', 'Data.ExposureConfiguration.KeywordConfiguration', DPS.MD_LE1_NISP_DATAFILE]

visDPSFile = ossFile + "_" + startdate + '_vis.dat'
nispDPSFile = ossFile + "_" + startdate + '_nisp.dat'

if rebuildCache or not os.path.isfile(visDPSFile):
    DPS.queryToFile(visDPSFile, DPS.CL_LE1_VIS_FRAME, criteria, visOutput, LDAP_USER, LDAP_PASS)

if rebuildCache or not os.path.isfile(nispDPSFile):
    DPS.queryToFile(nispDPSFile, DPS.CL_LE1_NISP_FRAME, criteria, nispOutput, LDAP_USER, LDAP_PASS)

visLE1 = pd.read_csv(visDPSFile)
visLE1 = visLE1.rename(columns={
    DPS.MD_LE1_PLANNINGID: 'vis_' + DPS.MD_LE1_PLANNINGID,
    DPS.MD_LE1_OBSMODE: 'vis_' + DPS.MD_LE1_OBSMODE
    })

print(visLE1.keys())

nispLE1 = pd.read_csv(nispDPSFile)
nispLE1 = nispLE1.rename(columns={
    DPS.MD_LE1_PLANNINGID: 'nisp_' + DPS.MD_LE1_PLANNINGID,
    DPS.MD_LE1_OBSMODE: 'nisp_' + DPS.MD_LE1_OBSMODE
    })

print(nispLE1.keys())

ossData = OSS.oss2df(ossFile)
ossData.to_csv('oss.csv')

ossXvis = pd.merge(ossData, visLE1, how='outer', left_on='visPlanningId', right_on='vis_Data.PlanningId')
ossXnisp = pd.merge(ossData, nispLE1, how='outer', left_on='nispPlanningId', right_on='nisp_Data.PlanningId')

ossXvis.to_excel('ossXvis.xls')
ossXnisp.to_excel('ossXnisp.xls')

# ossXall = pd.concat([ossXvis, ossXnisp])
# ossXall.to_excel('all.xls')

# result = visLE1.to_html()
# with open(visDPSFile + ".html",'w') as dps_file:
#     dps_file.writelines(result)
#     dps_file.close()   

# result = nispLE1.to_html()
# with open(nispDPSFile + ".html",'w') as dps_file:
#     dps_file.writelines(result)
#     dps_file.close()   






