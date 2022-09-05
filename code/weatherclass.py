import network, socket
import urequests as requests
import urequests
import gc
from micropython import *
from Maix import GPIO
from fpioa_manager import fm
from board import board_info
import time
import lcd
import image
try:
    import ussl
except Exception:
    import ussl

gc.collect()

lcd.init()
img = image.Image()
img.draw_string(0, 0, "Initializing...", scale=2)
lcd.display(img)

bg = image.Image()

WIFI_SSID = "Wolfgang"
WIFI_PASSWD = "wu923872681999"

def connectAP(ssid,passwd):
    fm.register(25,fm.fpioa.GPIOHS10, force=True)
    fm.register(8,fm.fpioa.GPIOHS11, force=True)
    fm.register(9,fm.fpioa.GPIOHS12, force=True)
    fm.register(28,fm.fpioa.GPIOHS13, force=True)
    fm.register(26,fm.fpioa.GPIOHS14, force=True)
    fm.register(27,fm.fpioa.GPIOHS15, force=True)
    nic = network.ESP32_SPI(cs=fm.fpioa.GPIOHS10,rst=fm.fpioa.GPIOHS11,rdy=fm.fpioa.GPIOHS12, mosi=fm.fpioa.GPIOHS13,miso=fm.fpioa.GPIOHS14,sclk=fm.fpioa.GPIOHS15)
    print("ESP32_SPI firmware version:", nic.version())
    err = 0
    while 1:
        try:
            nic.connect(ssid, passwd)
        except Exception:
            err += 1
            print("Connect AP failed, now try again")
            if err > 3:
                raise Exception("Conenct AP fail")
            continue
        break
    print(nic.ifconfig())
    print(nic.isconnected())

connectAP(WIFI_SSID,WIFI_PASSWD)

img.draw_string(0, 30, "Successfully Connected to AP", scale=2)
lcd.display(img)

class weatherModule:
    URL = 'http://route.showapi.com/9-2?showapi_appid=425616&showapi_sign=85c8d864857943849ed1883302877903&area='
    def __init__(self,cityname):
        self.URL = self.URL+cityname

    def rq(self):
        try:
            return requests.get(self.URL)
        except Exception:
            return requests.get(self.URL)

def trs(words):
    try:
        return requests.get('http://fanyi.youdao.com/translate?&doctype=json&type=AUTO&i='+words)
    except Exception:
        return requests.get('http://fanyi.youdao.com/translate?&doctype=json&type=AUTO&i='+words)

class infoModule:
    city = 'ss'
    weatherNow = 'ss'
    temp = 0
    tempRange = 'ss'
    weatherCode = 0
    rainProp = 'ss'
    day = 1
    weekday = 0
    def __init__(self,jsons):
        self.city = jsons.json()['showapi_res_body']['cityInfo']['c4']
        try:
            self.weatherNow = trs(jsons.json()['showapi_res_body']['now']['weather']).json()["translateResult"][0][0]["tgt"]
        except Exception:
            self.weatherNow = trs(jsons.json()['showapi_res_body']['now']['weather']).json()["translateResult"][0][0]["tgt"]

        self.temp = int(jsons.json()['showapi_res_body']['now']['temperature'])
        self.tempRange = jsons.json()['showapi_res_body']['f1']['night_air_temperature'] + "~" + jsons.json()['showapi_res_body']['f1']['day_air_temperature']
        self.weatherCode = int(jsons.json()['showapi_res_body']['now']['weather_code'])
        self.rainProp = jsons.json()['showapi_res_body']['f1']['jiangshui']
        self.weekday = jsons.json()['showapi_res_body']['f1']['weekday']


    def fc2refreshInfo(self,jsons):
        try:
            self.weather = trs(jsons.json()['showapi_res_body']['f2']['day_weather']).json()["translateResult"][0][0]["tgt"]
        except Exception:
            self.weather = trs(jsons.json()['showapi_res_body']['f2']['day_weather']).json()["translateResult"][0][0]["tgt"]
        self.temp = int((int(jsons.json()['showapi_res_body']['f3']['day_air_temperature']) + int(jsons.json()['showapi_res_body']['f3']['night_air_temperature']))/2)
        self.tempRange = jsons.json()['showapi_res_body']['f2']['night_air_temperature'] + "~" + jsons.json()['showapi_res_body']['f2']['day_air_temperature']
        self.weatherCode = int(jsons.json()['showapi_res_body']['f2']['day_weather_code'])
        self.rainProp = jsons.json()['showapi_res_body']['f2']['jiangshui']
        self.day = 2
        self.weekday = jsons.json()['showapi_res_body']['f2']['weekday']
    def fc3refreshInfo(self,jsons):
        try:
            self.weather = trs(jsons.json()['showapi_res_body']['f3']['day_weather']).json()["translateResult"][0][0]["tgt"]
        except Exception:
            self.weather = trs(jsons.json()['showapi_res_body']['f3']['day_weather']).json()["translateResult"][0][0]["tgt"]
        self.temp = int((int(jsons.json()['showapi_res_body']['f3']['day_air_temperature']) + int(jsons.json()['showapi_res_body']['f3']['night_air_temperature']))/2)
        self.tempRange = jsons.json()['showapi_res_body']['f3']['night_air_temperature'] + "~" + jsons.json()['showapi_res_body']['f3']['day_air_temperature']
        self.weatherCode = int(jsons.json()['showapi_res_body']['f3']['day_weather_code'])
        self.rainProp = jsons.json()['showapi_res_body']['f3']['jiangshui']
        self.day = 3
        self.weekday = jsons.json()['showapi_res_body']['f3']['weekday']
    def printInfo(self):
        print(self.city)
        print(self.weatherNow)
        print(self.temp)
        print(self.tempRange)
        print(self.rainProp)


class timeModule:
    URL = 'http://quan.suning.com/getSysTime.do'
    def rq(self):
        try:
            return requests.get(self.URL)
        except Exception:
            return requests.get(self.URL)

class timeInfo:
    year = 0
    month = 0
    day = 0
    hour = 0
    minute = 0
    second = 0

    def __init__(self,r):
        self.year = int(r.json()['sysTime1'][0:4])
        self.month = int(r.json()['sysTime1'][4:6])
        self.day = int(r.json()['sysTime1'][6:8])
        self.hour = int(r.json()['sysTime1'][8:10])
        self.mintue = int(r.json()['sysTime1'][10:12])
        self.second = int(r.json()['sysTime1'][12:14])+4

    def printTime(self):
        img.draw_string(0, 170, str(self.year)+","+str(self.month)+","+str(self.day)+" "+str(self.hour)+":"+str(self.mintue), scale=2)
        print(str(self.year)+","+str(self.month)+","+str(self.day)+": ")
        print(str(self.hour)+":"+str(self.mintue))


class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):

        yield self.match
        raise StopIteration

    def match(self, *args):

        if self.fall or not args:
            return True
        elif self.value in args:
            self.fall = True
            return True
        else:
            return False

def loadingPic(weatherCode):
    for case in switch(weatherCode):
        if case(0):
            return image.Image("/flash/d00.bmp")
            break
        if case(1):
            return image.Image("/flash/d01.bmp")
            break
        if case(2):
            return image.Image("/flash/d02.bmp")
            break
        if case(3):
            return image.Image("/flash/d03.bmp")
            break
        if case(4):
            return image.Image("/flash/d04.bmp")
            break
        if case(5):
            return image.Image("/flash/d05.bmp")
            break
        if case(6):
            return image.Image("/flash/d06.bmp")
            break
        if case(7):
            return image.Image("/flash/d07.bmp")
            break
        if case(8):
            return image.Image("/flash/d08.bmp")
            break
        if case(9):
            return image.Image("/flash/d08.bmp")
            break
        if case(10):
            return image.Image("/flash/d09.bmp")
            break
        if case(11):
            return image.Image("/flash/d11.bmp")
            break
        if case(12):
            return image.Image("/flash/d12.bmp")
            break
        if case(13):
            return image.Image("/flash/d13.bmp")
            break
        if case(14):
            return image.Image("/flash/d14.bmp")
            break
        if case(15):
            return image.Image("/flash/d15.bmp")
            break
        if case(16):
            return image.Image("/flash/d15.bmp")
            break
        if case(17):
            return image.Image("/flash/d17.bmp")
            break
        if case(18):
            return image.Image("/flash/d18.bmp")
            break
        if case(19):
            return image.Image("/flash/d19.bmp")
            break
        if case(20):
            return image.Image("/flash/d20.bmp")
            break
        if case(21):
            return image.Image("/flash/d21.bmp")
            break
        if case(22):
            return image.Image("/flash/d21.bmp")
            break
        if case(23):
            return image.Image("/flash/d23.bmp")
            break
        if case(24):
            return image.Image("/flash/d24.bmp")
            break
        if case(25):
            return image.Image("/flash/d24.bmp")
            break
        if case(26):
            return image.Image("/flash/d15.bmp")
            break
        if case(27):
            return image.Image("/flash/d16.bmp")
            break
        if case(28):
            return image.Image("/flash/d17.bmp")
            break
        if case(29):
            return image.Image("/flash/d20.bmp")
            break
        if case(30):
            return image.Image("/flash/d20.bmp")
            break
        if case(31):
            return image.Image("/flash/d20.bmp")
            break
        if case(53):
            return image.Image("/flash/d18.bmp")
            break
        if case(301):
            return image.Image("/flash/d07.bmp")
            break
        if case(302):
            return image.Image("/flash/d14.bmp")
            break

def uiscript(temp,tl,city,cl,weather,wl,tempRange,trl,ip,rainProp,img,bg,weekday,day):
    bg.clear()

    if(weekday==1):
        bg.draw_string(20,100,"Mon.",color=(0,255,147),scale = 14)
        bg.draw_string(21,101,"Mon.",color=(176,196,222),scale = 14)
        bg.draw_string(22,102,"Mon.",color=(0,0,139),scale = 14)
    elif(weekday==2):
        bg.draw_string(20,100,"Tue.",color=(0,255,147),scale = 14)
        bg.draw_string(21,101,"Tue.",color=(176,196,222),scale = 14)
        bg.draw_string(22,102,"Tue.",color=(0,0,139),scale = 14)
    elif(weekday==3):
        bg.draw_string(20,100,"Wed.",color=(0,255,147),scale = 14)
        bg.draw_string(21,101,"Wed.",color=(176,196,222),scale = 14)
        bg.draw_string(22,102,"Wed.",color=(0,0,139),scale = 14)
    elif(weekday==4):
        bg.draw_string(20,100,"Thur.",color=(0,255,147),scale = 14)
        bg.draw_string(21,101,"Thur.",color=(176,196,222),scale = 14)
        bg.draw_string(22,102,"Thur.",color=(0,0,139),scale = 14)
    elif(weekday==5):
        bg.draw_string(20,100,"Fri.",color=(0,255,147),scale = 14)
        bg.draw_string(21,101,"Fri.",color=(176,196,222),scale = 14)
        bg.draw_string(22,102,"Fri.",color=(0,0,139),scale = 14)
    elif(weekday==6):
        bg.draw_string(20,100,"Sat.",color=(0,255,147),scale = 14)
        bg.draw_string(21,101,"Sat.",color=(176,196,222),scale = 14)
        bg.draw_string(22,102,"Sat.",color=(0,0,139),scale = 14)
    elif(weekday==7):
        bg.draw_string(20,100,"Sun.",color=(0,255,147),scale = 14)
        bg.draw_string(21,101,"Sun.",color=(176,196,222),scale = 14)
        bg.draw_string(22,102,"Sun.",color=(0,0,139),scale = 14)

    bg.draw_string(200-(tl-1)*50,20,str(temp),color=(30,144,255),scale=10)

    bg.draw_string(202-(tl-1)*50,22,str(temp),color=(255,144,255),scale=10)

    bg.draw_string(204-(tl-1)*50,24,str(temp),color=(255,0,255),scale=10)

    bg.draw_string(260,20,"o",color=(30,144,255),scale = 2)

    bg.draw_string(261,21,"o",color=(255,144,255),scale = 2)

    bg.draw_string(262,22,"o",color=(255,0,255),scale = 2)

    bg.draw_string(280,20,"C",color=(30,144,255),scale = 4)
    bg.draw_string(282,22,"C",color=(255,144,255),scale = 4)
    bg.draw_string(284,24,"C",color=(255,0,255),scale = 4)

    bg.draw_string(250-(cl-6)*12,130,city,color=(30,144,255),scale = 2)

    bg.draw_string(251-(cl-6)*12,131,city,color=(255,144,255),scale = 2)

    bg.draw_string(252-(cl-6)*12,132,city,color=(255,0,255),scale = 2)

    bg.draw_string(240-(trl-5)*10,150,tempRange,color=(30,144,255),scale = 2)
    bg.draw_string(241-(trl-5)*10,151,tempRange,color=(255,144,255),scale = 2)
    bg.draw_string(242-(trl-5)*10,152,tempRange,color=(255,0,255),scale = 2)

    bg.draw_string(300,150,"o",color=(30,144,255),scale = 1)
    bg.draw_string(301,151,"o",color=(255,144,255),scale = 1)
    bg.draw_string(302,152,"o",color=(255,0,255),scale = 1)

    bg.draw_string(305,150,"C",color=(30,144,255),scale = 2)
    bg.draw_string(306,151,"C",color=(255,144,255),scale = 2)
    bg.draw_string(307,152,"C",color=(255,0,255),scale = 2)

    if(wl<=17):
        bg.draw_string(5,150,weather,color=(30,144,255),scale = 2.5)
        bg.draw_string(7,152,weather,color=(255,144,255),scale = 2.5)
        bg.draw_string(9,154,weather,color=(255,0,255),scale = 2.5)
    else:
        bg.draw_string(5,150,weather,color=(30,144,255),scale = 1.5)
        bg.draw_string(6,151,weather,color=(255,144,255),scale = 1.5)
        bg.draw_string(7,152,weather,color=(255,0,255),scale = 1.5)

    bg.draw_string(5,190,"Rain prop: "+rainProp,color=(30,144,255),scale = 1.5)
    bg.draw_string(6,191,"Rain prop: "+rainProp,color=(255,144,255),scale = 1.5)
    bg.draw_string(7,192,"Rain prop: "+rainProp,color=(255,0,255),scale = 1.5)

    bg.draw_string(5,210,ip,color=(30,144,255),scale = 2)
    bg.draw_string(7,212,ip,color=(255,144,255),scale = 2)
    bg.draw_string(9,214,ip,color=(255,0,255),scale = 2)

    if(day==1):
        bg.draw_string(5,120,"Today is",color=(255,255,0),scale = 2)
        bg.draw_string(6,121,"Today is",color=(255,193,193),scale = 2)
        bg.draw_string(7,122,"Today is",color=(255,106,106),scale = 2)
    elif(day==2):
        bg.draw_string(5,120,"Tomorrow is",color=(255,255,0),scale = 2)
        bg.draw_string(6,121,"Tomorrow is",color=(255,193,193),scale = 2)
        bg.draw_string(7,122,"Tomorrow is",color=(255,106,106),scale = 2)
    elif(day==3):
        bg.draw_string(5,120,"Day after tomorrow is",color=(255,255,0),scale = 1.5)
        bg.draw_string(6,121,"Day after tomorrow is",color=(255,193,193),scale = 1.5)
        bg.draw_string(7,122,"Day after tomorrow is",color=(255,106,106),scale = 1.5)


    lcd.display(bg)
    lcd.display(img,oft=(0,0))

if __name__ == '__main__':
    #time_start = time.time()
    ww = weatherModule("广州")

    try:
        r = ww.rq()
    except Exception:
        r = ww.rq()

    try:
        i = infoModule(r)
    except Exception:
        i = infoModule(r)

    i.printInfo()
    img.draw_string(0,60,"Processing data...",scale=2)

    lcd.clear()
    lcd.display(img)
    time.sleep(1)

    weathercode = i.weatherCode

    wimg = loadingPic(weathercode)



    lcd.clear()

    uiscript(i.temp,len(str(i.temp)),i.city,len(i.city),i.weatherNow,len(i.weatherNow),i.tempRange,len(i.tempRange),WIFI_SSID,i.rainProp,wimg,bg,i.weekday,i.day)
    #time_end = time.time()

    #time_c = time_end - time_start

    #print("Time costing: ",time_c,"s")
    time.sleep(10)
    i.fc2refreshInfo(r)
    uiscript(i.temp,len(str(i.temp)),i.city,len(i.city),i.weatherNow,len(i.weatherNow),i.tempRange,len(i.tempRange),WIFI_SSID,i.rainProp,wimg,bg,i.weekday,i.day)

    time.sleep(10)

    i.fc3refreshInfo(r)
    uiscript(i.temp,len(str(i.temp)),i.city,len(i.city),i.weatherNow,len(i.weatherNow),i.tempRange,len(i.tempRange),WIFI_SSID,i.rainProp,wimg,bg,i.weekday,i.day)

    time.sleep(10)
