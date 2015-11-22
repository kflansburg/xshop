FROM kflansburg/maverick64
FROM_XSHOPVB Maverick64

# Install Kernel
RUN ln -s /usr/bin/python /usr/bin/python2
RUN mkdir ~/packages
ADD {{ library }}-{{ version }} ~/packages/
WORKDIR ~/packages/{{ library }}-{{ version }}
RUN dpkg -i *.deb
RUN sudo apt-get -y remove linux-image-2.6.35-22-server
RUN sudo apt-get -y remove linux-image-2.6.35-32-server
KERNEL {{ version }}
