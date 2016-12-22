__author__ = 'leibert'

# Get weather data
import requests
import time
import datetime
import argparse
from xml.etree import ElementTree
from wxcodes import wxcode
from collections import defaultdict
import os

WUKey = os.getenv("WUKey")
WUState = "MA"
WUCity = "Somerville"
adamsbuses = defaultdict(list)



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

def msgchop(text, increment,config=""):
    response=""
    for i in range(0,(len(text)+increment),increment):
        response+=config + text[i:(i+increment)]
        response+="\n"
        i+=increment
    return response






def getcurrentwx():
    datastring = ""

    r = requests.get(('http://api.wunderground.com/api/' + WUKey + '/conditions/q/' + WUState + '/' + WUCity + '.json'))
    # print r.status_code
    if (r.status_code != 200):
        return "WX ERROR"

    # print r.headers['content-type']
    # print r.encoding
    # print r.text
    WXjson = r.json()
    # print "START DECODE"
    # print WXjson

    # print "CURRENT TEMP is:" + WXjson['current_observation']['feelslike_string']
    # print "WEATHER is:" + WXjson['current_observation']['weather']
    # print "WXSHORT is:" + WXjson['current_observation']['icon']
    # print "Wind" + str(WXjson['current_observation']['wind_mph']) + " " + str(WXjson['current_observation']['wind_dir'])
    if int(float(WXjson['current_observation']['feelslike_f'])) <50:
        datastring += "[R2000]"
    elif int(float(WXjson['current_observation']['feelslike_f'])) >65 and int(float(WXjson['current_observation']['feelslike_f'])) < 85 :
        datastring += "[G2000]"
    else:
        datastring += "[Y2000]"

    datastring += WXjson['current_observation']['feelslike_string'] + "\n"

    datastring += WXjson['current_observation']['weather'] + "\n"

    datastring += WXjson['current_observation']['wind_dir']+" @ " + str(WXjson['current_observation']['wind_mph']) + "mph\n"

    r = requests.get(('http://api.wunderground.com/api/' + WUKey + '/alerts/q/' + WUState + '/' + WUCity + '.json'))
    # r = requests.get(('http://api.wunderground.com/api/' + WUKey + '/alerts/q/ND/Dickinson.json'))
    # print r.status_code
    if (r.status_code != 200):
        return "WX ERROR"
    alerts = r.json()
    for entry in alerts['alerts']:
        if entry.has_key("description") and entry["type"] != "SPE":
            print entry["description"]
            datastring += "[R800]"+entry["description"] +"\n"
            datastring += "[R800]\n"
            datastring += "[R800]"+entry["description"] +"\n"
            datastring += "[R800]\n"
            datastring += "[R800]"+entry["description"] +"\n"
            datastring += "[R800]\n"
            datastring += "[R800]"+entry["description"] +"\n"
            datastring += "[R800]\n"
            datastring += "[R800]"+entry["description"] +"\n"
            message=entry["message"].replace('\n', ' ').replace('*', '').replace(',', ' ').replace('...', ' ').replace('  ', '').replace('\n\n', '\n')
            datastring += msgchop(message,14,"[R500]")




    return datastring


def getforecastwx():
    datastring = ""

    r = requests.get(('http://api.wunderground.com/api/' + WUKey + '/hourly/q/' + WUState + '/' + WUCity + '.json'))
    # print r.status_code
    if (r.status_code != 200):
        return "HOURLY FORECAST ERROR"

    # print r.headers['content-type']
    # print r.encoding
    # print r.text
    hourlyWXjson = r.json()
    # for period in hourlyWXjson['hourly_forecast']:
    #     print period["Description"]
    # print "START DECODE"
    # print WXjson
    for x in xrange(1,6):
        period=hourlyWXjson['hourly_forecast'][(x*4)]
        if int(float(period['feelslike']['english'])) < 40:
            datastring += "[R1000]"
        elif int(float(period['feelslike']['english'])) >65 and int(float(period['feelslike']['english'])) < 85 :
            datastring += "[G1000]"
        else:
            datastring += "[Y1000]"
        # datastring+=period['FCTTIME']['weekday_name_abbrev']
        datastring+="%02d" % (int(period['FCTTIME']['hour']))+"00: "
        datastring+=period['feelslike']['english']+"F "
        datastring+=wxcode[period['icon']]+"\n"





    r = requests.get(('http://api.wunderground.com/api/' + WUKey + '/forecast/q/' + WUState + '/' + WUCity + '.json'))
    # print r.status_code
    if r.status_code != 200:
        return "LONG FORECAST ERROR"
    longtermwx=r.json()

    for x in xrange(1,4):
        period=longtermwx['forecast']['simpleforecast']['forecastday'][x]
        if float(period['high']['fahrenheit']) <40:
            datastring += "[R1500]"
        elif float(period['high']['fahrenheit']) >65 and float(period['high']['fahrenheit'] < 85) :
            datastring += "[G1500]"
        else:
            datastring += "[Y1500]"
        datastring+=period['date']['weekday_short']+" "+period['high']['fahrenheit']+"/"+period['low']['fahrenheit']+" "+wxcode[period['icon']]+"\n"


    return datastring


def getAstronomy():
    datastring=""
    r = requests.get(('http://api.wunderground.com/api/' + WUKey + '/astronomy/q/' + WUState + '/' + WUCity + '.json'))
    # print r.status_code
    if (r.status_code != 200):
        return "Astronomy error"
    astro = r.json()
    datastring+=astro['sun_phase']['sunrise']['hour']+astro['sun_phase']['sunrise']['minute']+"\n"
    datastring+=astro['sun_phase']['sunset']['hour']+astro['sun_phase']['sunset']['minute']
    return datastring



def constructheader():
    lcltime = time.localtime()
    datastring = ""
    datastring = "[R1000]GOOD"
    if (lcltime.tm_hour < 12) and (lcltime.tm_hour>3):
        datastring += " MORNING"
    elif (lcltime.tm_hour < 17) and (lcltime.tm_hour>3):
        datastring += " AFTERNOON"
    else:
        datastring += " EVENING"
    datastring += "\n"
    datastring += "[R2000]"+time.strftime("%a %b %-d") + "\n"
    datastring += "[R1000]"+time.strftime("%H:%M") + "\n"
    return datastring


def getmbtabustimes(stop,routenum="",routecfg=""):
    r = requests.get(('http://webservices.nextbus.com/service/publicXMLFeed?command=predictions&a=mbta&stopId='+ stop ))
    # print r.status_code
    if (r.status_code != 200):
        return "MBTA FAIL"

    # print r.encoding
    # print r.content
    # print r.text
    # WXjson = r.
    busdata=ElementTree.fromstring(r.content)

    responsetext=""
    # print busdata
    # print "START DECODE"
    try:
        for route in busdata:
            # print route.tag, route.attrib["routeTag"],route.attrib["routeTitle"]
            if route.attrib['routeTag'] == routenum or routenum =="":
                # print "this is a route of interest"
                for direction in route:
                    # print direction.attrib["title"]
                    for trip in direction:
                        # print trip.attrib["dirTag"], trip.attrib["minutes"], trip.attrib["isDeparture"]
                        if trip.attrib["dirTag"] == routecfg or routecfg =="":
                            # print "this route config is of interest"
                            if(responsetext!=""):
                                responsetext +=", "
                            responsetext+=trip.attrib["minutes"]
                            # if trip.attrib.has_key("isDeparture"):
                            #     responsetext+="*"

        if(responsetext==""):
            return ""
        else:
            return responsetext
    except:
        return "ERROR"

def getMBTAalerts():
    datastring=""
    r = requests.get(("http://realtime.mbta.com/developer/api/v2/alerts?api_key="+os.getenv("MBTAdev")+"&include_access_alerts=false&include_service_alerts=true&format=json"))
    # print r.status_code
    if (r.status_code != 200):
        return "MBTA APIv2 ERROR"

    # print r.headers['content-type']
    # print r.encoding
    # print r.text
    alerts = r.json()
    for alert in alerts["alerts"]:
        # try:
            if alert["effect_name"]=="Shuttle" or alert["effect_name"]=="Delay":
                for service in alert["affected_services"]["services"]:
                    if service["route_id"]=="Red" or service["route_id"]=="Orange":
                        # print time.time()+172800
                        # print time.time()+86400
                        # print alert["effect_periods"][0]["effect_start"]
                        # print str(time.time())
                        # print alert["effect_periods"][0]["effect_end"]
                        if (time.time()+86400) > int(alert["effect_periods"][0]["effect_start"]) and time.time() < int(alert["effect_periods"][0]["effect_end"]):
                            print alert["effect_periods"][0]["effect_start"]
                            print time.time()
                            print alert
                            alertstring=alert["short_header_text"].replace(',', ' ').replace('  ', ' ')
                            datastring += msgchop(alertstring,14,"[R600]")
                            break

        # except:
        #     print "MBTA ALERTS ERROR"
        #     pass
    return datastring



# def getnearbymbtainfo():
    # getmbtabustimes("02730","89","") #89 to DAVIS

def updateAdamsBuses():
    davis89=getmbtabustimes("02730","89","89_0_var1")
    davis89+=getmbtabustimes("02730","89","89_0_var2")

    print davis89
    adamsbuses['DAVIS89'].append(davis89)
    adamsbuses['SULLIVAN89'].append(getmbtabustimes("02702"))
    adamsbuses["SULLIVAN101"].append(getmbtabustimes("05303"))
    adamsbuses["LECH80"].append(getmbtabustimes("02385"))

def formatedAdamsbuses():

    print adamsbuses
    responsetext=""
    if(adamsbuses["DAVIS89"]!=None):
        responsetext+="[R1000]TO: Davis\n"
        bus="".join(str(x) for x in adamsbuses["DAVIS89"])
        responsetext+="[R2000]89: "+bus.replace('[','').replace(']','')
        responsetext+="\n"


    responsetext+="[G1000]TO: Sullivan\n"

    if(adamsbuses["SULLIVAN89"]!=None):
        bus="".join(str(x) for x in adamsbuses["SULLIVAN89"])
        responsetext+="[R2000]89: "+bus.replace('[','').replace(']','')
        responsetext+="\n"

    if(adamsbuses["SULLIVAN101"]!=None):
        bus="".join(str(x) for x in adamsbuses["SULLIVAN101"])
        responsetext+="[R2000]101: "+bus.replace('[','').replace(']','')
        responsetext+="\n"

    if(adamsbuses["LECH80"]!=None):
        responsetext+="[Y1000]TO: Lechmere\n"
        bus="".join(str(x) for x in adamsbuses["LECH80"])
        responsetext+="[R2000]80: "+bus.replace('[','').replace(']','')
        responsetext+="\n"
    # print "RESPONSE:"
    # print responsetext
    return responsetext


def updatecoffee():
    if getstoredState("coffee")== None:
        return ""
    brewedat=getstoredState("coffee")

    diff=datetime.datetime.now()-datetime.datetime.strptime(brewedat, "%Y-%m-%d %H:%M:%S.%f")
    print diff.seconds
    minutes = (diff.seconds/60)
    if minutes <45:
        return "[G2000]Coffee "+str(minutes)+"m old\n"
    elif minutes <90:
        return "[Y2000]Coffee "+str(minutes)+" old\n"
    return ""






def updateCMDCTRLdwn():
    content = "~\n"
    content += constructheader()
    content += readstoredWeather()
    content += formatedAdamsbuses()
    content += getMBTAalerts()
    content += updatecoffee()
    # content += "COFFEE.PY"
    writeDWNSTRLEDcmdctrl(content)
    print content

def updateCMDCTRLbuses():
    responsetext=""
    if getstoredState("coffee")== None:
        responsetext+= "CFE:000\n"
    else:
        brewedat=getstoredState("coffee")

        diff=datetime.datetime.now()-datetime.datetime.strptime(brewedat, "%Y-%m-%d %H:%M:%S.%f")
        print diff.seconds
        minutes = (diff.seconds/60)+1

        if minutes <100:
            responsetext += "CFE:"+str(minutes).zfill(3)+"\n"
        else:
            responsetext += "CFE:000\n"


    if adamsbuses["DAVIS89"][0]:
        print adamsbuses["DAVIS89"]
        responsetext+="D89:"+str(adamsbuses["DAVIS89"][0][0]).zfill(3)
        responsetext+="\n"



    if adamsbuses["SULLIVAN89"][0]:
        responsetext+="S89:"+str(adamsbuses["SULLIVAN89"][0][0]).zfill(3)
        responsetext+="\n"

    if adamsbuses["SULLIVAN101"][0]:
        responsetext+="S101:"+str(adamsbuses["SULLIVAN101"][0][0]).zfill(3)
        responsetext+="\n"

    if adamsbuses["LECH80"][0]:
        responsetext+="L80:"+str(adamsbuses["LECH80"][0][0]).zfill(3)
        responsetext+="\n"

    print "RESPONSE:"
    print responsetext
    # return responsetext
    writeBUSEScmdctrl(responsetext)

def updateAstronomy():
    content=""
    content += getAstronomy()

    f = open('/var/www/html/espserve/CMDCTRL/02238astronomy.dat', 'w')
    # f = open('test/02238astronomy.dat', 'w')
    f.seek(0)
    f.write(content)
    f.truncate()
    f.close()



def updateWeather():
    content=""
    content += getcurrentwx()
    content += getforecastwx()

    f = open('/var/www/html/espserve/CMDCTRL/02238wx.dat', 'w')
    # f = open('test/02238wx.dat', 'w')
    f.seek(0)
    f.write(content)
    f.truncate()
    f.close()

def readstoredWeather():
    return open('/var/www/html/espserve/CMDCTRL/02238wx.dat', 'r').read()
    # return open('test/02238wx.dat', 'r').read()

def writeDWNSTRLEDcmdctrl(content):
    f = open('/var/www/html/espserve/CMDCTRL/DWNSTRLEDsign.cmd', 'w')
    # f = open('test/DWNSTRLEDsign.cmd', 'w')

    f.seek(0)
    f.write(content)
    f.truncate()
    f.close()

def writeBUSEScmdctrl(content):
    f = open('/var/www/html/espserve/CMDCTRL/buses.cmd', 'w')
    # f = open('test/buses.cmd', 'w')
    print "buses"
    print content
    f.seek(0)
    f.write(content)
    f.truncate()
    f.close()

def readstoredStates():
    d= {}
    try:
        with open('/var/www/html/espserve/CMDCTRL/housestates.dat', 'r') as file:
        # with open('test/housestates.dat', 'r') as file:

            for line in file:
                line=line.replace('\n','')
                (key, val) = line.split(',')
                if key is None:
                        continue
                d[key] = val
    except:
        print "error parsing states file"
        return None
    return d

def getstoredState(key):
    d=readstoredStates()
    try:
        if key in d:
            return d[key]
        else:
            return None
    except:
        return None

def writeStates(dict):
    f = open('/var/www/html/espserve/CMDCTRL/housestates.dat', 'w')
    # f = open('housestates.dat', 'w')

    f.seek(0)

    for key, value in dict.iteritems():
        f.write(key+","+value)
        f.write('\n')

    f.truncate()
    f.close()

def updateState(key,value):
    d=readstoredStates()
    if d is None:
        d={}
    if value == "TS":
        value = str(datetime.datetime.now())
    d[key]=value
    writeStates(d)



parser = argparse.ArgumentParser()

parser.add_argument('--buses', action='store_true', help='update buses')
parser.add_argument('--weather', action='store_true', help='update weather')
parser.add_argument('--astronomy', action='store_true', help='update astronomy')
parser.add_argument('--state', action='store', help='update a house state key=value')
# parser.add_argument('--weather', action='store_true', help='update weather') Do something for coffee...action bots? pass in a CMD
parser.add_argument('--all', action='store_true', help='update all')



args = parser.parse_args()
# print args

if args.buses:
    print "buses only"
    updateAdamsBuses()
    updateCMDCTRLbuses()
    updateCMDCTRLdwn()

elif args.weather:
    print "WEATHER"
    updateWeather()

elif args.astronomy:
    print "ASTRONOMY"
    updateAstronomy()

elif args.state:
    print "STATE UPDATE"
    data=args.state.split("=")
    updateState(data[0], data[1])

elif args.all:
    print "ALL"
    updateWeather()
    updateAdamsBuses()
    updateCMDCTRLdwn()
    updateCMDCTRLbuses()
    updateAstronomy()

# else:
    # print "NO OPTIONS ALL"
    # update02238Weather()
    # updateCMDCTRL()





