FROM xshop:base_test_image

#
# Installation
#

WORKDIR /home/

#{% if install_type=="debian" %}
#    ADD {{ library }}-{{ version }} /home/

#    RUN dpkg -i {{ library }}_{{ version }}-1_amd64.deb
#    RUN apt-get -y install -f

#{% elif install_type=="source" %}
	RUN apt-get -y install patch
	ADD {{ library }}-{{ version }}.tar.gz /home/
	WORKDIR /home/{{ library }}-{{ version }}
	ADD patches .
	{% for i in range(1,patch|int+1) %}
		RUN patch -p0 < bash43-{{ "%03d" % i }}
	{% endfor %} 
    RUN ./configure --prefix=/usr
    RUN make
    RUN make install

#{% else %}
#    RUN apt-get -y install {{ library }}={{ version }}-1

#{% endif %}

#
#   Add any configuration for the software
#
