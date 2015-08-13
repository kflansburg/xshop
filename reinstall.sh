#!/bin/bash

set -e

echo "Installing xshop:"
echo "	Copying module to /usr/lib/python2.7/"
cp -r xshop /usr/lib/python2.7/
echo "Copying command line utility to /usr/bin/xshop"
cp run /usr/bin/xshop

echo "Done!"


