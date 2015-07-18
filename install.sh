#!/bin/bash

set -e

echo "You must have docker installed and be in docker group."
echo "If you do not, run:"
echo "	wget -qO- https://get.docker.com/ | sh"
echo "	sudo usermod -aG docker <your_user_name>"
echo "And then log out and back in."
echo "Checking: "
sudo -H -u $SUDO_USER bash -c 'docker info'
echo
echo "Make sure pip is installed:"
apt-get -y install python-pip

echo "Jinja2:"
pip install Jinja2

echo "Docker Py:"
pip install docker-py

echo "Docker-Compose"
pip install -U docker-compose

echo "Installing xshop:"
echo "	Copying module to /usr/lib/python2.7/"
cp -r xshop /usr/lib/python2.7/
echo "Copying command line utility to /usr/bin/xshop"
cp run /usr/bin/xshop


echo "Building base_test_image"
python -c "from xshop import dockerw;dockerw.build_image('base_test_image')"

echo "Done!"


