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


    '''-----------------------------------------------------------

    SECTION: SAVING



    '''




    def save_video(self, framerate=5, **kwargs):
        if 'name' in kwargs:
            name = kwargs['name']
        else:
            name =   '.'.join(self.filename.split('.')[:1])+'.avi'

        if self.foldername!='':
            name = self.foldername.strip('/n') + '/' + name    
            #print(name)
            if self.foldername not in os.listdir('.') and self.foldername!='.':
                os.mkdir(self.foldername.strip('/n'))

        if 'compression' in kwargs:
            if kwargs['compression']==0:
                fourcc = cv.VideoWriter_fourcc(*'DIB ')


                print('Written?')
            else:
                fourcc = cv.VideoWriter_fourcc(*'DIVX')    
        else:
            fourcc = cv.VideoWriter_fourcc(*'DIVX') 

        if 'mp4' in kwargs:
            if kwargs['mp4']==True:
                fourcc=cv.VideoWriter_fourcc(*'X264')

        out = cv.VideoWriter(name, fourcc,5, (self.x, self.y))
        for frame in self.frames:
            frame = ((frame - self.frames.min()) * (1/(self.frames.max() - self.frames.min()) * 255)).astype('uint8')
            frame = cv.cvtColor(frame,cv.COLOR_GRAY2BGR)
            #print(frame.shape)
            out.write(frame)
        out.release()    

    


    def save_tif_stack(self, **kwargs):
        if 'name' in kwargs:
            name = kwargs['name']
            if name[-4:]!='.tif':
                name+='.tif'        
        else:
            name = '.'.join(self.filename.split('.')[:1])+'.tif'    
        
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
                




        '''-----------------------------------------------------------------------------------------------------------------------
        SECTION: BASIC FUNCTIONS

            add_frames : this sums all the frames of a video together if the frames are saved individually, input is a list of frames, can be generated using the group frames method in the motioncorrection section 
            convert to 8bit: this is important to create a easily openable and lower filesize output image good for viewing. 


        '''
    def convert_to_8bit(self):
        #  this will scale the pixels to between 0 and 255, this will automatically scale the image to its max and min
        self.frames= (self.frames - self.frames.min())*(1/(self.frames.max()-self.frames.min())*255)
        self.frames = self.frames.astype('uint8')
        print(self.frames.dtype)
        #for i in range(len(self.frames)):
        #    self.frames[i] = ((self.frames[i] - self.frames.min()) * (1/(self.frames.max() - self.frames[i].min()) * 255)).astype('uint8')

    def bin(self, value=2):
        i=0
        frames = []
        for frame in self.frames:

            frame = cv.resize(frame, (int(frame.shape[0]/value), int(frame.shape[1]/value)), interpolation=cv.INTER_CUBIC)
            frames.append(frame)
            i+=1
        self.frames=np.array(frames)
        print(self.frames.shape)
        self.pixelSize= self.pixelSize*value
        self.x = self.frames[0].shape[1]
        self.y = self.frames[0].shape[0]

# Can be deleted I think... But should allow a function for opening series as video 
    def add_frames(self, frames):
        for frame in frames:
            next_frame = nci.dm.dmReader(frame)
            self.image = self.image + next_frame['data']

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
        self.choose_scalebar_size()
        self.choose_scalebar_color(color)
        for i in range(len(self.frames)):
            #print(self.frames[i])
            self.frames[i][self.scalebar_y:self.scalebar_y+self.height,self.scalebar_x:self.scalebar_x+self.width]=self.pixvalue
            
            textposition = ((self.scalebar_x+self.width/2),self.scalebar_y-5)
            
            #if pixelUnit!='nm':
             #   Utext = str(n)+u'\u00b5'+ 'm'
              #  text = str(n)+'microns'
            #else:
            self.text = '{}{}'.format(self.n,self.pixelUnit) 
             

            pil_image = Image.fromarray(self.frames[i])

            if texton==True:
                #print('TEXTON!')
                draw = ImageDraw.Draw(pil_image)        
                
                fontsize=int(self.scalebar_x/(25))
                font = ImageFont.truetype("/home/bat_workstation/helveticaneue.ttf", fontsize)
                draw.text(textposition, self.text, anchor ='mb', fill=self.textcolor, font=font, stroke_width=1)
                self.frames[i] = np.array(pil_image)    



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
    def show_im(self):
        plt.subplots(figsize=(50,40))
        plt.imshow(self.frames[0])
        plt.show()

    def show_pair(self,other_image):
        fig, ax = plt.subplots(1,2, figsize=(50,30))
        ax[0].imshow(self.frames[0])
        ax[1].imshow(other_image)
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
