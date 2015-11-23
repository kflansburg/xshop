FROM xshop:base_test_image
FROM_VAGRANT ubuntu/precise64
#
# Installation
#

WORKDIR /home/

#{% if install_type=="debian" %}
#    ADD {{ library }}-{{ version }} /home/
#    RUN dpkg -i {{ library }}_{{ version }}-1_amd64.deb
#    RUN apt-get -y install -f

#{% elif install_type=='source' %}
    ADD {{ library }}-{{ version }}.tar.gz /home/
    WORKDIR /home/{{ library }}-{{ version }}/
    RUN ./config --prefix=/usr
    RUN make
    RUN make install_sw

#{% else %}
#    RUN apt-get -y install {{ library }}={{ version }}-1

#{% endif %}

#
#   Add any configuration for the software
#

#Add self signed cert
WORKDIR /home/
