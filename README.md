# Raster Table Accessibility

## How to run

- ./run.sh <input_file_name>
- Eg: ./run.sh image_name
- Make sure input file should be in input folder

#How to run the file for image containig table
- ./image.sh <input_file_name>
- Eg: ./run.sh image_name
- Make sure input file should be in input folder

## Java Dependencies
### OpenJDK: Manual Installation:
- sudo apt-get install openjdk-8-jdk
- sudo apt-get install openjfx

### OpenCv:
https://advancedweb.hu/2016/03/01/opencv_ubuntu/

- git clone https://github.com/opencv/opencv.git
- cd opencv
- mkdir build
- cd build
- export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
- sudo apt-get install ant
- sudo apt install cmake
- cmake -DBUILD_SHARED_LIBS=OFF ..
- make -j7
- sudo make install
