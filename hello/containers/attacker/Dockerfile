FROM xshop:base_test_image

ENV CONTAINER_NAME {{ container_name }}

WORKDIR /home/

#
#	Add test files
#
ADD test /home/

CMD while true; do sleep .1; done
