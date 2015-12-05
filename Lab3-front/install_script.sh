#!/bin/bash
sudo apt-get install build-essential -y
sudo apt-get update -y
sudo apt-get install python-dev -y
cd bottle-0.12.7
sudo python setup.py install
cd ../httplib2-0.8
sudo python setup.py install
cd ../setuptools-18.7.1
sudo python setup.py install
cd ../Beaker-1.7.0
sudo python setup.py install
cd ../numpy-1.10.1
sudo python setup.py install
cd ..
python bottle_kkt.py