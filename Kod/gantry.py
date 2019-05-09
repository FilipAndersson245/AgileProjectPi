import time
import serial
from serial import SerialException
import RPi.GPIO as GPIO

SIM808_RESET_Pin = 15
SIM808_STATUS_Pin = 12

serialGSM = serial.Serial('/dev/ttyS0', baudrate=115200, 
								timeout=0.5,
								parity=serial.PARITY_NONE,
								stopbits=serial.STOPBITS_ONE,
								bytesize=serial.EIGHTBITS
								)

"""serialGPS = serial.Serial('/dev/ttyUSB0', baudrate=9600, 
								timeout=0.5,
								parity=serial.PARITY_NONE,
								stopbits=serial.STOPBITS_ONE,
								bytesize=serial.EIGHTBITS
								)"""

class Gantry:

	########################
	# FONA Device handling #
	########################
	def FonaReset(self):

		return 0
		
	def FonaInit(self):
		# Serial Init
		try :
			serialGSM = serial.Serial('/dev/ttyS0', baudrate=115200, 
								timeout=5,
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
		#eturn self.FonaReset()

	###################
	# Serial handling #
	###################
	def FonaWrite(self, command):
		serialGSM.write(command.encode() + b'\r')
		print(command)
		time.sleep(1)

	def FonaWriteVerify(self, command):
		self.FonaWrite(command)
		ret = self.FonaReadResponseLine()
		#print("WriteVerify: " + command + ", Response: " + ret)
		if ret == "ERROR":
			print("Error in response: " + ret)
			return -1
		elif ret == "OK":
			return 0

	def FonaWriteRetry(self, command):
		retries = 0
		while True:
			if retries >= 3:
				return -1
			ret = self.FonaWriteVerify(command)
			if ret == 0:
				return 0
			else:
				print("Command: " + command + " failed, retrying...")
				retries += 1
			time.sleep(0.5)

	def FonaReadResponse(self, bytes=500): # Response format <CR><LF><Response><CR><LF>
		response = serialGSM.read(bytes) # Read up to 100 bytes or until LF with 0.5 sec timeout
		response = response.replace(b"\r", b"").replace(b"\n", b"") # Remove <CR><LF>
		print(response)
		return response

	def FonaReadResponses(self, bytes=500): # Response format <CR><LF><Response><CR><LF>
		response = serialGSM.read(bytes) # Read up to 100 bytes or until LF with 0.5 sec timeout
		response = response.replace(b"\r", b"").replace(b"\n", b"") # Remove <CR><LF>
		print(response)
		response = serialGSM.read(bytes) # Read up to 100 bytes or until LF with 0.5 sec timeout
		response = response.replace(b"\r", b"").replace(b"\n", b"") # Remove <CR><LF>
		print(response)
		return response

	def FonaReadResponseLine(self, terminator='\n', size=500):
		# Eat <CR><LF>
		#serialGSM.read_until(terminator=terminator, size=size)
		response = serialGSM.read_until(terminator=terminator, size=size) # Read up to 100 bytes or until LF with 0.5 sec timeout
		print(response)
		response = response.replace(b"\r", b"").replace(b"\n", b"") # Remove <CR><LF>
		response = response.decode()
		#print(response)
		return response
		
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
		#response = serialGPS.readlines(10)
		#print(response)
		#response = self.FonaReadResponseLine().split(",")
	""" location[0] = response[1]
		location[1] = response[2]
		return location """

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
		#while line != None:
			#response = response + bytes('\n') + line
		line = self.FonaReadResponse()

	

	def GprsInit(self, apn="online.telia.se"):
		""" if self.EnableGPRS() != 0:
			return -1 """
		self.FonaWriteRetry('AT+SAPBR=3,1,"CONTYPE","GPRS"')
		self.FonaWriteRetry('AT+SAPBR=3,1,"APN","' + apn + '"')
		self.FonaWriteRetry('AT+SAPBR=1,1')

		return 0

	def GprsClose(self):
		self.FonaWrite('AT+SAPBR=0,1')

	#################
	# HTTP handling #
	#################

	def HttpInit(self, url, content, userdata):
		self.FonaWriteRetry('AT+HTTPINIT')
		self.FonaWriteVerify('AT+HTTPPARA="CID",1')
		self.FonaWriteVerify('AT+HTTPPARA="URL","' + url + '"')
		self.FonaWriteVerify('AT+HTTPPARA="CONTENT","' + content + '"')
		self.FonaWriteVerify('AT+HTTPPARA="USERDATA","' + userdata + '"')
		return 0

	def HttpSendPost(self, post):
		size = len(post)
		print(size)
		self.FonaWrite('AT+HTTPDATA=' + str(size) + ',10000')
		ret = self.FonaReadResponseLine()
		if ret == "DOWNLOAD":
			self.FonaWrite(post)
			ret = self.FonaReadResponseLine()
		else:
			print("Post fail")
			return -1
		print("Data done")

	def HttpGetPostResponse(self):
		ret = ""

		self.FonaWrite('AT+HTTPACTION=1')
	
		# Read OK
		ret = self.FonaReadResponse(6)
		# Read response
		ret = self.FonaReadResponseLine()
		if "HTTPACTION" and "200" in ret:
			self.FonaWrite("AT+HTTPREAD")
			ret = self.FonaReadResponseLine()
			post = self.FonaReadResponseLine()
			ret = self.FonaReadResponseLine()
			return post
	
		print("HTTP Get POST Failed")
		ret = self.FonaReadResponseLine()
		print(ret)
		return -1
		
	def HttpTerminate(self):
		self.FonaWrite('AT+HTTPTERM')
	
	def HttpReadResponse(self):
		self.FonaWriteVerify('AT+HTTPREAD')


		
