#!/bin/sh

cp ./output1.png ./output/$1_PostProc.png
cp ./output1.png ./output/$1_HoughLines.png
cp ./output1.png ./output/$1_mergelines.png
cp ./output1.png ./output/$1_removedup.png
cp ./output1.png ./output/$1_combineend.png
cp ./output1.png ./output/$1_intersectionBasedCorrection.png
echo "output file copied"

python ./src/rescale.py $1.png ./input/ ./output/ 2
echo "Image Rescaled"

python ./src/preprocess.py $1_rescaled.png ./output/ ./output/ 2 
# 2 represents scaling factor
echo "Image preprocessed"

python ./src/run.py $1.png ./input/ ./output/ 2 > output.txt
# Here also 2 represents the factor
# Factor must be same at both places
echo "Executed successfully"
