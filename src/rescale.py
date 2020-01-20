from PIL import Image
import cv2 as cv
import sys

img_name = sys.argv[1]   # command line  argument
path = sys.argv[2]# input image path
path_op = sys.argv[3] # path to output folder
factor = int(sys.argv[4]) # rescaling factor



img = cv.imread(path+img_name)
width = int(img.shape[1] * factor)
height = int(img.shape[0] * factor)
dim = (width, height)
# resize image
resized = cv.resize(img, dim, interpolation = cv.INTER_CUBIC)

img_name = img_name.split(".")[0]; # extracts 104 from 104.png/104.jpg
cv.imwrite(path_op+img_name+"_rescaled.png", resized)