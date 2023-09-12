import requests
import datetime

urlprefix = 'http://euclid.esac.esa.int/webclient-ares/mustlink/dataproviders/EUCLID/parameters/data?'
urlsuffix = '&aggregationFunction=FIRST&aggregation=None&aggregationValue=1&compressionError=0&delta=0'

            # "&aggregationFunction=FIRST&aggregation=None&aggregationValue=1&compressionError=0&chunkCount=1749&delta=0"

def getKey():
    try: 
        header = {'Content-Type': 'application/json'}
        data = {"username": "NISP_1", "password": "hMBm8pt("}
        url = 'http://euclid.esac.esa.int/webclient-ares/mustlink/auth/login'
        response = requests.post(url, headers=header, json=data)
        jsonResponse = response.json()
        token = jsonResponse["token"]
        return token
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

# This should be deleted
def request(key, id, startyear, startdoy, endyear, enddoy, calibrate=True):

    start = datetime.datetime.strptime(str(startyear) + ' ' +  str(startdoy), '%Y %j')
    end = datetime.datetime.strptime(str(endyear) + ' ' +  str(enddoy), '%Y %j')

    header = {'Authorization': key}
    content = 'key=id&values=' + str(id) + "&from=" + str(start) + "&to=" + str(end)

    if calibrate is True:
        url = urlprefix + content + urlsuffix + '&calibrate=true'
    else:
        url = urlprefix + content + urlsuffix + '&calibrate=false'

    try: 
        response = requests.get(url, headers=header)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    
# This should be deleted
def getFilenameDOYRange(id, startyear, startdoy, endyear, enddoy, extension='.json'):
    return 'db/' + str(id) + "-" + str(startyear) + "-" + str(startdoy) + "-" + str(endyear) + "-" + str(enddoy) + extension

def getFilenameDOY(id, year, doy, extension='.json'):
    return 'db/' + str(id) + "-" + str(year) + "-" + str(doy) + extension

