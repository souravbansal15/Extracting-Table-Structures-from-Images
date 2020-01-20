from junction_detection import get_junctions
import sys,cv2

from convert_to_html import convert
from PIL import Image
from table_detection import get_joints


img_name = sys.argv[1]   # command line  argument
path = sys.argv[2]# input image path
path_op = sys.argv[3] # path to output folder
factor = 1 # rescaling factor

# pil_image = PIL.Image.open('image.jpg')
# opencvImage = cv2.cvtColor(numpy.array(pil_image), cv2.COLOR_RGB2BGR)



# 255: white 0: black

#image = rescaled(i,factor) #rescaled image
# preprocess(cv2.cvtColor(image,cv2.COLOR_BGR2GRAY),path,path_op,img_name) # getting proprocessed images output

#gray = cv2.cvtColor(i,cv2.COLOR_BGR2GRAY)
# convert image format from cv2 to PIL
# image_obj = Image.fromarray(get_rescaled_Text_only(gray))

junctions = get_junctions(path,img_name,factor)

img_name = img_name.split(".")[0]; # extracts 104 from 104.png/104.jpg

if(junctions=="no_borders"):
    print("Image with no borders")
    #junctions = get_joints(Image.fromarray(thresh_img),1) # for image without borders
    junctions = get_joints(Image.open(path_op+img_name+"_rescaled_binarized.png"),factor)
    convert(junctions, Image.open(path_op+img_name+"_rescaled_afterpadding.png"),path_op,img_name)

elif(junctions=="incomplete_table"):
    print("Image with imcomplete borders")
    junctions = get_joints(Image.open(path_op+img_name+"_rescaled_TextOnly.png"),factor) # for image without borders
    convert(junctions, Image.open(path_op+img_name+"_rescaled_TextOnly.png"),path_op,img_name)

else:   
    convert(junctions, Image.open(path_op+img_name+"_rescaled_TextOnly.png"),path_op,img_name)

# if(c=="0"):
#     html_data = convert(junctions, Image.open(path_op+img_name+"_rescaled_afterpadding.png"))
# else:

