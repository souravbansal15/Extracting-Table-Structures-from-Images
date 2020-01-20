from PIL import Image
import cv2
import pytesseract


def get_joints(im,factor):
    width, height = im.size
    #for h_lines
    l=[]
    threshold_count=0
    threshold=50
    count_pre=0
    blacks=0
    for y in range(height):
        count=0
        for x in range(width):
            if (im.getpixel((x,y))==0):
                count+=1
        l.append(count)
        if (count_pre!=0) & (count ==0):
            blacks+=1
        count_pre=count
        if (count!=0):
            threshold_count+=1
    if(blacks!=0):
        threshold=0.6*threshold_count/blacks

    #for vlines
    x=0
    y=0
    l_vlines=[]
    for x in range(width):
        count_v=0
        for y in range(height):
            if (im.getpixel((x,y))==0):
                count_v +=1
        l_vlines.append(count_v)


    i=0
    hlines=[]
    while i>=0:
       
        if l[i]==0:
            index_start=i
            index_end=i
            while l[index_end]==0:
                index_end+=1
                if index_end==len(l):
                    break
            if (index_end-index_start>=threshold):
                hlines.append(int((index_start+index_end-1)/2))
            i=index_end
            if index_end==len(l):
                break
        i=i+1
        if i==len(l):
            break


    print(l)
    print(l_vlines)
    #for vertical lines

    j=0

    vlines=[]
    while j>=0:
        if l_vlines[j]==0:
            index_start=j
            index_end=j
            while l_vlines[index_end]==0:
                index_end+=1
                if index_end==len(l_vlines):
                    break
            if (index_end-index_start)>(5*factor):
                vlines.append(int((index_start+index_end-1)/2))
            j=index_end
            if index_end==len(l_vlines):
                break
            
        j=j+1
        if j==len(l_vlines):
            break


    matrix=[]
    for n in range(len(hlines)):
        row=[]
        for m in range(len(vlines)):
            row.append((vlines[m],hlines[n]))
        matrix.append(row)
    print(matrix)
    return (matrix)
