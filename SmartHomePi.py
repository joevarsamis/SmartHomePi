import time,sys
import xively
import grovepi
import datetime
import os



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
XIVELY_API_KEY = "TiHw3RkV3yTES7UsJl2zC8670CRAQq1HKcRaTZeAXFRD23JE"
XIVELY_FEED_ID = "1767457191"
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
setText("----Welcome----")
time.sleep(3)
while True:
        try:
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
                time.sleep(30)
                [temp2,humidity] = grovepi.dht(sensor,blue)
                print ("temp2", temp2 - 1.5)
                time.sleep(30)
                [temp3,humidity] = grovepi.dht(sensor,blue)
                print ("temp3", temp3 - 1.5)
		[temp4,humidity] = grovepi.dht(sensor,blue)
		time.sleep(30)
                print ("temp4", temp4 - 1.5)
		time.sleep(5)
                temp = round(((temp1-1.5)+(temp2-1.5)+(temp3-1.5)+(temp4-1.5))/4,1)
                print ("temp", temp)
                if (temp) < 21 :
                        grovepi.digitalWrite(relay,1)
                        grovepi.digitalWrite(led1,1)
                        radiator = "ON"
                        print (radiator,st)
			setRGB(0,128,64)
                	setRGB(0,255,0)
                	setText("Temperature:" + str(temp) + '\n' "Humidity:" + str(int(humidity)) + "%")
			feed.datastreams = [
			xively.Datastream(id='light', current_value=light, at=now),
                        xively.Datastream(id='sound', current_value=sound, at=now),
                        xively.Datastream(id='temp', current_value=temp, at=now),
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
			setRGB(0,128,64)
                        setRGB(0,255,0)
                        setText("Temperature:" + str(temp) + '\n' "Humidity:" + str(int(humidity)) + "%")
			feed.datastreams = [
			xively.Datastream(id='light', current_value=light, at=now),
                        xively.Datastream(id='sound', current_value=sound, at=now),
                        xively.Datastream(id='temp', current_value=temp, at=now),
                        xively.Datastream(id='humidity', current_value=humidity, at=now),
                        xively.Datastream(id='radiator', current_value=radiator, at=now),
                ]
                        feed.update()
                        time.sleep(1000)
        except KeyboardInterrupt:
                grovepi.digitalWrite(led1,0)
                grovepi.digitalWrite(relay,0)
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
		os.system('systemctl restart relay.service')


