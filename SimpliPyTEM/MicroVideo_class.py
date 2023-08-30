import argparse
import os
import subprocess as sb
import time
from copy import deepcopy
import hyperspy.api as hs
from cherrypicker import CherryPicker
import cv2 as cv
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import mrcfile
import ncempy.io as nci
import numpy as np
import pandas as pd
import tifffile
from matplotlib import font_manager
from moviepy.editor import ImageSequenceClip
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from SimpliPyTEM.Micrograph_class import Micrograph, default_image_pipeline, make_outdir

plt.gray()


class MicroVideo:
    """
    A class holding video data and various methods to edit the frames.

    Attributes
    ----------
    filename:str
        The file name opened (blank if not opened in object)
    pixel_size:float
        The pixel size in the image, should be initialised when opening data assuming the pixel size is included, if not can easily be altered
    pixel_unit:str
        The unit of the pixel size
    metadata_tags:dict
        The metadata of the file should be stored in this dictionary (works with digital micrograph files)
    shape:tuple
        The shape of the video (nframes, y, x)
    x:int
        The size of the x axis in the image
    y:int
        The size of the y axis in the image
    frames:numpy array
        The video data

    List of functions in MicroVideo
    -------------------------------
    Imports:
        open_dm - Opening digital micrograph files
        open_video - Opening a .mp4 or .avi video files
        open_array - Loading a numpy array
    Saving:
        save_tif_stack
        save_tif_sequence
        write_video - save .mp4 or .avi version of the video
        write_image - save video frame or video average as an image
    Basic functions:
        bin - reduce size of xy axis by binning pixels, factor is specified in call
        convert_to_8bit - converts to 8bit video by scaling pixel values between 0-255.
        make_scalebar - creates suitably sized scalebar
        Average_frames - averages frames in groups of n
        Running_average - performs a running average of the video
        reset_xy - reset the object x, y and shape attributes upon change of video, useful if video is cropped.
    Contrast enhancement:
        clip_contrast - enhances contrast by making a percentage of values saturated (absolute black/white) and scaling the rest of the pixels between these (my preferred contrast enhancement)
        enhance_contrast - enhances contrast based on alpha (contrast), beta (brightness) and gamma (non-linear contrast) values
        eqHist - equalises histogram, ensuring even converage of pixel values from 0-255
        Normalise_video - normalises contrast between frames of the video
    Metadata (currently relies on dm3/dm4 metadata):
        show_metadata - shows all metadata tags and values
        get_mag - prints and returns magnification (indicated and actual)
        get_voltage - prints and returns voltage
        get_exposure - prints and returns frame rate, exposure time
        get_date_time - prints aquisition date and time
    Image filters:
        gaussian_filter
        median_filter
        low_pass_filter
        weiner_filter
        non_local_means_filter
    Plotting:
        imshow - plots still image (either single frame or average) of video
        plot_histogram - plots the histogram of the video
        show_video - shows video in a jupyter notebook (very slow)
    Other functions:
        Sidebyside - Sticks two videos together so they play side by side.
        motioncorrect_vid - Uses motioncor2 to align the video frames (requires motioncor exectutable to be set)




    """

    def __init__(self, filename=None):
        if filename:
            self.log = []
            self.video = True
            self.pixel_size = 1
            self.pixel_unit = "pixels"
            self.filename = filename
            self.open_file(filename)
        else:
            self.filename = ""
            # self.image='Undefined'
            self.pixel_size = 1
            self.pixel_unit = "pixels"
            self.log = []
            self.video = True
        """-------------------------------------------------------------------------------------------------------------------------------------------
        SECTION: IMPORT IMAGES

            can be imported as dm3, dm4, mrc, **numpy array or tifs ** add the tifs 
            need to add numpy and tif functionality


        """
    def copy(self):
        '''Returns a copy of the object 

        Returns
        -------

            MicroVideo: MicroVideo
                Copy of original MicroVideo object'''

        return deepcopy(self)
        
    def open_dm(self, file, pixelcorrection=True):
        """
        Imports digital micrograph files into the micrograph object, initialising all the default attributes required, including saving the metadata into self.metadata_tags.
        By default, video dm files (dose fractionations) will be summed to create a single image file, there is also an option (video_average) to use the first frame only.

        Some DM files have 'hot pixels' which have anomalously high signal due to detector malfunction, these often lead to contrast issues.
        To correct for this any pixel which has a higher value than the mean value + (20 x standard deviation) is set to the mean pixel value, this is on by default but can be turned off using pixel_correction=False

        This uses the ncempy.io.dm package to read DM files, more information can be found here: https://openncem.readthedocs.io/en/latest/ncempy.io.html


        Parameters
        ----------
            file : str
                The name of the dm file to open. The path to the file can also be included if it is not in the same directory.

            pixel_correction: bool
                Set anomalous 'hot' pixels to the image mean, anomalous pixels defined as image_mean + 20*image_standard_deviation. Default is on (True).

        """
        dm_input = nci.dm.dmReader(file)
        # if len(dm_input['data'].shape)==2:
        #    image = dm_input['data']
        #    dm = '_Image_'

        # at the moment it automatically averages a video into a single image. This will be changed soon to allow for video analysis.
        if len(dm_input["data"].shape) == 3:
            self.frames = dm_input["data"]
            # image = np.average(images, axis=0)
            dm = "_Video_"
        else:
            print(
                "Error, {} is not a video, consider using Micrograph() class unless you are running open_series".format(
                    file
                )
            )
        dmfile = nci.dm.fileDM(file)
        self.metadata_tags = dmfile.allTags
        if (
            ".ImageList.2.ImageTags.Acquisition.Parameters.High Level.Frame Exposure"
            in self.metadata_tags
        ):
            self.fps = 1 / float(
                self.metadata_tags[
                    ".ImageList.2.ImageTags.Acquisition.Parameters.High Level.Frame Exposure"
                ]
            )
        # extract x and y shapes
        self.x = self.frames[0].shape[1]
        self.y = self.frames[0].shape[0]

        pixel_size = float(dm_input["pixelSize"][-1])
        # print(type(pixel_size))
        # print(pixel_size,type(pixel_size))
        pixel_unit = dm_input["pixelUnit"][-1]
        self.filename = file
        self.pixel_size = pixel_size
        self.pixel_unit = pixel_unit
        # this line converts the image to a float32 datatype, this will make it run slower if it starts out as a 8 or 16 bit, I maybe should account for this, but its also required for median filter and others, so I'm performing as default.
        # This line removes any giant outliers (bright pixels) from the images
        # print(self.frames[self.frames>self.frames.mean()+self.frames.std()*50])

        # self.frames = np.flip(self.frames,axis=1)
        if pixelcorrection:
            self.frames[self.frames > self.frames.mean() + self.frames.std() * 8] = 0

        self.frames = self.frames.astype("float32")
        # for frame in self.frames:
        #    frame = frame.astype('float32')
        self.shape = self.frames.shape
        print(file + " opened as a MicroVideo object")

    #       #return image, x, y, pixel_size, pixel_unit
    def open_hyperspy(self, filename):
        '''
        Opens filetypes with [hyperspy](https://hyperspy.org/) - this is excellent for a range of electron microscope signal types, I recommend checking it out.

        This will allow opening a number of filetypes which will make SimpliPyTEM more accessible for more users, however I cannot verify that this will work with all filetypes and may cause an issue if non-image signals are included. 

        Please report any issues with this on github and I will try to fix them.

        Parameters
        ----------

            filename: str
                Name of file to open
        ''' 
        s = hs.load(filename)

        if len(s.data.shape)==3:
            self.frames = s.data
        elif len(s.data.shape)==2:
            print('Error - this appears to be an image, thus returning an image')
            raise Exception

        elif len(s.data.shape)>3: 
            print('Error - there are more than 3 dimensions, unclear what these are.')
            raise Exception

            
        self.filename = filename
        self.pixel_size = s.axes_manager[-1].scale
        self.pixel_unit = s.axes_manager[-1].units
        picker = CherryPicker(s.metadata.as_dictionary())

        self.metadata_tags = picker.flatten(delim='.').get()

        if 'Acquisition_instrument.TEM.Camera.exposure' in self.metadata_tags:
            self.fps = float(self.metadata_tags['Acquisition_instrument.TEM.Camera.exposure'])/s.data.shape[0]
        else:
            self.fps= -1
        self.reset_xy()


    def open_mrc(self, file):
        mrc = mrcfile.open(file)
        print(mrc.voxel_size)
        voxel_size = mrc.voxel_size

        self.pixel_size = float(str(voxel_size).split(",")[0].strip("("))
        self.frames = mrc.data
        self.frames.setflags(write=1)
        self.frames = np.flip(self.frames, axis=1)

        self.x = self.frames.shape[1]
        self.y = self.frames.shape[0]
        self.pixel_unit = "nm"
        self.filename = file

        # this line converts the image to a float32 datatype, this will make it run slower if it starts out as a 8 or 16 bit, I maybe should account for this, but its also required for median filter and others, so I'm performing as default.
        for frame in self.frames:
            frame = frame.astype("float32")

    def open_video(
        self,
        filename,
        pixel_size=1,
        pixel_unit="pixels",
    ):
        """
        Loads video files (eg. mp4 and avi, unsure if others will work) into microvideo object.
        The pixel size is not taken from the video by default, and so it should be included in the command, else the default of 1nm/pixel is used. This can be addedd later using video.pixel_size= {new pixel size}

        Parameters
        ----------

            filename: str
                Name of the video file to open
            pixel_size: float
                Size of one pixel (eg. 1nm/pixel), optionall.
            pixel_unit: str
                Unit for the pixel_size

        """

        cap = cv.VideoCapture(filename)
        frames = []
        self.filename = ".".join(filename.split(".")[:-1])
        while cap.isOpened():
            ret, frame = cap.read()

            # print(ret, frame)
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            # print(frame.shape)
            frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            # plt.imshow(frame)
            # cv.imshow('frame',frame)
            if cv.waitKey(1) == ord("q"):
                break
            frames.append(frame)
            # print(len(frames))
        self.frames = np.array(frames)
        print("{} frames loaded as micrograph object".format(len(self.frames)))
        print(
            "As format is avi, the pixelsize is not loaded automatically, please set this using micrograph.pixel_size = n"
        )
        cap.release()
        self.reset_xy()
        self.pixel_size = pixel_size
        self.pixel_unit = pixel_unit

    def open_array(self, arr, pixelsize=1, pixelunit="nm", filename="Loaded_array"):
        """
        Loads a numpy array into the microvideo object, allowing use of all the other available methods. Filename, pixel size and pixel unit should be given in the call, defaults of 1nm/pixel allow this to be avoided but correct pixel size should be loaded if a scalebar is required (as well as certain other functions)

        """
        print(arr.shape)
        if len(arr.shape) != 3:
            print(
                "Error, this doesnt appear to be an image stack, please double check!"
            )
            return 1

        self.frames = arr
        self.pixel_size = pixelsize
        self.pixel_unit = pixelunit
        self.filename = filename
        self.reset_xy()

    def open_series(self, frames):
        """
        Hasn't exactly been tested but should work!
        """
        self.open_dm(frame[0])
        new_frames = []
        for frame in frames[1:]:
            next_frame = nci.dm.dmReader(frame)
            new_frames.append(next_frame)
        self.frames = np.array(new_frames)

    def open_file(self, filename):
        if filename[-4:] == ".dm3" or filename[-4:] == ".dm4":
            self.open_dm(filename)
        elif filename[-4:] == ".mrc":
            self.open_mrc(filename)
        elif filename[-4:].lower() in ['.tif', 'tiff']:
            self.open_tif(filename)
        else:
            try:
                self.open_hyperspy(filename)
            except:
                try:
                    self.open_video(filename)
                except:
                    print("Error - unknown or unsupported filetype, if you think this should be supported please raise an issue on github")
                    raise Exception


    def open_tif(self, filename, pixel_size=None, pixel_unit=None):
        """
        Open a tif file into the microvideo object. If the tif has any metadata tags, these should be saved into the metadata_tags and will then be accessible with .show_metadata()
        The pixel size is likely to be included somewhere within the metadata and may be loaded, but the name of the tags are not always constant, and so this may need to be searched in  the .show_metadata output.

        Parameters
        ----------

            filename: str
                Name of image file to load into the object
            pixel_size: float
                The pixel size in the image, not necessary but can be included here, can also be loaded with set_scale()
            pixel_unit: str
                The unit for the pixel size included.
        """
        if pixel_size:
            self.pixel_size = pixel_size
        else:
            self.pixel_size = 1
        if pixel_unit:
            self.pixel_unit = pixel_unit
        else:
            self.pixel_unit = "pixels"

        if filename[-3:] in ["tiff", "tif", "TIF", "TIFF"]:
            with tifffile.TiffFile(filename) as tif:
                self.metadata_tags = {}
                self.frames = tif.asarray()
                if len(self.frames.shape)!=3:
                    print('Wrong number of dimensions, if this is an image, please use Micrograph({})'.format(filename))
                    raise Exception

                for page in tif.pages:
                    for tag in page.tags:
                        self.metadata_tags[tag.name] = tag.value
            if '65009' in self.metadata_tags: #for some reason this is the code for pixel_size in digital micrograph saved tifs
                self.pixel_size = self.metadata_tags['65009']
                self.pixel_unit = self.metadata_tags['65003']
            elif "XResolution" in self.metadata_tags: #this is standard = labelling for tif resolution. This requires a calculation (see below)
                #print(self.metadata_tags['XResolution'])
                #print(self.metadata_tags['YResolution'])
                if (
                    self.metadata_tags["XResolution"]
                    == self.metadata_tags["YResolution"]
                ):
                    try:
                        self.pixel_size = 1 / (
                            self.metadata_tags["XResolution"][0]
                            / self.metadata_tags["XResolution"][1]
                        )

                    except:
                        pass


            if "unit" in self.metadata_tags:
                self.pixel_unit = self.metadata_tags['unit']
            elif "ResolutionUnit" in self.metadata_tags:
                if self.metadata_tags["ResolutionUnit"]=='INCH' or self.metadata_tags['ResolutionUnit']==2: #Resolution is commonly in inches (resolutionunit =2 also means inches), this is then converted into nm.
                    self.pixel_unit = 'nm'
                    self.pixel_size = self.pixel_size*0.0254*1e9
            if self.pixel_unit == "micron":
                    self.pixel_unit = "µm"
           
        self.filename = filename
        self.reset_xy()

    def reset_xy(self):
        """
        Resets the image attributes for the x, y and shape of the image. Used by the binning method and is also useful following cropping of the micrograph

        """
        self.x = self.frames[0].shape[1]
        self.y = self.frames[0].shape[0]
        self.shape = self.frames.shape

    """-----------------------------------------------------------

    SECTION: SAVING



    """

    def save_tif_stack(self, name=None, outdir=None):
        """
        Saves the video as a single, multi-image tif file (stack). Files saved in current condition so if an 8bit tif is required, run video.convert_to_8bit() before use.
        These can be useful for viewing editted video in imageJ

        Parameters
        ----------
            name:str
                Prefix for the outputted filename.

            outdir:str
                The output directory for the files, if this directory doesn't exist (in the cwd) a new one will be created.

        Outputs
        -------

            Saves a multi-image tif stack into the output directory listed (cwd is default)

        """

        if name:
            if name[-4:] != ".tif":
                name += ".tif"
        else:
            name = ".".join(self.filename.split(".")[:-1]) + ".tif"

        if self.pixel_unit != "nm":
            pu = "um"
        else:
            pu = "nm"

        if outdir:
            make_outdir(outdir)
            name = outdir + "/" + name
        tifffile.imsave(
            name,
            self.frames,
            imagej=True,
            resolution=(1 / self.pixel_size, 1 / self.pixel_size),
            metadata={"unit": pu},
        )

    def save_tif_sequence(self, name=None, outdir=None):
        """
        Saves each frame of the video as a tif, this is saved in the current format, so if an 8bit tif is required, run video.convert_to_8bit() before use.
        nameand outdir can be included to give a name (prefix) and  the output directory.

        Parameters
        ----------
            name:str
                Prefix for the outputted filenames.

            outdir:str
                The output directory for the files, if this directory doesn't exist (in the cwd) a new one will be created.

        Outputs
        -------

            Saves a sequence of Tif files into the output directory listed (cwd is default)

        """
        if name:
            if name[-4:] == ".tif":
                name = name.strip(".tif")
        else:
            name = ".".join(self.filename.split(".")[:1])

        if outdir:
            make_outdir(outdir)
            name = outdir + "/" + name

        if self.pixel_unit != "nm":
            pu = "um"
        else:
            pu = "nm"

        for i in range(len(self.frames)):
            j = 4 - len(str(i))
            zeros = "0000"
            count = str(zeros[:j]) + str(i)
            savename = name + "_{}".format(count) + ".tif"
            tifffile.imsave(
                savename,
                self.frames[i],
                imagej=True,
                resolution=(1 / self.pixel_size, 1 / self.pixel_size),
                metadata={
                    "unit": pu,
                    "Labels": "{}/{} -{}".format(i, len(self.frames), self.filename),
                },
            )

    def save_gif(self, fps=5, **kwargs):
        if "name" in kwargs:
            name = kwargs["name"]
            if name[-4:] != ".gif":
                name = name + ".gif"
        else:
            name = ".".join(self.filename.split(".")[:1]) + ".gif"

        if "outdir" in kwargs:
            outdir = str(kwargs["outdir"])
            if outdir not in os.listdir(".") and outdir != ".":
                os.mkdir(outdir)
            name = outdir + "/" + name

        from moviepy.editor import ImageSequenceClip

        arr = video.frames
        arr = np.expand_dims(arr, 3)
        clip = ImageSequenceClip(list(arr), fps=fps)
        clip.to_videofile(name, fps)

    def write_video(self, name=None, outdir=None, fps=None):
        """
        This allows saving as an mp4 or a raw avi file (imageJ compatible)

        Parameters
        ----------
            name:str
                Output filename. Outputted files can be in mp4 or uncompressed avi (imageJ readable) filetypes (mp4 by default), this is denoted by the suffix of the name.

            outdir:str
                The output directory for the files, if this directory doesn't exist (in the cwd) a new one will be created.

            fps:int
                Optionally the output movie frame rate can be added (in frames per second)
        Outputs
        -------

            Saves a sequence of Tif files into the output directory listed (cwd is default)
        """
        if name:
            # name = kwargs['name']
            if name[-4:] != ".mp4" and name[-4:] != ".avi":
                name = name + ".mp4"
                outformat = "mp4"
            elif name[-4:] == ".avi":
                outformat = "avi"
            else:
                outformat = ".mp4"
        else:
            name = ".".join(self.filename.split(".")[:-1]) + ".mp4"
            outformat = "mp4"

        if outdir:
            make_outdir(outdir)
            name = outdir + "/" + name

        if not fps and hasattr(self, "fps"):
            fps = self.fps
        elif not fps:
            fps = 10

        outvid = []
        for frame in self.frames:
            frame = cv.cvtColor(frame, cv.COLOR_GRAY2BGR)
            outvid.append(frame)
        outvid = np.array(outvid)

        clip = ImageSequenceClip(list(outvid), fps=fps)
        # print(clip)
        if outformat == "avi":
            clip.write_videofile(name, codec="rawvideo", fps=fps)
        else:
            clip.write_videofile(name, fps=fps)

    def write_image(
        self, name=None, ftype="jpg", average=True, framenumber=0, outdir=None
    ):
        """
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

            average:bool
                Do you want to save an image of the average of the video? True or False (y/n)

            framenumber:int
                If not saving the average (average=False), this chooses which frame to save - index starts at zero and negative numbers count from the end

        """

        if outdir:
            make_outdir(outdir)
            name = outdir + "/" + name
        print("Start name :", name)
        if name:
            print("if name : ", name)
            if name[-4:] == ".jpg":
                ftype = "jpg"
                name = name[:-4]
            elif name[-4:] == ".tif":
                ftype = "tif"
                name = name[:-4]
            if len(name.split(".")) > 2:
                name = ".".join(name.split(".")[:-1])
                print("if len name: ", name)
                print(".".join(name.split(".")[:-1]))
        else:
            name = ".".join(self.filename.split(".")[:-1])
            print("else_name = ", name)
        # try:
        #    name += '_'+self.scalebar_size+'scale.{}'.format(ftype)
        # except AttributeError:
        name += "." + ftype
        # if self.foldername!='':
        #        name = '/'+self.foldername.strip('/n') + '/' + name.split('/')[-1]
        # if self.foldername=='':
        #    newname = self.filename.split('.dm')[0]+'_'+self.text+'scale.jpg'
        # else:
        #    newname = self.foldername.strip('\n') + '/' +self.filename.split('.dm')[0]+'_'+self.text+'scale.jpg'
        if average:
            image = np.sum(self.frames, axis=0)

        else:
            image = self.frames[framenumber]

        if ftype == "jpg":
            if image.max() != 255 or image.min() != 0:
                print(image.max(), image.min())
                image = (image - image.min()) * (1 / (image.max() - image.min()) * 255)
                image = image.astype("uint8")
                print("converting to 8bit")
            cv.imwrite(name, image)
        elif ftype == "tif":
            tifffile.imsave(
                name,
                image,
                imagej=True,
                resolution=(1 / self.pixel_size, 1 / self.pixel_size),
                metadata={"unit": self.pixel_unit},
            )

        # self.pil_image.save(name, quality=self.quality)
        print(name, "Done!")

    def write_mrc(self, name=None, outdir=None, overwrite=False):
        """
        Function to save video as an mrc file. Currently Metadata is not supported.
        """

        if name:
            # print('if name : ',name)
            if len(name.split(".")) > 2:
                name = ".".join(name.split(".")[:-1])
                print(".".join(name.split(".")[:-1]))
        else:
            name = ".".join(self.filename.split(".")[:-1])

        if name[-4:] != ".mrc":
            name += ".mrc"

        if outdir:
            make_outdir(outdir)
            name = outdir + "/" + name
        frames_yflipped =  np.flip(self.frames, axis=1)
        with mrcfile.new(name, overwrite=overwrite) as mrc:
            mrc.set_data(frames_yflipped)
        

    def toMicrograph(self):
        """
        Returns a micrograph object with the average of the image so the video average can be treated as a single image

        Returns
        -------

            micrograph:Micrograph
                Micrograph object with the same metadata and an average of all the image frames.

        """
        im = Micrograph()
        for key in self.__dict__.keys():
            if key != "frames":
                setattr(im, key, self.__dict__[key])
        im.image = np.sum(self.frames, 0)
        return im
        """-----------------------------------------------------------------------------------------------------------------------
        SECTION: BASIC FUNCTIONS

            add_frames : this sums all the frames of a video together if the frames are saved individually, input is a list of frames, can be generated using the group frames method in the motioncorrection section 
            convert to 8bit: this is important to create a easily openable and lower filesize output image good for viewing. 


        """

    def convert_to_8bit(self):
        """Returns a microvideo object with the image scaled between 0 and 255 (an 8-bit image). Improves contrast, reduces data size and is a more usable image format than higher bit rates.

        Returns
        -------
            MicroVideo8bit : MicroVideo
                A copy of the microvideo object with the image scaled between 0 and 255
        """
        #  this will scale the pixels to between 0 and 255, this will automatically scale the image to its max and min
        vid8bit = deepcopy(self)
        vid8bit.frames = (self.frames - self.frames.min()) * (
            1 / (self.frames.max() - self.frames.min()) * 255
        )
        vid8bit.frames = vid8bit.frames.astype("uint8")
        # print(self.frames.dtype)
        # for i in range(len(self.frames)):
        #    self.frames[i] = ((self.frames[i] - self.frames.min()) * (1/(self.frames.max() - self.frames[i].min()) * 255)).astype('uint8')
        vid8bit.log.append("convert_to_8bit()")
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
        i = 0
        frames = []
        for frame in self.frames:
            frame = cv.resize(
                frame,
                (int(frame.shape[1] / value), int(frame.shape[0] / value)),
                interpolation=cv.INTER_CUBIC,
            )
            frames.append(frame)
            i += 1
        binned = deepcopy(self)
        binned.frames = np.array(frames)
        # print(self.frames.shape)
        binned.pixel_size = self.pixel_size * value
        binned.reset_xy()
        binned.log.append("binned()")
        return binned

    def clip_contrast(self, saturation=0.2, maxvalue=None, minvalue=None):
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

            Contrast_enhanced_microvideo : Microvideo
                Return a copy of the object with the contrast clipped at either end of the image

        Usage
        -----

            MicrovideoContrastClipped = video.clip_contrast(saturation=1)

            or

            MicrovideoContrastClipped = video.clip_contrast(maxvalue=220, minvalue=20)

        """
        new_vid = self.convert_to_8bit()
        # print(new_vid)
        # print(new_vid.frames)

        if not maxvalue:
            print("Saturation = ", saturation)
            maxvalue = np.percentile(new_vid.frames, 100 - saturation)
            print("Maxmium value : ", maxvalue)
        if not minvalue:
            minvalue = np.percentile(new_vid.frames, saturation)
            print("Minimum value : ", minvalue)
        frames = new_vid.frames.astype(np.int16)
        print(maxvalue, minvalue)
        new_vid.frames = (frames - minvalue) * (255 / (maxvalue - minvalue))
        new_vid.frames[new_vid.frames > 255] = 255
        new_vid.frames[new_vid.frames < 0] = 0
        new_vid.frames = new_vid.frames.astype(np.uint8)
        new_vid.log.append("clip_contrast()")
        return new_vid

    # This, much like the filters below returns the enhanced version as a new object, I have made it this way to allow tuning of alpha and beta.
    def enhance_contrast(self, alpha=1.3, beta=1.1, gamma=1):
        """
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

            Contrast_enhanced_microvidoe : MicroVideo
                Return a copy of the object with the contrast enhanced.
        """

        enhanced_object = deepcopy(self)
        for i in range(len(enhanced_object.frames)):
            # print(enhanced_object.frames.dtype)
            enhanced_object.frames[i] = cv.convertScaleAbs(
                enhanced_object.frames[i], alpha=alpha, beta=beta
            )

        # print(enhanced_object.frames[0].dtype)
        if enhanced_object.frames[i].dtype == "uint8" and gamma != 1:
            LUT = np.empty((1, 256), np.uint8)
            for i in range(256):
                LUT[0, i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
            res = cv.LUT(enhanced_object.frames, LUT)
            print("Gamma adjusted...")
            enhanced_object.frames = res
        # enhanced_object.image = enhanced_image
        enhanced_object.log.append("enhance_contrast()")
        return enhanced_object

    def eqHist(self):
        """
        Spreads the contrast across complete range of values, leading to an evened, flattened histogram. This can be very effective at enhancing midtones in images with very bright or very dark patches.

        Returns
        -------
            Contrast_enhanced_microvideo : MicroVideo
                Return a copy of the object with the contrast enhanced.

        """
        enhanced_object = deepcopy(self)
        enhanced_object = enhanced_object.convert_to_8bit()
        for i in range(len(enhanced_object.frames)):
            enhanced_object.frames[i] = cv.equalizeHist(enhanced_object.frames[i])
        enhanced_object.log.append("eqHist()")
        return enhanced_object

    def __len__(self):
        return self.frames.shape[0]

    def normalise_video(self, normtype="mean"):
        """
        Normalises the video frames to have equal contrast, either through  mean or median normalisation

        Parameters
        ----------

            normtype:str
                options are mean or median - changes the type of normalisation, either the mean of each frame  is equal or the median of each frame is equal.


        Returns
        -------

            Normalised_microvideo: MicroVideo
                Returns  a normalised copy of the original object.

        """
        dtype = self.frames.dtype
        norm_frames = []
        normtypes = ["median", "mean"]
        if normtype not in normtypes:
            raise Exception(
                "this normalisation type is not supported, currently only median or mean are supported"
            )
        elif normtype == "mean":
            vid_norm = np.mean(self.frames)
        elif normtype == "median":
            vid_norm = np.median(self.frames)

        # vid_median= np.median(self.frames)

        norm_object = deepcopy(self)
        for frame in self.frames:
            if normtype == "mean":
                frame_norm = np.mean(self.frames)
            elif normtype == "median":
                frame_norm = np.median(self.frames)
            # frame_median = np.median(self.frames)
            norm_frames.append(frame * vid_norm / frame_norm)
        norm_object.frames = np.array(norm_frames)
        norm_object.log.append("normalise_video()")
        norm_object.frames = norm_object.frames.astype(dtype)
        return norm_object

    def local_normalisation(
        self, numpatches, padding=15, pad=False, normalise_all=True
    ):
        """
        Normalises contrast across the video frames, ensuring even contrast throughout.
        frames are taken and split into patches, following which the median of the patches ('local median') is compared to the median of the video ('global median').
        The patch (local area) is then normalised using the medians (patch = patch* global_median/local_medium) leading to a uniform contrast in the video frame and video itself.

        The patch median was chosen so there would be less effect if there is a large dark/bright particle, however if this is too large compared with the patch size it will affect the resulting contrast.

        Padding can be applied which will greatly reduce edge artefacts. However doing this well will greatly increase the run time.
        Note: if there is a black region (eg. edge of beam or grid) in the image this may lead to bad results.

        Parameters
        ----------

            numpatches:int
                The number of patches on each axis to split the image into, ie image is split into n x n patches and these are given the same median

            padding: int
                percentage overlap between patches (only used if pad=True)

            pad:bool
                Setting to true reduces edge artifacts from the patches of the image, however it also greatly increases processing time.

        Returns
        -------

            new_vid: Micrograph
                Copy of the MicroVideo object with a video that has normalised contrast
        """
        new_vid = deepcopy(self)

        # Create patches
        xconst = int(new_vid.frames.shape[1] / numpatches)
        yconst = int(new_vid.frames.shape[2] / numpatches)
        x_coords = [i * xconst for i in range(numpatches)]
        y_coords = [i * yconst for i in range(numpatches)]
        patch_coords = list(itertools.product(x_coords, y_coords))

        if normalise_all:
            global_median = np.median(new_vid.frames)
        else:
            global_median = None
        new_frames = []
        for frame in new_vid.frames:
            new_frame = self.local_normalisation_frame(
                frame, global_median, patch_coords, pad, padding, xconst, yconst
            )
            # print(new_frame)
            new_frames.append(new_frame)
        new_vid.frames = np.array(new_frames)
        new_vid.log.append("local_normalisation")
        return new_vid

    def local_normalisation_frame(
        self, frame, global_median, patch_coords, pad, padding, xconst, yconst
    ):
        """
        Function to perform local normalisation on each frame. This function is called by the local_normalisation() function and can be ignored for users.
        """
        if pad:
            arrs = []
        else:
            padding = 0

        if global_median == None:
            global_median = np.median(frame)

        for coord in patch_coords:
            x_low = coord[0]
            x_high = coord[0] + xconst + int((padding / 100) * xconst)
            y_low = coord[1]
            y_high = coord[1] + yconst + int((padding / 100) * yconst)

            local_patch = frame[x_low:x_high, y_low:y_high]
            local_median = np.median(local_patch)
            local_patch = local_patch * global_median / local_median

            if pad:
                # Creates arrays for each coordinate and sets the patch equal to the normalise local patch, the rest are zeros
                # print(coord)
                empty_arr = np.zeros_like(frame, dtype="float32")
                # Set all values to not-a-number
                # print(empty_arr.dtype)
                empty_arr[:] = np.nan
                # Set patch in empty array
                empty_arr[x_low:x_high, y_low:y_high] = local_patch
                arrs.append(empty_arr)
            else:
                frame[x_low:x_high, y_low:y_high] = local_patch

        if pad:
            # Creates array of arrays
            arrs = np.array(arrs)
            # Creates mean of array (ignoring not-a-number values)
            new_arr = np.nanmean(arrs, axis=0)
            return new_arr

        else:
            # print(frame)
            return frame

    """--------------------------------------------------------------------------------
    SECTION: METADATA

        If a dm file has been opened, the metadata is saved in MicroVideo.metadata_tags, this is unformatted and awkward to use
        but all the raw data can be found. These methods allow easy extraction of some key metadata items: mag, voltage,
        exposure and aquisition date/time. 
    """

    def show_metadata(self):
        """
        prints the metadata tags, this can be useful for finding the names of metadata features within the metadata.tags file.

        """
        for tag in self.metadata_tags:
            print("{} : {}\n".format(tag, self.metadata_tags[tag]))

    def get_mag(self):
        """

        Returns Micrograph magnifications (indicated and actual) and saves them as microvideo attributes (microscope.indicated_mag, microscope.actual_mag)

        Returns
        -------

            indicated_mag:float
                Indicated magnification (i.e. what the microscope tells you the mag is) for the image
            actual_mag: float
                Actual magnification of the image at the camera.

        """
        try:
            self.indicated_mag = self.metadata_tags[
                ".ImageList.2.ImageTags.Microscope Info.Indicated Magnification"
            ]
        except KeyError:
            try:
                self.indicated_mag = self.metadata_tags[
                    ".ImageList.2.ImageTags.Microscope Info.Formatted Indicated Mag"
                ]
            except KeyError:
                try:
                    self.indicated_mag = self.metadata_tags["Acquisition_instrument.TEM.magnification"]
                except:
                    print(
                        "Sorry, indicated mag cannot be located in tags, please find manually using .show_metadata()"
                    )
        try:
            self.actual_mag = self.metadata_tags[
                ".ImageList.2.ImageTags.Microscope Info.Actual Magnification"
            ]
        except KeyError:
            try:
                actual_mag = self.metadata_tags[
                    ".ImageList.2.ImageTags.Microscope Info.Formatted Actual Mag"
                ]
            except:
                print(
                    "Sorry, indicated mag could not be found, try searching for it manually with the show_metadata method"
                )

        if hasattr(self, "actual_mag") and hasattr(self, "indicated_mag"):
            # print('Indicated mag: {}'.format(self.indicated_mag))
            # print('Actual mag: {}'.format(self.actual_mag))
            return self.indicated_mag, self.actual_mag
        elif hasattr(self, "indicated_mag"):
            return self.indicated_mag, -1
        else:
            return -1, -1

    def get_voltage(self):
        """
        Returns voltage and saves is as micrograph attribute

        Returns
        -------

            Voltage:int
                Microscope voltage for the image
        """
        try:
            self.voltage = self.metadata_tags[
                ".ImageList.2.ImageTags.Microscope Info.Voltage"
            ]
            return self.voltage
        except:
            try: 
                self.voltage = self.metadata_tags['Acquisition_instrument.TEM.beam_energy']
                return self.voltage
            except KeyError:
                print("Voltage was not found")
                return -1

    def get_exposure(self, print_values=True):
        """
        Prints and returns the frame rate, exposure time per frame, imaging time and number of frames.

        Returns
        -------

            fps:int
                Frame rate of the video in frames per second

            Imaging_time:int
                The total imaging time for the video. s
        """
        try:
            self.exposure = self.metadata_tags[
                ".ImageList.2.ImageTags.Acquisition.Parameters.High Level.Exposure (s)"
            ]
        except: 
            try:
                self.exposure = self.metadata_tags['Acquisition_instrument.TEM.Camera.exposure']
            except:
                self.exposure = -1
        return (
            self.fps,
            self.exposure
        )

    def get_date_time(self):
        """
        Prints and returns the aquisition date and time for the image.

        Returns
        -------

            AqDate:str
                Date on which the micrograph was captured
            AqTime:str
                Time at which the micrograph was captured
        """
        try:
            self.AqDate = self.metadata_tags[
                ".ImageList.2.ImageTags.DataBar.Acquisition Date"
            ]
            self.AqTime = self.metadata_tags[
                ".ImageList.2.ImageTags.DataBar.Acquisition Time"
            ]
        # print('Date: {} '.format(self.AqDate))
        # print('Time {} '.format(self.AqTime))
            return self.AqDate, self.AqTime
        except:
            try:
                self.AqDate = self.metadata_tags[
                    "General.date"
                ]
                self.AqTime = self.metadata_tags[
                    "General.time"
                ]            
                return self.AqDate, self.AqTime 
            except:

                return "UNK", "UNK"

    def export_metadata(self, name='metadata.csv', outdir="."):
        """ """
        make_outdir(outdir)

        dt = self.get_date_time()
        date_time = pd.to_datetime(dt[0] + " " + dt[1])

        metadata = {
            "Image name": self.filename,
            "Indicated Magnification": self.get_mag()[0],
            "Actual Magnifiation": self.get_mag()[1],
            "Date": str(date_time.date()),
            "Time": str(date_time.time()),
            "Pixel size": self.pixel_size,
            "Pixel unit": self.pixel_unit,
            "Exposure Time (s)": self.get_exposure(print_values=False)[1],
            "Voltage": self.get_voltage(),
            "Size (px)": "{}x{}".format(self.shape[1], self.shape[2]),
            "Video": self.video,
            "Frame Rate (fps)": self.fps,
            "Number of frames": self.frames.shape[0],
        }
        # print(metadata)

        df = pd.DataFrame(metadata, index=[0])

        if name in os.listdir(outdir):
            old_df = pd.read_csv(outdir + "/" + name)
            new_df = pd.concat([old_df, df], ignore_index=True)
            new_df.sort_values(by=["Date", "Time"], inplace=True)
            new_df.to_csv(outdir + "/" + name, index=False)
        else:
            df.to_csv(outdir + "/" + name, index=False)

    """-----------------------------------------------------------------------------------------------------------------------
    SECTION: SCALEBAR

        Adds well-sized scalebar to the image. use make_scalebar function for use. 




    """

    def change_scale_unit(self, new_unit, scaling_factor=None):
        """
        Function to change the unit of the scale in the image. The method is built to allow easy transfer between nanometers ('nm') and microns ('µm'), however can be used to give any new unit providing a scaling factor to multiply the current value by is included.

        Parameters
        ----------

            new_unit : str
                The new unit for the scale, commonly 'nm' or 'µm'

            scaling_factor: int/float
                The value to multiply the current value by to give the new scale. This isnt necessary with 'µm'/'nm' transitions, but without it any other change will change unit only.

        """
        if new_unit == self.pixel_unit:
            print("The unit is already {}! Skipping file.".format(new_unit))
        elif new_unit == "nm" and self.pixel_unit == "µm":
            self.pixel_size *= 1000
            self.pixel_unit = "nm"
        elif new_unit != "nm" and new_unit != "µm":
            self.pixel_unit = new_unit

            if scaling_factor != None:
                self.pixel_size *= scaling_factor
            else:
                print(
                    "Setting new scale unit but not changing the value, please include a scaling factor to also change the value."
                )
        elif new_unit == "µm" and self.pixel_unit == "nm":
            self.pixel_size = self.pixel_size / 1000
            self.pixel_unit = "µm"

        elif (
            self.pixel_unit not in ["µm", "nm"]
            and new_unit in ["µm", "nm"]
            and scaling_factor == None
        ):
            print(
                "Error! You want to switch to {} but the transition from {} is not naturally supported, please include a scaling factor (even if its just 1) to ensure correct conversion.".format(
                    new_unit, self.pixel_unit
                )
            )
        elif (
            self.pixel_unit not in ["µm", "nm"]
            and new_unit in ["µm", "nm"]
            and scaling_factor != None
        ):
            self.pixel_size *= scaling_factor
            self.pixel_unit = new_unit

        else:
            print(
                "Not sure how we got here! Check inputs and try again - if genuine error, raise an issue on github!"
            )

        self.log.append("change_scale_unit({},{})".format(new_unit, scaling_factor))

    def set_scale(self, pixels, dist, unit):
        """
        Set the scale in the image with a measurement (number of pixels and size, with unit)

        Parameters
        ----------

            pixels : int/float
                Number of pixels measured

            dist : int/float
                Distance measured
            unit : str
                Unit of measurement

        """
        self.pixel_size = dist / pixels
        self.pixel_unit = unit

    def choose_scalebar_size(self):
        """
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
                Size of the scalebar in scaled units (pixel_unit)
        """
        y, x = self.frames.shape[1], self.frames.shape[2]

        # make coordinates for the scalebar, currently set to y-12.5%,x-5% of image size from the bottom right corner
        # of the image to bottom left of the scalebar - change this by editing /20 and /7.5 values (this just looked good to me)
        scalebar_y = y - int(y / 25)
        scalebar_x = x - int(x / 6.5)
        # print(x,scalebar_x)

        # possible scalebar sizes are given here, if its >500nm it should be in unit micron

        possible_sizes = [0.5, 1, 2, 5, 10, 25, 50, 100, 250, 500, 1000]

        # to select sizes, iterate through possible sizes, if the width of the resulting scalebar (n*pixelsize)
        # is over 15% of the image size, the size is chose, if none are over 15% of image size
        # the largest size is chosen as default
        for n in possible_sizes:
            width = int(n * 1 / self.pixel_size)
            # print(n, image.shape([0]/10)
            if width > (x / 16):
                break

        # This if statement checks whether the scalebar is too close to the edge or bigger than the size.
        # This should ensure it is at least one 100th of the image width away from the edge.

        if scalebar_x + width >= x:
            print(True)
            diff = x - scalebar_x + width
            scalebar_x = scalebar_x - diff - x / 100
        elif scalebar_x + width + x / 100 > x:
            scalebar_x = scalebar_x - x / 100

        # choose height of scalebar (default is scalebar width/6), convert width into an integer
        height = int(y / 60)
        width = int(width)
        scalebar_x = int(scalebar_x)
        scalebar_y = int(scalebar_y)
        scalebar_size = n
        # return int(scalebar_x/xybin), int(scalebar_y/xybin), int(height/xybin), int(width/xybin), n
        return scalebar_x, scalebar_y, width, height, scalebar_size

    def choose_scalebar_color(self, color, scalebar_x, scalebar_y, width, height):
        """
        Function for choosing the scalebar color and returns the pixelvalue and text color for the annotation.
        Called through make_scalebar(), not a standalone function
        """
        if color == "black":
            pixvalue = 0
            textcolor = "black"
        elif color == "white":
            pixvalue = 255
            textcolor = "white"
        elif color == "grey":
            pixvalue = 150
            textcolor = "grey"
        else:  # default is black, unless it is a particularly dark area - if the mean pixvalue of the scale bar region is significantly less than the overall image mean, the scalebar will be white
            if (
                np.mean(
                    self.frames[0][
                        scalebar_y : scalebar_y + height,
                        scalebar_x : scalebar_x + width,
                    ]
                )
                < np.mean(self.frames[0]) / 1.5
            ):
                pixvalue = 255
                textcolor = "white"
            else:
                pixvalue = 0
                textcolor = "black"
        # add scalebar (set pixels to color)

        return pixvalue, textcolor

    def make_scalebar(self, texton=True, color="Auto", fontsize="M"):
        """
        Automated method to create a scalebar of a suitable size, shape and color. Returns a new object with a scalebar.
        The color will be selected between black and white based on mean value of the region of the scalebar compared to the mean value of the whole video. To override this the color can be defined as black white or grey.
        This will work best for 8-bit images, as the scalebar will be given values of 0 or 255.

        You can change the fontsize of the scalebar label with the fontsize option, this is medium ('M') by default but can be made larger or smaller ('S','L', 'XL'), if none of these look good to you, you can choose the fontsize by entering an integer instead of these options. For reference, the fontsize given by these values (calculated based on image size) is printed.

        Parameters
        ----------

            color : str
                The color of the scalebar, the options are 'white'. 'black' or 'grey'
            texton : bool
                Text can be turned off using texton=False, the selected size of the scalebar can be accessed using micrograph.scalebar_size
            fontsize: str
                Choose the fontsize from S,M,L,XL or give an integer value
        Returns
        -------
            Micrograph_object_with_scalebar: Micrograph
                Copy of the micrograph object with a scale bar.
        """
        # print(pixvalue, textcolor)
        vidSB = deepcopy(self)
        vidSB.reset_xy()

        (
            scalebar_x,
            scalebar_y,
            width,
            height,
            scalebar_size,
        ) = self.choose_scalebar_size()
        pixvalue, textcolor = self.choose_scalebar_color(
            color, scalebar_x, scalebar_y, width, height
        )
        textposition = ((scalebar_x + width / 2), scalebar_y - 5)

        if fontsize == "M":
            fontsize = int(scalebar_x / (22))
        elif fontsize == "L":
            fontsize = int(scalebar_x / (18))
        elif fontsize == "XL":
            fontsize = int(scalebar_x / (15))
        elif fontsize == "S":
            fontsize = int(scalebar_x / (27))

        for i in range(len(self.frames)):
            # print(self.frames[i])
            vidSB.frames[i][
                scalebar_y : scalebar_y + height, scalebar_x : scalebar_x + width
            ] = pixvalue

            # if pixel_unit!='nm':
            #   Utext = str(n)+u'\u00b5'+ 'm'
            #  text = str(n)+'microns'
            # else:
            vidSB.scalebar_size = "{}{}".format(scalebar_size, vidSB.pixel_unit)

            pil_image = Image.fromarray(vidSB.frames[i])

            if texton == True:
                # print('TEXTON!')
                draw = ImageDraw.Draw(pil_image)

                # fontsize=int(vidSB.scalebar_x/(25))
                try:
                    file = font_manager.findfont("DejaVu Sans")
                    font = ImageFont.truetype(file, fontsize)
                except:
                    font_search = font_manager.FontProperties(
                        family="sans-serif", weight="normal"
                    )
                    file = font_manager.findfont(font_search)
                    font = ImageFont.truetype(file, fontsize)

                draw.text(
                    textposition,
                    vidSB.scalebar_size,
                    anchor="mb",
                    fill=textcolor,
                    font=font,
                    stroke_width=1,
                )
                vidSB.frames[i] = np.array(pil_image)
            else:
                print("The scalebar added is {}".format(vidSB.scalebar_size))
        print("Fontsize:", fontsize)
        vidSB.log.append("make_scalebar()")
        return vidSB

    """------------------------------------------------------------------------------------------------------------------------
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


    """

    def low_pass_filter(self, radius):
        """
        This low pass filters the image. The pixel size is used to scale the radius to whatever the pixel unit is (ie radius 10 is 10nm/10um)
        If pixelsize is undefined the radius will refer to pixels only

        Parameters
        ----------

            radius : int (or potentially float)
                The effects of this vary depending on if the pixelsize is defined in self.pixel_size.:
                     - Assuming your micrograph object has a pixel size defined, the filter works by removing any features smaller than the size you input as a parameter (the unit is the same as the pixelsize), A larger number yields a stronger filter, if it is too large, you won't see any features.
                    Effective filter sizes depends on features and magnification, so with something between 1-5 and tune it to your needs.
                    - If your micrograph is missing a pixelsize the size input will be the radius of a circle kept in the power spectrum. Here the input number does the inverse - a smaller number leads to stronger filter. In this case, much larger numbers will be needed, 50 is a good starting value.

        Returns
        -------
                Low_pass_filtered_object :MicroVideo
                    Low pass filtered copy of the microvideo object.

        """
        # print(N)
        N = self.frames[0].shape[0]
        if (
            type(self.pixel_size) == int
            or type(self.pixel_size) == float
            and self.pixel_size != 0
        ):
            radius = int((N * self.pixel_size) / radius)

        filtered_object = deepcopy(self)
        for i in range(len(filtered_object.frames)):
            fft = np.fft.fft2(filtered_object.frames[i])
            fshift = np.fft.fftshift(fft)
            magnitude_spectrum = np.log(np.abs(fshift))
            crow, ccol = int(self.y / 2), int(self.x / 2)
            fshift_filtered = np.copy(fshift)
            mask = np.zeros_like(self.frames[i])

            mask = cv.circle(cv.UMat(mask), (crow, ccol), radius * 2, 1, -1)
            # print(fshift_filtered)
            mask = mask.get()
            fcomplex = fshift[:, :] * 1j
            fshift_filtered = mask * fcomplex
            f_filtered_shifted = np.fft.fftshift(fshift_filtered)
            # magnitude_spectrum_filter = np.log(np.abs(f_filtered_shifted))
            inv_image = np.fft.ifft2(f_filtered_shifted)
            filtered_object.frames[i] = np.abs(inv_image)
            filtered_object.frames[i] -= filtered_object.frames[i].min()
        filtered_object.log.append("low_pass_filter({})".format(radius))
        return filtered_object

    def high_pass_filter(self, radius):
        """
        This high pass filters the image. This can be effective for evening out uneven contrast in the image. The pixel size is used to scale the radius to whatever the pixel unit is (ie radius 10 is 10nm/10um)
        If pixelsize is undefined the radius will refer to pixels only

        Parameters
        ----------

            radius : int (or potentially float)
                The effects of this vary depending on if the pixelsize is defined in self.pixel_size.:
                     - Assuming your micrograph object has a pixel size defined, the filter works by removing any features smaller than the size you input as a parameter (the unit is the same as the pixelsize), A larger number yields a stronger filter, if it is too large, you won't see any features.
                    Effective filter sizes depends on features and magnification, so with something between 1-5 and tune it to your needs.
                    - If your micrograph is missing a pixelsize the size input will be the radius of a circle kept in the power spectrum. Here the input number does the inverse - a smaller number leads to stronger filter. In this case, much larger numbers will be needed, 50 is a good starting value.

        Returns
        -------
                Low_pass_filtered_object :MicroVideo
                    Low pass filtered copy of the microvideo object.

        """
        # print(N)
        N = self.frames[0].shape[0]
        if (
            type(self.pixel_size) == int
            or type(self.pixel_size) == float
            and self.pixel_size != 0
        ):
            radius = int((N * self.pixel_size) / radius)

        filtered_object = deepcopy(self)
        for i in range(len(filtered_object.frames)):
            fft = np.fft.fft2(filtered_object.frames[i])
            fshift = np.fft.fftshift(fft)
            magnitude_spectrum = np.log(np.abs(fshift))
            crow, ccol = int(self.y / 2), int(self.x / 2)
            fshift_filtered = np.copy(fshift)
            mask = np.zeros_like(self.frames[i])

            mask = cv.circle(cv.UMat(mask), (crow, ccol), radius * 2, 1, -1)
            # print(fshift_filtered)
            mask = mask.get()
            mask =~mask.astype(bool)
            fcomplex = fshift[:, :] * 1j
            fshift_filtered = mask * fcomplex
            f_filtered_shifted = np.fft.fftshift(fshift_filtered)
            # magnitude_spectrum_filter = np.log(np.abs(f_filtered_shifted))
            inv_image = np.fft.ifft2(f_filtered_shifted)
            filtered_object.frames[i] = np.abs(inv_image)
            filtered_object.frames[i] -= filtered_object.frames[i].min()
        filtered_object.log.append("high_pass_filter({})".format(radius))
        return filtered_object

    def median_filter(self, kernal=3):
        """
        Returns a median filtered copy of the Microvideo object, kernal size defined in the call (default is 3)

        Parameters
        ----------
                kernal:int
                    The n x n kernal for median filter is defined here, must be an odd integer

        Returns
        -------
                Median_filtered_object :Microvideo
                    Median filtered copy of Microvideo object with median filtered image
        """
        filtered_object = deepcopy(self)
        for i in range(len(filtered_object.frames)):
            filtered_object.frames[i] = cv.medianBlur(filtered_object.frames[i], kernal)
        filtered_object.log.append("median_filter({})".format(kernal))
        return filtered_object

    def weiner_filter(self, kernal=5):
        """
        Returns a Weiner filtered copy of the Microvideo object, kernal size defined in the call (default is 5)

        Parameters
        ----------

                n :int
                    The n x n kernal for Weiner filter is defined here, must be an odd integer

        Returns
        -------

                Weiner_filtered_object : Microvideo
                    Weiner filtered copy of Microvideo object
        """

        from scipy.signal import wiener

        filtered_object = deepcopy(self)
        for i in range(len(filtered_object.frames)):
            filtered_object.frames[i] = wiener(
                filtered_object.frames[i], (kernal, kernal)
            )
        weiner_filter.log.append("weiner_filter({})".format(kernal))
        return filtered_object

    def NLM_filter(self, h=5):
        """
        Returns a non-local means filtered copy of the Microvideo, filter strength is defined in the call.
        More information on non-local means filtering can be found here: https://docs.opencv.org/3.4/d5/d69/tutorial_py_non_local_means.html

        Parameters
        ----------
                h:int
                    Defines the strength of the Non-local means filter, default is 5
        Returns
        -------
                nlm_filtered_object : Microvideo
                    Non-local means filtered copy of the Microvideo object
        """

        filtered_object = deepcopy(self)
        for i in range(len(filtered_object.frames)):
            filtered_object.frames[i] = cv.fastNlMeansDenoising(
                np.uint8(filtered_object.frames[i]), h
            )

        filtered_object.log.append("NLM_filter({})".format(h))
        return filtered_object

    def gaussian_filter(self, kernal=3):
        """
        Returns a Gaussian filtered copy of the micrograph object, kernal size defined in the call (default is 3)

        Parameters
        ----------
                n:int
                    The n x n kernal for median filter is defined here, *must be an odd integer*

        Returns
        -------
                Gaussian_filtered_object :Micrograph
                    Gaussian filtered copy of micrograph object with gaussian filtered image
        """
        if len(self.frames.shape) != 3:
            raise Exception("There should be 3 axis for this, erroring here.")
        swapped = np.swapaxes(self.frames, 0, 2)
        # print(kernal)
        swapped = cv.GaussianBlur(swapped, (kernal, kernal), 0)
        swapped = np.swapaxes(swapped, 0, 2)

        filtered_object = deepcopy(self)
        filtered_object.frames = swapped
        filtered_object.log.append("gaussian_filter({})".format(kernal))
        return filtered_object

    def topaz_denoise(
        self,
        model="unet",
        use_cuda=True,
        lowpass=0,
        cutoff=0,
        gaus=None,
        inv_gaus=None,
        deconvolve=False,
        deconv_patch=1,
        patch_size=1024,
        padding=200,
        normalize=False,
    ):
        """
        Denoise micrograph with topaz denoiser.

        Topaz (https://doi.org/10.1038/s41467-020-18952-1) is a pre-trained implementation of the deeplearning based noise2noise method (https://doi.org/10.48550/arXiv.1803.04189).
        It has been specifically trained on cryo-EM datasets but works pretty well for dryTEM and liquid-TEM images and videos. It is very effective at reducing noise and enhancing lower resolution features, although is not necessarily trustworthy for high resolution data.
        Use with caution, but it is a powerful method.

        Best to only perform on a machine with high RAM and ideally a CUDA GPU, as can take a long time with lesser computers.
        If topaz is not installed, simply type `pip install topaz-em` into the command line.

        Unfortunately bespoke training is not currently included in SimpliPyTEM, so please use Topaz to train your own model.

        Parameters
        ----------
            The parameters here are not required for running with default options, these are available through the topaz code and thus documentation for more advanced options can be found in topaz documentation (https://github.com/tbepler/topaz/, https://topaz-em.readthedocs.io/en/latest/?badge=latest)
            The important parameters are which model is used, and whether to use a cuda GPU:

            model: str
                Which topaz denoising model is used, options are ['unet', 'unet-small', 'fcnn', 'affine', 'unet-v0.2.1']
            use_cuda: bool
                Use CUDA gpu(s)? true or false.




        """

        import topaz.denoise as dn
        from topaz.commands import denoise

        frames = self.frames.copy()
        frames = frames.astype("float32")

        im_denoised = deepcopy(self)
        denoised_frames = []

        if gaus != None and gaus > 0:
            gaus = dn.GaussianDenoise(gaus)
            if use_cuda:
                gaus.cuda()
        else:
            gaus = None

        if inv_gaus != None and inv_gaus > 0:
            inv_gaus = dn.InvGaussianFilter(inv_gaus)
            if use_cuda:
                inv_gaus.cuda()
        else:
            inv_gaus = None

        model = dn.load_model(model)
        if use_cuda:
            model.cuda()

        for frame in frames:
            output = denoise.denoise_image(
                frame,
                [model],
                lowpass=lowpass,
                cutoff=cutoff,
                gaus=gaus,
                inv_gaus=inv_gaus,
                deconvolve=deconvolve,
                deconv_patch=deconv_patch,
                patch_size=1024,
                padding=200,
                normalize=False,
                use_cuda=use_cuda,
            )
            denoised_frames.append(output)
        im_denoised.frames = np.array(denoised_frames)

        return im_denoised

    """
    ------------------------------------------------------------------------------------------------------------
    Section Visualising images

    used for plotting images using matplotlib. Functions very basic so only meant for rapid use, for better figures write own function or use save command

    """

    def imshow(self, title=None, vmax=None, vmin=None, framenumber=0, average=False):
        """
        Method to view the video as a static image. This method completely uses matplotlib's imshow function to show the image, however this allows control of display with a single command.

        This method allows control of the title, whether the image is averaged, which frame is plotted and the maximum and minimum values plotted.

        Parameters
        ----------

            title:str
                This gives a title to the plot.

            vmax:int or float
                The maximum value in the image such that any value above vmax is white.

            vmin: int or float
                The minimum value in the image such that any value below vmin is black.

            framenumber: int
                The index of the frame to be shown (starting from zero, minus numbers can also count from the final frame, i.e -1 is the final frame). If the frame number is out of range, an IndexError is raised.

            average: bool
                Setting to True shows an average of all the frames of the video rather than individual frame number


        """

        if average:
            av = np.sum(self.frames, axis=0)

        if not vmax:
            if not average:
                vmax = np.max(self.frames)
            else:
                vmax = np.max(av)
        if not vmin:
            if not average:
                vmin = np.min(self.frames)
            else:
                vmin = np.min(av)

        plt.subplots(figsize=(20, 10))
        if title:
            plt.title(title, fontsize=30)
        if average:
            plt.imshow(av, vmax=vmax, vmin=vmin)
        else:
            plt.imshow(self.frames[framenumber], vmax=vmax, vmin=vmin)
        plt.show()

    def imshow_pair(self, other_image, title1="", title2="", average=True):
        """
        Basic function for plotting 2 stills from videos side by side. this


        """
        fig, ax = plt.subplots(1, 2, figsize=(50, 30))
        ax[0].imshow(self.frames[0])
        if title1 != "":
            ax[0].set_title(title1, fontsize=30)

        ax[1].imshow(other_image)
        if title2 != "":
            ax[1].set_title(title2, fontsize=30)
        plt.show()

    def Sidebyside(self, Video2):
        """
        Joins a second video (in the form of a numpy array) to the original video, allowing them to be played side by side.

        Parameters
        ----------

            Video2:np array
                The second video to add to the original video

        Returns
        -------
            sidebyside:MicroVideo
                Copy of the original video with the second video grafted onto the side.
        """
        # Add video as numpy stack (Z,Y,X )
        # print(Video1.shape)
        z1, y1, x1 = self.frames.shape
        z2, y2, x2 = Video2.shape
        sidebyside = np.zeros((max(z1, z2), max(y1, y2), x1 + x2), dtype="uint8")

        # this was put here to invert the masked video, DO this BEFORE calling function.
        # masksinv=cv.bitwise_not(np.array(masks))
        sidebyside[:, :, :x1] = self.frames

        sidebyside[:, :, x1:] = Video2[:, :, :]
        # plt.imshow(sidebyside[0], cmap='magma')
        # plt.show()
        sidebyside_object = deep_copy(self)
        sidebyside_object.frames = sidebyside
        return sidebyside

    def plot_histogram(
        self, sidebyside=False, imAverage=True, histAverage=False, vmax=None, vmin=None
    ):
        """
        Plots the histogram of the video (or average of the video), this an be accompanied by either the first frame of the video or the sum of the video frames.

        Parameters
        ----------
            sidebyside:bool
                plots the histogram beside a still image of the video - either first frame or image sum

            imAverage:bool
                if plotting a still, this determines whether the still is the video sum (average) or the first frame, true for video sum.

            histAverage:bool
                Plot the histogram of the average frame? (True) or the histogram of the whole video (False)

             vmax:int or float
                The maximum value in the sidebyside plotted image such that any value above vmax is white.

            vmin: int or float
                The minimum value in the sidebyside plotted image such that any value below vmin is black.

        Output
        ------

            Plots the histogram of the video, can have a video still beside the histogram.


        """
        # evalute the vmaxes depending on imAverage
        if imAverage or histAverage:
            av = np.sum(self.frames, axis=0)

        if sidebyside:
            if not vmax:
                if not imAverage:
                    vmax = np.max(self.frames)
                else:
                    vmax = np.max(av)
            if not vmin:
                if not imAverage:
                    vmin = np.min(self.frames)
                else:
                    vmin = np.min(av)

            fig, ax = plt.subplots(1, 2, figsize=(30, 15))
            ax[1].tick_params(axis="x", labelsize=25)
            ax[1].tick_params(axis="y", labelsize=25)

            # plot image
            if imAverage:
                ax[0].imshow(av, vmax=vmax, vmin=vmin)
            else:
                ax[0].imshow(self.frames[0], vmax=vmax, vmin=vmin)

            if histAverage:
                ax[1].hist(av.ravel(), 100)
            else:
                if self.frames.dtype == "unit8":
                    ax[1].hist(self.frames.ravel(), 256, [0, 256])
                else:
                    ax[1].hist(self.frames.ravel(), 100)
            ax[1].set_xlabel("Pixel Values", fontsize=30)
            ax[1].set_ylabel("Frequency", fontsize=30)

        else:
            fig, ax = plt.subplots(1, 1, figsize=(5, 5))
            # ax.tick_params(axis='x', labelsize=25)
            # ax.tick_params(axis='y', labelsize=25)
            if histAverage:
                plt.hist(av.ravel(), 100)
            else:
                if self.frames.dtype == "unit8":
                    plt.hist(self.frames.ravel(), 256, [0, 256])

                else:
                    plt.hist(self.frames.ravel(), 100)

        plt.show()

    def show_video(self, width=500, fps=None, loop=0):
        """
        Method to show the video within a jupyter notebook.

        Parameters
        ----------

            fps: int
                The frame rate of the video show (in frames per second), default is to take it from the metadata, and failing that show it at 10fps.

            width:int
                The width of the video shown

            loop:int
                Set to 1 to make the video automatically loop.



        """
        if not fps and hasattr(self, "fps"):
            fps = self.fps
        elif not fps and not hasattr(self, "fps"):
            fps = 10

        outvid = []
        for frame in self.frames:
            frame = cv.cvtColor(frame, cv.COLOR_GRAY2BGR)
            outvid.append(frame)
        outvid = np.array(outvid)
        clip = ImageSequenceClip(list(outvid), fps=fps)
        return clip.ipython_display(width=width, loop=loop)

    """------------------------------------------
    SECTION: VIDEO SPECIFIC METHODS

    """

    def Average_frames(self, groupsize, keep_remainder=False):
        """
        Sums frames in groups, reducing the number of frames and the time resolution but increases contrast.

        Parameters
        ----------
            Groupsize:int
                Number of frames per group to average. Best as a multiple of the number of frames, else the final group will be the remainder (ie a 25 frame video split into groups of 10 will have 3 output frames: 1-10,11-20, 21-25 ).

            keep_remainder: bool
                Set to false to ignore the remainder when averaging (eg a 25 frame video split into sets of 10 leads to 2 frames, with the final 5 frames of the original being abandonned.)

        Returns
        -------
            SummedMicroVideo: Microvideo
                Copy of the original video object with frames averaged in groups of {groupsize}
        """

        newframes = []
        for x in range(0, len(self.frames), groupsize):
            if x + groupsize > len(self.frames):
                frame = np.sum(self.frames[x : len(self.frames)], axis=0)
            else:
                frame = np.sum(self.frames[x : x + groupsize], axis=0)
            newframes.append(frame)
        averaged_object = deepcopy(self)
        if len(self.frames) % groupsize != 0 and not keep_remainder:
            newframes = newframes[:-1]
        averaged_object.frames = np.array(newframes)
        averaged_object.reset_xy()
        averaged_object.log.append("Average_frames({})".format(groupsize))
        return averaged_object

    def Running_average(self, groupsize):
        """
        Sums frames in group of {groupsize} in a running or rolling average fashion - in this case these groups overlap with only a single frame offset, meaning the resulting video has (n - groupsize) frames.

        Parameters
        ----------
            Groupsize:int
                Number of frames per group to average. Best as a multiple of the number of frames, else the final group will be the remainder (ie a 25 frame video split into groups of 10 will have 3 output frames: 1-10,11-20, 21-25 ).
        Returns
        -------
            RunningAveragedMicrovideo:Microvideo
                Copy of the original video object with frames averaged into groups of {groupsize} with a 1 frame offset between frames
        """
        averaged_video = []
        for i in range(0, len(self.frames) - groupsize):
            frame_group = self.frames[i : i + groupsize]
            av_frame_group = np.sum(frame_group, axis=0)
            averaged_video.append(av_frame_group)
        averaged_object = deepcopy(self)
        averaged_object.frames = np.array(averaged_video)
        averaged_object.reset_xy()
        averaged_object.log.append("Running_average({})".format(groupsize))
        return averaged_object

    """---------------------------------
    SECTION MOTION CORRECTION
    
    This defines using motioncor2 to align video frames, these frames either need to be saved individually, in which case the function group_frames is needed on the image set before use
    Motioncorrect_video works on a dm4 file, converts it to mrc and then runs motioncor on this image stack. 


    """

    def motioncorrect_vid(self, vid_output=False):
        """
        This is tricky to use but can be incredibly effective, motioncorrecting LTEM videos can dramatically improve the signal to noise ratio of outputted averages.
        Here I use the publically available software motioncor2, which can be downloaded from here: https://emcore.ucsf.edu/ucsf-software which can correct for motion within the video.

        In order to use this function, you need to download this software, and then set a path to the executable, note that several versions will be downloaded so ensure you use the correct one for your CUDA setup, I believe CUDA is required for this.

        to set the executable, open terminal and type:
            ```export MOTIONCOR2_PATH='PATH/TO/EXECUTABLE'```

        to give an example of what this looks like, this is how it looks on my computer:

            ```export MOTIONCOR2_PATH='/home/Gabriel/Downloads/MotionCor2_1.4.4/MotionCor2_1.4.4_Cuda113-08-11-2021'```

        You can also set the executable directly from an ipython workbook by running `os.environ['MOTIONCOR2_PATH']='~/Downloads/MotionCor2_1.4.4/MotionCor2_1.4.4_Cuda113-08-11-2021'`

        To avoid needing to do this for every new terminal opened, add this line to your .bashrc file in your home directory (you can use the terminal text editor nano for this: ```nano ~/.bashrc```)

        After doing this, the function should hopefully work, just use:

            video=MicroVideo()
            video.open_dm('myfile.dm4')
            motioncorrected_vid = video.motioncorrect_vid()


        Parameters
        ----------

            vid_output:bool
                Do you want to output a video or just an average image? Image (False) is used for SimpliPyTEM-GUI, Video (True) produces far more data but gives more useful results.

        Returns
        -------

            MotionCorrected_video_object:

        """

        original_cwd = os.getcwd()
        tifname = "OutIntermediate.mrc"
        outname = ".".join(self.filename.split(".")[:-1]) + "Motion_corrected.mrc"
        outname = outname.replace(" ", "_")
        print("outname = ", outname)
        outname = outname.split("/")[-1]

        if "/" in self.filename:
            directory = "/".join(self.filename.split("/")[:-1])
        else:
            directory = os.getcwd()
        os.chdir(directory)
        print("cwd = ", os.getcwd())
        MCor_path = os.environ.get("MOTIONCOR2_PATH")
        if MCor_path:
            if vid_output:
                command = "{} -InMrc {} -OutMrc {} -Iter 10 -Tol 0.5 -Throw 1 -Kv 200 -PixlSize {} -OutStack 1".format(
                    MCor_path, tifname, outname, self.pixel_size * 10
                )
                MC_vid = deepcopy(self)
                inname = ".".join(outname.split(".")[:-1]) + "_Stk.mrc"
            else:
                command = "{} -InMrc {} -OutMrc {} -Iter 10 -Tol 0.5 -Throw 1 -Kv 200 -PixlSize {}".format(
                    MCor_path, tifname, outname, self.pixel_size * 10
                )
                MC_vid = Micrograph()
                inname = ".".join(outname.split(".")[:-1]) + ".mrc"
            self.write_mrc(name=tifname, overwrite=True)
            sb.call(command, shell=True, cwd=os.getcwd())
        else:
            print(
                "Sorry, the motioncor2 exectuable is not defined and so cannot be run. Please give the executable using \"export MOTIONCOR2_PATH='PATH/TO/EXECUTABLE'\" (or on windows: \"setx MY_EXECUTABLE_PATH 'path/to/executable'\") for more info, please see documentation  "
            )
            return 1

        try:
            MC_vid.open_mrc(inname)
        except FileNotFoundError:
            print(
                "The file isn't found - this usually appears to be a motioncor2 issue, sometimes it fails to save an image as a stack for some unknown reason (likely to do with filesize), maybe try decreasing the size by binning/averaging?"
            )
            return 1
        MC_vid.metadata_tags = self.metadata_tags
        MC_vid.pixel_size = self.pixel_size
        MC_vid.pixel_unit = self.pixel_unit
        MC_vid.fps = self.fps
        MC_vid.filename = self.filename + "_MotionCorrected"
        os.remove(tifname)
        os.chdir(original_cwd)
        MC_vid.log.append("motioncorrect_vid()")
        return MC_vid

    def display_fft(self, average=True, ret=False, vmax=None, vmin=None):
        """
        Function to see the 2D Fourier transform of the video.

        Parameters
        ----------

            Average:bool
                Do you want to see a powerspectrum for the average of the video? True or False (default=True) if true, it will be displayed automatically unless the `ret` paraameter is used to return it as a new micrograph object.


            vmax: int/float
                The 'white value' when plotting the power spectrum, such that anything above this value is set to white.

            vmin: int/float
                The 'black value' when plotting the power spectrum, such that anything below this value is set to black.

            ret: bool
                Set to true if you want to return a copy of the fft as a micrograph object. Only works if average=True, if average=False, a new object will always be returned.

        Returns
        -------

            If ret==True and average=True, a new micrograph object is returned with the power spectrum of the average of the video as the micrograph.image attribute, from here the same functions can be used

            if Average==False, a new MicroVideo object is returned with the powerspectrum of each frame sa the .frames attribute.


        """
        if average:
            av = np.sum(self.frames, axis=0)
            fft = np.fft.fft2(av)
            fshift = np.fft.fftshift(fft)
            magnitude_spectrum = np.log(np.abs(fshift))
            magnitude_spectrum = magnitude_spectrum.astype(np.float32)

            if not vmax:
                vmax = magnitude_spectrum.max()
            if not vmin:
                vmin = magnitude_spectrum.min()

            if ret:
                fft_ob = Micrograph()
                fft_ob.image = magnitude_spectrum
                fft_ob.reset_xy()
                filename = self.filename.split(".")[:-1]
                filename.append("_FFT")
                fft_ob.filename = filename
                return fft_ob
            else:
                plt.figure(figsize=(20, 20))
                plt.imshow(magnitude_spectrum, vmin=vmin, vmax=vmax)
                plt.show()
        else:
            fft_frames = []
            for frame in self.frames:
                fft = np.fft.fft2(frame)
                fshift = np.fft.fftshift(fft)
                magnitude_spectrum = np.log(np.abs(fshift))
                magnitude_spectrum = magnitude_spectrum.astype(np.float32)
                fft_frames.append(magnitude_spectrum)
            fft_ob = MicroVideo()
            fft_ob.frames = np.array(fft_frames)
            fft_ob.reset_xy()
            filename = self.filename.split(".")[:-1]
            filename.append("_FFT")
            fft_ob.filename = filename
            return fft_ob


# I had to move default pipeline outside of the class because the filters make a new instance of the class and I didnt want to multiply the number of instances in memory.
# Use: default_pipeline(micrograph)
def default_video_pipeline(
    filename,
    vid_type,
    contrast_enhance=True,
    medfilter=0,
    gaussfilter=3,
    scalebar=True,
    xybin=2,
    color="Auto",
    Average_frames=2,
    save_metadata=True,
    metadata_name="metadata.csv",
    outdir=".",
    name=None,
    topaz_denoise=False,
    denoise_with_cuda=False,
    im_type = 'jpg'
):
    """
    Use to automate default filtering, scalebar adding, binning,frame averaging and saving.

    From a coding point of view this function is a bit of a mess with if...elif...else statements so I should clear it up at some point.

    Parameters
    ----------

        filename: str
            The filename of the .dm3 or .dm4 file to open
        output type: str
            This needs to be one of the following: ['Save Tif Stack', 'Save Tif Sequence', 'Save Video as .mp4', 'Save video as .avi', 'Save MotionCorrected Average']. To save as an average, use default_image_pipeline (Micrograph_class module).
        medfilter: int
            Kernal value for a median filter to apply, zero is no filter
        gaussfilter: int
            Kernal for a gaussian filter to apply, zero is no filter
        xybin: int
            value by which the image is binned (reduced size) on both the x and y axis
        scalebar:bool
            True for adding scalebar, False for not adding scalebar
        Average_frames: int
            Average this number of frames together, only used for saving as video options.
        topaz_denoise: bool
            Denoise with topaz? True (default) or False (default)
        denoise_with_cuda: bool
            If denoising with topaz, use CUDA gpu for this? If availble this will dramatically increase speed.

    Outputs
    -------

        Performs filtering etc as parameters suggest, saves it in format defined in output_type.

    """

    print("Processing :", filename)

    MicroVideo_object = MicroVideo(filename)

    if save_metadata == True and filename[-4:-1] == ".dm":
        MicroVideo_object.export_metadata(metadata_name, outdir)

    # print(MicroVideo_object)
    if not name:
        name = ".".join(MicroVideo_object.filename.split(".")[:-1])

    if vid_type == "Save MotionCorrected Average":
        MCor_im = MicroVideo_object.motioncorrect_vid()
        if topaz_denoise:
            Mcor_im = Mcor_im.topaz_denoise(use_cuda=denoise_with_cuda)

        if MCor_im == 1:
            default_image_pipeline(
                filename,
                output_type=im_type,
                xybin=xybin,
                medfilter=medfilter,
                gaussfilter=gaussfilter,
                outdir=outdir,
            )
            return 1
        # aved =  MCor_vid.toMicrograph()
        print(medfilter, type(medfilter))
        if medfilter != 0:
            MCor_im = MCor_im.median_filter(int(medfilter))
        if gaussfilter != 0:
            MCor_im = MCor_im.gaussian_filter(gaussfilter)

        if xybin != 0 and xybin != 1:
            MCor_im = MCor_im.bin(xybin)
        if contrast_enhance:
            MCor_im = MCor_im.clip_contrast()
        if scalebar == True:
            MCor_im = MCor_im.make_scalebar()

        MCor_im.write_image(name, outdir=outdir + "/Images", ftype=im_type)

    else:
        if xybin != 0 and xybin != 1:
            MicroVideo_object = MicroVideo_object.bin(xybin)

        if topaz_denoise:
            MicroVideo_object = MicroVideo_object.topaz_denoise(
                use_cuda=denoise_with_cuda
            )

        if type(medfilter) == int and medfilter != 0:
            MicroVideo_object = MicroVideo_object.median_filter(medfilter)

        if type(gaussfilter) == int and gaussfilter != 0:
            MicroVideo_object = MicroVideo_object.gaussian_filter(gaussfilter)

        if not name:
            name = ".".join(MicroVideo_object.filename.split(".")[:1])
        # MicroVideo_object.bin(xybin)

        if vid_type == "Save Video as .mp4" or vid_type == "Save Video as .avi":
            if Average_frames != 0 and Average_frames != 1:
                MicroVideo_object = MicroVideo_object.Average_frames(
                    Average_frames, keep_remainder=False
                )
            print("Saving {} as video".format(filename))
            if contrast_enhance:
                MicroVideo_object = MicroVideo_object.clip_contrast()
            MicroVideo_object.convert_to_8bit()

            if scalebar == True:
                MicroVideo_object = MicroVideo_object.make_scalebar(color=color)
            name = name + vid_type[-4:]

            MicroVideo_object.write_video(name=name, outdir=outdir + "/Videos")

        elif vid_type == "Save Tif Stack":
            if scalebar == True:
                MicroVideo_object = MicroVideo_object.make_scalebar(color=color)
            if contrast_enhance:
                MicroVideo_object = MicroVideo_object.clip_contrast()
            MicroVideo_object.save_tif_stack(name=name, outdir=outdir + "/Videos")

        elif vid_type == "Save Tif Sequence":
            if scalebar == True:
                MicroVideo_object = MicroVideo_object.make_scalebar(color=color)
                # MicroVideo_object = MicroVideo_object.clip_contrast()
            if contrast_enhance:
                MicroVideo_object = MicroVideo_object.clip_contrast()
            MicroVideo_object.save_tif_sequence(name=name, outdir=outdir + "/Videos")

        else:
            print('Error "{}" is not an acceptable output type.'.format(vid_type))


# def group_frames( frames):
#    prefixes = []
#   prefix_set=set()
#   frames.sort()
#   tups = []
#   organised_dict= {}
#   for file in frames:
#        file2 = file[:-4]
#      end = file2[-9:]
#       ids = end.split('-')
#      vid_id = ids[0]
#      frame_id = ids[1]
#       tups.append((file, vid_id, frame_id))
#       prefix_set.add(vid_id)

#   for prefix in prefix_set:
#       images_per_prefix = [x[0] for x in tups if x[1]==prefix]
#       organised_dict[prefix]=images_per_prefix
#     return organised_dict
