import forecastio
import pytz
import time,sys
import xively
import grovepi
import datetime
import os
from forecastiopy import *



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



#XIVELY API
XIVELY_API_KEY = ""
XIVELY_FEED_ID = ""
api = xively.XivelyAPIClient(XIVELY_API_KEY)
feed = api.feeds.get(XIVELY_FEED_ID)
now = datetime.datetime.utcnow()
sensor = 4
blue = 0
led2 = 7
relay = 3
grovepi.pinMode(relay,"OUTPUT")
led1 = 2
grovepi.pinMode(led1,"OUTPUT")
grovepi.pinMode(led2,"OUTPUT")
setRGB(0,128,64)
setRGB(0,255,0)
setText("----Welcome----" "\n" "Loading......")
time.sleep(3)
while True:
        try:
		#FORECASTIOPY API
		setText("--FORECATIOPY--"  "\n"  "-Weather Report-" )
		time.sleep(5)
		apikey = ""
		Larisa = [39.640984, 22.421268]
		fio = ForecastIO.ForecastIO(apikey,
    		            units=ForecastIO.ForecastIO.UNITS_SI,
                            lang=ForecastIO.ForecastIO.LANG_ENGLISH,
                            latitude=Larisa[0], longitude=Larisa[1])
		print('Latitude', fio.latitude, 'Longitude', fio.longitude)
		print('Timezone', fio.timezone, 'Offset', fio.offset)
		#print(fio.get_url()) # You might want to see the request url
		if fio.has_currently() is True:
       			currently = FIOCurrently.FIOCurrently(fio)
        		print('Currently')
        		for item in currently.get().keys():
                		print(item + ' : ' + unicode(currently.get()[item]))
        		# Or access attributes directly
        		print("Current Temperature:",  currently.temperature)
        		print("Current Humidity:", currently.humidity * 100  )
		else:
        		print('No Currently data')
		setText('Weather data' '\n'  'loaded')
		time.sleep(3)
		setText("Temperature:" + str("%.1f" %(currently.temperature)) + '\n' "Humidity:" + str(float(currently.humidity * 100 ))  + "%")
		time.sleep(10)
		grovepi.digitalWrite(led2,1)
                ts = time.time()
                st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                now = datetime.datetime.utcnow()
                # unit initialization
		sound=int(grovepi.analogRead(1)/10.24)
                s = str(int(grovepi.analogRead(1)/10.24))
                light=int(grovepi.analogRead(0)/10.24)
                l = str(int(grovepi.analogRead(0)/10.24))
		setRGB(0,128,64)
		setRGB(0,255,0)
		setText("The System is" +"\n" +"now Loading")
		[temp1,humidity] = grovepi.dht(sensor,blue)
                print ("temp1", temp1 - 1.5)
                time.sleep(20)
                [temp2,humidity] = grovepi.dht(sensor,blue)
                print ("temp2", temp2 - 1.5)
                time.sleep(20)
                [temp3,humidity] = grovepi.dht(sensor,blue)
                print ("temp3", temp3 - 1.5)
		[temp4,humidity] = grovepi.dht(sensor,blue)
		time.sleep(20)
                print ("temp4", temp4 - 1.5)
		time.sleep(5)
                temp = round(((temp1-1.5)+(temp2-1.5)+(temp3-1.5)+(temp4-1.5))/4,1)
                print ("temp", temp)
                if temp < 19.5  and currently.temperature < 15 :
                        grovepi.digitalWrite(relay,1)
                        grovepi.digitalWrite(led1,1)
                        radiator = "ON"
                        print (radiator,st)
			print("Current Temperature:",  currently.temperature)
                        print("Current Humidity:", currently.humidity * 100  )
			print ("temp", temp)
			print ("Humidity", humidity )
			setRGB(0,128,64)
                	setRGB(0,255,0)
                	setText("Temperature:" + str(temp) + '\n' "Humidity:" + str(int(humidity)) + "%")
			feed.datastreams = [
			xively.Datastream(id='light', current_value=light, at=now),
                        xively.Datastream(id='sound', current_value=sound, at=now),
                        xively.Datastream(id='temp', current_value=temp, at=now),
			xively.Datastream(id='outside_temperature', current_value=currently.temperature, at=now),
			xively.Datastream(id='outside_humidity', current_value=currently.humidity * 100 , at=now),
                        xively.Datastream(id='humidity', current_value=humidity, at=now),
                        xively.Datastream(id='radiator', current_value=radiator, at=now),
                ]
                        feed.update()
                        time.sleep(1000)
		elif temp < 19.5  and currently.temperature > 15 :
			grovepi.digitalWrite(relay,0)
                        grovepi.digitalWrite(led1,0)
                        radiator = "OFF"
                        print (radiator,st)
                        print("Current Temperature:",  currently.temperature)
                        print("Current Humidity:", currently.humidity * 100  )
                        print ("temp", temp)
                        print ("Humidity", humidity )
			setRGB(0,128,64)
                	setRGB(0,255,0)
                	setText("Temperature:" + str(temp) + '\n' "Humidity:" + str(int(humidity)) + "%")
			feed.datastreams = [
			xively.Datastream(id='light', current_value=light, at=now),
                        xively.Datastream(id='sound', current_value=sound, at=now),
                        xively.Datastream(id='temp', current_value=temp, at=now),
			xively.Datastream(id='outside_temperature', current_value=currently.temperature, at=now),
                        xively.Datastream(id='outside_humidity', current_value=currently.humidity * 100 , at=now),
                        xively.Datastream(id='humidity', current_value=humidity, at=now),
                        xively.Datastream(id='radiator', current_value=radiator, at=now),
                ]
                        feed.update()
                        time.sleep(1800)
		elif temp > 19.5  and currently.temperature > 15 :
			grovepi.digitalWrite(relay,0)
                        grovepi.digitalWrite(led1,0)
                        radiator = "OFF"
                        print (radiator,st)
                        print("Current Temperature:",  currently.temperature)
                        print("Current Humidity:", currently.humidity * 100  )
                        print ("temp", temp)
                        print ("Humidity", humidity )
			setRGB(0,128,64)
                	setRGB(0,255,0)
                	setText("Temperature:" + str(temp) + '\n' "Humidity:" + str(int(humidity)) + "%")
			feed.datastreams = [
			xively.Datastream(id='light', current_value=light, at=now),
                        xively.Datastream(id='sound', current_value=sound, at=now),
                        xively.Datastream(id='temp', current_value=temp, at=now),
			xively.Datastream(id='outside_temperature', current_value=currently.temperature, at=now),
                        xively.Datastream(id='outside_humidity', current_value=currently.humidity * 100 , at=now),
                        xively.Datastream(id='humidity', current_value=humidity, at=now),
                        xively.Datastream(id='radiator', current_value=radiator, at=now),
                ]
                        feed.update()
                        time.sleep(1800)
		elif temp < 20.5  and currently.temperature < 11 :
			grovepi.digitalWrite(relay,1)
                        grovepi.digitalWrite(led1,1)
                        radiator = "ON"
                        print (radiator,st)
                        print("Current Temperature:",  currently.temperature)
                        print("Current Humidity:", currently.humidity * 100  )
                        print ("temp", temp)
                        print ("Humidity", humidity )
			setRGB(0,128,64)
                	setRGB(0,255,0)
                	setText("Temperature:" + str(temp) + '\n' "Humidity:" + str(int(humidity)) + "%")
			feed.datastreams = [
			xively.Datastream(id='light', current_value=light, at=now),
                        xively.Datastream(id='sound', current_value=sound, at=now),
                        xively.Datastream(id='temp', current_value=temp, at=now),
			xively.Datastream(id='outside_temperature', current_value=currently.temperature, at=now),
                        xively.Datastream(id='outside_humidity', current_value=currently.humidity * 100 , at=now),
                        xively.Datastream(id='humidity', current_value=humidity, at=now),
                        xively.Datastream(id='radiator', current_value=radiator, at=now),
                ]
                        feed.update()
                        time.sleep(2000)
		elif temp < 20.5 and temp > 17  and currently.temperature > temp :
			grovepi.digitalWrite(relay,0)
                        grovepi.digitalWrite(led1,0)
                        radiator = "OFF"
                        print (radiator,st)
                        print("Current Temperature:",  currently.temperature)
                        print("Current Humidity:", currently.humidity * 100  )
                        print ("temp", temp)
                        print ("Humidity", humidity )
			setRGB(0,128,64)
                	setRGB(0,255,0)
                	setText("Temperature:" + str(temp) + '\n' "Humidity:" + str(int(humidity)) + "%")
			feed.datastreams = [
			xively.Datastream(id='light', current_value=light, at=now),
                        xively.Datastream(id='sound', current_value=sound, at=now),
                        xively.Datastream(id='temp', current_value=temp, at=now),
			xively.Datastream(id='outside_temperature', current_value=currently.temperature, at=now),
                        xively.Datastream(id='outside_humidity', current_value=currently.humidity * 100 , at=now),
                        xively.Datastream(id='humidity', current_value=humidity, at=now),
                        xively.Datastream(id='radiator', current_value=radiator, at=now),
                ]
                        feed.update()
                        time.sleep(2000)
		elif currently.temperature > temp :
			grovepi.digitalWrite(relay,0)
                        grovepi.digitalWrite(led1,0)
                        radiator = "OFF"
                        print (radiator,st)
                        print("Current Temperature:",  currently.temperature)
                        print("Current Humidity:", currently.humidity * 100  )
                        print ("temp", temp)
                        print ("Humidity", humidity )
			setRGB(0,128,64)
                	setRGB(0,255,0)
                	setText("Temperature:" + str(temp) + '\n' "Humidity:" + str(int(humidity)) + "%")
			feed.datastreams = [
			xively.Datastream(id='light', current_value=light, at=now),
                        xively.Datastream(id='sound', current_value=sound, at=now),
                        xively.Datastream(id='temp', current_value=temp, at=now),
			xively.Datastream(id='outside_temperature', current_value=currently.temperature, at=now),
                        xively.Datastream(id='outside_humidity', current_value=currently.humidity * 100 , at=now),
                        xively.Datastream(id='humidity', current_value=humidity, at=now),
                        xively.Datastream(id='radiator', current_value=radiator, at=now),
                ]
                        feed.update()
                        time.sleep(1800)
		elif temp < 19 and currently.temperature < 10	:
                        grovepi.digitalWrite(relay,1)
                        grovepi.digitalWrite(led1,1)
                        radiator = "ON"
                        print (radiator,st)
			print("Current Temperature:",  currently.temperature)
                        print("Current Humidity:", currently.humidity * 100  )
                        print ("temp", temp)
                        print ("Humidity", humidity )
                        setRGB(0,128,64)
                        setRGB(0,255,0)
                        setText("Temperature:" + str(temp) + '\n' "Humidity:" + str(int(humidity)) + "%")
                        feed.datastreams = [
                        xively.Datastream(id='light', current_value=light, at=now),
                        xively.Datastream(id='sound', current_value=sound, at=now),
                        xively.Datastream(id='temp', current_value=temp, at=now),
                        xively.Datastream(id='outside_temperature', current_value=currently.temperature, at=now),
                        xively.Datastream(id='outside_humidity', current_value=currently.humidity * 100 , at=now),
                        xively.Datastream(id='humidity', current_value=humidity, at=now),
                        xively.Datastream(id='radiator', current_value=radiator, at=now),
                ]
                        feed.update()
                        time.sleep(1800)
				
                else:
                        grovepi.digitalWrite(relay,0)
                        grovepi.digitalWrite(led1,0)
                        radiator = "OFF"
                        print (radiator,st)
			print("Current Temperature:",  currently.temperature)
                        print("Current Humidity:", currently.humidity * 100  )
                        print ("temp", temp)
                        print ("Humidity", humidity )
			setRGB(0,128,64)
                        setRGB(0,255,0)
                        setText("Temperature:" + str(temp) + '\n' "Humidity:" + str(int(humidity)) + "%")
			feed.datastreams = [
			xively.Datastream(id='light', current_value=light, at=now),
                        xively.Datastream(id='sound', current_value=sound, at=now),
                        xively.Datastream(id='temp', current_value=temp, at=now),
			xively.Datastream(id='outside_temperature', current_value=currently.temperature, at=now),
                        xively.Datastream(id='outside_humidity', current_value=currently.humidity * 100 , at=now),
                        xively.Datastream(id='humidity', current_value=humidity, at=now),
                        xively.Datastream(id='radiator', current_value=radiator, at=now),
                ]
                        feed.update()
                        time.sleep(1000)
        except KeyboardInterrupt:
                grovepi.digitalWrite(relay,0)
                grovepi.digitalWrite(led1,0)
                radiator = "OFF"
                print ("  except keyboard_interrupt "  + radiator)
		setRGB(0,128,64)
                setRGB(0,255,0)
                setText("except keyboard_interrupt")
		feed.datastreams = [
                xively.Datastream(id='radiator', current_value=radiator, at=now),
                ]
                feed.update()
                break
        except:
                grovepi.digitalWrite(led1,0)
                grovepi.digitalWrite(relay,0)
                radiator = "OFF"
                print (" except false" + radiator)
		setRGB(0,128,64)
                setRGB(0,255,0)
                setText("except error")
                feed.datastreams = [
                xively.Datastream(id='radiator', current_value=radiator, at=now),
                ]
                feed.update()
		os.system('systemctl restart myscript.service')
		break

grovepi.digitalWrite(relay,0)
grovepi.digitalWrite(led1,0)


