from __future__ import division
from numpy import empty
import cv2
from PIL import Image
import pytesseract
import numpy as np

from operator import itemgetter
from convert_to_html import convert

def adaptive_threshold(img, process_background=False, blocksize=15, c=-2):
    """Thresholds an image using OpenCV's adaptiveThreshold.
    Parameters
    ----------
    imagename : string
    Path to image file.
    process_background : bool, optional (default: False)
        Whether or not to process lines that are in background.
    blocksize : int, optional (default: 15)
        Size of a pixel neighborhood that is used to calculate a
        threshold value for the pixel: 3, 5, 7, and so on.
    c : int, optional (default: -2)
        Constant subtracted from the mean or weighted mean.
        Normally, it is positive but may be zero or negative as well.
    -------
    img : object
        numpy.ndarray representing the original image.
    threshold : object
        numpy.ndarray representing the thresholded image.
    """
    
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("gray.png",gray)
    if process_background:
        threshold = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, blocksize, c)
    else:
        threshold = cv2.adaptiveThreshold(
            np.invert(gray), 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, blocksize, c)
    return img, threshold


def find_lines(threshold, regions=None, direction='horizontal',
               line_scale=15, iterations=0):
    """Finds horizontal and vertical lines by applying morphological
    transformations on an image.
    Parameters
    ----------
    threshold : object
        numpy.ndarray representing the thresholded image.
    regions : list, optional (default: None)
        List of page regions that may contain tables of the form x1,y1,x2,y2
        where (x1, y1) -> left-top and (x2, y2) -> right-bottom
        in image coordinate space.
    direction : string, optional (default: 'horizontal')
        Specifies whether to find vertical or horizontal lines.
    line_scale : int, optional (default: 15)
        Factor by which the page dimensions will be divided to get
        smallest length of lines that should be detected.
        The larger this value, smaller the detected lines. Making it
        too large will lead to text being detected as lines.
    iterations : int, optional (default: 0)
        Number of times for erosion/dilation is applied.
          -------
    dmask : object
        numpy.ndarray representing pixels where vertical/horizontal
        lines lie.
    lines : list
        List of tuples representing vertical/horizontal lines with
        coordinates relative to a left-top origin in
        image coordinate space.
    """
    lines = []

    if direction == 'vertical':
        size = threshold.shape[0] // line_scale
        el = cv2.getStructuringElement(cv2.MORPH_RECT, (1, size))
    elif direction == 'horizontal':
        size = threshold.shape[1] // line_scale
        el = cv2.getStructuringElement(cv2.MORPH_RECT, (size, 1))
    elif direction is None:
        raise ValueError("Specify direction as either 'vertical' or"
                         " 'horizontal'")

    if regions is not None:
        region_mask = np.zeros(threshold.shape)
        for region in regions:
            x, y, w, h = region
            region_mask[y : y + h, x : x + w] = 1
        threshold = np.multiply(threshold, region_mask)

    threshold = cv2.erode(threshold, el)
    threshold = cv2.dilate(threshold, el)
    dmask = cv2.dilate(threshold, el, iterations=iterations)

    try:
        _, contours, _ = cv2.findContours(
            threshold.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    except ValueError:
        # for opencv backward compatibility
        contours, _ = cv2.findContours(
            threshold.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        x1, x2 = x, x + w
        y1, y2 = y, y + h
        if direction == 'vertical':
            lines.append(((x1 + x2) // 2, y2, (x1 + x2) // 2, y1))
        elif direction == 'horizontal':
            lines.append((x1, (y1 + y2) // 2, x2, (y1 + y2) // 2))

    return dmask, lines


def find_contours(vertical, horizontal):
    """Finds table boundaries using OpenCV's findContours.
    Parameters
    ----------
    vertical : object
        numpy.ndarray representing pixels where vertical lines lie.
    horizontal : object
        numpy.ndarray representing pixels where horizontal lines lie.
    Returns
    -------
    cont : list
        List of tuples representing table boundaries. Each tuple is of
        the form (x, y, w, h) where (x, y) -> left-top, w -> width and
        h -> height in image coordinate space.
    """
    mask = vertical + horizontal

    try:
        __, contours, __ = cv2.findContours(
            mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    except ValueError:
        # for opencv backward compatibility
        contours, __ = cv2.findContours(
            mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # sort in reverse based on contour area and use first 10 contours
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

    cont = []
    for c in contours:
        c_poly = cv2.approxPolyDP(c, 3, True)
        x, y, w, h = cv2.boundingRect(c_poly)
        cont.append((x, y, w, h))
    return cont


def find_joints(contours, vertical, horizontal):
    """Finds joints/intersections present inside each table boundary.
    Parameters
    ----------
    contours : list
        List of tuples representing table boundaries. Each tuple is of
        the form (x, y, w, h) where (x, y) -> left-top, w -> width and
        h -> height in image coordinate space.
    vertical : object
        numpy.ndarray representing pixels where vertical lines lie.
    horizontal : object
        numpy.ndarray representing pixels where horizontal lines lie.
    Returns
    """
    joints = np.multiply(vertical, horizontal)
    joint_coords = []
    x_set=set()
    y_set=set()
    for c in contours:
        x, y, w, h = c
        roi = joints[y : y + h, x : x + w]
        try:
            __, jc, __ = cv2.findContours(
                roi.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        except ValueError:
            # for opencv backward compatibility
            jc, __ = cv2.findContours(
                roi.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        if len(jc) <= 4:  # remove contours with less than 4 joints
            continue
        
        for j in jc:
            jx, jy, jw, jh = cv2.boundingRect(j)
            c1, c2 = x + (2 * jx + jw) // 2, y + (2 * jy + jh) // 2
            joint_coords.append((c1, c2))
            x_set.add(c1)
            y_set.add(c2)
        #tables[(x, y + h, x + w, y)] = joint_coords

    return joint_coords,sorted(x_set),sorted(y_set)


#calling the functions
def get_junctions(path,img_name,factor):
    image =cv2.imread(path+img_name)
    img, threshold = adaptive_threshold(image)
    h_dmask, h_lines = find_lines(threshold, regions=None, direction='horizontal',line_scale=15, iterations=0)
    v_dmask, v_lines = find_lines(threshold, regions=None, direction='vertical',line_scale=15, iterations=0)
    cont = find_contours(v_dmask, h_dmask)
    print(cont)
    joints,x_set,y_set = find_joints(cont, v_dmask, h_dmask)

    if((len(y_set)<=3)&(len(y_set)>0)):
        return "incomplete_table"
    if(len(y_set)==0):
        return "no_borders"
    joints=sorted(joints,key=itemgetter(1,0))



    matrix=[] #matrix with all the coordinates of junctions in a table
    k=0
    i=0
    j=0
    for j in range(len(y_set)):
        l=[]
        for i in range(len(x_set)):
            if ((x_set[i],y_set[j])==joints[k]):
                l.append((x_set[i]*factor,y_set[j]*factor))
                k=k+1
            else:
                l.append((-1,-1))
        matrix.append(l)



    for num in range(len(matrix)):
        print(matrix[num])
    return matrix

