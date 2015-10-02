FROM xshop:clang38

WORKDIR /home/

{% for d in builddeps %}
  RUN apt-get -y install {{ d }}
{% endfor %}

ADD . /home/

# compile
{% if compiler == 'clang++' %}

  RUN clang++ vuln.cpp -o vuln

{% elif compiler == 'g++' %}
  
  RUN g++ vuln.cpp -o vuln

{% elif compiler == 'g++ -fvtable-verify=std' %}
  
  RUN ./gcc/usr/local/bin/g++ -fvtable-verify=std vuln.cpp -o vuln

{% elif compiler == 'clang++ -fsanitize=cfi' %}
  
  RUN clang++ vuln.cpp -o vuln -fsanitize=cfi -flto

{% endif %} 
