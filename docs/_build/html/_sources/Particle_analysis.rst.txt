Particle analysis module
===================

This is a module for some basic analysis of particle size and shape by thresholding the particle and extracting data, this works for videos and for images. There is a tutorial for using this module in the tutorials folder on the github (thresholding)
While this module is relatively basic, it can be very easily and effectively used. 

Usage
-----

The basic method is:
   1. apply threshold to get binary image (Threshold())
   2. Find particles from binary image (Find_contours()) and filter by size
   3. Collect data (Collect_particle_data())

This can be done as follows::
      
      #import module 
      from simpliPyTEM.Particle_analysis import * 

      #Threshold the image using pixel value 100 (for example)
      thresh = Threshold(image, 100)

      #Find the edge of the particle from binary image, only consider particles over 200 pixels in area
      contours_im, mask = Find_contours(thresh, minsize=200)

      #Collect the data from the contours_im (edge coordinates)
      particle_data = Collect_particle_data(contours_im, pixelSize, multimeasure)

      #Plot a histogram of the radius data extracted from the particles.
      plt.hist(particle_data['radius'])
      plt.show()

     
Documentation
-------------
.. automodule:: Particle_analysis
   :members:
   :undoc-members:
   :show-inheritance:
