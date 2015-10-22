FROM kflansburg/maverick64

# Install Kernel
RUN apt-get -y install python
RUN mkdir ~/packages
WORKDIR ~/packages
ADD {{ library }}-{{ version }}/* ~/packages/
RUN dpkg -i *.deb
KERNEL {{ version }}
