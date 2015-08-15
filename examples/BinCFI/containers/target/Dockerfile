# Select any base image
#
# xshop:base_test_image is updated/upgraded and has:
# 	python
#	gcc
#	make
#	clang
#
# xshop:clang38 has the latest version of llvm/clang, built from the
#	SVN repository. Additionally it has:
#	python
#	cmake
#	gcc
#	g++
#	subversion
#	git
#	libc i386
#

FROM xshop:base_test_image

#
#	This file should completely install the target library. 
#
#	Any support files for launching the test environment should
#	be in the test folder. This should be installation only. 
#
#	For example, in the Heartbleed test, we need basic certificates
#	to launch the server. These should be in the test folder and
#	not this build context so that this target could be used for other
#	tests that do not need the certificates.
#


WORKDIR /home/
