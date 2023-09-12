import xmltodict
from datetime import datetime
import pandas as pd

#
#
#
#
#
def oss(file):
    with open(file) as xml_file:
        data_dict = xmltodict.parse(xml_file.read())

        data = []
        observations = data_dict['ns2:OperationalSurvey']['Observation']
        for obs in observations:
            if 'Name' in obs and 'Target' in obs: # These fields are only present for ICRs. It would be better to explicitly state the source as an attribute of the Observation element
                data.append(processIcr(obs))
            else: 
                data.append(processSurvey(obs))

        out = []
        for field in data:
            for exp in field:
                out.append(exp)

        return out
    
#
#
#
#
#
def generateOssTimeseries(filename, oss_ids):

    ossTimeSeries = {}
    for id in oss_ids:
        name = id[1]
        ossTimeSeries[name] = {}

    # Then populate the timestamps from the OSS
    ossData = oss(filename)
    for pointing in ossData:
        utc_dt = datetime.strptime(pointing['date'], '%Y-%m-%dT%H:%M:%SZ')
        timeStamp = int((utc_dt - datetime(1970, 1, 1)).total_seconds())

        for id in oss_ids:
            name = id[1]
            series = ossTimeSeries[name]
            series[timeStamp] = pointing[id[0]]

    return ossTimeSeries

#
#
#
#
#
def processPointing(pointing, obsData):
    data = {}
    data['id'] = obsData['id']
    data['source'] = obsData['source']
    data['survey'] = obsData['survey']
    data['nispPlanningId'] = int(pointing['@nispPlanningId'])
    data['visPlanningId'] = int(pointing['@visPlanningId'])
    data['mode'] = pointing['PointingActivity']['Description']
    data['date'] = pointing['StartTimeUtc']
    data['duration'] = pointing['Duration']
    data['longEcl'] = pointing['EclipticAttitude']['Longitude']
    data['latEcl'] = pointing['EclipticAttitude']['Latitude']
    data['pa'] = pointing['EclipticAttitude']['PositionAngle']
    data['fovLong1'] = pointing['FoV']['@long1']
    data['fovLat1'] = pointing['FoV']['@lat1']
    data['fovLong2'] = pointing['FoV']['@long2']
    data['fovLat2'] = pointing['FoV']['@lat2']
    data['fovLong3'] = pointing['FoV']['@long3']
    data['fovLat3'] = pointing['FoV']['@lat3']
    data['fovLong4'] = pointing['FoV']['@long4']
    data['fovLat4'] = pointing['FoV']['@lat4']

    for parameter in pointing['PointingActivity']['Parameters']:
        data['variant'] = 'UNDEF'
        for p1 in pointing['PointingActivity']['Parameters'][parameter]:
            if (p1['Key']) == 'ObsId':
                data['obsId'] = p1['LongValue']
            if (p1['Key']) == 'Variant':
                data['variant'] = p1['StringValue']

    return data

#
#
#
#
#
def processObservation(obs, data):
    pointData = []
    if type(obs['Pointing']) is list:
        for ros in obs['Pointing']:
            pointData.append(processPointing(ros, data))
    else:
        pointData.append(processPointing(obs['Pointing'], data))

    return pointData

#
#
#
#
#
def processSurvey(obs):
    data = {}
    data['id'] = obs['@id']
    data['survey'] = obs['SurveyId']
    data['source'] = obs['ObservationType']
    fieldinfo = processObservation(obs, data)
    return fieldinfo

#
#
#
#
#
def processIcr(obs):
    data = {}
    data['id'] = obs['@id']
    data['survey'] = obs['SurveyId']
    data['source'] = obs['ObservationType']
    fieldinfo = processObservation(obs, data)
    return fieldinfo

#
#
#
#
#
def oss2df(file):
    with open(file) as xml_file:
        data_dict = xmltodict.parse(xml_file.read())

        data = []
        observations = data_dict['ns2:OperationalSurvey']['Observation']
        for obs in observations:
            if 'Name' in obs and 'Target' in obs: # These fields are only present for ICRs. It would be better to explicitly state the source as an attribute of the Observation element
                data.append(processIcr(obs))
            else: 
                data.append(processSurvey(obs))

        out = []
        for field in data:
            for exp in field:
                out.append(exp)

        df = pd.DataFrame.from_dict(out)
        df.index.name = 'index'
        return df

