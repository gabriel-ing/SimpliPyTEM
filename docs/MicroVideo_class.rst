MicroVideo Class
================

Module containing the class MicroVideo, this is the main tool of video analysis within the SimpliPyTEM package. The videos are loaded using one of the loading methods (open_dm or open_video), at which point the MicroVideo object contains the video data as a numpy array within the .frames attribute.  Many methods can be run with this object, including image filtering, converting to 8bit, improving contrast, plotting the image and the histogram. 

The aim of this module was to make python-based analysis/basic enhancements of in situ TEM videos more simple by putting the majority of desired methods in a single package with simple commands. 

This works in the same way as the Micrograph class but is designed for video data instead. As with the micrograph class, there are too many functions to include description of all here, beyond the autodoc documentation, however I recommend checking out the interactive jupyter notebook tutorial (docs/Tutorials/MicroVideoAnalysisTutorial.ipynb). This is also available here: 

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   Tutorials/MicroVideoAnalysisTutorial

Please note that this tutorial is automatically generated from the jupyter notebook tutorial and some things have imported poorly or have errored (mainly because files are note available).

Example
-------
Basic example including many of the functions :: 

    #Import module
    from SimpliPyTEM.MicroVideo_class import MicroVideo
    
    #Initialise video
    video = MicroVideo('My_video.dm4')
    
    #Bin video (reduce size) 
    video = video.bin(2)

    #Gaussian filter (smooth) video
    video = video.gaussian_filter(3)

    #Convert to 8bit (pixel values from 0-255)
    video.convert_to_8bit()

    #Improve contrast
    video = video.clip_contrast()

    #Add a suitably sized scalebar
    video = video.make_scalebar()

    #Show the first frame
    video.imshow(average=False, frame_number=0)

    #Show an image of the average frame
    video.imshow(average=True)

    #Average the video, combining 5 frames 
    av = video.average_frames(5)

    #Save video as mp4
    video.write_video('Output.mp4')

Note that in each of these function examples I am overwriting the previous copy of the video by running (e.g.) video=video.bin() , can be desireable to reduce memorey use but you can also save them as separate to ensure you  keep the originals. 


List of functions in MicroVideo
-------------------------------

Imports:
    * open_dm - Opening digital micrograph files
    * open_video - Opening a .mp4 or .avi video files
    * open_array - Loading a numpy array 
    * open_hyperspy 

Saving: 
    * save_tif_stack
    * save_tif_sequence
    * write_video - save .mp4 or .avi version of the video
    * write_image - save video frame or video average as an image
    * write_mrc - saves file as .mrc file

Basic functions: 
    * bin - reduce size of xy axis by binning pixels, factor is specified in call
    * convert_to_8bit - converts to 8bit video by scaling pixel values between 0-255. 
    * make_scalebar  - creates suitably sized scalebar 
    * Average_frames - averages frames in groups of n
    * Running_average - performs a running average of the video 
    * reset_xy - reset the object x, y and shape attributes upon change of video, useful if video is cropped. 

Contrast enhancement: 
    * clip_contrast - enhances contrast by making a percentage of values saturated (absolute black/white) and scaling the rest of the pixels between these (my preferred contrast enhancement)
    * enhance_contrast - enhances contrast based on alpha (contrast), beta (brightness) and gamma (non-linear contrast) values
    * eqHist - equalises histogram, ensuring even converage of pixel values from 0-255
    * Normalise_video - normalises contrast between frames of the video

Metadata (currently relies on dm3/dm4 metadata):
    * show_metadata - shows all metadata tags and values
    * get_mag - prints and returns magnification (indicated and actual)
    * get_voltage - prints and returns voltage
    * get_exposure - prints and returns frame rate, exposure time
    * get_date_time - prints aquisition date and time 
    * export_metadata - saves metadata into a .csv file

Image filters:
    * gaussian_filter
    * median_filter
    * low_pass_filter
    * weiner_filter
    * non_local_means_filter
    * topaz_denoise - Denoise with topaz, run `pip install topaz-em` before use. 
    * high_pass_filter

Plotting:
    * imshow - plots still image (either single frame or average) of video
    * plot_histogram - plots the histogram of the video 
    * show_video - shows video in a jupyter notebook (very slow)

Other functions:
    * Sidebyside - Sticks two videos together so they play side by side. 
    * local_normalisation - evens out the contrast within the frames of a video, correcting for uneven illumination.

Documentation 
-------------

.. automodule:: MicroVideo_class
    :members:
    :undoc-members:
    :show-inheritance:

