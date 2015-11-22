FROM kflansburg/maverick64
FROM_XSHOPVB Maverick64

RUN ln -s /usr/bin/python /usr/bin/python2
RUN apt-get -y install python
RUN mkdir ~/packages
WORKDIR ~/packages
ADD {{ library }}-{{ version }} ~/packages/
WORKDIR ~/packages/{{library}}-{{version}}
RUN dpkg -i *.deb
RUN ls
KERNEL {{ version }}
