import unittest
import os
import shutil
from xshop import test
from xshop import exceptions

def make_sample_config():
	os.mkdir('containers')
	os.mkdir('containers/target')
	f = open('containers/target/Dockerfile','w')
	f.write("{{ foo }}")
	f.close()
	f = open('docker-compose.yml','w')
	f.write('target:\n  build: containers/target/\n')
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

class TestPrepare_Build(unittest.TestCase):
	def setUp(self):
		os.mkdir('prepare-build-test')
		os.chdir('prepare-build-test')
		make_sample_config()
	
	def test(self):
		test.prepare_build(['target'],{'foo':'bar'})

		os.chdir('..')
		
		# Check folder structure
		self.assertTrue(os.path.isdir('build-tmp'))
		self.assertTrue(os.path.isdir('build-tmp/containers'))

		# Check that docker compose file was copied
		f = open('build-tmp/docker-compose.yml')
		self.assertEqual(f.read(),'target:\n  build: containers/target/\n')
		f.close()

		# Check that build_context was called for target
		self.assertTrue(os.path.isdir('build-tmp/containers/target'))

		# Check that dictionary was passed to template
		f = open('build-tmp/containers/target/Dockerfile','r')
		self.assertEqual(f.read(),'bar')
		f.close()

	def tearDown(self):
		os.chdir('..')
		shutil.rmtree('prepare-build-test')

class TestCleanBuild(unittest.TestCase):
	def setUp(self):
		os.mkdir('build-tmp')
	
	def test(self):
		test.clean_build([])
		self.assertFalse(os.path.exists('build-tmp'))

def make_sample_project():
	shutil.copytree('test/test_project/','test_project')

#
#	Test Running Tests
#
class TestRunVuln(unittest.TestCase):
	def setUp(self):
		make_sample_project()
		os.chdir('test_project')
		os.remove('test/xshop_test.py')
		f = open('test/xshop_test.py','w')
		f.write("run_exploit():\n\treturn 1")
		f.close()
	
	def test(self):
		self.assertTrue(test.run_test('2.9-2+deb8u1','debian'))
	
	def tearDown(self):
		os.chdir('..')
		shutil.rmtree('test_project')

class TestRunInvuln(unittest.TestCase):
	def setUp(self):
		make_sample_project()
		os.chdir('test_project')

	def test(self):
		self.assertFalse(test.run_test('2.9-2+deb8u1','debian'))
	
	def tearDown(self):
		os.chdir('..')
		shutil.rmtree('test_project')

if __name__ == '__main__':
	unittest.main()
