FROM xshop:clang38

WORKDIR /home/

{% for d in builddeps %}
RUN apt-get -y install {{ d }}
{% endfor %}

# move sources
ADD . /home/

RUN echo make CXX=clang++ CXXFLAGS='{{ cxxflags }}'
RUN make CXX=clang++ CXXFLAGS='{{ cxxflags }}'

