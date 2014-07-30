import random
import unittest
# from geoserver.geoserver import Geoserver


class TestGeosever(unittest.TestCase):

    def setUp(self):
        self.seq = range(10)

    def test_shuffle(self):
        # make sure the shuffled sequence does not lose any elements
        random.shuffle(self.seq)
        self.seq.sort()
        self.assertEqual(self.seq, range(10))

if __name__ == '__main__':
    unittest.main()
