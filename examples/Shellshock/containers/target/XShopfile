FROM_VAGRANT ubuntu/precise64
FROM_DOCKER xshop:base_test_image
{% if install_type=="source" %}
	#
	#	For installation from source, we first install 
	# 	dependencies mentioned in config.yaml
	#
	{% for d in build_dependencies %}
		RUN apt-get -y install {{ d }}
	{% endfor %}

	#
	# 	Next, we run a standard autotools installation
	#
	ADD {{ library }}-{{ version }}.tar.gz ~/
	WORKDIR ~/{{ library }}-{{ version }}
	ADD patches .

	{% for i in range(1,patch|int+1) %}
		RUN patch -p0 < bash{{ version | replace(".","") }}-{{ "%03d" % i }}
	{% endfor %}
	
	RUN ./configure --prefix=/usr
    	RUN make
    	RUN make install
{% endif %}
