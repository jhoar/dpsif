import HMS
import OSS
import json
import numpy as np
import os.path

from datetime import datetime, timezone, timedelta

#
#
#
#
#
def generate(t_start, t_end, ares_ids, force=False):

    hmsTimeSeries = {}
    lastValues = {}
    merged = {}
    invalidTimestamps = []

    # Generate HMS files
    generateHmsFiles(t_start, t_end, ares_ids, force)

    # Ensure UTC
    start = int(t_start.replace(tzinfo=timezone.utc).timestamp())
    end = int(t_end.replace(tzinfo=timezone.utc).timestamp())

    # First populate the timestamps from ares
    for ares_data in ares_ids:
        id = ares_data[0]
        calibrate = ares_data[2]
        ts = generateTimeline(id, t_start, t_end, calibrate=calibrate)
        hmsTimeSeries[ares_data[1]] = ts

    for id in hmsTimeSeries:
        timeSeries = hmsTimeSeries[id]
        lastValues[id] = ""
        for time in timeSeries:
            merged[time] = {}

    timeStamps = list(merged.keys())
    timeStamps.sort()
    master = {i: merged[i] for i in timeStamps}

    for timeStamp in master:
        if (timeStamp >= start and timeStamp < end):
            master[timeStamp]['utc'] = datetime.utcfromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S')

            for id in hmsTimeSeries:
                if timeStamp in hmsTimeSeries[id]:
                    master[timeStamp][id] = hmsTimeSeries[id][timeStamp]
                    lastValues[id] = hmsTimeSeries[id][timeStamp]
                else: 
                    master[timeStamp][id] = lastValues[id]

        else:
            invalidTimestamps.append(timeStamp) 

    # clean empty TS
    for ts in invalidTimestamps:
        del master[ts]

    return master

#
#
#
#
#
def generateHmsFiles(t_start, t_end, ares_ids, force=False):
    token = HMS.getKey()

    n_s_tt = t_start.utctimetuple()
    n_e_tt = t_end.utctimetuple()

    normalized_start = datetime(n_s_tt.tm_year, n_s_tt.tm_mon, n_s_tt.tm_mday)
    normalized_end = datetime(n_e_tt.tm_year, n_e_tt.tm_mon, n_e_tt.tm_mday)
    
    delta = normalized_end - normalized_start

    for ares_data in ares_ids:
        ares_id = ares_data[0]
        calibrate = ares_data[2]

        for i in range(delta.days + 1):
            s_date = normalized_start + timedelta(days=i)
            e_date = normalized_start + timedelta(days=i+1)

            s_tt = s_date.utctimetuple()
            e_tt = e_date.utctimetuple()

            filename = HMS.getFilenameDOY(ares_id, year=s_tt.tm_year, doy=s_tt.tm_yday)
            
            if force or not os.path.isfile(filename):

                stuff = HMS.request(token, ares_id, 
                                startyear=s_tt.tm_year, 
                                startdoy=s_tt.tm_yday, 
                                endyear=e_tt.tm_year, 
                                enddoy=e_tt.tm_yday, 
                                calibrate=calibrate)
                json_formatted_str = json.dumps(stuff, indent=2)

                with open(filename, "w") as outfile:
                    outfile.write(json_formatted_str)

#
#
#
#
#
def generateTimeline(ares_id, t_start, t_end, calibrate=False):
    timeSeries = {}

    n_s_tt = t_start.utctimetuple()
    n_e_tt = t_end.utctimetuple()

    normalized_start = datetime(n_s_tt.tm_year, n_s_tt.tm_mon, n_s_tt.tm_mday)
    normalized_end = datetime(n_e_tt.tm_year, n_e_tt.tm_mon, n_e_tt.tm_mday)
    
    delta = normalized_end - normalized_start

    for i in range(delta.days + 1):
        s_date = normalized_start + timedelta(days=i)
        s_tt = s_date.utctimetuple()

        filename = HMS.getFilenameDOY(ares_id, year=s_tt.tm_year, doy=s_tt.tm_yday)

        with open(filename, "r") as outfile:
            input = json.load(outfile)
            lastValue = None
            for datum in input[0]['data']:
                timeStamp = int(int(datum['date']) / 1000)

                if calibrate:
                    value = datum['calibratedValue']
                else:
                    value = datum['value']

                if value != lastValue:
                    timeSeries[timeStamp] = value
                    lastValue = value

    return timeSeries

#
#
#
#
#
def generateCsvFromTimeline(master, filename):

    with open(filename, "w") as outfile:
        line = [ 'time' ]

        first = list(master.keys())[0]
        for id in master[first]:
            line.append(id)

        outfile.write(','.join(line) + "\n")

        for timeStamp in master:
            line = [ ]
            for id in master[timeStamp]:
                line.append(str(master[timeStamp][id]))

            outfile.write(','.join(line) + "\n")

#
#
#
#
#
def generateMasterTimeline(t_start, t_end, ares_ids, ossFile, oss_ids):

    hmsTimeSeries = {}
    lastValues = {}
    merged = {}
    invalidTimestamps = []

    start = int(t_start.replace(tzinfo=timezone.utc).timestamp())
    end = int(t_end.replace(tzinfo=timezone.utc).timestamp())

    # First populate the timestamps from ares
    for ares_data in ares_ids:
        id = ares_data[0]
        calibrate = ares_data[2]
        ts = generateTimeline(id, t_start, t_end, calibrate=calibrate)
        hmsTimeSeries[ares_data[1]] = ts

    ossTimeSeries = OSS.generateOssTimeseries(ossFile, oss_ids)

    for id in hmsTimeSeries:
        timeSeries = hmsTimeSeries[id]
        lastValues[id] = ""
        for time in timeSeries:
            merged[time] = {}

    for id in ossTimeSeries:
        timeSeries = ossTimeSeries[id]
        lastValues[id] = ""
        for time in timeSeries:
            merged[time] = {}

    timeStamps = list(merged.keys())
    timeStamps.sort()
    master = {i: merged[i] for i in timeStamps}

    for timeStamp in master:

        if (timeStamp >= start and timeStamp < end):

            master[timeStamp]['utc'] = datetime.utcfromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S')

            for id in hmsTimeSeries:
                if timeStamp in hmsTimeSeries[id]:
                    master[timeStamp][id] = hmsTimeSeries[id][timeStamp]
                    lastValues[id] = hmsTimeSeries[id][timeStamp]
                else: 
                    master[timeStamp][id] = lastValues[id]

            for id in ossTimeSeries:
                if timeStamp in ossTimeSeries[id]:
                    master[timeStamp][id] = ossTimeSeries[id][timeStamp]
                    lastValues[id] = ossTimeSeries[id][timeStamp]
                else: 
                    master[timeStamp][id] = lastValues[id]
        else:
            invalidTimestamps.append(timeStamp) 

    # clean empty TS
    for ts in invalidTimestamps:
        del master[ts]

    return master
