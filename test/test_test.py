import unittest
import os
import shutil
from xshop import test

def make_sample_config():
	os.mkdir('containers')
	os.mkdir('containers/target')
	f = open('containers/target/Dockerfile','w')
	f.write("{{ foo }}")
	f.close()
	os.mkdir('test')
	f = open('test/test.py','w') 
	f.write('foobar')
	f.close()

class TestBuildContext(unittest.TestCase):
	def setUp(self):
		os.mkdir('build-context-test')
		os.chdir('build-context-test')
		make_sample_config()
		os.mkdir('build-tmp')
		os.mkdir('build-tmp/containers')
	
	def test(self):
		test.build_context('target', {"foo":"bar"})

		# Check folder structures
		self.assertTrue(os.path.isdir('build-tmp/containers/target'))
		self.assertTrue(os.path.isdir('build-tmp/containers/target/test'))

		# Check file placement and templating
		f = open('build-tmp/containers/target/test/test.py','r')
		self.assertEqual(f.read(),"foobar")
		f.close()
		f = open('build-tmp/containers/target/Dockerfile')
		self.assertEqual(f.read(),"bar")
		f.close()

	def tearDown(self):
		os.chdir('..')
		shutil.rmtree('build-context-test')

class TestParseDockerCompose(unittest.TestCase):
	def setUp(self):
		shutil.copy2('xshop/defaults/docker-compose-test-default.yml','docker-compose.yml')

	def test(self):
		containers = test.parse_docker_compose()		
		self.assertEqual(sorted(containers),sorted(['attacker','target']))

	def tearDown(self):
		pass
		os.remove('docker-compose.yml')

if __name__ == '__main__':
	unittest.main()
