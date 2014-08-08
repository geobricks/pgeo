import unittest
from pgeo.gis import geocoding


class GeoCodingTestClass(unittest.TestCase):

    def test_get_location(self):
        location = geocoding.get_location("FAO, rome")
        self.assertAlmostEqual(41.8824862, location.latitude)
        self.assertAlmostEqual(12.4884563824, location.longitude)

if __name__ == '__main__':
    unittest.main()
