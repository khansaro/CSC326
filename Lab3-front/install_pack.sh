#!/bin/bash
export DEBIAN_FRONTEND=noninteractive
echo ""
echo "Installing gcc..."
apt-get update -y &> /dev/null
apt-get upgrade -y  &> /dev/null
apt-get install -y build-essential  &> /dev/null
echo "Installing python-dev..."
apt-get install -y python-dev  &> /dev/null
echo "Installing dos2unix..."
apt-get install -y dos2unix &> /dev/null
dos2unix Lab3-front/install_tools.sh
cd Lab3-front
/bin/bash install_tools.sh
