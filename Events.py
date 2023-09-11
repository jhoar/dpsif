import Timeline
import HMS

def generateReport(master):
    P_FGS_MODE = None
    P_TRACK_MODE = None
    p_row = None

    ABORT_NISP = set()
    ABORT_VIS = set()
    TRACK_NISP = set()
    TRACK_VIS = set()

    for timeStamp in master:
        row = master[timeStamp]
        FGS_MODE = row['DB_AOCS_AHK_SUBSTATE_APPT0838']
        TRACK_MODE = row['FGS_OPMODE_FAAT2010']

        NISP_EXP = row['NISP_DPU1_MODE_NIST3847'] == 'EEF_EXPOSING' or row['NISP_DPU2_MODE_NIST7943'] == 'EEF_EXPOSING'
        VIS_EXP = row['VIS_MODE_VOGT2849'] == 'EXPOSURE_STAT'

        OBID = None
        SOCID = None

        try:
            OBID = int(row['ONBOARD_PLAN_ID'])
        except:
            OBID = -1 

        SOCID = row['NISP_PLAN_ID']

        if OBID != SOCID:
            PLAN_ID = row['ONBOARD_PLAN_ID']
        else:
            PLAN_ID = row['NISP_PLAN_ID']


        if FGS_MODE != 'SCM_SO' and NISP_EXP:
            print('FGS_MODE is not SCM_SO with NISP exposing')
            ABORT_NISP.add((row['utc'], PLAN_ID))
            print(row)

        if FGS_MODE != 'SCM_SO' and VIS_EXP:
            print('FGS_MODE is not SCM_SO with VIS exposing')
            ABORT_VIS.add((row['utc'], PLAN_ID))
            print(row)

        if P_FGS_MODE == 'SCM_SO' and FGS_MODE == 'SCM_AB' and NISP_EXP:
            print('FGS_MODE switch SO to AB with NISP exposing')
            ABORT_NISP.add((row['utc'], PLAN_ID))
            print(p_row)
            print(row)

        if P_FGS_MODE == 'SCM_SO' and FGS_MODE == 'SCM_AB' and VIS_EXP:
            print('FGS_MODE switch SO to AB with VIS exposing')
            ABORT_VIS.add((row['utc'], PLAN_ID))
            print(p_row)
            print(row)

        P_FGS_MODE = FGS_MODE

        if TRACK_MODE != P_TRACK_MODE:

            if TRACK_MODE != 'ATM_TP' and NISP_EXP:
                print('TRACK_MODE is not ATM_TP with NISP exposing')
                TRACK_NISP.add((row['utc'], PLAN_ID))
                print(row)

            if TRACK_MODE != 'ATM_TP' and VIS_EXP:
                print('TRACK_MODE is not ATM_TP with VIS exposing')
                TRACK_VIS.add((row['utc'], PLAN_ID))
                print(row)

            if P_TRACK_MODE == 'ATM_TP' and TRACK_MODE == 'SCM_AB' and NISP_EXP:
                print('TRACK_MODE switch SO to AB with NISP exposing')
                TRACK_NISP.add((row['utc'], PLAN_ID))
                print(p_row)
                print(row)

            if P_TRACK_MODE == 'ATM_TP' and TRACK_MODE == 'SCM_AB' and VIS_EXP:
                print('TRACK_MODE switch SO to AB with VIS exposing')
                TRACK_VIS.add((row['utc'], PLAN_ID))
                print(p_row)
                print(row)

        p_row = row

    print('VIS Exposures affected by SCM_AB')
    print(ABORT_NISP)
    print('NISP Exposures affected by SCM_AB')
    print(ABORT_VIS)
    print('VIS Exposures affected by tracking loss')
    print(TRACK_NISP)
    print('NISP Exposures affected by tracking loss')
    print(TRACK_VIS)


ares_ids = [
    (8308, 'FGS_OPMODE_FAAT2010', True), 
    (4158, 'DB_AOCS_AHK_SUBSTATE_APPT0838', True), 
    (26052, 'NISP_DPU1_MODE_NIST3847', True),
    (26165, 'NISP_DPU2_MODE_NIST7943', True),
    (26760, 'NISP_FWA_POS_NIST0259', False),
    (30441, 'VIS_MODE_VOGT2849', True),
    (26758, 'ONBOARD_PLAN_ID', False)
]



oss_ids = {
    ('visPlanningId', 'VIS_PLAN_ID'), 
    ('nispPlanningId', 'NISP_PLAN_ID'), 
    ('variant', 'VARIANT'), 
    ('obsId', 'OBS_ID'), 
    ('source', 'ACTIVITY')
}

pv_001 = {
    'startyear': 2023,
    'endyear': 2023,
    'startdoy': 215,
    'enddoy': 224,
    'ossFile': 'pv\OSS_COMMISSIONING_20230803T040000-20230816T231915_005.xml'
}

pv = {
    'startyear': 2023,
    'endyear': 2023,
    'startdoy': 224,
    'enddoy': 229,
    'ossFile': 'pv\OSS_PV_20230812T000000-20230819T104213_006.xml'
}

timerange = pv

# Timeline.generateHmsFiles(timerange, ares_ids)
master = Timeline.generateMasterTimeline(timerange, ares_ids, timerange['ossFile'], oss_ids)
Timeline.generateCsvFromTimeline(master, HMS.getFilename('master', startyear=timerange['startyear'], 
                            startdoy=timerange['startdoy'], 
                            endyear=timerange['endyear'], 
                            enddoy=timerange['enddoy'], extension=".csv"))

generateReport(master)

# FAAT2010 = 8308 == 36
# APPT0838 = 4158 == 24
# NIST3847 = 26052 == 1 DPU1
# NIST7943 = 26165 == 1 DPU2
# VOGT2849 = 30441 = 

# 24715 NISP Planning Id
# 24714 VIS Planning Id
# NIST3847 NISP_DPUAG_SC_EEF_Status    (EEF_IDLE (raw value 0)  exposure not going on,  EEF_EXPOSING (raw value 1) exposure on going) 
# NIST7943 NISP_DPUBG_SC_EEF_Status    (EEF_IDLE = 0 exposure not going on,  EEF_EXPOSING= 1 exposure on going)

#  Then we have the FWA position NIST0259  and the GWA position NIST0129
# When FWA position = 0 it means that NISP is taking a Dark image (such keyword is reported also in the heade of the image file)