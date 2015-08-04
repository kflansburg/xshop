FROM xshop:base_test_image

#
# Installation
#

WORKDIR /home/

{% if install_type=="debian" %}
    ADD {{ library }}-{{ version }} /home/

    RUN dpkg -i {{ library }}_{{ version }}-1_amd64.deb
    RUN apt-get -y install -f

{% elif install_type=="source" %}
	ADD {{ library }}-{{ version }}.tar.gz /home/
	WORKDIR /home/{{ library }}-{{ version }}
    RUN ./configure --prefix=/usr
    RUN make
    RUN make install

{% else %}
    RUN apt-get -y install {{ library }}={{ version }}-1

{% endif %}

#
#   Add any configuration for the software
#
