FROM debian:stable
RUN apt-get update
RUN apt-get -y install python
RUN apt-get -y install cmake
RUN apt-get -y install gcc
RUN apt-get -y install g++
RUN apt-get -y install subversion

# Checkout Code
WORKDIR /home/
RUN svn co http://llvm.org/svn/llvm-project/llvm/trunk llvm
WORkDIR /home/llvm/tools
RUN svn co http://llvm.org/svn/llvm-project/cfe/trunk clang
WORKDIR /home/llvm/projects
RUN svn co http://llvm.org/svn/llvm-project/compiler-rt/trunk compiler-rt

# Build
WORKDIR /home/
RUN mkdir build
WORKDIR /home/build
RUN cmake -G "Unix Makefiles" ../llvm
RUN make -j128
RUN make install
