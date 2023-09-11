import HMS
import OSS
import json
import numpy as np
from datetime import datetime, timezone


def timeWithMillis(timestamp):
        timewithMills = int(timestamp)
        time = int( timewithMills / 1000)
        millis = timewithMills % time
        dateTime = datetime.utcfromtimestamp(time)
        return dateTime.strftime('%Y-%m-%d %H:%M:%S') + '.' + f'{millis:03}'

def generateHmsFiles(timerange, ares_ids):
    token = HMS.getKey()

    for ares_data in ares_ids:
        id = ares_data[0]
        calibrate = ares_data[2]

        stuff = HMS.requestDOYRange(token, id, 
                            startyear=timerange['startyear'], 
                            startdoy=timerange['startdoy'], 
                            endyear=timerange['endyear'], 
                            enddoy=timerange['enddoy'], 
                            calibrate=calibrate)
        json_formatted_str = json.dumps(stuff, indent=2)

        with open(HMS.getFilenameDOYRange(id, startyear=timerange['startyear'], 
                            startdoy=timerange['startdoy'], 
                            endyear=timerange['endyear'], 
                            enddoy=timerange['enddoy']), "w") as outfile:
            outfile.write(json_formatted_str)

def generateTimeline(id, startyear, startdoy, endyear, enddoy, calibrate=False):
    timeSeries = {}
    with open(HMS.getFilenameDOYRange(id, startyear=startyear, startdoy=startdoy, endyear=endyear, enddoy=enddoy), "r") as outfile:
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

def generateMasterTimeline(timerange, ares_ids, ossFile, oss_ids):

    hmsTimeSeries = {}

    s = datetime.strptime(str(timerange['startyear']) + ' ' +  str(timerange['startdoy']), '%Y %j')
    start = int(s.replace(tzinfo=timezone.utc).timestamp())

    e = datetime.strptime(str(timerange['endyear']) + ' ' +  str(timerange['enddoy']), '%Y %j')
    end = int(e.replace(tzinfo=timezone.utc).timestamp())

    # First populate the timestamps from ares
    for ares_data in ares_ids:
        id = ares_data[0]
        calibrate = ares_data[2]
        ts = generateTimeline(id, startyear=timerange['startyear'], 
                            startdoy=timerange['startdoy'], 
                            endyear=timerange['endyear'], 
                            enddoy=timerange['enddoy'], calibrate=calibrate)
        hmsTimeSeries[ares_data[1]] = ts

    ossTimeSeries = OSS.generateOssTimeseries(ossFile, oss_ids)

    lastValues = {}
    merged = {}

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

    invalidTimestamps = []

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

def generateHmsTimeline(timerange, ares_ids):

    hmsTimeSeries = {}

    s = datetime.strptime(str(timerange['startyear']) + ' ' +  str(timerange['startdoy']), '%Y %j')
    start = int(s.replace(tzinfo=timezone.utc).timestamp())

    e = datetime.strptime(str(timerange['endyear']) + ' ' +  str(timerange['enddoy']), '%Y %j')
    end = int(e.replace(tzinfo=timezone.utc).timestamp())

    # First populate the timestamps from ares
    for ares_data in ares_ids:
        id = ares_data[0]
        calibrate = ares_data[2]
        ts = generateTimeline(id, startyear=timerange['startyear'], 
                            startdoy=timerange['startdoy'], 
                            endyear=timerange['endyear'], 
                            enddoy=timerange['enddoy'], calibrate=calibrate)
        hmsTimeSeries[ares_data[1]] = ts

    lastValues = {}
    merged = {}

    for id in hmsTimeSeries:
        timeSeries = hmsTimeSeries[id]
        lastValues[id] = ""
        for time in timeSeries:
            merged[time] = {}

    timeStamps = list(merged.keys())
    timeStamps.sort()
    master = {i: merged[i] for i in timeStamps}

    invalidTimestamps = []

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


