html\_writer module
===================

This creates html files with the images and movies from an experiment, which can be viewed as a webpage.

 These have the advantage over pdfs when dealing with in situ data, that movies can be played. The downside is that the media files are only linked in the html file, and therefore to share the file the images and movies need to be shared as well. 

 There is also a function to write a css file which gives the document basic formatting, this is far from high quality formating but is a start. 

 I recommend using a directory structure something like this:


Experiment>Media>Images 
Experiment>Media>Videos

Where experiment contains the raw data, media contains the html and css and Images & Videos contain the .jpg (or .tif/.png) images and .mp4 videos respectively 
Then run the functions below from the media folder. 


Usage
-----
Simple usage is summed up below::
   
      #import module
      from SimpliPyTEM.html_writer import *

      #if you are not already in the Media directory (shown above) use:
      import os
      os.chdir(/Path/To/Media)

      #Get files in lists 
      image_files, video_files = get_files(Images_dir, Video_dir)

      #Write the html file
      html_writer(image_files, video_files, title='Experiment title', note='Add some notes about the experiment here...')

      #Write the css file
      write_css()



.. automodule:: html_writer
   :members:
   :undoc-members:
   :show-inheritance:
