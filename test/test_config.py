import unittest
from xshop import config
import os
import shutil

class TestFileExists(unittest.TestCase):
	def setUp(self):
		os.mkdir('config_test')
		os.chdir('config_test')
		f = open('.config','w')
		f.write("foobar")
		f.close()

	def test(self):
		self.assertTrue(config.check())

	def tearDown(self):
		os.chdir("..")
		shutil.rmtree("config_test")

class TestFileMissing(unittest.TestCase):
	def setUp(self):
		os.mkdir('config_test')
		os.chdir('config_test')

	def test(self):
		self.assertFalse(config.check())

	def tearDown(self):
		os.chdir("..")
		shutil.rmtree("config_test")

class TestConfigNoConfig(unittest.TestCase):
	def setUp(self):
		os.mkdir('config_test')
		os.chdir('config_test')

	def test(self):
		config.Config()
		f = open('.config','r')
		self.assertEqual(f.read(),'{}')
		f.close()

	def tearDown(self):
		os.chdir("..")
		shutil.rmtree("config_test")

class TestConfigConfig(unittest.TestCase):
	def setUp(self):
		os.mkdir('config_test')
		os.chdir('config_test')
		f=open('.config','w')
		f.write('{"foo": "bar"}')
		f.close()

	def test(self):
		config.Config()
		f = open('.config','r')
		self.assertEqual(f.read(),'{"foo": "bar"}')
		f.close()

	def tearDown(self):
		os.chdir("..")
		shutil.rmtree("config_test")

class TestConfigGet(unittest.TestCase):
	def setUp(self):
		os.mkdir('config_test')
		os.chdir('config_test')
		f=open('.config','w')
		f.write('{"foo": "bar"}')
		f.close()

	def test(self):
		c=config.Config()
		self.assertEqual(c.get('foo'),'bar')

	def tearDown(self):
		os.chdir("..")
		shutil.rmtree("config_test")

class TestConfigPut(unittest.TestCase):
	def setUp(self):
		os.mkdir('config_test')
		os.chdir('config_test')

	def test(self):
		config.Config().put('foo','bar')
		f = open('.config','r')
		self.assertEqual(f.read(),'{"foo": "bar"}')
		f.close()

	def tearDown(self):
		os.chdir("..")
		shutil.rmtree("config_test")

if __name__ == '__main__':
	unittest.main()
