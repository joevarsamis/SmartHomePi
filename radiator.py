#!/usr/bin/env python
import time,sys
import xively,os
import grovepi
import datetime

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

#XIVELY API
XIVELY_API_KEY = "TiHw3RkV3yTES7UsJl2zC8670CRAQq1HKcRaTZeAXFRD23JE"
XIVELY_FEED_ID = "1767457191"
api = xively.XivelyAPIClient(XIVELY_API_KEY)
feed = api.feeds.get(XIVELY_FEED_ID)
now = datetime.datetime.utcnow()
# Connect the Grove Relay to digital port D3
# SIG,NC,VCC,GND
sensor = 4
blue = 0
relay = 3
ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
grovepi.pinMode(relay,"OUTPUT")
led1 = 2
os.system('sudo systemctl stop relay.service')
while True:
    try:
        # switch on
        grovepi.digitalWrite(relay,1)
	grovepi.digitalWrite(led1,1)
	[temp,humidity] = grovepi.dht(sensor,blue)
    	radiator_remote = "ON"
	setRGB(0,128,64)
	setRGB(0,255,0)
	setText("Activated Since"+"\n" + st )
        feed.datastreams = [
	xively.Datastream(id='temp', current_value=temp, at=now),
        xively.Datastream(id='radiator_remote', current_value=radiator_remote, at=now),
        ]
	print ("on since:")
	print (st)
        feed.update()
	time.sleep(1800)
	grovepi.digitalWrite(relay,0)
        grovepi.digitalWrite(led1,0)
        radiator_remote = "OFF"
	time.sleep(5)
        feed.datastreams = [
        xively.Datastream(id='radiator_remote', current_value=radiator_remote, at=now),
        ]
        feed.update()
        os.system('sudo systemctl start relay.service')
	sys.exit()
    except KeyboardInterrupt:
        grovepi.digitalWrite(relay,0)
	grovepi.digitalWrite(led1,0)
	radiator_remote = "OFF"
        feed.datastreams = [
        xively.Datastream(id='radiator_remote', current_value=radiator_remote, at=now),
        ]
        feed.update()
	os.system('sudo systemctl start relay.service')
	break
    except IOError:
        print ("Error")
	grovepi.digitalWrite(led1,0)
        grovepi.digitalWrite(relay,0)
	radiator_remote = "OFF"
        feed.datastreams = [
        xively.Datastream(id='radiator_remote', current_value=radiator_remote, at=now),
        ]
        feed.update()
	os.system('sudo systemctl start relay.service')
