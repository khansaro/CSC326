#!/bin/bash
export DEBIAN_FRONTEND=noninteractive
apt-get update -y > /dev/null
apt-get upgrade -y  > /dev/null
apt-get install -y build-essential  > /dev/null
apt-get install -y python-dev  > /dev/null
cd bottle-0.12.7
python setup.py install  > /dev/null
cd ../httplib2-0.8
python setup.py install  > /dev/null
cd ../setuptools-18.7.1
python setup.py install  > /dev/null
cd ../Beaker-1.7.0
python setup.py install  > /dev/null
cd ..
tar -xvf numpy-1.10.1.tar.gz  > /dev/null
cd numpy-1.10.1
python setup.py install  > /dev/null
cd ..
echo "Search engine is available on port 8080 at:"
dig +short myip.opendns.com @resolver1.opendns.com
python bottle_kkt.py
