import unittest
from xshop import new
import os
import shutil

class TestFileExists(unittest.TestCase):
	def setUp(self):
		os.mkdir('new-test')

	def test(self):
		with self.assertRaises(OSError):
			new.new_test_project('hello','new-test')

	def tearDown(self):
		shutil.rmtree('new-test')

#
#	Test structure of new projects and that config file
#	is correct.
#
class TestSuccess(unittest.TestCase):
	def test(self):
		new.new_test_project('hello','new-test')
		
		self.assertTrue(os.path.isdir('new-test'))
		self.assertTrue(os.path.isdir('new-test/containers'))	
		self.assertTrue(os.path.isdir('new-test/containers/target'))	
		self.assertTrue(os.path.isdir('new-test/containers/attacker'))
		self.assertTrue(os.path.isdir('new-test/test'))	
		
		self.assertTrue(os.path.isfile("new-test/docker-compose.yml"))	
		self.assertTrue(os.path.isfile("new-test/test/xshop_test.py"))	
		self.assertTrue(os.path.isfile("new-test/containers/attacker/Dockerfile"))	
		self.assertTrue(os.path.isfile("new-test/containers/target/Dockerfile"))	
	
		self.assertTrue(os.path.isfile('new-test/config.yaml'))

	def tearDown(self):
		shutil.rmtree('new-test')

if __name__ == '__main__':
	unittest.main()
