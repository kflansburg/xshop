import unittest
import os
import shutil
from xshop import fileselect

# Check if the most common case passes
class TestListFilesBasic(unittest.TestCase):
	def setUp(self):
		os.mkdir('test_folder')
		os.mkdir('test_folder/debian_ubuntu')

	def test(self):
		self.assertEqual(fileselect.list_files('test_folder','debian'), ['debian_ubuntu'])

	def tearDown(self):
		shutil.rmtree('test_folder')

# Check that it picks up the default with no qualifiers
class TestListFilesDefault(unittest.TestCase):
	def setUp(self):
		os.mkdir('test_folder')
		os.mkdir('test_folder/debian_ubuntu')
		os.mkdir('test_folder/debian')

	def test(self):
		self.assertEqual(sorted(fileselect.list_files('test_folder','debian')), sorted(['debian_ubuntu','debian']))

	def tearDown(self):
		shutil.rmtree('test_folder')

# Check that it ignores other files and malformed files
class TestListFilesOther(unittest.TestCase):
	def setUp(self):
		os.mkdir('test_folder')
		os.mkdir('test_folder/debian_ubuntu')
		os.mkdir('test_folder/Dockerfile')
		os.mkdir('test_folder/_debian_armel')
		os.mkdir('test_folder/debian_vivid_')

	def test(self):
		self.assertEqual(fileselect.list_files('test_folder','debian'), ['debian_ubuntu'])

	def tearDown(self):
		shutil.rmtree('test_folder')

# Check that a typical string is parsed correctly
class TestParseQualifiersBasic(unittest.TestCase):
	def test(self):
		pass
	
if __name__ == '__main__':
	unittest.main()
