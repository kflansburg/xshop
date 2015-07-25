FROM xshop:base_test_image

ENV CONTAINER_NAME {{ container_name }}

#
# Installation
#

WORKDIR /home/

{% if install_type=="debian" %}
    ADD {{ library }}-{{ version }} /home/

    RUN dpkg -i {{ library }}_{{ version }}-1_amd64.deb
    RUN apt-get -y install -f

{% elif install_type=="source" %}
	{% for d in builddeps %}
		RUN apt-get -y install {{ d }}
	{% endfor %}

	ADD {{ library }}-{{ version }}.tar.gz /home/
	RUN sed -r -i 's/(3..89..)/\1 | 4.*/' {{ library }}-{{ version}}/configure
	RUN mkdir /home/build
	WORKDIR /home/build
	RUN mkdir /usr/local/build
	RUN ../{{ library }}-{{ version }}/configure --prefix=/usr/local/build
	RUN make -j128
	RUN make install

{% else %}
    RUN apt-get -y install {{ library }}={{ version }}-1

{% endif %}

#
#   Add any configuration for the software
#

