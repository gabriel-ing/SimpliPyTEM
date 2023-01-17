SimpliPyTEM-GUI
===============

While using python will allow one to get the most out of the package, for many learning python is intimidating, and time ends up being wasted manually processing images. Here I am introducing a GUI-based pipeline to create high quality JPEGs, with a good size scale bar automatically added, minor filtering (median and gaussian filtering) available, and video (or dose-fractionation) processing options included. 

Combined with this, there are options to create html or pdf documentss containing the images (and videos in the case of html) generated. These documents can be a very useful way to easily evaluate the images/videos taken in an TEM experiment. 

.. image:: Media/Images/SimpliPyTEM_figures.001.png
    :width: 600
    :alt: Figure showing aim of SimpliPyTEM-GUI



Usage - Section 1: Image generation
-----------------------------------

App usage is fairly simple, and is presented in a stepwise fashion here;

Open terminal and call: 

```python SimpliPyTEM_app.py```  **Need to find a way to make this run from anywhere** 

The GUI should appear as follows: 

.. image:: Media/Images/App_screenshot1.png
    :width: 300
    :alt: a screenshot showing the app GUI


This app is split into two main sections, The top section containing the Image/video generator. You can either select a folder, a file or run live processing:
    
    **Folder** - process each .dm3 or .dm4 file in the folder

    **File** - process a single file

    **Live processing** - process new .dm3/.dm4 files which appear within the folder. 

After selecting this option, a folder/file needs to be selected using the 'Choose Folder' button, this should open a file dialog where you can navigate to the intended folder/file.

The options below are the basic processing options available, these are: 
    
    **Median filter** - applies a median filter to reduce salt-and-pepper noise in the output. The number next to it denotes the kernal size of the filter 

    **Gaussian filter** - applies a gaussian filter to smooth the output. The number next to it denotes the kernal size of the filter 

    **Bin image** - Reduces the size of the image on the x&y axis 

    **Scalebar** - Adds a suitably-sized scalebar to the image

Below this there is an option to give an output folder name. The images will be saved in a directory called Images, and the videos in a directory called Videos. These can be contained in an extra directory, which is particularly useful for holding  html/css files you may wish generate later. 

Add an output folder name or leave blank, as you wish. 

There are then options on how to handle video, or image stack files (collected as dose-fractionations on Gatan Direct electron detectors). If you do not have video files, you can ignore this. If video files are included in the dataset, there are a few options: 

    **Save Average** - Saves a time-average of the frames in the video 

    **Save Video as MP4** - Save video as mp4 file (good for making an html) 

    **Save Tif Sequence** - Saves each frame of the video as tif file 

    **Save MotionCorrected average** - Motioncorrects video using motionCor2 (executable must be set, see motioncorrection page)

After the options are selected press the **'Run!'** button and the files will be processed. 



Section 2: Document Generation 
------------------------------

This section handles the generation of html or pdf documents containing your images/videos for easy post-experiment image evaluation and sharing. 

The videos are found based on the folder choices in section 1, but will work even if you haven't Run! this section. To generate the document do as follows: 

    Choose folder with the raw data  by clicking 'Choose Folder' 
    Choose output folder name within this in the 'Give' output folder a name' box  (leave blank if you are happy with the same folder). 
        - The key point here is that this folder (or the previous folder if this one is blank) should have a folder called 'Images' in. 

    Add an experiment title and/or notes about the experiment in the boxes in the document section

    Click **'Make HTML!'** for an html file (this also generates a .css file to improve the style of this doc)
    Click **'Make PDF!'** for a pdf file.
