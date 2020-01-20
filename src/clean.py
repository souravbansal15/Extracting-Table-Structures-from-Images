import cv2,sys
import numpy as np

img_name=sys.argv[1]
path_in = sys.argv[2]
path_op = sys.argv[3]
img = cv2.imread(path_in+img_name+".png")

alpha = 2.0
beta = -160

new = alpha * img + beta
new = np.clip(new, 0, 255).astype(np.uint8)

cv2.imwrite(path_op+img_name+".png")