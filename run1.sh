#!/bin/sh

cp ./output1.png ./output/$1_PostProc.png
cp ./output1.png ./output/$1_HoughLines.png
cp ./output1.png ./output/$1_mergelines.png
cp ./output1.png ./output/$1_removedup.png
cp ./output1.png ./output/$1_combineend.png
cp ./output1.png ./output/$1_intersectionBasedCorrection.png
echo "output file copied"

# python ./src/preprocess.py $1.png ./input/ ./output/

find ./src/ -name *.java > sources.txt
rm ./src/*.class
javac -cp ./etc/DependentPackage/opencv/build/bin/opencv-410.jar -d ./ @sources.txt
echo "Files compiled"
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:"/usr/local/share/java/opencv4"
#export LD_LIBRARY_PATH="C:\Users\Dell\AppData\Local\Packages\CanonicalGroupLimited.UbuntuonWindows_79rhkp1fndgsc\LocalState\rootfs\usr\local\share\java\opencv4"
echo "Path set"
java -cp .:./etc/DependentPackage/opencv/build/bin/opencv-410.jar src.Driver $1

echo "executed successfully"

