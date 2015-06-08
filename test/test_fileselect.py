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

# Test matching function for basic match
class TestMatchMatch(unittest.TestCase):
	def test(self):
		self.assertTrue(fileselect.match('foo','foo'))

# Test matching for wildcard
class TestMatchWildcard(unittest.TestCase):
	def test(self):
		self.assertTrue(fileselect.match('0.1.X','0.1.1c-beta1'))

# Test matching for -/_
class TestMatchUnderscore(unittest.TestCase):
	def test(self):
		self.assertTrue(fileselect.match('foo-bar','foo_bar'))

# Test mismatch
class TestMatchMismatch(unittest.TestCase):
	def test(self):
		self.assertFalse(fileselect.match('foo','bar'))

# Check that a typical string is parsed correctly
class TestParseQualifiersBasic(unittest.TestCase):
	def test(self):
		pass
	
if __name__ == '__main__':
	unittest.main()
