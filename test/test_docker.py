import unittest
from xshop import docker
import os
import shutil

p = os.path.dirname(os.path.realpath(docker.__file__))+"/defaults/contexts/"

class TestBuildImageMissingContext(unittest.TestCase):
	def test(self):
		with self.assertRaises(IOError):
			docker.build_image('null_context')

class TestBuildImageMissingDockerfile(unittest.TestCase):
	def setUp(self):
		os.mkdir(p+"test_image")
	
	def test(self):
		with self.assertRaises(IOError):
			docker.build_image('test_image')

	def tearDown(self):
		shutil.rmtree(p+'test_image')

class TestBuildImageGoodContext(unittest.TestCase):
	def setUp(self):
		os.mkdir(p+"test_image")
		f = open(p+"test_image/Dockerfile",'w')
		f.write("FROM debian:stable")
		f.close()	
	def test(self):
		self.assertFalse(docker.build_image('test_image'))

	def tearDown(self):
		shutil.rmtree(p+'test_image')		

if __name__ == '__main__':
	unittest.main()
