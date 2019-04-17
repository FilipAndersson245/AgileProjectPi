import unittest

from fona import Fona

class TestGPS(unittest.TestCase):
	def testReset(self):
		"""
		Test reset power sequence
		"""
		self.assert_(Fona.FonaReset())
		
	def testLocation(self):
		""" 
		Test to request location and validate coordinates
		"""
		coordinates = [12345, 12345]
		result = Fona.GetLocation()
		self.assertEqual(result, coordinates)
		print("Location passed")
		
if __name__ == '__main__':
	# unittest.main()
	TestGPS.testReset()
	TestGPS.testLocation()
	print("Everything passed")