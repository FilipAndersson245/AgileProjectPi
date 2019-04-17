import unittest
import time
import socket
import _thread
import httpPostTest as post
from fona import Fona 

class TestGPS(unittest.TestCase):
	
	def testReset(self):
		"""
		Test reset power sequence
		"""
		self.assertEqual(Fona().FonaReset(), 0, "Reset failed\n")
		
	def testLocation(self):
		""" 
		Test to request location and validate coordinates
		"""
		coordinates = [12345, 12345]
		result = Fona().GetLocation()
		self.assertEqual(result, coordinates)
		print("Location passed")

	def testLongDurationLocation(self):
		""" 
		Test if location is static for a long duration (1 hour)
		Polls location every 1 min
		"""
		duration = 60
		origin = Fona().GetLocation()
		
		while duration > 0:
			time.sleep(60)
			check = Fona().GetLocation()
			self.assertEqual(check, origin)

class testHTTP(unittest.TestCase):

	def testPost(self):
		"""
		Test HTTP post request code 
		"""
		sockS = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
		sockS.bind(('127.0.0.1', 60006))
		sockS.listen(1)

		print('Listening...\n')
		(sockC, addr) = sockS.accept()
		print('Connection from {}' .format(addr))

		clientData = sockC.recv(1024)
		clientDataDecoded = clientData.decode('ascii')
		print('Post Receive test:\n')
		print(clientDataDecoded)
		time.sleep(1)
		sockC.sendall(bytearray("HTTP/1.1 200 ok\n", "ASCII"))
		sockC.sendall(bytearray("\n", "ASCII"))
		sockC.sendall(bytearray("200\n", "ASCII"))

		sockC.close()

	def runTest(self):   
		_thread.start_new_thread(testHTTP().testPost, ())
		print("Thread 1 started")
		_thread.start_new_thread(post.clientsidePost, ())
		print("Thread 2 started")



		
if __name__ == '__main__':
	# unittest.main()
	#TestGPS().testReset()
	#Fona().FonaInit()
	#TestGPS().testLocation()
	testHTTP().runTest()
	print("Everything passed")