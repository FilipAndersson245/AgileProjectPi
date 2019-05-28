import serial
import time
from gantry import Gantry
import RPi.GPIO as GPIO

FIX_LED_Pin = 7
ON_BTN_Pin = 11

time.sleep(4)

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(FIX_LED_Pin, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(ON_BTN_Pin, GPIO.OUT, initial=GPIO.HIGH)

gsm_Port = '/dev/ttyS0'
gsm_Baud = 115200
gsm_Timeout = 5

gps_Port = '/dev/ttyUSB0'
gps_Baud = 9600
gps_Timeout = 0.5

def SendCoord():
    # Get coordinates from GPS
    position = gantry.NmeaGetLocation()
    gantry.Debug("Location: " + position)
    if position == "No fix":
        GPIO.output(FIX_LED_Pin, GPIO.LOW)
        return
    GPIO.output(FIX_LED_Pin, GPIO.HIGH)
    position = position.split(",")
    
    lat_dd = int(float(position[0])/100)
    lat_mm = float(position[0]) - (lat_dd * 100)
    lat_dec = lat_dd + lat_mm/60

    lon_dd = int(float(position[1])/100)
    lon_mm = float(position[1]) - (lon_dd * 100)
    lon_dec = lon_dd + lon_mm/60

    strlat = "{:.6f}".format(lat_dec)
    strlon = "{:.6f}".format(lon_dec)
    position = strlat + "," + strlon

    # Send to API
    gantry.HttpSendPost('{"position": [' + position + ']}')
    #gantry.HttpGetPostResponse()

def CheckSend():
    if gantry.HttpVerifySend() == 0:
        gantry.Debug("Send OK")
    else:
        gantry.Debug("Send failed")

def ErrorFlash():
    while True:
        GPIO.output(FIX_LED_Pin, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(FIX_LED_Pin, GPIO.LOW)
        time.sleep(0.5)

def SleepMinutes(minutes):
    time.sleep(minutes*60)


gantry = Gantry()

if gantry.GsmSerialInit() < 0:
    ErrorFlash()
if gantry.GpsSerialInit() < 0:
    ErrorFlash()
gantry.Debug("SerialInit complete")

gantry.FonaWriteVerify('ATE0')
gantry.Debug("Echo off complete")
gantry.CheckDevice()
gantry.EnableGPRS()
gantry.Debug("Enable GPRS complete")
gantry.GprsInit("online.telia.se")
gantry.Debug("GprsInit complete")
gantry.HttpInit(url="http://agileserver-env.yttgtpappn.eu-central-1.elasticbeanstalk.com/gantries/AAAABBBBCCCC",
                content="application/json",
                userdata="authorization: weH6fcv+Se1anMqdtwzn2/MxtSmy4aMK1/E0u5gXdrF7uWgshJoORVNSSV236ONbX+kQ6YiqhNOL3HT5DFYLOA")
gantry.Debug("HttpInit complete")

gantry.FonaReadResponseLine()

while True:
    # Send coordinates to API
    SendCoord()

    # Check send valid
    gantry.HttpVerifySend()

    # Sleep for 20 min
    time.sleep(10)



