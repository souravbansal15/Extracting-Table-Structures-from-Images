from __future__ import division
import csv
import numpy as np
from operator import itemgetter
from PIL import Image
import pytesseract
import cv2
from numpy import genfromtxt
from unstructured_tables import no_borders,incomplete_borders




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







def get_array(name):


    image =cv2.imread("./output/"+name+"_rescaled_DiagramOnly.png")
    img, threshold = adaptive_threshold(image)
    h_dmask, h_lines = find_lines(threshold, regions=None, direction='horizontal',line_scale=15, iterations=0)
    
    if(len(h_lines)==0):
        return no_borders(name)
    if(len(h_lines)<4):
        return incomplete_borders(name)

    v_dmask, v_lines = find_lines(threshold, regions=None, direction='vertical',line_scale=15, iterations=0)
    for l in range(len(h_lines)):
        print(h_lines[l])
    print("/////////////////")
    for l in range(len(v_lines)):
        print(v_lines[l])
    
    array_rows=np.concatenate((h_lines, v_lines))
    #array_rows = genfromtxt('./CSV/lines_ncert9.csv', delimiter=',')
    n_rows=len(array_rows)
    n_columns=len(array_rows[0])

    array_rows=array_rows.transpose()
  

    x_array=np.array([array_rows[0],array_rows[2]])
    y_array=np.array([array_rows[1],array_rows[3]])

    x_array=x_array.flatten()
    y_array=y_array.flatten()
  
    x_sorted_indexes=np.argsort(x_array)
    y_sorted_indexes=np.argsort(y_array)
    

    i=0
    while (i < (len(x_sorted_indexes)-1)):
        if((x_array[x_sorted_indexes[i+1]]-x_array[x_sorted_indexes[i]])<5):
            start=i
            end=i+1
            count=1
            sum=x_array[x_sorted_indexes[i]]
            while(x_array[x_sorted_indexes[end]]-x_array[x_sorted_indexes[start]]<5):
                sum+=x_array[x_sorted_indexes[end]]
                count=count+1
                end=end+1
                if(end==len(x_sorted_indexes)):
                    break
            for j in range(start,end):
                x_array[x_sorted_indexes[j]]=(sum/count)
            i=end-1
        i=i+1




    i=0
    while (i < (len(y_sorted_indexes)-1)):
        if((y_array[y_sorted_indexes[i+1]]-y_array[y_sorted_indexes[i]])<=5):
            start=i
            end=i+1
            count=1
            sum=y_array[y_sorted_indexes[i]]
            while(y_array[y_sorted_indexes[end]]-y_array[y_sorted_indexes[start]]<=5):
                sum+=y_array[y_sorted_indexes[end]]
                count=count+1
                end=end+1
                if(end==len(y_sorted_indexes)):
                    break
            print(start,end)
            for j in range(start,end):
                print(j)
                y_array[y_sorted_indexes[j]]=(round(sum/count))
            i=end-1
        i=i+1

    print("length =",len(y_sorted_indexes))




    x_array=x_array.reshape(2,n_rows)
    
    y_array=y_array.reshape(2,n_rows)
    final_array=np.array([x_array[0],y_array[0],x_array[1],y_array[1]])
    
    final_array=final_array.transpose()
    
    final_array=final_array
    print("/////////////////")
    print(final_array)
    return final_array