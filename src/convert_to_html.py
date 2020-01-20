from __future__ import division
from numpy import empty
import cv2
from PIL import Image
import pytesseract
import numpy as np
from ocr import getText

def convert(matrix, image_obj,path_op,img_name):
    len_x=len(matrix[0])
    len_y=len(matrix)
    html_data = """
    <html>
        <head>
            <title>
        Table
            </title>
            <style>
            table, tr, td {
            border: 1px solid black;
            }
    </style>
        </head>
        <body>
        
        <table style="border: solid 1px #000000">
        <tr>"""

    #image1=cv2.imread('../output/image3_TextOnly.png')
    #img1 = r.rescaled(image1)

    #image_obj = Image.open('../output/image6_afterpadding.png')



    count_x=0
    count_y=0

    row_span=1
    col_span=1
    i=0
    j=0





    while (i<len_y-1) or (j<len_x-1):
        if(i==len_y-1):
            break
        if (j==0):
            html_data+="</tr><tr>"
        if matrix[i][j]!=(-1,-1):

            if (matrix[i][j+count_x+1]!=(-1,-1)) & (matrix[i+count_y+1][j]!=(-1,-1)):
                cropped_image = image_obj.crop((matrix[i][j][0],matrix[i][j][1],matrix[i][j+count_x+1][0],matrix[i+count_y+1][j][1]))
                col_span=col_span+count_x
                row_span=row_span+count_y
                html_data += "<td rowspan='" + str(row_span) + "' colspan='" + str(col_span) + "'>" + getText(cropped_image) + "</td>"
                count_x=0
                count_y=0
                row_span=1
                col_span=1
                if(j!=len_x-2):
                    j+=1
                else:
                    j=0
                    i+=1
                    
            else:
                if matrix[i][j+count_x+1]==(-1,-1):
                    count_x +=1
                if matrix[i+count_y+1][j]==(-1,-1):
                    count_y +=1
                    
        
        else:

            if(j!=len_x-2):
                j+=1
            else:
                j=0
                i+=1


    html_data += "</tr>"
    html_data += "</table></body></html>"

    with open(path_op+"csv/output_"+img_name+".html","w", encoding="utf-8") as html_fil:
        html_fil.write(html_data)