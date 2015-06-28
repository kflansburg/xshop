import unittest
from xshop import config
from xshop import exceptions
import os
import shutil

class TestFileMissing(unittest.TestCase):
	def setUp(self):
		os.mkdir('config_test')
		os.chdir('config_test')

	def test(self):
		with self.assertRaises(exceptions.ConfigError):
			config.Config()	

	def tearDown(self):
		os.chdir("..")
		shutil.rmtree("config_test")

class TestConfigConfig(unittest.TestCase):
	def setUp(self):
		os.mkdir('config_test')
		os.chdir('config_test')
		f=open('config.yaml','w')
		f.write('foo: bar\n')
		f.close()

	def test(self):
		config.Config()
		f = open('config.yaml','r')
		self.assertEqual(f.read(),'foo: bar\n')
		f.close()

	def tearDown(self):
		os.chdir("..")
		shutil.rmtree("config_test")

class TestConfigGet(unittest.TestCase):
	def setUp(self):
		os.mkdir('config_test')
		os.chdir('config_test')
		f=open('config.yaml','w')
		f.write('foo: bar\n')
		f.close()

	def test(self):
		c=config.Config()
		self.assertEqual(c.get('foo'),'bar')

	def tearDown(self):
		os.chdir("..")
		shutil.rmtree("config_test")

class TestGenerateConfig(unittest.TestCase):
	def setUp(self):
		os.mkdir('config_test')
		os.chdir('config_test')

	def test(self):
		config.generate_new_config()
		f = open('config.yaml','r')
		self.assertEqual(f.read(),'{}\n')
		f.close()

	def tearDown(self):
		os.chdir('..')
		shutil.rmtree('config_test')
		
class TestConfigPut(unittest.TestCase):
	def setUp(self):
		os.mkdir('config_test')
		os.chdir('config_test')

	def test(self):
		config.generate_new_config()
		config.Config().put('foo','bar')
		f = open('config.yaml','r')
		self.assertEqual(f.read(),'{foo: bar}\n')
		f.close()

	def tearDown(self):
		os.chdir("..")
		shutil.rmtree("config_test")

if __name__ == '__main__':
	unittest.main()
