Micrograph Class
================

The micrograph class is the main container for all the image processing. Micrographs are loaded into the object, including metadata and then many methods can be run with this object, including image filtering, converting to 8bit, improving contrast, plotting the image and the histogram. The image data is stored as a numpy array within the .image attribute.

There is too much to write detailed documentation alongside the autodoc documentation listed below, however full explanations for all of this can be found in the jupyter tutorial (tutorials/MicrographAnalysisTutorial), which is also available on this site: 

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   Tutorials/MicrographAnalysisTutorial

Example
-------
Here is a basic example showing a micrograph being opened, gaussian filtered, converted to 8bit, contrast enhanced, scalebar added, plotted and saved as a jpg::
        
        #import the class 
        from SimpliPyTEM.Micrograph_class import Micrograph

        #initialise class and open file
        image = Micrograph('My_file.dm4')

        #gaussian filter
        im_gaussian =image.gaussian_filter(5)

        #convert to 8-bit
        im8bit = im_gaussian.convert_to_8bit()
        
        # enhance contrast
        im_contrast_enhanced = im8bit.clip_contrast()

        #add scalebar 
        im_contrast_enhanced_SB = im_contrast_enhanced.make_scalebar()
        
        #plot image
        im_contrast_enhanced_SB.imshow()

        #save image
        im_contrast_enhanced.write_image('output.jpg')

List of functions in MicroVideo
-------------------------------

Imports:
    * open_dm - Opening digital micrograph files
    * open_mrc - Opening an mrc file
    * open_image - Opening .tif, .jpg, .png
    * open_video - Open .mp4 or .avi as an all-frame average
    * open_file - Opening any image/video file (using other functions)

Saving: 
    * write_image - save video frame or video average as an image

Basic functions: 
    * reset_xy - reset the object x, y and shape attributes upon change of video, useful if video is cropped. 
    * bin - reduce size of xy axis by binning pixels, factor is specified in call
    * convert_to_8bit - converts to 8bit video by scaling pixel values between 0-255. 
    * make_scalebar  - creates suitably sized scalebar 
    * Average_frames - averages frames in groups of n
    * Running_average - performs a running average of the video 

Contrast enhancement: 
    * clip_contrast - enhances contrast by making a percentage of values saturated (absolute black/white) and scaling the rest of the pixels between these (my preferred contrast enhancement)
    * enhance_contrast - enhances contrast based on alpha (contrast), beta (brightness) and gamma (non-linear contrast) values
    * eqHist - equalises histogram, ensuring even converage of pixel values from 0-255
    * local_normalisation - Evens out contrast across the image 

Metadata (currently relies on dm3/dm4 metadata):
    * show_metadata - shows all metadata tags and values
    * get_mag - prints and returns magnification (indicated and actual)
    * get_voltage - prints and returns voltage
    * get_exposure - prints and returns frame rate, exposure time
    * get_date_time - prints aquisition date and time 

Image filters:
    * gaussian_filter
    * median_filter
    * low_pass_filter
    * weiner_filter
    * non_local_means_filter
    * denoise_with_topaz - denoises with topaz (https://doi.org/10.1038/s41467-020-18952-1), run `pip install topaz-em` before use.

Plotting:
    * imshow - plots image
    * plot_histogram - plots the histogram of the image 
    * imshow_pair - plots two images side by side  

Others:
    * display_fft - shows the 2D Fourier Transform of the image
    



Documentation 
-------------

.. automodule:: Micrograph_class
        :members:
        :undoc-members:
        :show-inheritance: