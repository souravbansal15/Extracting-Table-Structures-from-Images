#!/bin/sh

set -e
apt-get -y update
apt-get -y upgrade
apt-get -y dist-upgrade

apt-get -y install python3
apt-get -y install python3-pip
pip3 install --upgrade pip
apt-get -y install python-opencv python3-numpy python3-tk

set +e
python3 -c "import skimage"
if [ $? -ne 0 ];
then 
set -e
pip3 install scikit-image
fi

set +e
python3 -c "import cv2"  
if [ $? -ne 0 ];
then
set -e
pip3 install opencv-python
fi


apt-get -y install openjdk-8-jdk
apt-get -y install openjfx

mkdir -p etc
cd etc
mkdir -p DependentPackages
cd DependentPackages
apt-get -y install git 
apt-get -y install ant
apt-get -y install cmake

set +e
test -f "/usr/local/share/java/opencv4/opencv-410.jar"
if [ $? -ne 0 ];
then 
set -e
git clone https://github.com/opencv/opencv.git
cd opencv
mkdir build
cd build
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
cmake -DBUILD_SHARED_LIBS=OFF ..
make -j7
make install
fi