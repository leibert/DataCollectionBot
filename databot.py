__author__ = 'leibert'

# Get weather data
import requests
import time
import keys
from xml.etree import ElementTree

WUKey = keys.WUkey
WUState = "MA"
WUCity = "Somerville"



# Feels 57F/10C
# Cloudy Calm
# Wind 8N
# [Y2000]0800 30 OVR
# [G2000]1300 42 SUN
# [R2000]1600 38 SNW
# [R2000]2000 38 SNW
# [R1500]TUE 40 RAIN
# [Y1500]WED 50 OVRCAST
# [Y1500]THU 50 OVRCAST




def getcurrentwx():
    datastring = ""
    r = requests.get(('http://api.wunderground.com/api/' + WUKey + '/conditions/q/' + WUState + '/' + WUCity + '.json'))
    print r.status_code
    if (r.status_code != 200):
        return "WX ERROR"

    print r.headers['content-type']
    print r.encoding
    print r.text
    WXjson = r.json()
    print "START DECODE"
    # print WXjson

    print "CURRENT TEMP is:" + WXjson['current_observation']['feelslike_string']
    print "WEATHER is:" + WXjson['current_observation']['weather']
    print "WXSHORT is:" + WXjson['current_observation']['icon']
    print "Wind" + str(WXjson['current_observation']['wind_mph']) + " " + str(WXjson['current_observation']['wind_dir'])
    datastring += "FEELS " + WXjson['current_observation']['feelslike_string'] + "\n"
    datastring += WXjson['current_observation']['weather'] + "\n"
    datastring += WXjson['current_observation']['wind_dir']+" @ " + str(WXjson['current_observation']['wind_mph']) + "mph\n"
    return datastring


def getforecastwx():
    datastring = ""
    r = requests.get(('http://api.wunderground.com/api/' + WUKey + '/conditions/q/' + WUState + '/' + WUCity + '.json'))
    print r.status_code
    if (r.status_code != 200):
        return "FORECAST ERROR"

    print r.headers['content-type']
    print r.encoding
    print r.text
    WXjson = r.json()
    print "START DECODE"
    # print WXjson

    print "FORECAST TO GO HERE"
    return "FORECAST MISSING\n"


def constructheader():
    lcltime = time.localtime()
    datastring = ""
    datastring = "GOOD"
    if (lcltime.tm_hour < 12):
        datastring += " MORNING"
    elif (lcltime.tm_hour < 17):
        datastring += " AFTERNOON"
    else:
        datastring = +" EVENING"
    datastring += "\n"
    datastring += time.strftime("%a %b %-d") + "\n"
    datastring += time.strftime("%H:%M") + "\n"
    return datastring


def constructpage():
    content = ""
    content += constructheader()
    content += getcurrentwx()
    content += getforecastwx()
    return content

def getmbtabustimes(stop,routenum="",routecfg=""):
    r = requests.get(('http://webservices.nextbus.com/service/publicXMLFeed?command=predictions&a=mbta&stopId='+ stop ))
    print r.status_code
    if (r.status_code != 200):
        return "MBTA FAIL"

    print r.encoding
    print r.content
    # print r.text
    # WXjson = r.
    busdata=ElementTree.fromstring(r.content)

    responsetext=""
    print busdata
    print "START DECODE"
    try:
        for route in busdata:
            print route.tag, route.attrib["routeTag"],route.attrib["routeTitle"]
            if route.attrib['routeTag'] == routenum or routenum =="":
                print "this is a route of interest"
                for direction in route:
                    print direction.attrib["title"]
                    for trip in direction:
                        print trip.attrib["dirTag"], trip.attrib["minutes"], trip.attrib["isDeparture"]
                        if trip.attrib["dirTag"] == routecfg or routecfg =="":
                            print "this route config is of interest"
                            if(responsetext!=""):
                                responsetext +=", "
                            responsetext+=trip.attrib["minutes"]
                            if(trip.attrib["isDeparture"]!="true"):
                                responsetext+="*"

        if(responsetext==""):
            return "NONE"
        else:
            return responsetext
    except:
        return "ERROR"





# def getnearbymbtainfo():
    # getmbtabustimes("02730","89","") #89 to DAVIS

def getAdamsbuses():
    getmbtabustimes("02702","89")
    getmbtabustimes("02730")
    getmbtabustimes("05303")
    getmbtabustimes("02401")

    #check coffee





print "PROGRAM"
# print constructpage()
getAdamsbuses()