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
import tifffile
plt.gray()

class Micrograph: 
    '''
    A class holding the micrograph image data along with associated parameters and methods.
    ... 
    Attributes
    ----------
    filename:str
        The file name opened (blank if not opened in object)
    pixelSize:float
        The pixel size in the image, should be initialised when opening data assuming the pixel size is included, if not can easily be altered
    pixelUnit:str
        The unit of the pixel size
    metadata_tags:dict
        The metadata of the file should be stored in this dictionary (works with digital micrograph files)
    shape:tuple
        The shape of the image 
    x:int
        The size of the x axis in the image
    y:int    
        The size of the y axis in the image

    Methods
    -------
    Filehandling: 

    open_dm(filename, video_average=True):
        Opens Digital Micrograph (dm3 or dm4) files
    open_mrc(filename):
        opens .mrc files
    write_image(name='', ftype='jpg', **kwargs)    
        Writes image files, filetype jpg or tif can be assigned with the suffix of the name or the ftype option. 
    

    Basic image functions: 

    bin_image(value=2):
        Bins the image on the x and y axis by the value given (default 2), returns a new object. 
    convert_to_8bit():
        Scales the data between 0 and 255 and makes the datatype 8-bit, returns a new object.
    enhance_contrast(alpha, beta, gamma):
        enhances contrast
    equalizeHist():
        converts to 8 bit and equalises the histogram, returns a new object.
    reset_xy():
        resets the image shape, x and y properties (if its cropped or changed image or similar)
    

    Fetching Metadata:
    
    get_exposure():
        Prints and returns the exposure time metadata
    get_voltage():
        Prints and returns the voltage metadata
    get_mag():
        Prints and returns the image magnification
    get_date_time():
        prints and returns the image aquisition date and time
    show_metadata()
        prints all the metadata tags and associated values
    




    '''
    def __init__(self):
        self.filename = ''
        self.image='Undefined'
        self.pixel_size= 'Undefined'





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




        
    def write_image(self, name='', ftype='jpg', **kwargs):#use name='outname' to give a filename   
        #if self.foldername!='':
        
        #if self.foldername not in os.listdir('.') and self.foldername.split('/')[-1] not in os.listdir('/'.join(self.foldername.split('/')[:-1])):
        #    print(self.foldername)
        #    os.mkdir(self.foldername)        
        if 'outdir' in kwargs:
            outdir = str(kwargs['outdir'])
            if '/' in outdir:
                if outdir.split('/')[-1] not in os.listdir('/'.join(outdir.split('/')[:-1])):
                    os.mkdir(outdir)
            elif outdir not in os.listdir('.'):
                os.mkdir(outdir)
            name=outdir+'/'+name    

        if name!='':
                if name[-3:]=='jpg':
                    ftype='jpg'
                elif name[-3:]=='tif':
                    ftype='tif'    
                if len(name.split('.'))>1:
                    name='.'.join(name.split('.')[:-1])

        else:
                name = '.'.join(self.filename.split('.')[:-1])

        try:
            name += '_'+self.scalebar_size+'scale.{}'.format(ftype)
        except AttributeError:
            name+='.'+ftype
        #if self.foldername!='':
        #        name = '/'+self.foldername.strip('/n') + '/' + name.split('/')[-1]
        #if self.foldername=='':
        #    newname = self.filename.split('.dm')[0]+'_'+self.text+'scale.jpg'
        #else:
        #    newname = self.foldername.strip('\n') + '/' +self.filename.split('.dm')[0]+'_'+self.text+'scale.jpg'
        
        if ftype=='jpg':
            if self.image.max()!=255 or self.image.min()!=0:
                print(self.image.max(), self.image.min())
                self = self.convert_to_8bit()
                print('converting to 8bit')
            cv.imwrite(name,self.image)
        elif ftype=='tif':
            tifffile.imsave(name, self.image,imagej=True, resolution=(1/self.pixelSize, 1/self.pixelSize), metadata={'unit':self.pixelUnit})

        #self.pil_image.save(name, quality=self.quality)
        print(name, 'Done!')

        #    def average_video(self):
        #       self.image = np.average(image, axis=0)
    
    def reset_xy(self):
            self.x = self.image.shape[1]
            self.y = self.image.shape[0]

    

        
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
            binned_image.image = cv.resize(self.image, (int(self.image.shape[1]/value), int(self.image.shape[0]/value)), interpolation=cv.INTER_CUBIC) 
            binned_image.pixelSize= binned_image.pixelSize*value
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
        self.scalebar_size = '{}{}'.format(self.n,self.pixelUnit) 
         

        pil_image = Image.fromarray(self.image)

        if texton==True:
            #print('textoff')
            draw = ImageDraw.Draw(pil_image)        
            
            fontsize=int(self.scalebar_x/(25))
            font = ImageFont.truetype("/home/bat_workstation/helveticaneue.ttf", fontsize)
            draw.text(textposition, self.scalebar_size, anchor ='mb', fill=self.textcolor, font=font, stroke_width=1)
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

    def median_filter(self, n=3):
        '''
        Returns a median filtered copy of the micrograph object, kernal size defined in the call (default is 3)

            Parameters
            ----------
                n:int
                    The n x n kernal for median filter is defined here, must be an odd integer

            Returns
            -------
                Median_filtered_object :Micrograph
                    Median filtered copy of micrograph object with median filtered image
        '''
        filtered_image = cv.medianBlur(self.image,kernal)
        filtered_object = deepcopy(self)
        filtered_object.image = filtered_image
        return filtered_object

    def weiner_filter(self, kernal=5):
        '''
        Returns a Weiner filtered copy of the micrograph object, kernal size defined in the call (default is 3)

            Parameters
            ----------

                n :int
                    The n x n kernal for Weiner filter is defined here, must be an odd integer

            Returns
            -------

                Weiner_filtered_object : Micrograph
                    Weiner filtered copy of micrograph object 
        '''
        filtered_image = wiener(self.image, (kernal, kernal))
        filtered_object = deepcopy(self)
        filtered_object.image = filtered_image
        return filtered_object

    def nlm_filter(self, h=5):
        '''
        Returns a non-local means filtered copy of the micrograph, filter strength is defined in the call. 
        More information on non-local means filtering can be found here: https://docs.opencv.org/3.4/d5/d69/tutorial_py_non_local_means.html

            Parameters
            ----------
                h:int
                    Defines the strength of the Non-local means filter, default is 5
            Returns
            -------
                nlm_filtered_object : Micrograph
                    Non-local means filtered copy of the micrograph object
        '''
        filtered_image = cv.fastNlMeansDenoising(np.uint8(self.image), h)
        filtered_object = deepcopy(self)
        filtered_object.image = filtered_image
        return filtered_object

    def gaussian_filter(self, kernal=3):
        '''
        Returns a Gaussian filtered copy of the micrograph object, kernal size defined in the call (default is 3)

            Parameters
            ----------
                n:int
                    The n x n kernal for median filter is defined here, must be an odd integer

            Returns
            -------
                Gaussian_filtered_object :Micrograph
                    Gaussian filtered copy of micrograph object with gaussian filtered image
        '''
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
        '''
        Basic function for plotting the micrograph image

        Parameters
        ----------

            title:str
                Optional title to be added to the plot 

        '''
        plt.subplots(figsize=(30,20))
        plt.imshow(self.image)
        if title!='':
            plt.title(title, fontsize=30)
        plt.show()

    def show_pair(self,other_image, title1='', title2=''):
        '''
        Basic function for plotting pairs of images for comparison 

        Parameters
        ----------
            other_image : 2D Numpy array
                Second image of the plot - if using Micrograph object remember to use micrograph.image
            title1 : str
                Title for the first image (the object being used to plot the images) - Optional
            title2 : str
                Title for the second image - Optional 

        '''
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
        try:
            self.indicated_mag = self.metadata_tags['.ImageList.2.ImageTags.Microscope Info.Indicated Magnification']
        except KeyError:
            try:
                self.indicated_mag = self.metadata_tags['.ImageList.2.ImageTags.Microscope Info.Formatted Indicated Mag']
                  
            except KeyError:
                print('Sorry, indicated mag cannot be located in tags, please find manually using .show_metadata()')
        
        try:
            self.actual_mag = self.metadata_tags['.ImageList.2.ImageTags.Microscope Info.Actual Magnification']
        except KeyError:
            try:
                self.actual_mag = self.metadata_tags['.ImageList.2.ImageTags.Microscope Info.Formatted Actual Mag']
            except KeyError:
                print('Sorry, actual mag cannot be located in tags, please find manually using .show_metadata()')


        #self.indicated_mag = self.metadata_tags['.ImageList.2.ImageTags.Microscope Info.Indicated Magnification']
        if hasattr(self, 'indicated_mag') and hasattr(self, 'actual_mag'):
            print('Indicated mag: {}'.format(self.indicated_mag))
            print('Actual mag: {}'.format(self.actual_mag))
            return self.indicated_mag, self.actual_mag

    def get_voltage(self):
        '''
        Returns voltage and saves is as micrograph attribute

        Returns
        -------

            Voltage:int
                Microscope voltage for the image
        '''
        self.voltage = self.metadata_tags['.ImageList.2.ImageTags.Microscope Info.Voltage']
        return self.voltage

    def get_exposure(self):
        '''
        Prints and returns the exposure time for the image. 

        Returns
        -------

            exposure:int
                Capture time for the image
        '''
        #print('Frame rate : {}fps'.format(self.fps))
        #print('Exposure time per frame: {}s '.format(1/self.fps))
        print('Imaging time: {}s'.format(self.metadata_tags['.ImageList.2.ImageTags.Acquisition.Parameters.High Level.Exposure (s)']))
        self.exposure = self.metadata_tags['.ImageList.2.ImageTags.Acquisition.Parameters.High Level.Exposure (s)']
        return self.exposure

    def get_date_time(self): 
        '''
        Prints and returns the exposure time for the image. 

        Returns
        -------

            AqDate:str
                Date on which the micrograph was captured
            AqTime:str
                Time at which the micrograph was captured
        '''

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
    '''
    Advanced method which requires editing the code to use. Uses Motioncor2 to motion correct a series of frames and output a number of motion corrected images as a micrograph object
    
    Parameters
    ----------
        frames_dict:dict
            A dictionary of videos and frames in the directory which will be motion corrected, this is created by the 'group_frames()' function
    
    This actually wont work well (will only open the final vid in the frames dictionary). Depreciated function.
    '''

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
    ''' 
    Advanced method which requires editing the source code to use. Uses Motioncor2 to motion correct a video and output a motion corrected image as a micrograph object
    
    This function first converts the dm3 to an mrc file, followed by using motioncor by the exectuable defined in motion_cor_command - change this executible to use. 
    
    An aligned mrc file should be saved in the directory and automatically opened in this Micrograph object.
    Parameters
    ----------
        filename:str
            The filename to motion correct



    '''
        outfile = '_'.join(file.split('.')[:-1])+'.mrc'
        outfile_aligned = '_'.join(file.split('.')[:-1])+'_aligned.mrc'
        pixelsize = nci.dm.fileDM(file).scale[2]
        #print(pixelsize)
        sb.call('dm2mrc {} {} '.format(file, outfile), shell=True, cwd=os.getcwd())
        motion_cor_command = '~/Downloads/MotionCor2_1.4.4/MotionCor2_1.4.4_Cuda113-08-11-2021 -InMrc {} -OutMrc {} -Iter 10 -Tol 0.5 -Throw 1 -Kv 200 -PixSize {} '.format(outfile, outfile_aligned, pixelsize)
        sb.call(motion_cor_command, shell=True, cwd=os.getcwd())
        os.remove(outfile)
        self.open_mrc(outfile_aligned)            

     







# I had to move default pipeline outside of the class because the filters make a new instance of the class and I didnt want to multiply the number of instances in memory. 
# Use: default_pipeline(micrograph)
def default_image_pipeline(filename,  name='', medfilter=3, gaussfilter=0, scalebar=True, texton = True, xybin=2, color='Auto',**kwargs):
    
    Micrograph_object = Micrograph()
    if filename[-3:-1]=='dm':
        Micrograph_object.open_dm(filename)
    else:
        print('Sorry only dm files  are currently supported here.')
    if type(medfilter)==int and medfilter!=0: 
        Micrograph_object = Micrograph_object.median_filter(medfilter)
    
    if type(gaussfilter)==int and gaussfilter!=0:  
        Micrograph_object = Micrograph_object.gaussian_filter(medfilter)

    if xybin!= 0 and xybin!=1:
        Micrograph_object = Micrograph_object.bin_image(xybin)

    if name !='':
        name = name
    else:
        name = '.'.join(Micrograph_object.filename.split('.')[:-1])
        #print(filename)
    #if 'outdir' in kwargs:
    #print('name=',name)
    #Micrograph_object = Micrograph_object.enhance_contrast()
    Micrograph_object=Micrograph_object.convert_to_8bit()

    if scalebar==True:
        Micrograph_object.make_scalebar(texton=texton, color=color)

    if 'outdir' in kwargs:
        Micrograph_object.write_image(name=name,outdir=kwargs['outdir'])
    else:
        Micrograph_object.write_image(name=name) 
    #Micrograph_object.save_image(outname=name)

def default_pipeline_class(Micrograph_object ,name='', medfilter=3, gaussfilter=0, scalebar=True, texton = True, xybin=2, color='Auto',**kwargs):
    if type(medfilter)==int and medfilter!=0: 
        Micrograph_object = Micrograph_object.median_filter(medfilter)
    
    if type(gaussfilter)==int and gaussfilter!=0:  
        Micrograph_object = Micrograph_object.gaussian_filter(medfilter)

    if xybin!= 0 and xybin!=1:
        Micrograph_object = Micrograph_object.bin_image(xybin)

    if name !='':
        name = name
    else:
        name = '.'.join(Micrograph_object.filename.split('.')[:-1])
        #print(filename)
    #if 'outdir' in kwargs:
    #print('name=',name)
    #Micrograph_object = Micrograph_object.enhance_contrast()
    Micrograph_object=Micrograph_object.convert_to_8bit()

    if scalebar==True:
        Micrograph_object.make_scalebar(texton=texton, color=color)

    if 'outdir' in kwargs:
        Micrograph_object.write_image(name=name,outdir=kwargs['outdir'])
    else:
        Micrograph_object.write_image(name=name) 
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
