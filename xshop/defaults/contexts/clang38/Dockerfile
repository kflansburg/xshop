FROM debian:stable
RUN apt-get update
RUN apt-get -y install python
RUN apt-get -y install cmake
RUN apt-get -y install gcc
RUN apt-get -y install g++
RUN apt-get -y install subversion
RUN apt-get -y install libc6-dev-i386

RUN apt-get -y install binutils-dev
RUN apt-get -y install binutils-gold

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
RUN cmake -LLVM_BUILD_32_BITS=ON -DCMAKE_BUILD_TYPE=DEBUG -DLLVM_BINUTILS_INCDIR=/usr/include -G "Unix Makefiles" ../llvm
RUN make -j128
RUN make install


RUN apt-get -y install bison
RUN apt-get -y install flex
RUN apt-get -y install texinfo
RUN apt-get -y install git

WORKDIR /home/
RUN git clone --depth 1 git://sourceware.org/git/binutils-gdb.git binutils
RUN mkdir binutils-build
WORKDIR /home/binutils-build
RUN ../binutils/configure --enable-gold --enable-plugins --disable-werror
RUN make all-gold
RUN cp gold/ld-new /usr/bin/ld

WORKDIR /home/
