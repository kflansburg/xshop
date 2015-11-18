FROM kflansburg/maverick64

# Install Kernel
RUN ln -s /usr/bin/python /usr/bin/python2
RUN apt-get -y install python
RUN mkdir ~/packages
WORKDIR ~/packages
ADD {{ library }}-{{ version }}/* ~/packages/
RUN dpkg -i *.deb
KERNEL {{ version }}
