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
		d = {'DIST':'ubuntu','RELEASE':'vivid'}
		ans = {'filename':'debian_ubuntu_vivid','len':2,'ranks':[0,1]}
		result = fileselect.parse_qualifiers('debian_ubuntu_vivid',d)
		self.assertEqual(result,ans)

# Check that the default folder with no qualifiers is parsed correctly
class TestParseQualifiersDefault(unittest.TestCase):
	def test(self):
		d = {'DIST':'ubuntu','RELEASE':'vivid'}
		result = fileselect.parse_qualifiers('debian',d)
		ans = {'filename':'debian','len':0,'ranks':[]}
		self.assertEqual(result,ans)

# Check that a mismatch returns false
class TestParseQualifiersMismatch(unittest.TestCase):
	def test(self):
		d = {'DIST':'ubuntu','RELEASE':'oneric'}
		self.assertFalse(fileselect.parse_qualifiers('debian_ubuntu_vivid',d))

#
#	Integration testing for main function
#
class TestSelect(unittest.TestCase):
	def setUp(self):
		pass

	def test(self):
		pass
	
	def tearDown(self):
		pass

if __name__ == '__main__':
	unittest.main()
