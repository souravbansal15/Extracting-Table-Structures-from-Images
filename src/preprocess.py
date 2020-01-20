import sys, copy, cv2, scipy, os
import scipy
from skimage.morphology import thin
import numpy as np
from skimage.filters import threshold_sauvola
from PIL import Image
import logging
import csv

sys.stderr = open('errorlog.txt','w')
LOG_FILENAME='status.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

#Sauvola binarization- local thresholding technique: Instead of calculating a single global threshold for the entire image, several thresholds are calculated for every pixel by using specific formulae that take into account the mean and standard deviation of the local neighborhood (defined by a window centered around the pixel)
#Reference: J. Sauvola and M. Pietikainen,"Adaptive document image binarization",Pattern Recognition 33(2), pp. 225-236, 2000. Elsevier. 
#URL: DOI:10.1016/S0031-3203(99)00055-2

def binarization(image):
	binarized_image = copy.deepcopy(image)
	window_size = 33 #Parameter window_size determines the size of the window that contains the surrounding pixels, window size must be odd and greater than 1
	thresh_matrix = threshold_sauvola(image, window_size=window_size) #Return matrix of thresholds
	sauvola_image = image > thresh_matrix	#Comparing pixel value with the threshold
	binarized_image[sauvola_image == False] = 0  
	binarized_image[sauvola_image == True] = 255
	return binarized_image

#thins the binary_sauvola
def thin_image(DiagramOnly):
	#thinning the binary image (black: false, white: true)
	thinned = thin(DiagramOnly==0, max_iter = 9) #DiagramOnly==0 means thin the pixels with value 0(since foreground has value 0)
	#max_iter: Regardless of this parameter, the thinned image is returned immediately if an iteration produces no change. If this parameter is specified it thus sets an upper bound on the number of iterations performed.

	# image_res is a thinned grayscale image(unique values 0 and 255)
	DiagramOnly[thinned==True]=0
	DiagramOnly[thinned==False]=255
	return DiagramOnly
	
#marks different connected components
def Segmentation(image):                                                                  
	#scipy.ndimage.label takes 0 to be background and all non-zero to be foreground, so we need to change image as follows:

	# setting foreground pixels to 1 (initially foreground pixels [black] have value 0 in grayscale format)
	image[image == 0] = 1  
	# setting background pixels to 0
	image[image == 255] = 0

	# array([[1,1,1],[1,1,1],[1,1,1]]) is A structuring element that defines feature connections. 
	# segmented_matrix is an array where elements of each disconnected component are numbered uniquely, num_segments is the number of disconnected components
	segmented_matrix, num_segments = scipy.ndimage.label(image,np.array([[1,1,1],[1,1,1],[1,1,1]]))
	#structuring element ([[0,1,0],[1,1,1],[0,1,0]]) works on our dataset which has thick edges in diagrams. For thin edged diagrams or to be on the safe side, use structuring element ([[1,1,1],[1,1,1],[1,1,1]]) - it might join some nearly connected labels with main diagram but at least the main diagram edges will surely not be lost during disconnection.
	
	#np.savetxt("export_log.csv",segmented_matrix, delimiter=",")
	#logging.debug("num_segments "+str(num_segments))
	
	# find_objects returns an array of bounding box coordinates of slices found [((x1,x2), (y1,y2)) , (..)] where x1x2y1y2 are coordinates for bounding box of first slice (ie. object)
	slices = scipy.ndimage.find_objects(segmented_matrix)  
	
	#logging.debug("loc_array "+str(loc_array))
	
	return segmented_matrix, slices


#save and disconnects bounding box of labels
def DiagramTextSeperator(segmented_matrix, slices): 

	#SegmentedComponents is a dictionary having index as key and the original image of that disconnected component as value
	SegmentedComponents = {idx:segmented_matrix[i] for idx, i in enumerate(slices)}	#Images of every disconnected component
	
	BiggestComponent = max(list(SegmentedComponents), key = lambda s: (SegmentedComponents[s].shape[0]*SegmentedComponents[s].shape[1]))	#Determining SegmentedComponent having max area
	AreaBiggestComponent = SegmentedComponents[BiggestComponent].shape[0]*SegmentedComponents[BiggestComponent].shape[1]
	
	DiagramOnly = copy.deepcopy(segmented_matrix)
	TextOnly = copy.deepcopy(segmented_matrix)

	for i, s in enumerate(SegmentedComponents):
		if(SegmentedComponents[i].shape[0] > SegmentedComponents[i].shape[1]):
			height = SegmentedComponents[i].shape[1]
			width = SegmentedComponents[i].shape[0]
		else:
			height = SegmentedComponents[i].shape[0]
			width = SegmentedComponents[i].shape[1]

		if(SegmentedComponents[i].shape[0]*SegmentedComponents[i].shape[1] < 0.02*AreaBiggestComponent and (height/width > 0.1)):
			DiagramOnly[DiagramOnly == i+1] = 0 #erase labels from original diagram
		else:
			TextOnly[TextOnly == i+1] = 0	#erase diagram from original diagram

	TextOnly[TextOnly != 0] = 1
	TextOnly[TextOnly == 0] = 255
	TextOnly[TextOnly == 1] = 0

	DiagramOnly[DiagramOnly != 0] = 1
	DiagramOnly[DiagramOnly == 0] = 255
	DiagramOnly[DiagramOnly == 1] = 0
			
	return DiagramOnly, TextOnly


def main():
	img_name = sys.argv[1]   # command line  argument
	path_in = sys.argv[2]# input image path
	path_op = sys.argv[3] # path to output folder

	# 255: white 0: black
	image = cv2.imread(path_in+img_name,0)  # 0 indicates reading image in grayscale
	img_name = img_name.split(".")[0]; # extracts 104 from 104.png/104.jpg

	# padding the input image by 5 pixels on all 4 sides
	y = np.ones((5, image.shape[1])).astype(int)*255
	image = np.append(y,image,axis=0)
	image = np.append(image,y,axis=0)
	x = np.ones((image.shape[0],5)).astype(int)*255
	image = np.append(x,image,axis=1)
	image = np.append(image,x,axis=1) 
	scipy.misc.imsave(path_op+img_name+"_afterpadding.png",image)

	binarized_image = binarization(image)
	scipy.misc.imsave(path_op+img_name+"_binarized.png",binarized_image)
	logging.debug("Padding added")
	
	segmented_matrix, slices = Segmentation(binarized_image)

	DiagramOnly, TextOnly = DiagramTextSeperator(segmented_matrix, slices)
	scipy.misc.imsave(path_op+img_name+"_DiagramOnly.png", DiagramOnly)
	scipy.misc.imsave(path_op+img_name+"_TextOnly.png", TextOnly)

	ThinnedDiagramOnly = thin_image(DiagramOnly)
	scipy.misc.imsave(path_op+img_name+"_thinned.png",ThinnedDiagramOnly)   #using thinned_partial	

main()