#!/usr/bin/python
#!/usr/bin/env python
from __future__ import print_function
import paho.mqtt.publish as publish
import psutil
import string
import random
import forecastio
import time,sys
import grovepi
import datetime
import os
import math
import argparse
from forecastiopy import *
os.system('systemctl stop radiatoron.service')
os.system('avrdude -c gpio -p m328p')
time.sleep(2)
led2 = 3
grovepi.pinMode(led2,"OUTPUT")
grovepi.digitalWrite(led2,1)
time.sleep(7)
#python file handler
def main():
     #f = open("timeCounter.txt","w+")
     #f=open("timeCounter.txt","a+")
     #for i in range(10):
         #f.write("This is line %d\r\n" % (i+1))
     #f.close()
     #Open the file back and read the contents
     f = open("/home/pi/Desktop/GrovePi/Software/Python/timeCounter.txt", "r")
     if f.mode == 'r':
     #try:
     #contents = int(file.read())
     #print ("timeCounter:" , timeCounter , "contents:" , contents)
     #finally:
     #file.close()
     #close Read File

        contents = int(f.read())
        #print ("contents:" , contents)
        return contents
     f.close()
     #or, readlines reads the individual line into a list
     #fl =f.readlines()
     #for x in fl:
     #print x
if __name__== "__main__":
  main()
#python file handler
def Write(timeCounter,contents):
        #f = open("/home/pi/Desktop/GrovePi/Software/Python/timeCounter.txt", "r")
        #contents = int(f.read())
        #return contents
        #f.close()
        f = open("/home/pi/Desktop/GrovePi/Software/Python/timeCounter.txt", "w+")
        timeCounter = timeCounter + contents
        f.write("%d\n" % timeCounter)
        #print ("Write timeCounter:" , timeCounter)
        #return timeCounter
        f.close()
if __name__== "__Write__":
  Write()

# screen utilization
if sys.platform == 'uwp':
    import winrt_smbus as smbus
    bus = smbus.SMBus(1)
else:
    import smbus
    import RPi.GPIO as GPIO
    rev = GPIO.RPI_REVISION
    if rev == 2 or rev == 3:
        bus = smbus.SMBus(1)
    else:
        bus = smbus.SMBus(0)
# this device has two I2C addresses
DISPLAY_RGB_ADDR = 0x62
DISPLAY_TEXT_ADDR = 0x3e
# set backlight to (R,G,B) (values from 0..255 for each)
def setRGB(r,g,b):
    bus.write_byte_data(DISPLAY_RGB_ADDR,0,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,1,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,0x08,0xaa)
    bus.write_byte_data(DISPLAY_RGB_ADDR,4,r)
    bus.write_byte_data(DISPLAY_RGB_ADDR,3,g)
    bus.write_byte_data(DISPLAY_RGB_ADDR,2,b)

# send command to display (no need for external use)
def textCommand(cmd):
    bus.write_byte_data(DISPLAY_TEXT_ADDR,0x80,cmd)
# set display text \n for second line(or auto wrap)
def setText(text):
    textCommand(0x01) # clear display
    time.sleep(.05)
    textCommand(0x08 | 0x04) # display on, no cursor
    textCommand(0x28) # 2 lines
    time.sleep(.05)
    count = 0
    row = 0
    for c in text:
        if c == '\n' or count == 16:
            count = 0
            row += 1
            if row == 2:
                break
            textCommand(0xc0)
            if c == '\n':
                continue
        count += 1
        bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))

#Update the display without erasing the display
def setText_norefresh(text):
    textCommand(0x02) # return home
    time.sleep(.05)

    textCommand(0x08 | 0x04) # display on, no cursor
    textCommand(0x28) # 2 lines
    time.sleep(.05)
    count = 0
    row = 0
    for c in text:
        if c == '\n' or count == 16:
            count = 0
            row += 1
            if row == 2:
                break
            textCommand(0xc0)
            if c == '\n':
                continue
        count += 1
        bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))
#---------------Let's Begin------------
now = datetime.datetime.utcnow()
sensor = 8
blue = 0
#radiator relay
relay = 7
grovepi.pinMode(relay,"OUTPUT")
#red led
led1 = 2

#counter for how much time has the radiator been turned on(sec/min)
#timeCounter = 0
#contents = 0
grovepi.pinMode(led1,"OUTPUT")
grovepi.pinMode(led2,"OUTPUT")
setRGB(0,128,64)
setRGB(0,128,0)
setText("----Welcome----" "\n" "Loading......")
time.sleep(3)
while True :
        clientID = ''
        # Create a random clientID.
        for x in range(1,16):
            clientID+=random.choice(string.alphanum)
        try:
            ts = time.time()
                st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                now = datetime.datetime.utcnow()
                print ('TIMESTAMP:', st)
                #write = Write(timeCounter)
                #timeCounter =  contents / 60
                #print ("Radiator_ON for:" , timeCounter , "min \t since:", st , " \n\n ")
                #FORECASTIOPY API
                setText("--FORECASTIOPY--"  "\n"  "-Weather Report-" )
                time.sleep(5)
                apikey = "90d3e695cf5f55650c4ffa88d012ca70"
                Larisa = [39.640984, 22.421268]
                fio = ForecastIO.ForecastIO(apikey,
                        units=ForecastIO.ForecastIO.UNITS_SI,
                        lang=ForecastIO.ForecastIO.LANG_ENGLISH,
                        latitude=Larisa[0], longitude=Larisa[1])
                print('Latitude', fio.latitude, 'Longitude', fio.longitude)
                print('Timezone', fio.timezone, 'Offset', fio.offset)
                print(fio.get_url()) # You might want to see the request url
                #get current weather data from darksky.net
                if fio.has_currently() is True:
                        currently = FIOCurrently.FIOCurrently(fio)
                        print('Currently')
                        for item in currently.get().keys():
                                print(item + ' : ' + unicode(currently.get()[item]))
                                # Or access attributes directly
                        print("Current Temperature:", "%.1f" %(currently.temperature))
                        print("Current Humidity:", "%.1f"  %(  currently.humidity * 100)  )
                        print("Current WindSpeed:", "%.2f" % (currently.windSpeed))
                        print("Current CloudCover:", "%.3f" % (currently.cloudCover))
                        print("Current precipIntensity:", "%.1f" % (currently.precipIntensity))
                        print("Current precipProbality:", "%.1f" % (currently.precipProbability))
                        print("Current Summary:" , currently.summary)
                        else:
                        print('No Currently data')
                if currently.cloudCover == 1:
                        print("It's gonna Rain!!")
                elif currently.cloudCover !=0 and currently.summary == "Clear":
                        print("Good Weather!!")
                else:
                        print("OK weather")

                #get hourly weather data from darksky.net
                #if fio.has_hourly() is True:
                        #hourly = FIOHourly.FIOHourly(fio)
                        #print('Hourly')
                        #print('Summary:', hourly.summary)
                        #print('Icon:', hourly.icon)

                        #for hour in range(0, hourly.hours()):
                                #print('Hour', hour+1)
                                #for item in hourly.get_hour(hour).keys():
                                        #print(item + ' : ' + str(hourly.get_hour(hour)[item]))
                                # Or access attributes directly for a given minute.
                                # hourly.hour_5_time would also work
                                #print(hourly.hour_3_time)
                #else:
                        #print('No Hourly data')

                setText('Weather data' '\n'  'loaded')
                time.sleep(4)
                setText("Temperature:" + str("%.1f" %(currently.temperature)) + '\n' "Humidity:" + $
                time.sleep(21)
                time.sleep(4)
                grovepi.digitalWrite(led2,1)
                # unit initialization
                sound=int(grovepi.analogRead(1)/10.24)
                s = str(int(grovepi.analogRead(1)/10.24))
                print ("sound", s)
                time.sleep(5)
                light=int(grovepi.analogRead(2)/10.24)
                l = str(int(grovepi.analogRead(2)/10.24))
                print ("light", l)
                #os.system('avrdude -c gpio -p m328p')
                setRGB(0,128,64)
                setRGB(0,128,0)
                setText("The System is" +"\n" +"now Loading")
                [tempTest,humidity] = grovepi.dht(sensor,blue)
                print ("tempTest", tempTest )
                time.sleep(15)
                [temp1,humidity] = grovepi.dht(sensor,blue)
                print ("temp1", temp1 - 1.5)
                time.sleep(18)
                [temp2,humidity] = grovepi.dht(sensor,blue)
                print ("temp2", temp2 - 1.5)
                time.sleep(15)
                [temp3,humidity] = grovepi.dht(sensor,blue)
                print ("temp3", temp3 - 1.5)
                [temp4,humidity] = grovepi.dht(sensor,blue)
                print ("temp4", temp4 - 1.5)
                time.sleep(6)
                temp = round(((temp1-1.5)+(temp2-1.5)+(temp3-1.5)+(temp4-1.5))/4,1)
                print ("temp", temp , "humidity" , humidity)
                if humidity > 29 and humidity < 45  and humidity !=0 :
                        if temp < 19.5  and currently.temperature > 12.5 :
                                grovepi.digitalWrite(relay,1)
                                grovepi.digitalWrite(led1,1)
                                radiator = "ON"
                                time.sleep(20)
                                grovepi.digitalWrite(relay,1)
                                value  = 1      #radiator
                                value2 = 0      #radiatorRemote
                                allData="field1="+str(temp)+"&field2="+str(humidity)+"&field3="+str$
                                publish.single(topic, payload=allData, hostname=mqttHost, transport$
                                print (radiator,st)
                                print("Current Temperature:",  currently.temperature)
                                print("Current Humidity:", currently.humidity * 100  )
                                print ("temp", temp)
                                print ("Humidity", humidity )
                                setRGB(0,128,64)
                                setRGB(0,128,0)
                                setText("Temperature:" + str(temp) + '\n' "Humidity:" + str(int(hum$
                                print("case 1")
                                time.sleep(1800)
                                timeCounter = 1800
                                contents = main()
                                Write(timeCounter,contents)
                        elif temp < 19.5  and currently.temperature > 15 :
                                grovepi.digitalWrite(relay,0)
                                grovepi.digitalWrite(led1,0)
                                radiator = "OFF"
                                time.sleep(20)
                                grovepi.digitalWrite(relay,0)
                                value  = 0   #radiator
                                value2 = 0  #radiatorRemote
                                allData="field1="+str(temp)+"&field2="+str(humidity)+"&field3="+str$
                                publish.single(topic, payload=allData, hostname=mqttHost, transport$
                                print (radiator,st)
                                print("Current Temperature:",  currently.temperature)
                                print("Current Humidity:", currently.humidity * 100  )
                                print ("temp", temp)
                                print ("Humidity", humidity )
                                setRGB(0,128,64)
                                setRGB(0,128,0)
                                setText("Temperature:" + str(temp) + '\n' "Humidity:" + str(int(hum$
                                print("case 2")
                                time.sleep(1500)
                        elif    currently.temperature > 17.5 :
                                grovepi.digitalWrite(relay,0)
                                grovepi.digitalWrite(led1,0)
                                radiator = "OFF"
                                time.sleep(20)
                                grovepi.digitalWrite(relay,0)
                                value  = 0  #radiator
                                value2 = 0  #radiatorRemote
                                allData="field1="+str(temp)+"&field2="+str(humidity)+"&field3="+str$
                                publish.single(topic, payload=allData, hostname=mqttHost, transport$
                                print (radiator,st)
                                print("Current Temperature:",  currently.temperature)
                                print("Current Humidity:", currently.humidity * 100  )
                                print ("temp", temp)
                                print ("Humidity", humidity )
                                setRGB(0,128,64)
                                setRGB(0,128,0)
                                setText("Temperature:" + str(temp) + '\n' "Humidity:" + str(int(hum$
                                print("case 2")
                                time.sleep(1500)
                        elif    currently.temperature > 17.5 :
                                grovepi.digitalWrite(relay,0)
                                grovepi.digitalWrite(led1,0)
                                radiator = "OFF"
                                time.sleep(20)
                                grovepi.digitalWrite(relay,0)
                                value  = 0  #radiator
                                value2 = 0  #radiatorRemote
                                allData="field1="+str(temp)+"&field2="+str(humidity)+"&field3="+str$
                                publish.single(topic, payload=allData, hostname=mqttHost, transport$
                                print (radiator,st)
                                print("Current Temperature:",  currently.temperature)
                                print("Current Humidity:", currently.humidity * 100  )
                                print ("temp", temp)
                                print ("Humidity", humidity )
                                setRGB(0,128,64)
                                setRGB(0,128,0)
                                setText("Temperature:" + str(temp) + '\n' "Humidity:" + str(int(hum$
                                print("case OFF")
                                time.sleep(3500)

                        elif temp > 19.5  and currently.temperature > 15 :
                                grovepi.digitalWrite(relay,0)
                                grovepi.digitalWrite(led1,0)
                                radiator = "OFF"
                                time.sleep(20)
                                grovepi.digitalWrite(relay,0)
                                value  = 0   #radiator
                                value2 = 0  #radiatorRemote
                                allData="field1="+str(temp)+"&field2="+str(humidity)+"&field3="+str$
                                publish.single(topic, payload=allData, hostname=mqttHost, transport$
                                print (radiator,st)
                                print("Current Temperature:",  currently.temperature)
                                print("Current Humidity:", currently.humidity * 100  )
                                print ("temp", temp)
                                print ("Humidity", humidity )
                                setRGB(0,128,64)
                                setRGB(0,128,0)
                                setText("Temperature:" + str(temp) + '\n' "Humidity:" + str(int(hum$
                                print ("case 3")
                                time.sleep(2500)
                        elif temp < 19.5  and currently.temperature < 10 :
                                grovepi.digitalWrite(relay,1)
                                grovepi.digitalWrite(led1,1)
                                radiator = "ON"
                                time.sleep(20)
                                grovepi.digitalWrite(relay,1)
                                value  = 1   #radiator
                                value2 = 0  #radiatorRemote
                                allData="field1="+str(temp)+"&field2="+str(humidity)+"&field3="+str$
                                publish.single(topic, payload=allData, hostname=mqttHost, transport$
                                print (radiator,st)
                                print("Current Temperature:",  currently.temperature)
                                print("Current Humidity:", currently.humidity * 100  )
                                print ("temp", temp)
                                print ("Humidity", humidity )
                                setRGB(0,128,64)
                                setRGB(0,128,0)
                                setText("Temperature:" + str(temp) + '\n' "Humidity:" + str(int(hum$
                                print("case 4")
                                time.sleep(2000)
                                timeCounter = 2000
                                contents = main()
                                Write(timeCounter,contents)
                        elif temp < 20.5 and temp > 17  and currently.temperature > temp :
                                grovepi.digitalWrite(relay,0)
                                grovepi.digitalWrite(led1,0)
                                radiator = "OFF"
                                time.sleep(20)
                                grovepi.digitalWrite(relay,0)
                                value  = 0   #radiator
                                value2 = 0  #radiatorRemote
                                allData="field1="+str(temp)+"&field2="+str(humidity)+"&field3="+str$
                                publish.single(topic, payload=allData, hostname=mqttHost, transport$
                                print (radiator,st)
                                print("Current Temperature:",  currently.temperature)
                                print("Current Humidity:", currently.humidity * 100  )
                                print ("temp", temp)
                                print ("Humidity", humidity )
                                setRGB(0,128,64)
                                setRGB(0,128,0)
                                setText("Temperature:" + str(temp) + '\n' "Humidity:" + str(int(hum$
                                print("case 5")
                                time.sleep(2500)
                        elif currently.temperature > temp :
                                grovepi.digitalWrite(relay,0)
                                grovepi.digitalWrite(led1,0)
                                radiator = "OFF"
                                time.sleep(20)
                                grovepi.digitalWrite(relay,0)
                                value  = 0   #radiator
                                value2 = 0  #radiatorRemote
                                allData="field1="+str(temp)+"&field2="+str(humidity)+"&field3="+str$
                                publish.single(topic, payload=allData, hostname=mqttHost, transport$
                                print (radiator,st)
                                print("Current Temperature:",  currently.temperature)
                                print("Current Humidity:", currently.humidity * 100  )
                                print ("temp", temp)
                                print ("Humidity", humidity )
                                setRGB(0,128,64)
                                setRGB(0,128,0)
                                setText("Temperature:" + str(temp) + '\n' "Humidity:" + str(int(hum$
                                print ("case 6")
                                time.sleep(3000)
                        elif temp < 20.5 and currently.temperature < 13.5       :
                                grovepi.digitalWrite(relay,1)
                                grovepi.digitalWrite(led1,1)
                                radiator = "ON"
                                time.sleep(20)
                                grovepi.digitalWrite(relay,1)
                                value  = 1   #radiator
                                value2 = 0  #radiatorRemote
                                allData="field1="+str(temp)+"&field2="+str(humidity)+"&field3="+str$
                                publish.single(topic, payload=allData, hostname=mqttHost, transport$
                                print (radiator,st)
                                print("Current Temperature:",  currently.temperature)
                                print("Current Humidity:", currently.humidity * 100  )
                                print ("temp", temp)
                                print ("Humidity", humidity )
                                setRGB(0,128,64)
                                setRGB(0,128,0)
                                setText("Temperature:" + str(temp) + '\n' "Humidity:" + str(int(hum$
                                print ("case 7")
                                time.sleep(1500)
                                timeCounter = 1500
                                contents = main()
                                Write(timeCounter,contents)
                        elif temp < 20.8 and currently.temperature < 12.0       :
                                grovepi.digitalWrite(relay,1)
                                grovepi.digitalWrite(led1,1)
                                radiator = "ON"
                                time.sleep(20)
                                grovepi.digitalWrite(relay,1)
                                value  = 1  #radiator
                                value2 = 0  #radiatorRemote
                                allData="field1="+str(temp)+"&field2="+str(humidity)+"&field3="+str$
                                publish.single(topic, payload=allData, hostname=mqttHost, transport$
                                print (radiator,st)
                                print("Current Temperature:",  currently.temperature)
                                print("Current Humidity:", currently.humidity * 100  )
                                print ("temp", temp)
                                print ("Humidity", humidity )
                                setRGB(0,128,64)
                                setRGB(0,128,0)
                                setText("Temperature:" + str(temp) + '\n' "Humidity:" + str(int(hum$
                                print ("case 8")
                                time.sleep(1500)
                                timeCounter = 1500
                                contents = main()
                                Write(timeCounter,contents)
                        elif temp < 21.0 and currently.temperature < 1.0       :
                                grovepi.digitalWrite(relay,1)
                                grovepi.digitalWrite(led1,1)
                                radiator = "ON"
                                time.sleep(20)
                                grovepi.digitalWrite(relay,1)
                                value  = 1  #radiator
                                value2 = 0  #radiatorRemote
                                allData="field1="+str(temp)+"&field2="+str(humidity)+"&field3="+str$
                                publish.single(topic, payload=allData, hostname=mqttHost, transport$
                                print (radiator,st)
                                print("Current Temperature:",  currently.temperature)
                                print("Current Humidity:", currently.humidity * 100  )
                                print ("temp", temp)
                                print ("Humidity", humidity )
                                setRGB(0,128,64)
                                setRGB(0,128,0)
                                setText("Temperature:" + str(temp) + '\n' "Humidity:" + str(int(hum$
                                print ("case 9")
                                time.sleep(1800)
                                timeCounter = 1800
                                contents = main()
                                Write(timeCounter,contents)
                        else:
                                grovepi.digitalWrite(relay,0)
                                grovepi.digitalWrite(led1,0)
                                radiator = "OFF"
                                time.sleep(20)
                                grovepi.digitalWrite(relay,0)
                                value  = 0   #radiator
                                value2 = 0  #radiatorRemote
                                allData="field1="+str(temp)+"&field2="+str(humidity)+"&field3="+str$
                                publish.single(topic, payload=allData, hostname=mqttHost, transport$
                                print (radiator,st)
                                print("Current Temperature:",  currently.temperature)
                                print("Current Humidity:", currently.humidity * 100  )
                                print ("temp", temp)
                                print ("Humidity", humidity )
                                setRGB(0,128,64)
                                setRGB(0,128,0)
                                setText("Temperature:" + str(temp) + '\n' "Humidity:" + str(int(hum$
                                print ("case 10-else")
                                time.sleep(2000)
                else:
                        print("Humidity in Dangerous Levels!!!")
                        setRGB(0,128,64)
                        setRGB(0,128,0)
                        setText("---ATTENTION---" '\n' + str(temp) + str((inthumidity)) )
                        time.sleep(3600)
        except KeyboardInterrupt:
                grovepi.digitalWrite(relay,0)
                grovepi.digitalWrite(led1,0)
                radiator = "OFF"
                time.sleep(2)
                grovepi.digitalWrite(relay,0)
                print ("  except keyboard_interrupt "  + radiator)
                setRGB(0,128,64)
                setRGB(0,128,0)
                setText("except keyboard_interrupt")
                break
        except:
                grovepi.digitalWrite(led1,0)
                grovepi.digitalWrite(relay,0)
                radiator = "OFF"
                time.sleep(20)
                grovepi.digitalWrite(relay,0)
                print (" except false" + radiator)
                setRGB(0,128,64)
                setRGB(0,128,0)
                setText("except error")
                os.system('systemctl restart relay.service')
                break














