import serial
import time
from gantry import Gantry

HTTP_List = ['AT+CMGF=1\r', 'AT+CGATT=1\r', 'AT+SAPBR=3,1,"CONTYPE","GPRS"\r', 'AT+SAPBR=3,1,"APN","online.telia.se"\r',
             'AT+SAPBR=1,1\r', 'AT+HTTPINIT\r', 'AT+HTTPPARA="CID",1\r', 'AT+HTTPPARA="URL","http://agileserver-env.yttgtpappn.eu-central-1.elasticbeanstalk.com/gantries/abc123"\r',
             'AT+HTTPPARA="CONTENT","application/json"\r', 'AT+HTTPPARA="USERDATA","authorization: Bearer fhsakdjhjkfds"\r',
             'AT+HTTPACTION=1\r', 'AT+HTTPREAD\r', 'AT+HTTPTERM\r', 'AT+SAPBR=0,1\r']

# HTTP_List CONTENT
# 0: 'AT+CMGF=1\r'
# 1: 'AT+CGATT=1\r'
# 2: 'AT+SAPBR=3,1,"CONTYPE","GPRS"\r'
# 3: 'AT+SAPBR=3,1,"APN","online.telia.se"\r'
# 4: 'AT+SAPBR=1,1\r'
# 5: 'AT+HTTPINIT\r'
# 6: 'AT+HTTPPARA="CID",1\r'
# 7: 'AT+HTTPPARA="URL","http://agileserver-env.yttgtpappn.eu-central-1.elasticbeanstalk.com/gantries/abc123"\r'
# 8: 'AT+HTTPPARA="CONTENT","application/json"\r'
# 9: 'AT+HTTPPARA="USERDATA","authorization: Bearer fhsakdjhjkfds"\r'
# 10: 'AT+HTTPACTION=1\r'
# 11: 'AT+HTTPREAD\r'
# 12: 'AT+HTTPTERM\r'
# 13: 'AT+SAPBR=0,1\r'

### SEND DATA TO SERVER ###
#AT+HTTPDATA=21,10000
#DOWNLOAD
#        //SEND DATA OF 21 CHARS IN THIS SECTION {"position": [54,44]}
#OK

position = "22,33"

def SendCoord():
    #position = gantry.GetLocation()
    gantry.HttpSendPost('{"position": [' + position + ']}')


def SleepMinutes(minutes):
    time.sleep(minutes*60)

gantry = Gantry()

gantry.FonaInit()
print("FonaInit complete")
gantry.FonaWriteVerify('ATE0')
print("Echo off complete")
gantry.FonaWriteVerify("AT+CPIN=1786")

for i in range (10):
    gantry.FonaReadResponseLine()

gantry.EnableGPRS()
print("Enable GPRS complete")
gantry.GprsInit("4G.tele2.se")
print("GprsInit complete")
gantry.HttpInit(url="http://agileserver-env.yttgtpappn.eu-central-1.elasticbeanstalk.com/gantries/AAAABBBBCCCC",
                content="application/json",
                userdata="authorization: weH6fcv+Se1anMqdtwzn2/MxtSmy4aMK1/E0u5gXdrF7uWgshJoORVNSSV236ONbX+kQ6YiqhNOL3HT5DFYLOA")
print("HttpInit complete")
SendCoord()
print("SendCoord complete")
gantry.FonaReadResponseLine()
while True:
    # Send coordinates to API

    gantry.HttpGetPostResponse()

    # Sleep for 20 min
    time.sleep(10)



