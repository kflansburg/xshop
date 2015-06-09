import unittest
import os
import shutil
from xshop import template

#
# Create:
#
#	template-test
#	|- foo
#	|	|-bar
# 	|-bar
#
# To test that it opens directories and applys template to files`
#
def template_folder_setup():
	os.mkdir('template-test')
	f = open('template-test/bar','w')
	f.write('{{ var1 }}')
	f.close()
	os.mkdir('template-test/foo')
	f = open('template-test/foo/bar','w')
	f.write('{{ var2 }}')
	f.close()


class TestInsertion(unittest.TestCase):
	def setUp(self):
		f = open('template-test','w')
		f.write("{{ foo }}")
		f.close()

	def test(self):
		template.template_file('template-test',{'foo':'bar'})
		f = open('template-test','r')
		self.assertEqual(f.read(),'bar')
		f.close()

	def tearDown(self):
		os.remove('template-test')

class TestFolder(unittest.TestCase):
	def setUp(self):
		template_folder_setup()

	def test(self):
		template.template_folder('template-test',{'var1':'ubuntu','var2':'debian'})
		f = open('template-test/bar','r')
		self.assertEqual(f.read(),'ubuntu')
		f.close()
		f = open('template-test/foo/bar')
		self.assertEqual(f.read(),'debian')
		f.close()

	def tearDown(self):
		shutil.rmtree('template-test')

class TestCopy(unittest.TestCase):
	def setUp(self):
		template_folder_setup()

	def test(self):
		template.copy_and_template('template-test','template-test_2',{'var1':'ubuntu','var2':'debian'})
		self.assertTrue(os.path.isdir('template-test_2'))
		f = open('template-test_2/bar','r')
		self.assertEqual(f.read(),'ubuntu')
		f.close()
		f = open('template-test_2/foo/bar')
		self.assertEqual(f.read(),'debian')
		f.close()

	def tearDown(self):
		shutil.rmtree('template-test')
		shutil.rmtree('template-test_2')

if __name__ == '__main__':
	unittest.main()
