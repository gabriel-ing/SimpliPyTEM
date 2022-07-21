import cv2 as cv
import ncempy.io as nci
import os
import matplotlib.pyplot as plt
import numpy as np 


print('Dependancies imported')

def Generate_preview_dm3(dm3_file, color='', textoff=False):
    #make a folder called previews to save the folder 
    foldername = 'previews'
    if foldername not in os.listdir('.'):
        os.mkdir(foldername)
    
    #read the dm3 fille with ncempy 
    dm3_input = nci.dm.dmReader(dm3_file)
    #extract image from ncempy read 
    image = dm3_input['data']
    
    #extract x and y shapes
    x = image.shape[1]
    y = image.shape[0]

    
    #make coordinates for the scalebar, currently set to y-12.5%,x-5% of image size from the bottom right corner 
    #of the image to bottom left of the scalebar - change this by editing /20 and /7.5 values (this just looked good to me)
    
    scalebar_y = y-int(image.shape[0]/20)
    scalebar_x = x-int(image.shape[1]/7.5)
    

    #Save pixel size 
    pixelSize=dm3_input['pixelSize'][0]
    
    #possible scalebar sizes are given here, if its >500nm it should be in unit micron, hopefully this should only fail with very extreme examples
    possible_sizes = [1,2,5,10,25,50,100,250,500]
    

    #to select sizes, iterate through possible sizes, if the width of the resulting scalebar (n*pixelsize) 
    #is over 15% of the image size, the size is chose, if none are over 15% of image size
    #the largest size is chosen as default
    
    for n in possible_sizes:
        width = n*pixelSize
        #print(n, image.shape([0]/10)
        if width>(x/15):
            break
    #print(n)
    
    #choose height of scalebar (default is scalebar width/6), convert width into an integer
    height = int(y/60)
    width = int(width)
    
    #apply median filter and gaussian blur
    img_median = cv.medianBlur(image,5)
    img_gauss = cv.GaussianBlur(img_median, (3,3),0)
    
    #Scale image between 0-255 (turn it into an 8bit greyscale image)
    
    new_arr = ((img_median - img_median.min()) * (1/(img_median.max() - img_median.min()) * 255)).astype('uint8')
   
    #these commands can increase contrast, by default the contrast is stretched to limits in previous line though
    #new_image = cv.convertScaleAbs(img_gauss, alpha=alpha, beta=beta)
    #new_image = cv.equalizeHist(new_arr)

    #choose color - this can be given as black, white or grey in the function
    if color=='black':
        pixvalue = 0
        textcolor = (0,0,0)
    elif color=='white':
        pixvalue = 255
        textcolor=(255,255,255)
    elif color=='grey':
        pixvalue = 150
        textcolor=(150,150,150)
    else: #default is black, unless it is a particularly dark area - if the mean pixvalue of the scale bar region is significantly less than the overall image mean, the scalebar will be white
        
        if np.mean(new_arr[scalebar_y:scalebar_y+height,scalebar_x:scalebar_x+width])<np.mean(new_arr)/1.5:
            pixvalue = 255
            textcolor=(255,255,255)
        else:
            pixvalue = 0
            textcolor = (0,0,0)
    #add scalebar (set pixels to color)
    
    new_arr[scalebar_y:scalebar_y+height,scalebar_x:scalebar_x+width]=pixvalue
    
    #add label 
    if textoff==False:
        font= cv.FONT_HERSHEY_DUPLEX #can change to any opencv fonts, they're all quite rubbish 
        fontsize = image.shape[0]/1200 #this fontsize looks good to me
        text = '{}{}'.format(n,dm3_input['pixelUnit'][0]) 
        cv.putText(new_arr, text, (scalebar_x+3,scalebar_y-int(height*3/5)),font,fontsize, color=textcolor, thickness=int(fontsize*2.5))#can change thickness, color and position here 


    

    
    #Bin image to reduce filesize, comment out if you want full image size
    new_arr = cv.resize(new_arr, (int(new_arr.shape[0]/2), int(new_arr.shape[1]/2)), interpolation=cv.INTER_CUBIC) 
    #if you want to see it as it runs, can plot images heere
    #plt.gray()
    #plt.figure(figsize=(20,20))
    #plt.imshow(new_arr)
    #plt.show()
    
    #create filename(and path)
    newname = foldername+'/'+dm3_file.strip('.dm3')+'{}{}'.format(n,dm3_input['pixelUnit'][0])+'scale.jpg'
    status = cv.imwrite(newname, new_arr,[int(cv.IMWRITE_JPEG_QUALITY), 70])
    print(newname, 'saved?: ',status)

#collect the dm3 files in the folder and make a preview for them all 

dm3_files = [x for x in os.listdir('.') if x[-3:]=='dm3']
for file in dm3_files:
    Generate_preview_dm3(file)

