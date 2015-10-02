FROM xshop:base_test_image

WORKDIR /home/

RUN echo {{ builddeps[0] }} 

{% for d in builddeps %}
  RUN apt-get -y install {{ d }}
{% endfor %}

ADD cfi /home/cfi/
ADD install.sh /home/
ADD vuln.c /home/
ADD Makefile /home/

# run installation script
RUN /bin/bash ./install.sh
