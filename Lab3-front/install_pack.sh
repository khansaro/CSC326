#!/bin/bash
export DEBIAN_FRONTEND=noninteractive
apt-get update -y > /dev/null
apt-get upgrade -y  > /dev/null
apt-get install -y build-essential  > /dev/null
apt-get install -y python-dev  > /dev/null
apt-get install dos2unix
dos2unix Lab3-front/install_tools.sh
cd Lab3-front
/bin/bash install_tools.sh
