import serial
import time
from fona import Fona

serialport = serial.Serial('/dev/ttyS0', baudrate=115200, 
								timeout=1,
								parity=serial.PARITY_NONE,
								stopbits=serial.STOPBITS_ONE,
								bytesize=serial.EIGHTBITS
								)


serialport.write(b'AT+CMTE?\r')
rcv = serialport.read(100)
print(rcv.decode('ASCII'))
if rcv.decode('ASCII') == 'OK':
    print('GSM: OK')

time.sleep(3)
serialport.write(b'AT+CGPSPWR=1\r')
rcv = serialport.read(100)
if rcv.decode('ASCII') == 'OK':
    print('GPS POWER ON: OK')
else:
    print(rcv.decode('ASCII'))
time.sleep(3)
while True:
    serialport.write(b'AT+CGPSSTATUS?\r')
    rcv = serialport.read(100)
    time.sleep(0.1)
    print(rcv.decode('ASCII'))


