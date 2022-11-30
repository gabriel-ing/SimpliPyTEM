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
    A class holding the micrograph image data along with associated parameters and methods. This makes processing microscope images easier as it collects data and methods into a single place. 
    The majority of image handling methods here comes from OpenCV, the functions often have more options/parameters, as a result making them both more powerful and more complicated. 
    This package aims to simplify and automate these functions, however if more functionality is required, I recommend using OpenCV (https://docs.opencv.org/4.x/) as a starting point for your image analysis. 
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
    show_metadata():
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
    

    def open_dm(self, file, video_average=True, pixel_correction=True):
        '''
        Imports digital micrograph files into the micrograph object, initialising all the default attributes required, including saving the metadata into self.metadata_tags. 
        By default, video dm files (dose fractionations) will be summed to create a single image file, there is also an option (video_average) to use the first frame only. 
        
        Some DM files have 'hot pixels' which have anomalously high signal due to detector malfunction, these often lead to contrast issues.
        To correct for this any pixel which has a higher value than the mean value + (20 x standard deviation) is set to the mean pixel value, this is on by default but can be turned off using pixel_correction=False
        
        This uses the ncempy.io.dm package to read DM files, more information can be found here: https://openncem.readthedocs.io/en/latest/ncempy.io.html


        Parameters
        ----------
            file : str
                The name of the dm file to open. The path to the file can also be included if it is not in the same directory. 

            video_average : bool
                If file is a video, this controls whether to output an average (sum) of all the frames or the first frame. Default is to average the video (True), change to False to output a single frame

            pixel_correction: bool 
                Set anomalous 'hot' pixels to the image mean, anomalous pixels defined as image_mean + 20*image_standard_deviation. Default is on (True). 

        '''
        dm_input = nci.dm.dmReader(file)
        if len(dm_input['data'].shape)==2:
            image = dm_input['data']
            

        # at the moment it automatically averages a video into a single image. This will be changed soon to allow for video analysis.
        elif len(dm_input['data'].shape)==3:
            print('File is an image stack, averaging frames together, if you would open as a video, please us MicroVideo object')
            if video_average:

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
        if pixel_correction:
            self.image[self.image>self.image.mean()+self.image.std()*20]=image.mean()
        # this line converts the image to a float32 datatype, this will make it run slower if it starts out as a 8 or 16 bit, I maybe should account for this, but its also required for median filter and others, so I'm performing as default. 
        self.image = self.image.astype('float32')
        #       #return image, x, y, pixelSize, pixelUnit
        self.shape=self.image.shape
        print('{} opened as a Micrograph object'.format(file))

    def open_mrc(self, file, pixel_correction=True):
        '''
        Imports MRC image files into the Micrograph object. 

        Parameters
        ----------
            file : str
                The name of an MRC file to open, the path to the file can also be included. 
        '''

        mrc= mrcfile.open(file)
        print(mrc.voxel_size)
        voxel_size = mrc.voxel_size
        self.pixelSize = float(str(voxel_size).split(',')[0].strip('('))
        self.image = mrc.data
        self.x = self.image.shape[1]
        self.y = self.image.shape[0]
        self.pixelUnit='nm'
        self.filename = file
        if pixel_correction:
            self.image[self.image>self.image.mean()+self.image.std()*20]=image.mean()
        # this line converts the image to a float32 datatype, this will make it run slower if it starts out as a 8 or 16 bit, I maybe should account for this, but its also required for median filter and others, so I'm performing as default. 
        self.image = self.image.astype('float32')
        self.shape=self.image.shape




        
    def write_image(self, name='', ftype='jpg', **kwargs):
        '''
        Saves the image in a .jpg or .tif file for display or use with other programs. 

        Parameters
        ----------
            name: str
                Filename for saved image. Ending with either .jpg or .tif will define the format of the image, alternatively ftype argument can be used. 
                This is optional, without including a name the name of the original file opened will be used. 

            ftype: str
                Optional. Filetype of output image, either 'jpg' or 'tif' (default jpg), this is better defined using the suffix of the name. 
                Saving as a tif will save in whatever format it is currently in - this can be a 32-bit or 8-bit image, using convert_to_8bit() will ensure that latter.

            outdir: str
                Keyword argument (usage: outdir='/path/to/directory'). This defines the output location of the saved image, use a path relative to the current directory or an absolute path.
                The final directory in the path will be made if it does not already exist.
        '''


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
        '''
        Resets the image attributes for the x, y and shape of the image. Used by the binning method and is also useful following cropping of the micrograph

        '''
        self.x = self.image.shape[1]
        self.y = self.image.shape[0]
        self.shape = self.image.shape

    

        
    '''-----------------------------------------------------------------------------------------------------------------------
        SECTION: BASIC FUNCTIONS

            add_frames : this sums all the frames of a video together if the frames are saved individually, input is a list of frames, can be generated using the group frames method in the motioncorrection section 
            convert to 8bit: this is important to create a easily openable and lower filesize output image good for viewing. 


    '''
    def convert_to_8bit(self):
        ''' 
        Returns a micrograph object with the image scaled between 0 and 255 (an 8-bit image). Improves contrast and is a more usable image format than higher bits. 
        
        Returns
        -------
            Micrograph8bit : Micrograph
                A copy of the micrograph object with the image scaled between 0 and 255

        '''
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
        '''
        Function for enhancing contrast. This uses the OpenCV methods detailed here: https://docs.opencv.org/3.4/d3/dc1/tutorial_basic_linear_transform.html. 
        There are 3 input values which define contast controls: alpha, beta and gamma, the gamma value is optional. 
        
        Parameters
        ----------

            alpha:float
                Basic contrast control, usually in the range of 1-3. The histogram is streched. 

            beta: int (or float)
                Brightness control, this will add the value to every pixel in the image, only really has an effect with 8-bit images (and any pixels above 255 will be clipped to this)
            
            gamma:float
                Non-linear contrast control, values between 0-1 makes images brighter (particularly the dark areas), while values >1 darken the image(particularly the bright areas)
                Optional, if included image will be converted to 8 bit. 

        Returns 
        -------

            Contrast_enhanced_micrograph : Micrograph
                Return a copy of the object with the contrast enhanced.
        '''
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
        if self.image.dtype=='uint8':
            enhanced_image[enhanced_image>255]=255
        return enhanced_object

    def equalizeHist(self):
        '''
        Spreads the contrast across a range of values, leading to an evened, flattened histogram. This can be very effective at enhancing midtones in images with very bright or very dark patches. 
        
        Returns
        -------
            Contrast_enhanced_micrograph : Micrograph
                Return a copy of the object with the contrast enhanced.

        '''
        enhanced_object = deepcopy(self)
        enhanced_object = enhanced_object.convert_to_8bit()
        enhanced_object.image = cv.equalizeHist(enhanced_object.image)
        return enhanced_object

    '''-----------------------------------------------------------------------------------------------------------------------
    SECTION: SCALEBAR

        Adds well-sized scalebar to the image. use make_scalebar function for use. 




    '''
    def choose_scalebar_size(self):
        '''
        Function for choosing scalebar size, called through make_scalebar(), not a standalone function.

        Returns
        -------
            scalebar_x: int
                x coordinate for the scalebar 
            scalebar_y: int
                y coordinate for the scalebar 
            width:int
                width of scalebar
            height:int
                height of the scalebar
            scalebar_size:int (or float)
                Size of the scalebar in scaled units (pixelUnit)
        '''
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
        scalebar_x = int(scalebar_x)
        scalebar_y = int(scalebar_y)
        height = int(height)
        width = int(width)
        scalebar_size = n
        #return int(scalebar_x/xybin), int(scalebar_y/xybin), int(height/xybin), int(width/xybin), n
        return scalebar_x, scalebar_y, width, height, scalebar_size


    def choose_scalebar_color(self,color, scalebar_x, scalebar_y, width, height):
        '''
        Chooses the scalebar color and returns the pixelvalue and text color for the annotation. parameters are most of the outputs from choose_scalebar_size()


        Parameters
        ----------

            scalebar_x: int
                x coordinate for the scalebar 
            scalebar_y: int
                y coordinate for the scalebar 
            width:int
                width of scalebar
            height:int
                height of the scalebar
            scalebar_size:int (or float)
                Size of the scalebar in scaled units (pixelUnit)
        '''
        if color=='black' or self.image.dtype!='uint8':
            pixvalue = 0
            textcolor = 'black'
        elif color=='white':
            pixvalue = 255
            textcolor='white'
        elif color=='grey':
            pixvalue = 150
            textcolor='grey'
        else: #default is black, unless it is a particularly dark area - if the mean pixvalue of the scale bar region is significantly less than the overall image mean, the scalebar will be white
            
            if np.mean(self.image[scalebar_y:scalebar_y+height,scalebar_x:scalebar_x+width])<np.mean(self.image)/1.5:
                pixvalue = 255
                textcolor='white'
            else:
                pixvalue = 0
                textcolor = 'black'
        #add scalebar (set pixels to color) 

        return pixvalue, textcolor        


    def make_scalebar(self, texton = True, color='Auto'):
        '''
        Automated method to create a scalebar of a suitable size, shape and color. Returns a new object with a scalebar. 
        The color will be selected between black and white based on mean value of the region of the scalebar compared to the mean value of the whole video. To override this the color can be defined as black white or grey.
        This will work best for 8-bit images, as the scalebar will be given values of 0 or 255. 
        
        Parameters
        ----------

            color : str
                The color of the scalebar, the options are 'white'. 'black' or 'grey'
            texton : bool
                Text can be turned off using texton=False, the selected size of the scalebar can be accessed using micrograph.scalebar_size

        Returns
        -------
            Micrograph_object_with_scalebar: Micrograph
                Copy of the micrograph object with a scale bar.
        '''
        micrograph_SB = deepcopy(self)
        scalebar_x, scalebar_y , width, height, scalebar_size = self.choose_scalebar_size()
        
        pixvalue, textcolor = self.choose_scalebar_color(color,scalebar_x, scalebar_y , width, height)

        micrograph_SB.image[scalebar_y:scalebar_y+height,scalebar_x:scalebar_x+width]=pixvalue
        
        textposition = ((scalebar_x+width/2),scalebar_y-5)
        
        #if pixelUnit!='nm':
         #   Utext = str(n)+u'\u00b5'+ 'm'
          #  text = str(n)+'microns'
        #else:
        micrograph_SB.scalebar_size = '{}{}'.format(scalebar_size,self.pixelUnit) 
         

        pil_image = Image.fromarray(micrograph_SB.image)

        if texton==True:
            #print('textoff')
            draw = ImageDraw.Draw(pil_image)        
            
            fontsize=int(scalebar_x/(25))
            font = ImageFont.truetype("/home/bat_workstation/helveticaneue.ttf", fontsize)
            draw.text(textposition, micrograph_SB.scalebar_size, anchor ='mb', fill=textcolor, font=font, stroke_width=1)
            micrograph_SB.image = np.array(pil_image)    

        return micrograph_SB


    '''------------------------------------------------------------------------------------------------------------------------
        SECTION: IMAGE FILTERS
        These are filters to improve the visibility of features or decrease the noise levels. Included features are 
            
            - Median filter: performs a median filter with kernal size defined in the call (default is 3)
            - Gaussian filter: performs a Gaussian filter with kernal size defined in the call (default is 3)
            - Weiner filter: performs a Weiner filter with kernal size defined in the call (default is 5)
            - Low pass filter: performs a 2D fourier transform of the image and removes the  features at higher resolutions than the radius 
            - Non-local means filter: this compares similar regions of the image and denoises by averaging across them. This is performed by openCV, and more info can be found here: https://docs.opencv.org/3.4/d5/d69/tutorial_py_non_local_means.html

    These filters return an object with the same properties and methods (a copied instance of the class)
    Therefore to use: 

        filtered_micrograph = micrograph.gaussian_filter()
        plt.imshow(filtered_micrograph.image)
        filtered_micrograph.make_scalebar()


    '''
    def low_pass_filter(self, radius):
        '''
        This low pass filters the image. The pixel size is used to scale the radius to whatever the pixel unit is (ie radius 10 is 10nm/10um)
        If pixelsize is undefined the radius will refer to pixels only
        
        Parameters
        ----------

            radius : int (or potentially float)
                The effects of this vary depending on if the pixelsize is defined in self.pixelSize.: 
                     - Assuming your micrograph object has a pixel size defined, the filter works by removing any features smaller than the size you input as a parameter (the unit is the same as the pixelsize), A larger number yields a stronger filter, if it is too large, you won't see any features. 
                    Effective filter sizes depends on features and magnification, so with something between 1-5 and tune it to your needs.
                    - If your micrograph is missing a pixelsize the size input will be the radius of a circle kept in the power spectrum. Here the input number does the inverse - a smaller number leads to stronger filter. In this case, much larger numbers will be needed, 50 is a good starting value.
        
        Returns
        -------
                Low_pass_filtered_object :Micrograph
                    Low pass filtered copy of micrograph object.          

        '''    
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
        '''
        Returns a median filtered copy of the micrograph object, kernal size defined in the call (default is 3)

            Parameters
            ----------
                kernal:int
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
        '''
        prints the metadata tags, this can be useful for finding the names of metadata features within the metadata.tags file. 

        '''
        for tag in self.metadata_tags:
            print('{} : {}\n'.format(tag, self.metadata_tags[tag]))


    def get_mag(self):
        '''
                
        Returns Micrograph magnifications (indicated and actual) and saves them as micrograph attributes (microscope.indicated_mag, microscope.actual_mag)

        Returns
        -------

            indicated_mag:float
                Indicated magnification (i.e. what the microscope tells you the mag is) for the image
            actual_mag: float
                Actual magnification of the image at the camera. 
        
        '''

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
    '''
    Default pipeline to process image, add scalebar, filter, bin and save the image, speeding up automation.
    
    Parameters
    ----------
        Filename:str
            Filename of image to process

        name:str
            Name of the saved image

        medfilter:int 
            The kernal size for a median filter on the image, default is 3, use 0 for no median filter, otherwise must be odd. 

        gaussfilter:int
            The kernal size for a gaussian filter on the image, default is off (0), must be odd. 

        scalebar:bool
            Turns the scale bar on/off (default is on), use scalebar=False to turn off. 


        texton:bool
            Turns the text on the scalebar on or off (default is on)
         
        xybin:int
            Bins the image (x/y) axis

        color:str
            Chooses scalebar color 'black', 'white' or 'grey'

    '''
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
        Micrograph_object = Micrograph_object.make_scalebar(texton=texton, color=color)

    if 'outdir' in kwargs:
        Micrograph_object.write_image(name=name,outdir=kwargs['outdir'])
    else:
        Micrograph_object.write_image(name=name) 
    #Micrograph_object.save_image(outname=name)

def default_pipeline_class(Micrograph_object ,name='', medfilter=3, gaussfilter=0, scalebar=True, texton = True, xybin=2, color='Auto',**kwargs):

    '''
    Default pipeline to process from a Micrograph_object, add scalebar, filter, bin and save the image, speeding up automation.
    
    Parameters
    ----------
        Filename:str
            Filename of image to process

        name:str
            Name of the saved image

        medfilter:int 
            The kernal size for a median filter on the image, default is 3, use 0 for no median filter, otherwise must be odd. 

        gaussfilter:int
            The kernal size for a gaussian filter on the image, default is off (0), must be odd. 

        scalebar:bool
            Turns the scale bar on/off (default is on), use scalebar=False to turn off. 


        texton:bool
            Turns the text on the scalebar on or off (default is on)
         
        xybin:int
            Bins the image (x/y) axis

        color:str
            Chooses scalebar color 'black', 'white' or 'grey'

    '''
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
        Micrograph_object = Micrograph_object.make_scalebar(texton=texton, color=color)

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
