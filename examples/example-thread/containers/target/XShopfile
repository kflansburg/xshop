FROM xshop:base_test_image

ADD tsan_example.c /home/
RUN clang /home/tsan_example.c -pthread {{ cflag }} -o /home/a.out

