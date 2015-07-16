FROM debian:stable
ADD kflansburg.gpg /home/
RUN apt-key add /home/kflansburg.gpg
RUN echo "deb http://s3-us-west-2.amazonaws.com/legacy-repository/ stable main\n deb-src http://s3-us-west-2.amazonaws.com/legacy-repository/ stable main" >> /etc/apt/sources.list
RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install python
RUN apt-get -y install gcc
RUN apt-get -y install make
RUN apt-get -y install clang

