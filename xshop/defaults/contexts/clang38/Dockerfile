FROM debian:stable

RUN dpkg --add-architecture i386

RUN apt-get update
RUN apt-get -y install python
RUN apt-get -y install cmake
RUN apt-get -y install gcc
RUN apt-get -y install g++
RUN apt-get -y install subversion

RUN apt-get -y install libc6-dev-i386
RUN apt-get -y install binutils-dev
RUN apt-get -y install binutils-gold

# Install Binutils Gold
RUN apt-get -y install bison
RUN apt-get -y install flex
RUN apt-get -y install texinfo
RUN apt-get -y install git
WORKDIR /home/
RUN git clone --depth 1 git://sourceware.org/git/binutils-gdb.git binutils
RUN mkdir binutils-build
WORKDIR /home/binutils-build
RUN ../binutils/configure --enable-gold --enable-plugins --disable-werror
RUN make -j128 all-gold
RUN mv /usr/bin/ld /usr/bin/ld.old
RUN cp gold/ld-new /usr/bin/ld

# Build clang38

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
RUN ls /usr/include
RUN cmake -DCMAKE_BUILD_TYPE=RELEASE -DLLVM_BINUTILS_INCDIR=/usr/include  -G "Unix Makefiles" ../llvm
RUN make -j128
RUN make install

WORKDIR /home/
