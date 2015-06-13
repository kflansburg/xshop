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

class TestContainerRunning(unittest.TestCase):
	def test(self):
		pass #TODO

class TestRunHook(unittest.TestCase):
	def test(self):
		pass #TODO

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
	os.mkdir('Project_Name')
	shutil.copy2('xshop/defaults/docker-compose-test-default.yml','Project_Name/docker-compose.yml')
	os.mkdir('Project_Name/containers')
	os.mkdir('Project_Name/containers/target')
	os.mkdir('Project_Name/containers/attacker')
	os.mkdir('Project_Name/test')
	f = open('Project_Name/containers/attacker/Dockerfile','w')
	f.write('FROM debian:stable\nCMD /bin/bash -c "while true; do sleep 1; done"')
	f.close()	
	f = open('Project_Name/test/test.py','w')
	f.write('def run_exploit():\n\treturn ' + str(ret))
	f.close()

#
#	Test that compose up can start a good project and 
#	that compose down can kill running project
#
class TestComposeUpGood(unittest.TestCase):
	def setUp(self):
		create_test_project(0)
		f = open('Project_Name/containers/target/Dockerfile','w')
		f.write('FROM debian:stable\nCMD /bin/bash -c "while true; do sleep 1; done"')
		f.close()
		os.chdir('Project_Name')

	def test(self):
		logging.basicConfig(filename='../test.log',level=logging.DEBUG)
		dockerw.compose_up()
		self.assertTrue(dockerw.container_running('xshop_target_1'))
		self.assertTrue(dockerw.container_running('xshop_attacker_1'))
		dockerw.compose_down()
		self.assertFalse(dockerw.container_running('xshop_target_1'))
		self.assertFalse(dockerw.container_running('xshop_attacker_1'))

	def tearDown(self):
		os.chdir('..')
		shutil.rmtree('Project_Name')
		

if __name__ == '__main__':
	unittest.main()
