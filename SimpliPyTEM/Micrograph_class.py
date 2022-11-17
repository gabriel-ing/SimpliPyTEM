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
import subprocess as sb
from copy import deepcopy
from scipy.signal import wiener
plt.gray()

class Micrograph: 

    def __init__(self):
        self.filename = ''
        self.image='Undefined'
        self.pixel_size= 'Undefined'
        self.foldername='Images'


    def set_foldername(self, foldername='Images'):
        self.foldername = foldername


        '''-------------------------------------------------------------------------------------------------------------------------------------------
        SECTION: IMPORT IMAGES

            can be imported as dm3, dm4, mrc, **numpy array or tifs ** add the tifs 
            need to add numpy and tif functionality


        '''
    

    def open_dm(self, file, video_average=True):
        dm_input = nci.dm.dmReader(file)
        if len(dm_input['data'].shape)==2:
            image = dm_input['data']
            

        # at the moment it automatically averages a video into a single image. This will be changed soon to allow for video analysis.
        elif len(dm_input['data'].shape)==3:
            print('File is an image stack, averaging frames together, if you would open as a video, please us MicroVideo object')
            if video_average==True:

                images = dm_input['data']
                image= np.sum(images, axis=0)
            else:
                image=dm_input['data'][0]
        
        dmfile = nci.dm.fileDM(file)
        self.metadata_tags =dmfile.allTags        
        #extract x and y shapes
        x = image.shape[1]
        y = image.shape[0]
        pixelSize=dm_input['pixelSize'][-1]
        #print(pixelSize,type(pixelSize))
        pixelUnit = dm_input['pixelUnit'][-1]
        self.filename = file
        self.image = image
        self.x = x 
        self.y = y
        self.pixelSize= float(pixelSize)
        self.pixelUnit = pixelUnit
        
        #this line removes dead pixels which are super bright (any pixel which is more than mean+25*stddeviation
        self.image[self.image>self.image.mean()+self.image.std()*25]=image.mean()
        # this line converts the image to a float32 datatype, this will make it run slower if it starts out as a 8 or 16 bit, I maybe should account for this, but its also required for median filter and others, so I'm performing as default. 
        self.image = self.image.astype('float32')
        #       #return image, x, y, pixelSize, pixelUnit
        self.shape=self.image.shape
        print('{} opened as a Micrograph object'.format(file))

    def open_mrc(self, file):
        mrc= mrcfile.open(file)
        print(mrc.voxel_size)
        voxel_size = mrc.voxel_size
        self.pixelSize = float(str(voxel_size).split(',')[0].strip('('))
        self.image = mrc.data
        self.x = self.image.shape[1]
        self.y = self.image.shape[0]
        self.pixelUnit='nm'
        self.filename = file

        # this line converts the image to a float32 datatype, this will make it run slower if it starts out as a 8 or 16 bit, I maybe should account for this, but its also required for median filter and others, so I'm performing as default. 
        self.image = self.image.astype('float32')
        self.shape=self.image.shape




        
    def save_image(self, **kwargs):#use name='outname' to give a filename   
        if self.foldername not in os.listdir('.') and self.foldername.split('/')[-1] not in os.listdir('/'.join(self.foldername.split('/')[:-1])):
            os.mkdir(self.foldername)        
        if 'name' in kwargs:
                name = kwargs['name']
        else:
                name = '.'.join(self.filename.split('.')[:-1])
        name += '_'+self.text+'scale.jpg'
        if self.foldername!='':
                name = '/'+self.foldername.strip('/n') + '/' + name.split('/')[-1]
        #if self.foldername=='':
        #    newname = self.filename.split('.dm')[0]+'_'+self.text+'scale.jpg'
        #else:
        #    newname = self.foldername.strip('\n') + '/' +self.filename.split('.dm')[0]+'_'+self.text+'scale.jpg'
        cv.imwrite(name,self.image)
        #self.pil_image.save(name, quality=self.quality)
        print(name, 'Done!')

        #    def average_video(self):
        #       self.image = np.average(image, axis=0)
    

    

        
    '''-----------------------------------------------------------------------------------------------------------------------
        SECTION: BASIC FUNCTIONS

            add_frames : this sums all the frames of a video together if the frames are saved individually, input is a list of frames, can be generated using the group frames method in the motioncorrection section 
            convert to 8bit: this is important to create a easily openable and lower filesize output image good for viewing. 


    '''
    def convert_to_8bit(self):
        #  this will scale the pixels to between 0 and 255, this will automatically scale the image to its max and min
        image8bit = deepcopy(self)
        image8bit.image = ((self.image - self.image.min()) * (1/(self.image.max() - self.image.min()) * 255))
        image8bit.image = image8bit.image.astype('uint8')
        return image8bit

    def bin_image(self, value=2):
            binned_image = deepcopy(self)
            binned_image.image = cv.resize(self.image, (int(self.image.shape[0]/value), int(self.image.shape[1]/value)), interpolation=cv.INTER_CUBIC) 
            #self.pixelSize= self.pixelSize*value
            binned_image.reset_xy()
            return binned_image

    #def add_frames(self, frames):
    #    for frame in frames:
    #        next_frame = nci.dm.dmReader(frame)
    #        self.image = self.image + next_frame['data']

    # This, much like the filters below returns the enhanced version as a new object, I have made it this way to allow tuning of alpha and beta.
    def enhance_contrast(self, alpha=1.5, beta=0, gamma=''):
        enhanced_image = cv.convertScaleAbs(self.image, alpha=alpha, beta=beta)
        #print(self.image.dtype)
        #enhanced_image = cv.equalizeHist(enhanced_image)
        enhanced_object = deepcopy(self)
        enhanced_object.image = enhanced_image
        if type(gamma)==float or type(gamma)==int:
            if enhanced_object.image.dtype!='uint8':
                enhanced_object.convert_to_8bit()
            LUT =np.empty((1,256), np.uint8)
            for i in range(256):
                LUT[0, i]=np.clip(pow(i/255.0,gamma)*255.0, 0, 255)
            res =cv.LUT(enhanced_object.image, LUT) 
            print('Gamma adjusted...')

        return enhanced_object

    def equalizeHist(self):
        enhanced_object = deepcopy(self)
        enhanced_object = enhanced_object.convert_to_8bit()
        enhanced_object.image = cv.equalizeHist(enhanced_object.image)
        return enhanced_object

    '''-----------------------------------------------------------------------------------------------------------------------
    SECTION: SCALEBAR

        Adds well-sized scalebar to the image. use make_scalebar function for use. 




    '''
    def choose_scalebar_size(self):
        
        y,x = self.image.shape
        
        #make coordinates for the scalebar, currently set to y-12.5%,x-5% of image size from the bottom right corner 
        #of the image to bottom left of the scalebar - change this by editing /20 and /7.5 values (this just looked good to me)
        scalebar_y = y-int(y/25)
        scalebar_x = x-int(x/6.5)
        #print(x,scalebar_x)
        #possible scalebar sizes are given here, if its >500nm it should be in unit micron, hopefully this should only fail with very extreme examples
        
        possible_sizes = [0.5, 1,2,5,10,25,50,100,250,500]
        
        #to select sizes, iterate through possible sizes, if the width of the resulting scalebar (n*pixelsize) 
        #is over 15% of the image size, the size is chose, if none are over 15% of image size
        #the largest size is chosen as default
        
        for n in possible_sizes:
            width = n*1/self.pixelSize
            #print(n, image.shape([0]/10)
            if width>(x/15):
                break
                #print(width, x/15)
        #choose height of scalebar (default is scalebar width/6), convert width into an integer
        height = int(y/60)
        width = int(width)   
        self.scalebar_x = int(scalebar_x)
        self.scalebar_y = int(scalebar_y)
        self.height = int(height)
        self.width = int(width)
        self.n = n
    #return int(scalebar_x/xybin), int(scalebar_y/xybin), int(height/xybin), int(width/xybin), n



    def choose_scalebar_color(self,color):
    #choose color - this can be given as black, white or grey in the function
        if color=='black':
            self.pixvalue = 0
            self.textcolor = 'black'
        elif color=='white':
            self.pixvalue = 255
            self.textcolor='white'
        elif color=='grey':
            self.pixvalue = 150
            self.textcolor='grey'
        else: #default is black, unless it is a particularly dark area - if the mean pixvalue of the scale bar region is significantly less than the overall image mean, the scalebar will be white
            
            if np.mean(self.image[self.scalebar_y:self.scalebar_y+self.height,self.scalebar_x:self.scalebar_x+self.width])<np.mean(self.image)/1.5:
                self.pixvalue = 255
                self.textcolor='white'
            else:
                self.pixvalue = 0
                self.textcolor = 'black'
        #add scalebar (set pixels to color) 

        #return pixvalue, textcolor        


    def make_scalebar(self, texton = True, color='Auto'):
        #print(pixvalue, textcolor)
        self.choose_scalebar_size()
        self.choose_scalebar_color(color)
        
        self.image[self.scalebar_y:self.scalebar_y+self.height,self.scalebar_x:self.scalebar_x+self.width]=self.pixvalue
        
        textposition = ((self.scalebar_x+self.width/2),self.scalebar_y-5)
        
        #if pixelUnit!='nm':
         #   Utext = str(n)+u'\u00b5'+ 'm'
          #  text = str(n)+'microns'
        #else:
        self.text = '{}{}'.format(self.n,self.pixelUnit) 
         

        pil_image = Image.fromarray(self.image)

        if texton==True:
            #print('textoff')
            draw = ImageDraw.Draw(pil_image)        
            
            fontsize=int(self.scalebar_x/(25))
            font = ImageFont.truetype("/home/bat_workstation/helveticaneue.ttf", fontsize)
            draw.text(textposition, self.text, anchor ='mb', fill=self.textcolor, font=font, stroke_width=1)
            self.image = np.array(pil_image)    



    '''------------------------------------------------------------------------------------------------------------------------
        SECTION: IMAGE FILTERS
        These are filters to improve the visibility of features or decrease the noise levels. Included features are 
            
            - Median filter: performs a median filter with kernal size defined in the call (default is 3)
            - Gaussian filter: performs a Gaussian filter with kernal size defined in the call (default is 3)
            - Weiner filter: performs a Weiner filter with kernal size defined in the call (default is 5)
            - Low pass filter: performs a 2D fourier transform of the image and removes the  
            - Non-local means filter: this compares similar regions of the image and denoises by averaging across them. This is performed by openCV, and more info can be found here: https://docs.opencv.org/3.4/d5/d69/tutorial_py_non_local_means.html

    These filters return an object with the same properties and methods (a copied instance of the class)
    Therefore to use: 

        filtered_micrograph = micrograph.gaussian_filter()
        plt.imshow(filtered_micrograph.image)
        filtered_micrograph.make_scalebar()


    '''
    def low_pass_filter(self, radius):
    # This low pass filters the image. The pixel size is used to scale the radius to whatever the pixel unit is (ie radius 10 is 10nm/10um)
    # If pixelsize is undefined the radius will refer to pixels only
        
        N=self.image.shape[0]
        if type(self.pixelSize)==int or type(self.pixelSize)==float and self.pixelSize!=0:
            radius=int((N*self.pixelSize)/radius)
        
            
        fft = np.fft.fft2(self.image)
        fshift = np.fft.fftshift(fft)
        magnitude_spectrum = np.log(np.abs(fshift))
        rows, cols = self.image.shape
        crow, ccol = int(rows/2), int(cols/2)
        fshift_filtered=np.copy(fshift)
        mask = np.zeros_like(self.image)

        mask = cv.circle(mask, (crow, ccol),radius*2, 1, -1) 
        #print(fshift_filtered)
        fcomplex = fshift[:,:]*1j
        fshift_filtered = mask*fcomplex
        f_filtered_shifted = np.fft.fftshift(fshift_filtered)
        #magnitude_spectrum_filter = np.log(np.abs(f_filtered_shifted))
        inv_image = np.fft.ifft2(f_filtered_shifted)
        filtered_image = np.abs(inv_image)
        filtered_image -= filtered_image.min()
        filtered_object = deepcopy(self)
        filtered_object.image = filtered_image
        return filtered_object

    def median_filter(self, kernal=3):
        filtered_image = cv.medianBlur(self.image,kernal)
        filtered_object = deepcopy(self)
        filtered_object.image = filtered_image
        return filtered_object

    def weiner_filter(self, kernal=5):
        
        filtered_image = wiener(self.image, (kernal, kernal))
        filtered_object = deepcopy(self)
        filtered_object.image = filtered_image
        return filtered_object

    def NLM_filter(self, h=5):
        filtered_image = cv.fastNlMeansDenoising(np.uint8(self.image), h)
        filtered_object = deepcopy(self)
        filtered_object.image = filtered_image
        return filtered_object

    def gaussian_filter(self, kernal=3):
        filtered_image = cv.GaussianBlur(self.image, (kernal,kernal),0)
        filtered_object = deepcopy(self)
        filtered_object.image = filtered_image
        return filtered_object



    '''
    ------------------------------------------------------------------------------------------------------------
    Section Visualising images

    used for plotting images using matplotlib. Functions very basic so only meant for rapid use, for better figures write own function or use save command

    '''
    def imshow(self, title=''):
        plt.subplots(figsize=(30,20))
        plt.imshow(self.image)
        if title!='':
            plt.title(title, fontsize=30)
        plt.show()

    def show_pair(self,other_image, title1='', title2=''):
        fig, ax = plt.subplots(1,2, figsize=(30,20))
        ax[0].imshow(self.image)
        if title1!='':
            ax[0].set_title(title1, fontsize=30)

        ax[1].imshow(other_image)
        if title2!='':
            ax[1].set_title(title2, fontsize=30)
        plt.show()


    '''--------------------------------------------------------------------------------
    SECTION: METADATA

        If a dm file has been opened, the metadata is saved in MicroVideo.metadata_tags, this is unformatted and awkward to use
        but all the raw data can be found. These methods allow easy extraction of some key metadata items: mag, voltage,
        exposure and aquisition date/time. 
    '''
    def show_metadata(self):
        for tag in self.metadata_tags:
            print('{} : {}\n'.format(tag, self.metadata_tags[tag]))


    def get_mag(self):
        indicated_mag = self.metadata_tags['.ImageList.2.ImageTags.Microscope Info.Formatted Indicated Mag']
        actual_mag = self.metadata_tags['.ImageList.2.ImageTags.Microscope Info.Formatted Actual Mag']

        print('Indicated mag: {}'.format(indicated_mag))
        print('Actual mag: {}'.format(actual_mag))
        self.indicated_mag = self.metadata_tags['.ImageList.2.ImageTags.Microscope Info.Indicated Magnification']
        self.actual_mag = self.metadata_tags['.ImageList.2.ImageTags.Microscope Info.Actual Magnification']
        return self.indicated_mag, self.actual_mag

    def get_voltage(self):
        self.voltage = self.metadata_tags['.ImageList.2.ImageTags.Microscope Info.Voltage']
        return self.voltage

    def get_exposure(self):
        #print('Frame rate : {}fps'.format(self.fps))
        #print('Exposure time per frame: {}s '.format(1/self.fps))
        print('Imaging time: {}s'.format(self.metadata_tags['.ImageList.2.ImageTags.Acquisition.Parameters.High Level.Exposure (s)']))
        self.exposure = self.metadata_tags['.ImageList.2.ImageTags.Acquisition.Parameters.High Level.Exposure (s)']
        return self.exposure

    def get_date_time(self): 
        self.AqDate = self.metadata_tags['.ImageList.2.ImageTags.DataBar.Acquisition Date']
        self.AqTime = self.metadata_tags['.ImageList.2.ImageTags.DataBar.Acquisition Time']
        print('Date: {} '.format(self.AqDate))
        print('Time {} '.format(self.AqTime))
        return self.AqDate, self.AqTime

    '''---------------------------------
    SECTION MOTION CORRECTION

    This defines using motioncor2 to align video frames, these frames either need to be saved individually, in which case the function group_frames is needed on the image set before use
    Motioncorrect_video works on a dm4 file, converts it to mrc and then runs motioncor on this image stack. 


    '''        
    def motioncor_frames(self, frames_dict):
        for vid in frames_dict:
            frames = frames_dict[vid]
            outfile = '_'.join(frames[0].split('-')[:-1])+'.mrc'
            outfile_aligned = '_'.join(frames[0].split('.')[:-1])+'_aligned.mrc'
            pixelsize = nci.dm.fileDM(frames[0]).scale[2]
            sb.call('dm2mrc *{}-* {} '.format(vid, outfile), shell=True, cwd=os.getcwd())
            motion_cor_command = '~/Downloads/MotionCor2_1.4.4/MotionCor2_1.4.4_Cuda113-08-11-2021 -InMrc {} -OutMrc {} -Iter 10 -Tol 0.5 -Throw 1 -Kv 200 -PixSize {} '.format(outfile, outfile_aligned, pixelsize)
            sb.call(motion_cor_command, shell=True, cwd=os.getcwd())
            os.remove(outfile)
            self.open_mrc(outfile_aligned)  

    def motioncorrect_video(self, file):
        outfile = '_'.join(file.split('.')[:-1])+'.mrc'
        outfile_aligned = '_'.join(file.split('.')[:-1])+'_aligned.mrc'
        pixelsize = nci.dm.fileDM(file).scale[2]
        #print(pixelsize)
        sb.call('dm2mrc {} {} '.format(file, outfile), shell=True, cwd=os.getcwd())
        motion_cor_command = '~/Downloads/MotionCor2_1.4.4/MotionCor2_1.4.4_Cuda113-08-11-2021 -InMrc {} -OutMrc {} -Iter 10 -Tol 0.5 -Throw 1 -Kv 200 -PixSize {} '.format(outfile, outfile_aligned, pixelsize)
        sb.call(motion_cor_command, shell=True, cwd=os.getcwd())
        os.remove(outfile)
        self.open_mrc(outfile_aligned)            

     


    '''-----------------------------------------------------------------------------
    SECTION: DEPRECIATED FUNCTIONS


    '''



    # this is depreciated as functions within it have become standalone methods. 
    def image_conversion(self):
        #apply median filter and gaussian blur
        
        #print(self.image)
        print(self.image.dtype)
        self.image = self.image.astype('float32')
        if self.med==True:
            try:
                img_median = cv.medianBlur(self.image,self.medkernal)
            except Exception:
                print('median filter failed')
                img_median=self.image
        if self.gauss==True:
            img_gauss = cv.GaussianBlur(img_median, (self.gauss_kernal,self.gauss_kernal),0)
        
        #Scale image between 0-255 (turn it into an 8bit greyscale image)
        
        self.image = ((img_median - img_median.min()) * (1/(img_median.max() - img_median.min()) * 255)).astype('uint8')
       
        #these commands can increase contrast, by default the contrast is stretched to limits in previous line though
        #new_image = cv.convertScaleAbs(img_gauss, alpha=alpha, beta=beta)
        #new_image = cv.equalizeHist(new_arr)

        if self.xybin>1:
            self.image = cv.resize(self.image, (int(self.image.shape[0]/self.xybin), int(self.image.shape[1]/self.xybin)), interpolation=cv.INTER_CUBIC) 
            self.pixelSize= self.pixelSize*self.xybin

    def default_pipeline(self, medianfilter=3, gaussian_filter=0, scalebar=True, texton = True, bin=2):
        if self.image.shape == 3:
            self.average_video()
        #self.image_conversion()
        self.make_scalebar()
        
        
        self.save_image()




# I had to move default pipeline outside of the class because the filters make a new instance of the class and I didnt want to multiply the number of instances in memory. 
# Use: default_pipeline(micrograph)
def default_pipeline(Micrograph_object,  medfilter=3, gaussfilter=0, scalebar=True, texton = True, xybin=2, color='Auto',**kwargs):
    if type(medfilter)==int and medfilter!=0: 
        Micrograph_object = Micrograph_object.median_filter(medfilter)
    
    if type(gaussfilter)==int and gaussfilter!=0:  
        Micrograph_object = Micrograph_object.gaussian_filter(medfilter)

    if xybin!= 0 and xybin!=1:
        Micrograph_object.bin_image(xybin)

    if 'name' in kwargs:
        name = kwargs['name']
    else:
        name = '.'.join(Micrograph_object.filename.split('.')[:-1])
    
    #if 'outdir' in kwargs:
        
    Micrograph_object = Micrograph_object.enhance_contrast()
    Micrograph_object.convert_to_8bit()

    if scalebar==True:
        Micrograph_object.make_scalebar(texton=texton, color=color)

    if 'outdir' in kwargs:
        Micrograph_object.save_image(name=name,outdir=kwargs['outdir'])
    else:
        Micrograph_object.save_image(name=name) 
    #Micrograph_object.save_image(outname=name)




def group_frames(frames):
    prefixes = []
    prefix_set=set()
    frames.sort()
    tups = []
    organised_dict= {}
    for file in frames:
        file2 = file[:-4]
        end = file2[-9:]
        ids = end.split('-')
        vid_id = ids[0]
        frame_id = ids[1]
        tups.append((file, vid_id, frame_id))
        prefix_set.add(vid_id)

    for prefix in prefix_set: 
        images_per_prefix = [x[0] for x in tups if x[1]==prefix]
        organised_dict[prefix]=images_per_prefix
        return organised_dict
