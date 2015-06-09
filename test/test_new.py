import unittest
from xshop import new
import os
import shutil

class TestFileExists(unittest.TestCase):
	def setUp(self):
		os.mkdir('new-test')

	def test(self):
		with self.assertRaises(OSError):
			new.new_test_project('new-test')
		with self.assertRaises(OSError):
			new.new_build_project('new-test')

	def tearDown(self):
		shutil.rmtree('new-test')

if __name__ == '__main__':
	unittest.main()
