import unittest
from xshop import dockerw
from xshop import exceptions
import os
import shutil
import logging
from subprocess import call as sh

logging.basicConfig(filename=os.getcwd()+'/test.log',level=logging.DEBUG)

class TestContainerExistsYes(unittest.TestCase):
	def setUp(self):
		self.f = open('/dev/null', 'w')
		sh(['docker','run','--name=container_exists_test','debian:stable','ls'],stderr=self.f,stdout=self.f)

	def test(self):
		self.assertTrue(dockerw.container_exists('container_exists_test'))

	def tearDown(self):
		sh(['docker','rm','container_exists_test'],stderr=self.f,stdout=self.f)

class TestContainerExistsNo(unittest.TestCase):
	def test(self):
		self.assertFalse(dockerw.container_exists('container_exists_test'))

class TestImageExistsYes(unittest.TestCase):
	def setUp(self):
		self.f = open('/dev/null', 'w')
		sh(['docker','tag','debian:stable','xshop:image_exists_test'],stderr=self.f,stdout=self.f)

	def test(self):
		self.assertTrue(dockerw.image_exists('xshop:image_exists_test'))

	def tearDown(self):
		sh(['docker','rmi','xshop:image_exists_test'],stderr=self.f,stdout=self.f)

class TestImageExistsNo(unittest.TestCase):
	def test(self):
		self.assertFalse(dockerw.image_exists('xshop:image_exists_test'))

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
		with self.assertRaises(exceptions.DockerError):
			dockerw.build_image('test_image')

	def tearDown(self):
		shutil.rmtree(p+'test_image')		

#
#	Creates a sample project, target Dockerfile and 
#	test.py must still be populated
#
def create_test_project(ret):
	dockerw.build_image('base_test_image')
	os.mkdir('Project_Name')
	shutil.copy2('xshop/defaults/docker-compose-test-default.yml','Project_Name/docker-compose.yml')
	os.mkdir('Project_Name/containers')
	os.mkdir('Project_Name/containers/target')
	os.mkdir('Project_Name/containers/attacker')
	os.mkdir('Project_Name/containers/target/test')
	f = open('Project_Name/containers/target/Dockerfile','w')
	f.write('FROM xshop:base_test_image\nWORKDIR /home/\nADD test /home/\nCMD /bin/bash -c "while true; do sleep 1; done"')
	f.close()	
	f = open('Project_Name/containers/target/test/xshop_test.py','w')
	f.write('def run_exploit():\n\treturn ' + str(ret))
	f.close()

#
#	Test that compose up can start a good project and 
#	that compose down can kill running project
#
class TestComposeUpGood(unittest.TestCase):
	def setUp(self):
		create_test_project(0)
		f = open('Project_Name/containers/attacker/Dockerfile','w')
		f.write('FROM debian:stable\nCMD /bin/bash -c "while true; do sleep 1; done"')
		f.close()
		os.chdir('Project_Name')

	def test(self):
		logging.basicConfig(filename='../test.log',level=logging.DEBUG)
		dockerw.compose_up()
		self.assertTrue(dockerw.container_running('xshop_target_1'))
		self.assertTrue(dockerw.container_running('xshop_attacker_1'))
		dockerw.compose_down()

	def tearDown(self):
		os.chdir('..')
		shutil.rmtree('Project_Name')

#
#	Test that compose_down can handle when containers
#	aren't running
#
class TestComposeDown(unittest.TestCase):
	def setUp(self):
		create_test_project(0)
		os.chdir('Project_Name')
		os.remove('docker-compose.yml')
		f = open('docker-compose.yml','w')
		f.write('foobar:\n  build: .\n')
		f.close()

	def test(self):
		self.assertFalse(dockerw.compose_down())

	def tearDown(self):
		os.chdir('..')
		shutil.rmtree('Project_Name')

#
#	Test that compose up throws a dockererror when 
#	a build fails
#
class TestComposeUpBad(unittest.TestCase):
	def setUp(self):
		create_test_project(0)
		os.chdir('Project_Name')

	def test(self):
		with self.assertRaises(exceptions.DockerError):
			dockerw.compose_up()

	def tearDown(self):
		os.chdir('..')
		shutil.rmtree('Project_Name')

#
#	Test that running a hook returns the correct 
#	value
#
class TestRunningHook(unittest.TestCase):
	def setUp(self):
		create_test_project(132)
		f = open('Project_Name/containers/attacker/Dockerfile','w')
                f.write('FROM debian:stable\nCMD /bin/bash -c "while true; do sleep 1; done"')
                f.close()
                os.chdir('Project_Name')
		dockerw.compose_up()

	def test(self):
		self.assertEqual(dockerw.run_hook('xshop_target_1','run_exploit'),132)

	def tearDown(self):
		dockerw.compose_down()
		os.chdir('..')
		shutil.rmtree('Project_Name')

#
#	Test that running hook on nonrunning container
#	raises dockererror
#
class TestRunningHookBad(unittest.TestCase):
	def setUp(self):
		self.f = open('/dev/null')
		sh(['docker','run','-t','-i','--name=run_hook_test','debian:stable','ls'],stderr=self.f,stdout=self.f)

	def test(self):
		with self.assertRaises(exceptions.DockerError):
			dockerw.run_hook('run_hook_test','run_exploit')
	
	def tearDown(self):
		self.f.close()

class RemoveLog(unittest.TestCase):
	def test(self):
		pass
		os.remove('test.log')

if __name__ == '__main__':
	unittest.main()
