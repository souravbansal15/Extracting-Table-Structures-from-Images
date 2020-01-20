python ./src/rescale.py $1.png ./input/ ./output/ 2
echo "Image Rescaled"

python ./src/preprocess.py $1_rescaled.png ./output/ ./output/ 2 
# 2 represents scaling factor
echo "Image preprocessed"

python ./src/read.py $1_rescaled_DiagramOnly.png > output.txt
# Here also 2 represents the factor
# Factor must be same at both places
echo "Executed successfully"