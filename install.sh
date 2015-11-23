#!/bin/bash

set -e

echo "Installing:"
echo "	Jinja2"
pip install Jinja2

echo "	PyYaml"
pip install pyyaml

echo "	Requests"
pip install requests

echo "	Docker Compose"
pip install docker-compose

echo "	XShop:"
echo "		Copying module to /usr/lib/python2.7/"
cp -r xshop /usr/lib/python2.7/
echo "		Copying command line utility to /usr/bin/xshop"
cp run /usr/bin/xshop

echo "Done!"


