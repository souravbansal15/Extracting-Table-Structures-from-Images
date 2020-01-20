import cv2
import numpy as np

img = cv2.imread("ncert22.png")

alpha = 2.0
beta = -160

new = alpha * img + beta
new = np.clip(new, 0, 255).astype(np.uint8)

cv2.imwrite("cleaned.png", new)