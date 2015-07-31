FROM debian:wheezy
RUN apt-get update
RUN apt-get -y install python
RUN apt-get -y install gcc 
RUN apt-get -y install make


#
# Installation
#

WORKDIR /home/



{% if install_type=="debian" %}
	{% for d in deps %}
	RUN apt-get -y install {{ d }}
	{% endfor %}

    ADD {{ library }}-{{ version }} /home/

    RUN dpkg -i {{ library }}_{{ version }}-1.1_amd64.deb
    RUN apt-get -y install -f

{% elif install_type=="source" %}
	{% for d in builddeps %}
		RUN apt-get -y install {{ d }}
	{% endfor %}

	ADD {{ library }}-{{ version }}.tar.gz /home/
	WORKDIR /home/{{ library }}-{{ version }}
	RUN make 
	RUN ./install

{% else %}
    RUN apt-get -y install {{ library }}={{ version }}-1.1

{% endif %}

#
#   Add any configuration for the software
#
