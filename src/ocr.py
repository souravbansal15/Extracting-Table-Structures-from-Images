from __future__ import division
from numpy import empty
import cv2
from PIL import Image
import pytesseract
import numpy as np

def getText(cropped_image):
    line_change="""
"""
    tag="""<br>
    """
    str_detected=str(pytesseract.image_to_string(cropped_image, config="psm -6"))
    str_detected=str_detected.replace(line_change,tag)

    return str_detected