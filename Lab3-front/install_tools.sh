#!/bin/bash
echo "Installing bottle module..."
cd bottle-0.12.7
python setup.py install  &> /dev/null
echo "Installing httplib2 module..."
cd ../httplib2-0.8
python setup.py install  &> /dev/null
echo "Installing setuptools..."
cd ../setuptools-18.7.1
python setup.py install  &> /dev/null
echo "Installing Beaker..."
cd ../Beaker-1.7.0
python setup.py install  &> /dev/null
cd ..
echo "Installing numpy..."
tar -xvf numpy-1.10.1.tar.gz  &> /dev/null
cd numpy-1.10.1
python setup.py install  &> /dev/null
cd ..
echo ""
python bottle_kkt.py
