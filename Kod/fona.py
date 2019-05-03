import time
import serial
from serial import SerialException
import RPi.GPIO as GPIO

SIM808_RESET_Pin = 15
SIM808_STATUS_Pin = 12

ser = serial.Serial('/dev/ttyserial0', baudrate=115200, 
								timeout=0.5,
								parity=serial.PARITY_NONE,
								stopbits=serial.STOPBITS_ONE,
								bytesize=serial.EIGHTBITS
								)

class Fona:

	###################
	# Device handling #
	###################
	def FonaReset(self):
		# Reboot sequence
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(SIM808_RESET_Pin, GPIO.OUT, initial=0)
		GPIO.setup(SIM808_STATUS_Pin, GPIO.IN)

		GPIO.output(SIM808_RESET_Pin, GPIO.HIGH)
		time.sleep(10/1000) # 10 ms
		GPIO.output(SIM808_RESET_Pin, GPIO.LOW)
		time.sleep(100/1000) # 100 ms
		GPIO.output(SIM808_RESET_Pin, GPIO.HIGH)

		duration = 7
		# 7 seconds to boot
		while (GPIO.input(SIM808_STATUS_Pin) == GPIO.LOW):	
			time.sleep(0.1)
			duration -= 0.1
			if duration == 0:
				print ("Reset timeout")
				return -1
		
		print ("Reboot success")

		return 0
		
	def FonaInit(self):
		# Serial Init
		try :
			ser = serial.Serial('/dev/ttyserial0', baudrate=115200, 
								timeout=0.5,
								parity=serial.PARITY_NONE,
								stopbits=serial.STOPBITS_ONE,
								bytesize=serial.EIGHTBITS
								)
		except ValueError:
			print (ValueError)
			return -2
		except SerialException:
			print (SerialException)
			return -3

						
		time.sleep(1)
		
		# Reset device
		return self.FonaReset()

	###################
	# Serial handling #
	###################
	def FonaWrite(self, command):
		ser.write(command.encode() + b'\r')

	def FonaWriteVerify(self, command):
		self.FonaWrite(command)
		ret = self.FonaReadResponse()
		if ret == "ERROR":
			print("Error in response: " + ret)
			return -1
		elif ret == "OK":
			return 0

	def FonaWriteRetry(self, command):
		while True:
			if self.FonaWriteVerify == 0:
				break

	def FonaReadResponse(self, bytes=100): # Response format <CR><LF><Response><CR><LF>
		response = ser.read(bytes) # Read up to 100 bytes or until LF with 0.5 sec timeout
		return response.replace(b"\r", b"").replace(b"\n", b"") # Remove <CR><LF>

	def FonaReadResponseLine(self):
		response = ser.read_until(100) # Read up to 100 bytes or until LF with 0.5 sec timeout
		return response.replace(b"\r", b"").replace(b"\n", b"") # Remove <CR><LF>
		
	################
	# GPS handling #
	################
	def EnableGPS(self):
		self.FonaWrite('AT+CGPSPWR=1')
		ret = self.FonaReadResponse()
		if ret == "ERROR":
			return -1
		elif ret == "OK":
			return 0
	
	def DisableGPS(self):
		self.FonaWrite('AT+CGPSPWR=0')
		ret = self.FonaReadResponseLine()
		if ret == "ERROR":
			return -1
		elif ret == "OK":
			return 0

	def GetGpsStatus(self):
		self.FonaWrite('AT+CGPSSTATUS?')
		response = self.FonaReadResponseLine()

		if response == "Location Unknown":
			return 0
		elif response == "Location Not Fix":
			return 1
		elif response == "Location 2D Fix":
			return 2
		elif response == "Location 3D Fix":
			return 3
		
	def GetLocation(self):
		self.FonaWrite('AT+CGPSINF=0')
		location = [0, 0]
		response = self.FonaReadResponseLine().split(",")
		location[0] = response[1]
		location[1] = response[2]
		return location

	def GetPowerControl(self):
		self.FonaWrite('AT+CGPSPWR?')
		response = self.FonaReadResponse()

	
	def EnableGPSNMEA(self, nmea):
		return self.FonaReadResponse()
		
	################
	# GSM handling #
	################

	def EnablePhone(self):
		return self.FonaWriteVerify('AT+CFUN=1')

	def DisablePhone(self):
		return self.FonaWriteVerify('AT+CFUN=0')

	def EnableGPRS(self):
		return self.FonaWriteVerify('AT+CGATT=1')

	def DisableGPRS(self):
		return self.FonaWriteVerify('AT+CGATT=0')

	def CheckPinReQ(self):
		self.FonaWrite('AT+CPIN?')
		if self.FonaReadResponse() == "+CPIN: READY":
			if self.FonaReadResponse() == "OK":
				return 0
		else:
			print("Error: Pin required")
			return -1

	def StartTask(self, apn, user, pwd):
		return self.FonaWriteVerify('AT+CSTT="' + apn + '","' + user + '","' + pwd + '"')

	def CheckTask(self, apn, user, pwd):
		self.FonaWrite('AT+CSTT?')
		ret = self.FonaReadResponse()
		if ret != 'AT+CSTT: "' + apn + '","' + user + '","' + pwd + '"':
			return -1
		else:
			return 0

	def ConnectGPRS(self):
		return self.FonaWriteVerify('AT+CIICR')

	def GetLocalIP(self):
		self.FonaWrite('AT+CIFSR')
		if self.FonaReadResponse() == "ERROR":
			return -1
		else:
			return self.FonaReadResponse()

	def OpenConnection(self, mode, ip_or_domain, port):
		self.FonaWrite('AT+CIPSTART="' + mode + '","' + ip_or_domain + '",' + port)
		ret = self.FonaReadResponse()
		if ret != "OK":
			return -1
		else:
			ret = self.FonaReadResponse()
			if ret == "ALREADY CONNECT":
				return 1
			elif ret == "CONNECT OK": 
				return 0
			elif ret == "CONNECT FAIL":
				return -1

	def FonaSendData(self, data, size):
		self.FonaWrite('AT+CIPSEND=' + size)
		ret = self.FonaReadResponse()
		if ret == ">":
			self.FonaWrite(data)
			ret = self.FonaReadResponse()
			if ret == "SEND FAIL":
				return -1
			elif ret == "SEND OK": 
				return 0
		elif "ERROR" in ret:
			return -1

	def FonaDataResponse(self):
		line = ""
		response = ""

		line = self.FonaReadResponse()
		while line != None:
			response = response + '\n' + line
			line = self.FonaReadResponse()

	

	def GprsInit(self, apn="online.telia.se"):
		if self.EnableGPRS() != 0:
			return -1
		self.FonaWriteVerify('AT+SAPBR=3,1,"CONTYPE","GPRS"')
		self.FonaWriteVerify('AT+SAPBR=3,1,"APN","' + apn + '"')
		self.FonaWriteVerify('AT+SAPBR=1,1')

		return 0

	#################
	# HTTP handling #
	#################

	def HttpInit(self, url, content, userdata):
		self.FonaWriteVerify('AT+HTTPINIT')
		self.FonaWriteVerify('AT+HTTPPARA="CID",1')
		self.FonaWriteRetry('AT+HTTPPARA="URL","' + url + '"')
		self.FonaWriteRetry('AT+HTTPPARA="CONTENT","' + content + '"')
		self.FonaWriteRetry('AT+HTTPPARA="USERDATA","' + userdata + '"')
		return 0

	def HttpGetPost(self):
		self.FonaWriteVerify('AT+HTTPACTION=1')
		ret = self.FonaReadResponse()
		if "HTTPACTION" and "200" in ret:
			self.FonaWrite("AT+HTTPREAD")
			ret = self.FonaReadResponseLine()
			print(ret)
			post = self.FonaReadResponseLine()
			print(post)
			ret = self.FonaReadResponseLine()
			print(ret)
			return post
		print("HTTP Get POST Failed")
		return -1
		