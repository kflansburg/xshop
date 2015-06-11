import unittest
from xshop import dockerw
from xshop import exceptions
import os
import shutil
import logging

p = os.path.dirname(os.path.realpath(dockerw.__file__))+"/defaults/contexts/"

#
#	Test if context folder is missing
#
class TestBuildImageMissingContext(unittest.TestCase):
	def test(self):
		logging.basicConfig(filename='test.log',level=logging.DEBUG)
		with self.assertRaises(IOError):
			dockerw.build_image('null_context')

#
#	Test if no Dockerfile in context
#
class TestBuildImageMissingDockerfile(unittest.TestCase):
	def setUp(self):
		os.mkdir(p+"test_image")
	
	def test(self):
		logging.basicConfig(filename='test.log',level=logging.DEBUG)
		with self.assertRaises(IOError):
			dockerw.build_image('test_image')

	def tearDown(self):
		shutil.rmtree(p+'test_image')

#
#	Test a good build
#
class TestBuildImageGood(unittest.TestCase):
	def setUp(self):
		os.mkdir(p+"test_image")
		f = open(p+"test_image/Dockerfile",'w')
		f.write("FROM debian:stable")
		f.close()	
	def test(self):
		logging.basicConfig(filename='test.log',level=logging.DEBUG)
		self.assertFalse(dockerw.build_image('test_image'))

	def tearDown(self):
		shutil.rmtree(p+'test_image')	

#
#	Test if there is an error during the build process
#
class TestBuildImageBuildError(unittest.TestCase):
	def setUp(self):
		os.mkdir(p+"test_image")
		f = open(p+"test_image/Dockerfile",'w')
		f.write("FROM debian:stable\napt-get -y install python")
		f.close()	
	def test(self):
		logging.basicConfig(filename='test.log',level=logging.DEBUG)
		with self.assertRaises(exceptions.DockerError):
			dockerw.build_image('test_image')

	def tearDown(self):
		shutil.rmtree(p+'test_image')		
		os.remove('test.log')

if __name__ == '__main__':
	unittest.main()
