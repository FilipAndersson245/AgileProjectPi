import time, datetime
import serial
from serial import SerialException
import RPi.GPIO as GPIO

SIM808_RESET_Pin = 15
SIM808_STATUS_Pin = 12



class Gantry:

	serialGSM = serial.Serial()

	filename = datetime.datetime.now()
	f = open('../Log/' + str(filename)+'.log', 'w')
	f.close()

	###############
	# Debug print #
	###############
	def Debug(self, msg):
		self.f = open('../Log/' + str(self.filename)+'.log', 'a')
		print(msg)
		print(msg, file=self.f)
		self.f.close()


	########################
	# FONA Device handling #
	########################
	def FonaReset(self):

		return 0

	def GsmSerialInit(self, serialdevice='/dev/ttyS0', baud=115200, timeout=5):
		try :
			self.serialGSM = serial.Serial(serialdevice, baudrate=baud, 
								timeout=timeout,
								parity=serial.PARITY_NONE,
								stopbits=serial.STOPBITS_ONE,
								bytesize=serial.EIGHTBITS
								)
		except ValueError:
			self.Debug (ValueError)
			return -2
		except SerialException:
			self.Debug (SerialException)
			return -3

		time.sleep(1)

		return 0
		
	def GpsSerialInit(self, serialdevice='/dev/ttyUSB0', baud=9600, timeout=0.5):
		try :
			self.serialGPS = serial.Serial(serialdevice, baudrate=baud, 
								timeout=timeout,
								parity=serial.PARITY_NONE,
								stopbits=serial.STOPBITS_ONE,
								bytesize=serial.EIGHTBITS
								)
		except ValueError:
			self.Debug (ValueError)
			return -2
		except SerialException:
			self.Debug (SerialException)
			return -3
						
		time.sleep(1)
		
		return 0

	def CheckDevice(self):
		if self.FonaWriteVerify("AT") == -1:
			while True:
				self.Debug("GSM Device not found")
				time.sleep(10)
				if self.EnableGPRS() == 0:
					self.Debug("GSM Device Successfully connected")
					break

	###################
	# Serial handling #
	###################
	def FonaWrite(self, command):
		self.serialGSM.write(command.encode() + b'\r')
		self.Debug(command)
		time.sleep(1)

	def FonaWriteVerify(self, command):
		self.FonaWrite(command)
		ret = self.FonaReadResponseLine()
		#self.Debug("WriteVerify: " + command + ", Response: " + ret)
		if ret == "ERROR":
			self.Debug("Error in response: " + ret)
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
				self.Debug("Command: " + command + " failed, retrying...")
				retries += 1
			time.sleep(0.5)

	def FonaReadResponse(self, size=500): # Response format <CR><LF><Response><CR><LF>
		response = self.serialGSM.read(size) # Read up to 100 bytes or until LF with 0.5 sec timeout
		response = response.replace(b"\r", b"").replace(b"\n", b"") # Remove <CR><LF>
		response = response.decode()
		self.Debug(response)
		return response

	def FonaReadResponseLine(self, terminator=b'\n', size=500):
		# Eat <CR><LF>
		response = self.serialGSM.read_until(terminator=terminator, size=size)
		#self.Debug("Eaten: " + str(response))
		response = response + self.serialGSM.read_until(terminator=terminator, size=size) # Read up to 100 bytes or until LF with 0.5 sec timeout
		#self.Debug("Response: " + str(response))
		response = response.replace(b"\r", b"").replace(b"\n", b"") # Remove <CR><LF>
		response = response.decode()
		self.Debug(response)
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
		#self.Debug(response)
		#response = self.FonaReadResponseLine().split(",")
	""" location[0] = response[1]
		location[1] = response[2]
		return location """

	def GetPowerControl(self):
		self.FonaWrite('AT+CGPSPWR?')
		response = self.FonaReadResponse()

	
	def EnableGPSNMEA(self, nmea):
		return self.FonaReadResponse()

	def NmeaGetLocation(self):
		location = ""
		while True:
			line = self.serialGPS.read_until(terminator=b'\n')
			line = line.decode()
			#self.Debug(line)
			if "$GNGLL" in line:
				line = line.split(',')
				if line[6] == "V":
					return "No fix"
				latitude = line[1]
				longitude = line[3]
				if line[2] == "S":
					latitude = -latitude
				if line[4] == "W":
					longitude = -longitude
				location = latitude + "," + longitude
				break
		return location
		
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
			self.Debug("Error: Pin required")
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
		self.FonaWrite('AT+HTTPDATA=' + str(size) + ',100000')
		ret = self.FonaReadResponse()
		if "DOWNLOAD" in ret:
			self.FonaWrite(post)
			ret = self.FonaReadResponse()
		else:
			self.Debug("Post fail")
			return -1
		self.Debug("Data done")

	def HttpGetPostResponse(self):
		self.FonaWrite('AT+HTTPACTION=1')
	
	 	# ret = self.FonaReadResponse()
		# Read OK
		ret = self.FonaReadResponseLine()
		# Read response
		ret = self.FonaReadResponseLine()
		if "HTTPACTION" in ret:
			self.FonaWrite("AT+HTTPREAD")
			ret = self.FonaReadResponse()
			"""ret = self.FonaReadResponseLine()
			self.Debug("line1: " + ret)
			post = self.FonaReadResponseLine()
			self.Debug("line2: " + post)"""
			return ret
	
		self.Debug("HTTP Get POST Failed")
		"""ret = self.FonaReadResponseLine()
		self.Debug(ret)"""
		return -1

	def HttpVerifySend(self):
		self.FonaWrite('AT+HTTPACTION=1')
		# Read OK
		ret = self.FonaReadResponseLine()
		# Read response
		ret = self.FonaReadResponseLine()
		if "HTTPACTION" and "200" in ret:
			return 0
		else:
			return -1
		
	def HttpTerminate(self):
		self.FonaWrite('AT+HTTPTERM')
	
	def HttpReadResponse(self):
		self.FonaWriteVerify('AT+HTTPREAD')


		
