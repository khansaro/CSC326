#!/bin/bash
apt-get update
apt-get upgrade
apt-get install -y build-essential
apt-get install -y python-dev
cd bottle-0.12.7
python setup.py install
cd ../httplib2-0.8
python setup.py install
cd ../setuptools-18.7.1
python setup.py install
cd ../Beaker-1.7.0
python setup.py install
cd ..
tar -xvf numpy-1.10.1.tar.gz
cd numpy-1.10.1
python setup.py install
cd ..
echo "Search engine is available on port 8080 at:"
dig +short myip.opendns.com @resolver1.opendns.com
python bottle_kkt.py
