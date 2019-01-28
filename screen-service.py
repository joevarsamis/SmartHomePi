import time,sys
import xively
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
grovepi.pinMode(led2,"OUTPUT")
while True:
        try:
                now = datetime.datetime.utcnow()
                # unit initialization
                sound=int(grovepi.analogRead(1)/10.24)
                s = str(int(grovepi.analogRead(1)/10.24))
                light=int(grovepi.analogRead(0)/10.24)
                l = str(int(grovepi.analogRead(0)/10.24))
                [temp,humidity] = grovepi.dht(sensor,blue)
                # print in dos and screen
                grovepi.digitalWrite(led2,1)
                print((temp - 1),humidity,light,sound)
                setRGB(0,128,64)
                setRGB(0,255,0)
                setText("Temp:" + str(int(temp-1)) + " Hum:" + str(int(humidity)) + "%" + '\n' + "Snd:" + s + " Light:" + l)
                feed.datastreams = [
                        xively.Datastream(id='temp', current_value=temp-1, at=now),
                        xively.Datastream(id='humidity', current_value=humidity, at=now),
                        xively.Datastream(id='light', current_value=light, at=now),
                        xively.Datastream(id='sound', current_value=sound, at=now),
                ]
                feed.update()
                time.sleep(63)
        except KeyboardInterrupt:
                setRGB(0,128,64)
                setRGB(0,255,0)
                setText("Bye Bye Joe")
                break
        except:
               print("Error")
