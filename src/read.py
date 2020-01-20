from __future__ import division
import csv
import numpy as np
from operator import itemgetter
from PIL import Image
import pytesseract
import cv2
from rows import get_array
import sys

name=sys.argv[1]
readCSV = get_array(name)
if !(readCSV):
    return
img_name=name
x_points=set()
y_points=set()
horizontal_lines=[]
vertical_lines=[]
for row in readCSV:
    for n in range(len(row)):
        row[n]=float(row[n])
    if(row[0]==row[2]):
        vertical_lines.append(row)
    else:
        horizontal_lines.append(row)
    x_points.add(float(row[0]))
    y_points.add(float(row[1]))
    x_points.add(float(row[2]))
    y_points.add(float(row[3]))

print("no of horizontal lines")
print(len(horizontal_lines))
for l in range(len(horizontal_lines)):
    print(horizontal_lines[l])
print("no of vertical lines")
print(len(vertical_lines))
for l in range(len(vertical_lines)):
    print(vertical_lines[l])


x_set=sorted(x_points)
y_set=sorted(y_points)


print("x points are ", x_set)
print("y points are ", y_set)
'''
for i in range(len(x_points)-1):
    sum=0
    if(x_set[i+1]-x_set[i]>5):
        x.append(x_set[i])
    else:
        count=1
        start=i
        iter=i+1
        sum=x_set[i]
        while(x_set[iter]-x_set[start]<5):
            sum+=x_set[iter]
            count+=1
        x.append((sum/count))
        i=iter-1
x.append(x_set[i+1])
i=0
while (i<(len(y_set)-1)):
    if(y_set[i+1]-y_set[i]>5):
        y.append(y_set[i])
    else:
        count=1
        start=i
        sum=y_set[i]
        iter=i+1
        while(y_set[iter]-y_set[start]<5):
            sum+=y_set[iter]
            iter+=1
            count+=1
            if(iter==len(y_set)):
                break
        y.append(sum/count)
        i=iter-1
    i=i+1
y.append(y_set[i])     
'''
x=x_set
y=y_set
print("x points are ", x)
print("y points are ", y)

n_vertical=len(vertical_lines)
n_horizontal=len(horizontal_lines)

for h in range(len(horizontal_lines)):
    if(horizontal_lines[h][2]<horizontal_lines[h][0]):
        temp=horizontal_lines[h][0]
        horizontal_lines[h][0]=horizontal_lines[h][2]
        horizontal_lines[h][2]=temp
horizontal_lines=sorted(horizontal_lines,key=itemgetter(1,0))

for v in range(len(vertical_lines)):
    if(vertical_lines[v][3]<vertical_lines[v][1]):
        temp=vertical_lines[v][1]
        vertical_lines[v][1]=vertical_lines[v][3]
        vertical_lines[v][3]=temp
vertical_lines=sorted(vertical_lines,key=itemgetter(0,1))

print("/////////////////")
print(horizontal_lines)
print("/////////////////")
print(vertical_lines)
print("/////////////////")
print(x)
print(y)
print("/////////////////")
#horizontal lines
indexes_h=[]
horizontal_lines_np=np.array(horizontal_lines).transpose()
h_lines=np.zeros((len(y), (len(x)-1)))
for i in range(len(y)):
    indexes_h=np.where(horizontal_lines_np[1]==y[i])
    for j in range(len(x)-1):
        flag=0
        for index in range(len(indexes_h[0])):
            a=indexes_h[0][index]
            if ((horizontal_lines[a][0]<=x[j]) and (horizontal_lines[a][2]>=x[j+1])):
                flag=1
                break
        if(flag==0):
            h_lines[i][j]=1
print("For Horizontal Lines")
print(h_lines)

i=0
j=0
#vertical lines
indexes_v=[]
vertical_lines_np=np.array(vertical_lines).transpose()
v_lines=np.zeros((len(x),(len(y)-1)))
for j in range(len(x)):
    indexes_v=np.where(vertical_lines_np[0]==x[j])
    for i in range(len(y)-1):
        flag=0
        for index in range(len(indexes_v[0])):
            a=indexes_v[0][index]
            if((vertical_lines[a][1]<=y[i]) and (vertical_lines[a][3]>=y[i+1])):
                flag=1
                break
        if(flag==0):
            v_lines[j][i]=1
print("For Vertical Lines")
v_lines=v_lines.transpose()
print(v_lines)

i=0
j=0
#convert to HTML

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
        """

image_obj=Image.open("./output/"+img_name+"_rescaled_TextOnly.png")
spans=[]
while (i<(len(h_lines)-1)):
    html_data+="""<tr>"""
    j=0
    while (j<(len(h_lines[i]))):
        if((h_lines[i][j]==0) and (v_lines[i][j]==0)):
            count_x=1
            count_y=1
            h_iter=i+1
            v_iter=j+1
            while (h_lines[h_iter][j]!=0):
                count_y=count_y+1
                h_iter=h_iter+1
            while (v_lines[i][v_iter]!=0):
                count_x=count_x+1
                v_iter=v_iter+1
            rowspan=count_y
            colspan=count_x
            cropped_image=image_obj.crop((x[j],y[i],x[j+colspan],y[i+rowspan]))
            #cropped_image.save("../output/csv/"+str(i)+str(j)+".png")
            str_detected=str(pytesseract.image_to_string(cropped_image, config="psm -6"))
            html_data += "<td rowspan='" + str(rowspan) + "' colspan='" + str(colspan) + "'>" + str_detected + "</td>"
            spans.append([rowspan,colspan])
        j=j+1
    html_data += "</tr>"
    i=i+1
html_data += "</table></body></html>"

with open("./output/csv/output_"+img_name+".html","w", encoding="utf-8") as html_fil:
        html_fil.write(html_data)


