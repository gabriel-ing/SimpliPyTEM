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
import tifffile
from copy import deepcopy
from moviepy.editor import ImageSequenceClip
from SimpliPyTEM.Micrograph_class import *

plt.gray()

class MicroVideo: 

    def __init__(self):
        self.filename = ''
        #self.image='Undefined'
        self.pixel_size= 'Undefined'
        self.foldername='.'


    def set_foldername(self, foldername='Previews'):
        self.foldername = foldername


        '''-------------------------------------------------------------------------------------------------------------------------------------------
        SECTION: IMPORT IMAGES

            can be imported as dm3, dm4, mrc, **numpy array or tifs ** add the tifs 
            need to add numpy and tif functionality


        '''
    

    def open_dm(self, file):
        dm_input = nci.dm.dmReader(file)
        #if len(dm_input['data'].shape)==2:
        #    image = dm_input['data']
        #    dm = '_Image_'

        # at the moment it automatically averages a video into a single image. This will be changed soon to allow for video analysis.
        if len(dm_input['data'].shape)==3:
            self.frames = dm_input['data']
            #image = np.average(images, axis=0)
            dm='_Video_'
        else:
            print('Error, {} is not a video, please use Micrograph() class')
        dmfile = nci.dm.fileDM(file)
        self.metadata_tags =dmfile.allTags
        if '.ImageList.2.ImageTags.Acquisition.Parameters.High Level.Frame Exposure' in self.metadata_tags:
            self.fps = 1/float(self.metadata_tags['.ImageList.2.ImageTags.Acquisition.Parameters.High Level.Frame Exposure']) 
        #extract x and y shapes
        self.x = self.frames[0].shape[1]
        self.y = self.frames[0].shape[0]

        pixelSize=float(dm_input['pixelSize'][-1])
        #print(type(pixelSize))
        #print(pixelSize,type(pixelSize))
        pixelUnit = dm_input['pixelUnit'][-1]
        self.filename = file
        self.pixelSize= pixelSize
        self.pixelUnit = pixelUnit
        # this line converts the image to a float32 datatype, this will make it run slower if it starts out as a 8 or 16 bit, I maybe should account for this, but its also required for median filter and others, so I'm performing as default. 
        #This line removes any giant outliers (bright pixels) from the images
        #print(self.frames[self.frames>self.frames.mean()+self.frames.std()*50])
        self.frames[self.frames>self.frames.mean()+self.frames.std()*8]=0
        
        self.frames=  self.frames.astype('float32')
        #for frame in self.frames:
        #    frame = frame.astype('float32')
        self.shape = self.frames.shape
        print(file + ' opened as a MicroVideo object')

#       #return image, x, y, pixelSize, pixelUnit

    def open_mrc(self, file):
        mrc= mrcfile.open(file)
        print(mrc.voxel_size)
        voxel_size = mrc.voxel_size
        self.pixelSize = float(str(voxel_size).split(',')[0].strip('('))
        self.frames = mrc.data
        self.x = self.frames.shape[1]
        self.y = self.frames.shape[0]
        self.pixelUnit='nm'
        self.filename = file

        # this line converts the image to a float32 datatype, this will make it run slower if it starts out as a 8 or 16 bit, I maybe should account for this, but its also required for median filter and others, so I'm performing as default. 
        for frame in self.frames:
            frame = frame.astype('float32')

    def open_avi(self, filename):
        cap = cv.VideoCapture(filename)
        self.frames= []
        while cap.isOpened():
            ret, frame =cap.read()
            
            #print(ret, frame)
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            #print(frame.shape)
            frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            #plt.imshow(frame)
            #cv.imshow('frame',frame)
            if cv.waitKey(1)==ord('q'):
                break
            self.frames.append(frame)
        print('{} frames loaded as micrograph object'.format(len(frames)))
        print('As format is avi, the pixelsize is not loaded automatically, please set this using micrograph.pixelSize = n')
        cap.release()

        
    def open_array(self, arr, pixelsize='',pixelunit='nm', filename='Loaded_array'):
        print(arr.shape)
        if len(arr.shape)!=3:
            print('Error, this doesnt appear to be an image stack, please double check!')
            return 1 

        self.frames = arr 
        self.pixelSize=pixelsize
        self.pixelUnit=pixelunit
        self.filename=filename
        self.reset_xy()

    #def read_screen_records()

    def reset_xy(self):
        self.x = self.frames[0].shape[1]
        self.y = self.frames[0].shape[0]
        self.shape = self.frames.shape


    '''-----------------------------------------------------------

    SECTION: SAVING



    '''
    def save_tif_stack(self, **kwargs):
        if 'name' in kwargs:
            name = kwargs['name']
            if name[-4:]!='.tif':
                name+='.tif'        
        else:
            name = '.'.join(self.filename.split('.')[:-1])+'.tif'    
        
        if 'outdir' in kwargs:
            outdir = str(kwargs['outdir'])
            if outdir not in os.listdir('.') and outdir!='.':
                os.mkdir(outdir)
            name = outdir+'/'+name
        tifffile.imsave(name, self.frames,imagej=True, resolution=(1/self.pixelSize, 1/self.pixelSize), metadata={'unit':self.pixelUnit})


    def save_tif_sequence(self, **kwargs):
            
        if 'name' in kwargs:
            name = kwargs['name']
            if name[-4:]=='.tif':
                name= name.strip('.tif')
        else: 
            name = '.'.join(self.filename.split('.')[:1]) 

        if 'outdir' in kwargs:
            outdir = str(kwargs['outdir'])
            if outdir.split('/')[-1] not in os.listdir('/'.join(outdir.split('/')[:-1])) and outdir!='.':
                
                os.mkdir(outdir)
            name = outdir+'/'+name

        for i in range(len(self.frames)):
            j=4-len(str(i))
            zeros = '0000'
            count = str(zeros[:j])+str(i)
            savename = name+'_{}'.format(count)+'.tif'
            tifffile.imsave(savename, self.frames[i],imagej=True, resolution=(1/self.pixelSize, 1/self.pixelSize), metadata={'unit':self.pixelUnit, 'Labels':'{}/{} -{}'.format(i, len(self.frames),self.filename)})

    def save_gif(self, fps=5,**kwargs ):

        if 'name' in kwargs:
            name = kwargs['name']
            if name[-4:]!='.gif':
                name= name+'.gif'
        else: 
            name = '.'.join(self.filename.split('.')[:1])+'.gif' 

        if 'outdir' in kwargs:
            outdir = str(kwargs['outdir'])
            if outdir not in os.listdir('.') and outdir!='.':
                os.mkdir(outdir)
            name = outdir+'/'+name

        from moviepy.editor import ImageSequenceClip
        arr = video.frames    
        arr = np.expand_dims(arr, 3)
        clip = ImageSequenceClip(list(arrex), fps=fps)
        clip.to_videofile(name, fps)
    

    def write_video(self, name='', **kwargs):
        '''
        This allows saving as an mp4 or a raw avi file (imageJ compatible)
        '''    
        if name!='':
            #name = kwargs['name']
            if name[-4:]!='.mp4' and name[-4:]!='.avi':
                name= name+'.mp4'
                outformat='mp4'
            elif name[-4:]=='.avi':
                outformat = 'avi'   
            else:
                outformat='.mp4'    
        else: 
            name = '.'.join(self.filename.split('.')[:-1])+'.mp4' 
            outformat='mp4'

        if 'outdir' in kwargs:
            outdir = str(kwargs['outdir'])
            if outdir.split('/')[-1] not in os.listdir('/'.join(outdir.split('/')[:-1])) and outdir!='.':
                os.mkdir(outdir)
            name = outdir+'/'+name

        if 'fps' in kwargs:
            fps= kwargs['fps']
        else:
            fps = 10    

        outvid = []
        for frame in self.frames:
            frame = cv.cvtColor(frame, cv.COLOR_GRAY2BGR)
            outvid.append(frame)
        outvid = np.array(outvid)
        
        clip = ImageSequenceClip(list(outvid), fps=fps)
        #print(clip)
        if outformat=='avi':
            clip.write_videofile(name,codec='rawvideo', fps=fps)
        else:
            clip.write_videofile(name, fps=fps)
                


    def toMicrograph(self):
        im = Micrograph()
        for key in self.__dict__.keys():
            if key!= 'frames':
                setattr(im, key, self.__dict__[key])
        im.image = np.sum(self.frames, 0)
        return im
        '''-----------------------------------------------------------------------------------------------------------------------
        SECTION: BASIC FUNCTIONS

            add_frames : this sums all the frames of a video together if the frames are saved individually, input is a list of frames, can be generated using the group frames method in the motioncorrection section 
            convert to 8bit: this is important to create a easily openable and lower filesize output image good for viewing. 


        '''
    def convert_to_8bit(self):
        #  this will scale the pixels to between 0 and 255, this will automatically scale the image to its max and min
        vid8bit = deepcopy(self)
        vid8bit.frames= (self.frames - self.frames.min())*(1/(self.frames.max()-self.frames.min())*255)
        vid8bit.frames = vid8bit.frames.astype('uint8')
        #print(self.frames.dtype)
        #for i in range(len(self.frames)):
        #    self.frames[i] = ((self.frames[i] - self.frames.min()) * (1/(self.frames.max() - self.frames[i].min()) * 255)).astype('uint8')
        return vid8bit
    
    def bin(self, value=2):
        """
        This function applies binning to the frames in a micrograph object, reducing their size by a specified factor.
    
        Parameters
        ----------
        value : int
            The factor by which to reduce the size of the frames. The default value is 2.
    
        Returns
        -------
        Microvideo_binned: MicroVideo
            A new microvideo object with the binned frames.
        """
        i=0
        frames = []
        for frame in self.frames:

            frame = cv.resize(frame, (int(frame.shape[0]/value), int(frame.shape[1]/value)), interpolation=cv.INTER_CUBIC)
            frames.append(frame)
            i+=1
        binned = deepcopy(self)
        binned.frames=np.array(frames)
        #print(self.frames.shape)
        binned.pixelSize= self.pixelSize*value
        binned.x = binned.frames[0].shape[1]
        binned.y = binned.frames[0].shape[0]
        return binned

    # Can be deleted I think... But should allow a function for opening series as video 
    def add_frames(self, frames):
        for frame in frames:
            next_frame = nci.dm.dmReader(frame)
            self.image = self.image + next_frame['data']


    def clip_contrast(self, saturation=0.5, maxvalue=None, minvalue=None):
        """
        Function for enhancing the contrast in an image by clipping the histogram between two values. 
        These values can be defined directly or can be automatically decided using a saturation value, which the is percentage of the pixels above or below this value.
        I.e, if there are 1,000,000 pixels in an image and the saturation value is 0.1, the method searches the value for which only 0.1% or 1000 pixels are above/below. 
        These values then become the new minimum and maximum of the image, and are scaled to between 0 and 255.
        
        This method will automatically convert to 8 bit (scale between 0 and 255), if this is an issue raise and it can be changed in future versions.

        Parameters
        ----------

            saturation: Float
                The percentage cutoff above/below which the pixels are set to zero/255, default is 0.5% of pixels

            maxvalue: int
                The maximum value that is being clipped (to be decided from histogram). Optional. 

            minvalue: int
                The minimum value that is being clipped (to be decided from histogram). Optional. 

        Returns
        -------

            Contrast_enhanced_micrograph : Micrograph
                Return a copy of the object with the contrast clipped at either end of the image

        Usage
        -----

            MicrographContrastClipped = micrograph.clip_contrast(saturation=1)
            
            or 

            MicrographContrastClipped = micrograph.clip_contrast(maxvalue=220, minvalue=20)

        """
        new_vid  = self.convert_to_8bit()
        print('Satauration = ',saturation)
        if not maxvalue:
            #print(maxvalue)
            for maxvalue in range(int(new_vid.frames.mean()+np.std(new_vid.frames)), 255):
                #print(maxvalue, len(new_im.image[new_im.image>maxvalue]),new_im.image.size)
                if 100*(len(new_vid.frames[new_vid.frames>maxvalue])/new_vid.frames.size)<saturation:
                    #print(maxvalue, len(new_im.image[new_im.image>maxvalue]),new_im.image.size)
                    print('Maxmium value : ',maxvalue)
                    break
            #print(maxvalue)
        if not minvalue:
            for minvalue in range(int(new_vid.frames.mean()-np.std(new_vid.frames)), 0,-1):
                if 100*(len(new_vid.frames[new_vid.frames<minvalue])/new_vid.frames.size)<saturation:
                    print('Minimum value : ',minvalue)
                    break
            #print('Minimum value : ',minvalue)    
        frames =new_vid.frames.astype(np.int16)    
        new_vid.frames = (frames - minvalue)*(255/(maxvalue-minvalue))
        new_vid.frames[new_vid.frames>255]=255
        new_vid.frames[new_vid.frames<0]=0
        new_vid.frames = new_vid.frames.astype(np.uint8)
        return new_vid


    # This, much like the filters below returns the enhanced version as a new object, I have made it this way to allow tuning of alpha and beta.
    def enhance_contrast(self, alpha=1.3, beta=1.1, gamma=1):
        enhanced_object = deepcopy(self)
        for i in range(len(enhanced_object.frames)):
            #print(enhanced_object.frames.dtype)
            enhanced_object.frames[i] = cv.convertScaleAbs(enhanced_object.frames[i], alpha=alpha, beta=beta)

        #print(enhanced_object.frames[0].dtype)
        if enhanced_object.frames[i].dtype=='uint8' and gamma!=1:
            LUT =np.empty((1,256), np.uint8)
            for i in range(256):
                LUT[0, i]=np.clip(pow(i/255.0,gamma)*255.0, 0, 255)
            res =cv.LUT(enhanced_object.frames, LUT) 
            print('Gamma adjusted...')
            enhanced_object.frames = res
        #enhanced_object.image = enhanced_image
        return enhanced_object

    def eqHist(self):
        enhanced_object=deepcopy(self)
        enhanced_object.convert_to_8bit()
        for i in range(len(enhanced_object.frames)):
            enhanced_object.frames[i] = cv.equalizeHist(enhanced_object.frames[i])
        return enhanced_object

    def __len__(self):
        return self.frames.shape[0]

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
                print('Sorry, indicated mag could not be found, try searching for it manually with the show_metadata method')
        try:   
            self.actual_mag = self.metadata_tags['.ImageList.2.ImageTags.Microscope Info.Actual Magnification']
        except KeyError:
                try:
                    actual_mag = self.metadata_tags['.ImageList.2.ImageTags.Microscope Info.Formatted Actual Mag']
                except:
                    print('Sorry, indicated mag could not be found, try searching for it manually with the show_metadata method')
        
        if hasattr(self, actual_mag) and hasattr(self, indicated_mag):
            print('Indicated mag: {}'.format(self.indicated_mag))
            print('Actual mag: {}'.format(self.actual_mag))
            return self.indicated_mag, self.actual_mag

    def get_voltage(self):
        self.voltage = self.metadata_tags['.ImageList.2.ImageTags.Microscope Info.Voltage']
        return self.voltage

    def get_exposure(self):
        print('Frame rate : {}fps'.format(self.fps))
        print('Exposure time per frame: {}s '.format(1/self.fps))
        print('Imaging time: {}s'.format(self.metadata_tags['.ImageList.2.ImageTags.Acquisition.Parameters.High Level.Exposure (s)']))
        print('Number of frames: {}'.format(self.frames.shape[0]))
        return self.fps, self.metadata_tags['.ImageList.2.ImageTags.Acquisition.Parameters.High Level.Exposure (s)']

    def get_date_time(self): 
        self.AqDate = self.metadata_tags['.ImageList.2.ImageTags.DataBar.Acquisition Date']
        self.AqTime = self.metadata_tags['.ImageList.2.ImageTags.DataBar.Acquisition Time']
        print('Date: {} '.format(self.AqDate))
        print('Time {} '.format(self.AqTime))
        return self.AqDate, self.AqTime


    '''-----------------------------------------------------------------------------------------------------------------------
    SECTION: SCALEBAR

        Adds well-sized scalebar to the image. use make_scalebar function for use. 




    '''
    def choose_scalebar_size(self):
        
       
        
        #make coordinates for the scalebar, currently set to y-12.5%,x-5% of image size from the bottom right corner 
        #of the image to bottom left of the scalebar - change this by editing /20 and /7.5 values (this just looked good to me)
        scalebar_y = self.y-int(self.y/25)
        scalebar_x = self.x-int(self.x/6.5)
        #print(x,scalebar_x)
        #possible scalebar sizes are given here, if its >500nm it should be in unit micron, hopefully this should only fail with very extreme examples
        
        possible_sizes = [0.5, 1,2,5,10,25,50,100,250,500]
        
        #to select sizes, iterate through possible sizes, if the width of the resulting scalebar (n*pixelsize) 
        #is over 15% of the image size, the size is chose, if none are over 15% of image size
        #the largest size is chosen as default
        
        for n in possible_sizes:
            width = n*1/self.pixelSize
            #print(n, image.shape([0]/10)
            if width>(self.x/15):
                break
                #print(width, x/15)
        #choose height of scalebar (default is scalebar width/6), convert width into an integer
        height = int(self.y/60)
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
            
            if np.mean(self.frames[0][self.scalebar_y:self.scalebar_y+self.height,self.scalebar_x:self.scalebar_x+self.width])<np.mean(self.frames[0])/1.5:
                self.pixvalue = 255
                self.textcolor='white'
            else:
                self.pixvalue = 0
                self.textcolor = 'black'
        #add scalebar (set pixels to color) 

        #return pixvalue, textcolor        


    def make_scalebar(self, texton=True, color='Auto'):
        #print(pixvalue, textcolor)
        vidSB = deepcopy(self)
        vidSB.choose_scalebar_size()
        vidSB.choose_scalebar_color(color)
        for i in range(len(self.frames)):
            #print(self.frames[i])
            vidSB.frames[i][vidSB.scalebar_y:vidSB.scalebar_y+vidSB.height,vidSB.scalebar_x:vidSB.scalebar_x+vidSB.width]=vidSB.pixvalue
            
            textposition = ((vidSB.scalebar_x+vidSB.width/2),vidSB.scalebar_y-5)
            
            #if pixelUnit!='nm':
             #   Utext = str(n)+u'\u00b5'+ 'm'
              #  text = str(n)+'microns'
            #else:
            vidSB.text = '{}{}'.format(vidSB.n,vidSB.pixelUnit) 
             

            pil_image = Image.fromarray(vidSB.frames[i])

            if texton==True:
                #print('TEXTON!')
                draw = ImageDraw.Draw(pil_image)        
                
                fontsize=int(vidSB.scalebar_x/(25))
                font = ImageFont.truetype("/home/bat_workstation/helveticaneue.ttf", fontsize)
                draw.text(textposition, vidSB.text, anchor ='mb', fill=vidSB.textcolor, font=font, stroke_width=1)
                vidSB.frames[i] = np.array(pil_image)    
        return vidSB


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
        #print(N)
        N=self.frames[0].shape[0]
        if type(self.pixelSize)==int or type(self.pixelSize)==float and self.pixelSize!=0:
            radius=int((N*self.pixelSize)/radius)
        
        filtered_object = deepcopy(self)
        for i in range(len(filtered_object.frames)):
            fft = np.fft.fft2(filtered_object.frames[i])
            fshift = np.fft.fftshift(fft)
            magnitude_spectrum = np.log(np.abs(fshift))
            crow, ccol = int(self.y/2), int(self.x/2)
            fshift_filtered=np.copy(fshift)
            mask = np.zeros_like(self.frames[i])

            mask = cv.circle(mask, (crow, ccol),radius*2, 1, -1) 
            #print(fshift_filtered)
            fcomplex = fshift[:,:]*1j
            fshift_filtered = mask*fcomplex
            f_filtered_shifted = np.fft.fftshift(fshift_filtered)
            #magnitude_spectrum_filter = np.log(np.abs(f_filtered_shifted))
            inv_image = np.fft.ifft2(f_filtered_shifted)
            filtered_object.frames[i] = np.abs(inv_image)
            filtered_object.frames[i] -= filtered_object.frames[i].min()
            
        return filtered_object

    def median_filter(self, kernal=3):
        filtered_object = deepcopy(self)
        for i in range(len(filtered_object.frames)):
            filtered_object.frames[i] = cv.medianBlur(filtered_object.frames[i],kernal)
        return filtered_object

    def weiner_filter(self, kernal=5):
        from scipy.signal import wiener
        filtered_object = deepcopy(self)
        for i in range(len(filtered_object.frames)):
            filtered_object.frames[i] = wiener(filtered_object.frames[i], (kernal, kernal))
        return filtered_object

    def NLM_filter(self, h=5):
        filtered_object = deepcopy(self)
        for i in range(len(filtered_object.frames)):
            filtered_object.frames[i] = cv.fastNlMeansDenoising(np.uint8(filtered_object.frames[i]), h)
        
        
        return filtered_object

    def gaussian_filter(self, kernal=3):
        #for frame in filtered_object.frames:
        #    print(frame)
        #    print(type(frame))
        #    print(frame.shape)
        #    print(frame.dtype)
        #    filtered_image = cv.GaussianBlur(self.image, (kernal,kernal),0)
        swapped = np.swapaxes(self.frames, 0,2)
        #print(kernal)
        swapped = cv.GaussianBlur(swapped, (kernal,kernal), 0)
        swapped = np.swapaxes(swapped, 0, 2)

        filtered_object = deepcopy(self)        
        filtered_object.frames = swapped
        return filtered_object



    '''
    ------------------------------------------------------------------------------------------------------------
    Section Visualising images

    used for plotting images using matplotlib. Functions very basic so only meant for rapid use, for better figures write own function or use save command

    '''
    def imshow(self, title=None, vmax=None, vmin=None, framenumber=0, average=False):
        if average:
            av =  np.sum(self.frames, axis=0)

        if not vmax and not average:
            vmax = np.max(self.frames)
        if not vmin and not average:
            vmin = np.min(self.frames)
        if average and not vmax:
            vmax = np.max(av)
        if average and not vmin:
            vmin =np.min(av)


        plt.subplots(figsize=(30,20))
        if title:
            plt.title(title, fontsize=30)
        if average:
            plt.imshow(av, vmax=vmax, vmin=vmin)
        else:
            plt.imshow(self.frames[framenumber], vmax=vmax, vmin=vmin)
        plt.show()

    def imshow_pair(self,other_image, title1='', title2=''):
        fig, ax = plt.subplots(1,2, figsize=(50,30))
        ax[0].imshow(self.frames[0])
        if title1!='':
            ax[0].set_title(title1, fontsize=30)
        
        ax[1].imshow(other_image)
        if title2!='':
            ax[1].set_title(title2, fontsize=30)
        plt.show()

    def imshow_average(self, vmax=None, vmin=None):
        if not vmax:
            vmax = np.max(self.frames)
        if not vmin:
            vmin = np.min(self.frames)
        plt.subplots(figsize=(30,20))
        plt.imshow(np.sum(self.frames, axis=0), vmax=vmax, vmin=vmin)
        plt.show()

    def Sidebyside(self, Video2):
        #Add video as numpy stack (Z,Y,X ) 
        print(Video1.shape)
        z1,y1,x1 = self.frames.shape
        z2, y2, x2=Video2.shape
        sidebyside = np.zeros((max(z1,z2), max(y1,y2), x1+x2),dtype='uint8')

        # this was put here to invert the masked video, DO this BEFORE calling function. 
        #masksinv=cv.bitwise_not(np.array(masks))
        sidebyside[:, :, :x1] =Video1

        sidebyside[:, :, x1:] =Video2[:,:,:]
        #plt.imshow(sidebyside[0], cmap='magma')
        #plt.show()
        sidebyside_object =deep_copy(self)
        sidebyside_object.frames = sidebyside
        return sidebyside    

    def plot_histogram(self, sidebyside=False, average=False):
        if sidebyside:
            fig, ax = plt.subplots(1,2, figsize=(30,15))
            if average:
                av =  np.sum(self.frames, axis=0) 
                ax[0].imshow(av)
                
                ax[1].hist(av.ravel(), 100)
           
            else:
                ax[0].imshow(self.frames[0])
                if self.frames.dtype == 'unit8':
                    ax[1].hist(self.frames.ravel(), 256, [0,256])
                else:
                    ax[1].hist(self.frames.ravel(), 100)
            ax[1].set_xlabel('Pixel Values', fontsize=20)
            ax[1].set_ylabel('Frequency',fontsize=20)
        else:
            plt.figure(figsize=(5,5))
            if self.frames.dtype == 'unit8':
                plt.hist(self.frames.ravel(), 256, [0,256])
            else:
                plt.hist(self.frames.ravel(), 100)
        plt.show()

    '''------------------------------------------
    SECTION: VIDEO SPECIFIC METHODS

    

        

    '''
    def Average_frames(self, groupsize):
        newframes = []
        for x in range(0, len(self.frames), groupsize):
            if x+groupsize>len(self.frames):

                frame = np.sum(self.frames[x:len(self.frames)],axis=0)
            else:
                frame = np.sum(self.frames[x:x+groupsize],axis=0)    
            newframes.append(frame)
        averaged_object=deepcopy(self)    
        averaged_object.frames=np.array(newframes)
        return averaged_object


    def Running_average(self, groupsize):
        averaged_video = []
        for i in range(0, len(self.frames)-groupsize):
            frame_group = self.frames[i:i+groupsize]
            av_frame_group = np.sum(frame_group, axis=0)
            averaged_video.append(av_frame_group)
        averaged_object = deepcopy(self)
        averaged_object.frames=np.array(averaged_video)    
        return averaged_object

    '''---------------------------------
    SECTION MOTION CORRECTION

    NOT GONNA DEAL WITH THIS NOW!
    
    This defines using motioncor2 to align video frames, these frames either need to be saved individually, in which case the function group_frames is needed on the image set before use
    Motioncorrect_video works on a dm4 file, converts it to mrc and then runs motioncor on this image stack. 


    '''        

    def motioncorrect_vid(self):
        original_cwd = os.getcwd()
        tifname = 'OutIntermediateTiff.tif'
        outname= '.'.join(self.filename.split('.')[:-1])+'Motion_corrected.mrc'
        print('outname = ', outname)
        outname = outname.split('/')[-1]

        if '/' in self.filename:
            directory='/'.join(self.filename.split('/')[:-1])
        else:
            directory=os.getcwd() 
        os.chdir(directory)   
        print('cwd = ', os.getcwd())
        command = '/home/bat_workstation/Downloads/MotionCor2_1.4.4/MotionCor2_1.4.4_Cuda112-08-11-2021 -InTiff {} -OutMrc {} -Iter 10 -Tol 0.5 -Throw 1 -Kv 200 -PixlSize {} -OutStack 1'.format(tifname, outname, self.pixelSize*10)
        print(command)
        print('dir = ',directory)
        self.save_tif_stack(name=tifname)

        sb.call(command, shell=True, cwd=os.getcwd())
        MC_vid = deepcopy(self)
        inname = '.'.join(outname.split('.')[:-1])+'_Stk.mrc'
        MC_vid.open_mrc(inname)
        os.chdir(original_cwd)
        return MC_vid

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

    def save_image(self, **kwargs):#use name='outname' to give a filename   
        if self.foldername not in os.listdir('.') :
            os.mkdir(self.foldername)        
        if kwargs:
                name = kwargs['name']
        else:
                name = '.'.join(self.filename.split('.')[:1])
        name += '_'+self.text+'scale.jpg'
        if self.foldername!='':
                name = self.foldername.strip('/n') + '/' + name
        #if self.foldername=='':
        #    newname = self.filename.split('.dm')[0]+'_'+self.text+'scale.jpg'
        #else:
        #    newname = self.foldername.strip('\n') + '/' +self.filename.split('.dm')[0]+'_'+self.text+'scale.jpg'
        cv.imwrite(name,self.image)
        #self.pil_image.save(name, quality=self.quality)
        print(name, 'Done!')




# I had to move default pipeline outside of the class because the filters make a new instance of the class and I didnt want to multiply the number of instances in memory. 
# Use: default_pipeline(micrograph)
def default_video_pipeline(MicroVideo_object, medfilter=0, gaussfilter=3, scalebar=True, texton = True, xybin=2, color='Auto',Average_frames=5, **kwargs):
    
    if Average_frames!= 0 and Average_frames!=1:
        MicroVideo_object=MicroVideo_object.Average_frames(Average_frames)
    if xybin!= 0 and xybin!=1:
        MicroVideo_object.bin(xybin)
    if type(medfilter)==int and medfilter!=0: 
        MicroVideo_object = MicroVideo_object.median_filter(medfilter)
    
    if type(gaussfilter)==int and gaussfilter!=0:  
        MicroVideo_object = MicroVideo_object.gaussian_filter(gaussfilter)



    if 'name' in kwargs:
        name=kwargs['name']
    else:
        name = '.'.join(MicroVideo_object.filename.split('.')[:1])+'.mp4' 
	
    #MicroVideo_object.bin(xybin)
    
    
    MicroVideo_object.convert_to_8bit()
    #MicroVideo_object = MicroVideo_object.enhance_contrast(alpha=1.3, beta=5)
    if scalebar==True:
        MicroVideo_object.make_scalebar(texton=texton, color=color)

    if 'outdir' in kwargs:
        MicroVideo_object.write_video(name=name,outdir=kwargs['outdir'])
    else:
        MicroVideo_object.write_video(name=name)     
        




def group_frames(self, frames):
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
