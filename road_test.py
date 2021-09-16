#!/usr/bin/python

import sys,json,urllib2,time,os,ssl,httplib,datetime,random
# import json
# import urllib2
# import time
# import os
# import ssl
# import httplib
# import datetime



# Init from website.
# servicePublicId="da8488da9b5df26d32ca58c6d6a7973bedd5d98ad052d62b468d3b04b080ea25"

# 268 is Victoria too far away.
# 93, 273 are in Richmond
POS_IDS = [275,9]
# POS_IDS = [275,9,8,2,274,93,273,276,272,11,271,269,73,220,153,270,6,256,252,1,277,214,113,114,3]#,268]
# Month
# expectMonth = "2022-02"
expectMonths = ["2021-09-28", "2021-09-29", "2021-09-30", "2021-10-0"]
# SLEEP_TIME = 30
SLEEP_TIME_POS = 20
# MAX_TIME = 5 * 60
# MAX_TIME = 3 * 60 * 60 # 3 hours
MAX_TIME = 29 * 60 # 15 minutes

# Fix SSL
if hasattr(ssl, '_create_unverified_context'): ssl._create_default_https_context = ssl._create_unverified_context


# Read locations from json files.
def read_location_json(filename):
    with open(filename) as f:
        location_objs = json.load(f)
        ans = {}
        for loc in location_objs:
            obj = loc['pos']
            id = obj['posId']
            ans[id] = obj
        return ans

def send_notification(msg):
    # TODO: add notification to mobile or desktop.
    print msg
    make_bell_sound()

# make a sound in your computer 
def make_bell_sound():
    os.system("say 'ICBC appointment found.'")
    os.system("say 'ICBC appointment found.'")
    os.system("say 'ICBC appointment found.'")

def fetch_road_test(token,posID, driverLastName, licenceNumber):
    # json_body = '{"posIDs":[275,9,8,2,274,93,273,276,272,11,271,269,73,220,153,270,6,256,252,1,277,214,113,114,3,268],'
    # json_body = '{"aPosID":93,'
    json_body = '{"aPosID":' + str(posID) + ','
    json_body += '"examType":"5-R-1","examDate":"2021-09-23","ignoreReserveTime":false,"prfDaysOfWeek":"[0,1,2,3,4,5,6]",'
    json_body += '"prfPartsOfDay":"[0,1]","lastName":"' + driverLastName+'","licenseNumber":"'+licenceNumber+'"}'

    headers = {"Accept" : "application/json, text/plain, */*", "Content-Type" : "application/json", "Referer" : "https://onlinebusiness.icbc.com/webdeas-ui/booking",\
             "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36", \
             "Authorization" : token }

    conn = httplib.HTTPSConnection('onlinebusiness.icbc.com')
    conn.request('POST', '/deas-api/v1/web/getAvailableAppointments', json_body, headers)
    response = conn.getresponse()
    data = response.read() # same as r.text in 3.x
    if len(data.strip()) == 0:
        print 'read road test api fail.'
        print response.status
        print response.reason
        return [None]
    # print(data)
    return json.loads(data)

RED = ""

def fiterByDate(appointments, locations, token):
    ans = []
    if not appointments: return ans
    for ap in appointments:
        # for ap in array:
        # check 
        # print(ap)
        dt = ap['appointmentDt']['date']
        st = ap['startTm']
        et = ap['endTm']
        pos_id = ap['posId']
        loc = locations[pos_id]
        if isAvailable(ap, token):
            # found.
            msg = "%s %s-%s, %s%s" % (dt, st, et, RED, loc['address']) 
            send_notification(msg)
            ans.append(msg)

    return ans

# check slot if available 
def isAvailable(appointment, token):
    dt = appointment['appointmentDt']['date']
    return any(dt.startswith(expectMonth) for expectMonth in expectMonths)
    # if not dt.startswith(expectMonth):
    #     return False
    
    # if isLock(appointment, token):
    #     return False

    # return True



def isLock(appointment, token):
    appointment['bookedTs'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    appointment['drvrDriver'] = { "drvrId": 1662805 }
    appointment['instructorDlNum'] = None
    appointment['drscDrvSchl'] = {}
    headers = {"Accept" : "application/json, text/plain, */*", "Content-Type" : "application/json", "Referer" : "https://onlinebusiness.icbc.com/webdeas-ui/booking",\
             "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36", \
             "Authorization" : token }
    conn = httplib.HTTPSConnection('onlinebusiness.icbc.com')
    json_body = json.dumps(appointment)
    conn.request('PUT', '/deas-api/v1/web/lock', json_body, headers)
    response = conn.getresponse()
    return response.status == 400


# get login token.
def getToken(user):
    json_body = '{"drvrLastName":"%s","licenceNumber":"%s","keyword":"%s"}' % user
    # print(json_body)
    headers = {"Expires" : "0" ,"Accept": "application/json, text/plain, */*", "Cache-control" : "no-cache, no-store", "Content-Type" : "application/json","Referer" : "https://onlinebusiness.icbc.com/webdeas-ui/login;type=driver","User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"}
    conn = httplib.HTTPSConnection('onlinebusiness.icbc.com')
    conn.request('PUT', '/deas-api/v1/webLogin/webLogin', json_body, headers)
    response = conn.getresponse()
    token = response.getheader('Authorization')
    # print 'get token: ', token
    return token


def main():
    print 'start detecting appointments in', expectMonths, '...'
    driverLastName, licenceNumber = sys.argv[1], sys.argv[2]
    token = getToken((driverLastName, licenceNumber, sys.argv[3]))
    st = time.time()
    end = time.time()
    locations = read_location_json('road_test_positions.json')
    res = ''
    cnt = 0
    while True:
        end = time.time()

        if (end - st) > MAX_TIME:
            print 'Sorry I cannot help you.'
            break
        broken = False
        for posId in POS_IDS:
            appointments = fetch_road_test(token, posId, driverLastName, licenceNumber)
            if appointments and appointments[0] == None:
                broken = True
                break
            loc = locations[posId]
            address = loc['address']
            msg = "%d appointments. %s[%d]" % (len(appointments) if appointments else 0, address, posId)
            if appointments and len(appointments) > 0:
                ap = appointments[0]
                dt = ap['appointmentDt']['date']
                startTm, endTm = ap['startTm'], ap['endTm']
                msg += " | %s %s-%s" % (dt, startTm, endTm)
            print msg

            # print('>>>', len(appointments), 'appointments for ', address)
            res = fiterByDate(appointments, locations, token)
            if len(res) > 0:
                break
            time.sleep(random.randrange(SLEEP_TIME_POS - 3, SLEEP_TIME_POS + 2))
            sys.stdout.write(".")
            sys.stdout.flush()
            cnt += 1
        if len(res) > 0 or broken:
            break
        # time.sleep(random.randrange(SLEEP_TIME - 4, SLEEP_TIME + 4))
        sys.stdout.write(":")
        sys.stdout.flush()
    t = end - st
    print datetime.datetime.now(), 'run count:', cnt, ', time run:', t // (60 * 60), 'hours', (t % ( 60 * 60 )) / 60, 'minutes'
    print res

if __name__ == "__main__":
    # execute only if run as a script
    main()

    
    










