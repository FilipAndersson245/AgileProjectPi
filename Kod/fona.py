import time
import serial
import RPi.GPIO as GPIO

SIM808_RESET_Pin = 11
SIM808_STATUS_Pin = 12

ser = None

class Fona:

	###################
	# Device handling #
	###################
	def FonaReset(self):
		# Reboot sequence
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(SIM808_RESET_Pin, GPIO.OUT, initial=0)
		GPIO.output(SIM808_RESET_Pin, GPIO.HIGH)
		time.sleep(10)
		GPIO.output(SIM808_RESET_Pin, GPIO.LOW)
		time.sleep(100)
		GPIO.output(SIM808_RESET_Pin, GPIO.HIGH)

		# 7 seconds to boot
		while (GPIO.input(SIM808_STATUS_Pin) == GPIO.LOW):	
			time.sleep(0.1)

		return 0
		
	def FonaInit(self):
		# Serial Init
		ser = serial.Serial('/dev/ttyserial0', baudrate=115200, 
								timeout=0.5,
								parity=serial.PARITY_NONE,
								stopbits=serial.STOPBITS_ONE,
								bytesize=serial.EIGHTBITS
								)
						
		time.sleep(1)
		
		# Reset device
		self.FonaReset()

	###################
	# Serial handling #
	###################
	def FonaWrite(self, command):
		ser.write(command + '\r')

	def FonaReadResponse(self): # Response format <CR><LF><Response><CR><LF>
		response = ser.read(100) # Read up to 100 bytes with 0.5 sec timeout
		return response.replace("\r", "").replace("\n", "") # Remove <CR><LF>
		
	################
	# GPS handling #
	################
	def EnableGPS(self):
		self.FonaWrite('AT+CGPSPWR=1')
		if self.FonaReadResponse() == "ERROR":
			return -1
		elif self.FonaReadResponse() == "OK":
			return 0

	def GetGpsStatus(self):
		self.FonaWrite('AT+CGPSSTATUS?')
		response = self.FonaReadResponse()

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
		response = self.FonaReadResponse().split(",")
		location[0] = response[1]
		location[1] = response[2]
		return location
	
	def EnableGPSNMEA(self, nmea):
		return self.FonaReadResponse
		
			
