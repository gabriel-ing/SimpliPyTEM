import cv2 as cv
import ncempy.io as nci
import os
import cv2 as cv
import matplotlib.pyplot as plt
from PIL import Image, ImageOps, ImageFont, ImageDraw, ImageFilter
import numpy as np 
import time
import argparse
import mrcfile

def choose_scalebar_size(image,pixelSize, pixelUnit,xybin ):
    
    x,y = image.shape
    
    #make coordinates for the scalebar, currently set to y-12.5%,x-5% of image size from the bottom right corner 
    #of the image to bottom left of the scalebar - change this by editing /20 and /7.5 values (this just looked good to me)
    scalebar_y = y-int(y/20)
    scalebar_x = x-int(x/6)
    
    #possible scalebar sizes are given here, if its >500nm it should be in unit micron, hopefully this should only fail with very extreme examples
    
    possible_sizes = [0.5, 1,2,5,10,25,50,100,250,500]
    
    #to select sizes, iterate through possible sizes, if the width of the resulting scalebar (n*pixelsize) 
    #is over 15% of the image size, the size is chose, if none are over 15% of image size
    #the largest size is chosen as default
    
    for n in possible_sizes:

        width = n*1/pixelSize

        #print(n, image.shape([0]/10)
        if width>(x/15):
            break
            #print(width, x/15)
    #choose height of scalebar (default is scalebar width/6), convert width into an integer
    height = int(y/60)
    width = int(width)   
    
    return int(scalebar_x/xybin), int(scalebar_y/xybin), int(height/xybin), int(width/xybin), n
    
    
def choose_scale_color(color,new_arr, scalebar_x, scalebar_y, width, height):
#choose color - this can be given as black, white or grey in the function
    if color=='black':
        pixvalue = 0
        textcolor = 'black'
    elif color=='white':
        pixvalue = 255
        textcolor='white'
    elif color=='grey':
        pixvalue = 150
        textcolor='grey'
    else: #default is black, unless it is a particularly dark area - if the mean pixvalue of the scale bar region is significantly less than the overall image mean, the scalebar will be white
        
        if np.mean(new_arr[scalebar_y:scalebar_y+height,scalebar_x:scalebar_x+width])<np.mean(new_arr)/1.5:
            pixvalue = 255
            textcolor='white'
        else:
            pixvalue = 0
            textcolor = 'black'
    #add scalebar (set pixels to color) 
    return pixvalue, textcolor        

def make_scalebar(new_arr, scalebar_x, scalebar_y, width, height, pixelUnit, n, pixvalue,textcolor,xybin=1,textoff=0):
    #print(pixvalue, textcolor)
    new_arr[scalebar_y:scalebar_y+height,scalebar_x:scalebar_x+width]=pixvalue
    textposition = ((scalebar_x+width/2),scalebar_y-5)
    
    #if pixelUnit!='nm':
     #   Utext = str(n)+u'\u00b5'+ 'm'
      #  text = str(n)+'microns'
    #else:
    text = '{}{}'.format(n,pixelUnit) 
    Utext=  text  

    pil_image = Image.fromarray(new_arr)

    if textoff==0:
        draw = ImageDraw.Draw(pil_image)        
        
        fontsize=int(scalebar_x/(34))
        font = ImageFont.truetype("/Users/gabriel/helveticaneue.ttf", fontsize)
        draw.text(textposition, Utext, anchor ='mb', fill=textcolor, font=font, stroke_width=1)
        
    return pil_image, text

def image_conversion(image,xybin, med=True,medkernal=5,gauss =False, gauss_kernal =3 ):
        #apply median filter and gaussian blur
    
    print(image)
    print(image.dtype)
    image = image.astype('float32')
    if med==True:
    	try:
        	img_median = cv.medianBlur(image,medkernal)
    	except Exception:
    		print('median filter failed')
    		img_median=image
    if gauss==True:
        img_gauss = cv.GaussianBlur(img_median, (gauss_kernal,gauss_kernal),0)
    
    #Scale image between 0-255 (turn it into an 8bit greyscale image)
    
    new_arr = ((img_median - img_median.min()) * (1/(img_median.max() - img_median.min()) * 255)).astype('uint8')
   
    #these commands can increase contrast, by default the contrast is stretched to limits in previous line though
    #new_image = cv.convertScaleAbs(img_gauss, alpha=alpha, beta=beta)
    #new_image = cv.equalizeHist(new_arr)

    

    

    
    #Bin image to reduce filesize, comment out if you want full image size
    if xybin>1:
        new_arr = cv.resize(new_arr, (int(new_arr.shape[0]/xybin), int(new_arr.shape[1]/xybin)), interpolation=cv.INTER_CUBIC) 
    return new_arr
   


def Generate_preview_dm(file, color='', textoff=0, xybin=2, quality=80, foldername='Previews'):
    #make a folder called previews to save the folder 
    if foldername not in os.listdir('.'):
        os.mkdir(foldername)
        
    
    #read the dm3 fille with ncempy 
    print(file)

    if file[-4:-1]=='.dm':
        image, x, y, pixelSize, pixelUnit = open_dm(file)

    elif file[-4:]=='.mrc':
        image, x, y, pixelSize, pixelUnit = open_mrc(file)
    else:
        print(file[-4:-2])

    scalebar_x, scalebar_y, height, width,n = choose_scalebar_size(image, pixelSize, pixelUnit, xybin )
    
    new_arr = image_conversion(image, xybin, med=True, medkernal=3)

    pixvalue, textcolor = choose_scale_color(color, new_arr, scalebar_x, scalebar_y, width, height) 
    
    pil_image,text= make_scalebar(new_arr, scalebar_x, scalebar_y, width, height, pixelUnit,n,pixvalue,textcolor,xybin=xybin, textoff=0)
    if foldername=='':
        newname = file.split('.dm')[0]+'_'+text+'scale.jpg'
    else:
        #print('YES\n')
        #print(foldername.strip('\n'))
        newname = foldername.strip('\n') + '/' +file.split('.dm')[0]+'_'+text+'scale.jpg'
        print(newname)
    #newname = folder+file.split('.dm')[0]+'_'+text+'scale.jpg'
    
    pil_image.save(newname, quality=quality)

    print(newname, 'Done!')

def open_dm(file):
    dm_input = nci.dm.dmReader(file)
    if len(dm_input['data'].shape)==2:
        image = dm_input['data']
        dm = '_Image_'
    elif len(dm_input['data'].shape)==3:
        images = dm_input['data']
        image = np.average(images, axis=0)
        dm='_Video_'
    #extract x and y shapes
    x = image.shape[1]
    y = image.shape[0]
    pixelSize=dm_input['pixelSize'][-1]
    print(pixelSize,type(pixelSize))
    pixelUnit = dm_input['pixelUnit'][-1]
    return image, x, y, pixelSize, pixelUnit


def open_mrc(file):
    mrc= mrcfile.open(file)
    print(mrc.voxel_size)
    voxel_size = mrc.voxel_size
    pixelSize = float(str(voxel_size).split(',')[0].strip('('))
    image = mrc.data
    x = image.shape[1]
    y = image.shape[0]
    pixelUnit='nm'
    return image, x, y, pixelSize, pixelUnit



def motioncorrect_video(file):
    outfile = file.split('.')[0]+'.mrc'
    outfile_aligned = file.split('.')[0]+'_aligned.mrc'
    pixelsize = nci.dm.fileDM(file).scale[2]
    #print(pixelsize)
    sb.call('dm2mrc {} {} '.format(file, outfile), shell=True, cwd=os.getcwd())
    motion_cor_command = '~/Downloads/MotionCor2_1.4.4/MotionCor2_1.4.4_Cuda113-08-11-2021 -InMrc {} -OutMrc {} -Iter 10 -Tol 0.5 -Throw 1 -Kv 200 -PixSize {} '.format(outfile, outfile_aligned, pixelsize)
    sb.call(motion_cor_command, shell=True, cwd=os.getcwd())
    os.remove(outfile)
    return outfile_aligned
