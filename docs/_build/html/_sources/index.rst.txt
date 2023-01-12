.. SimpliPyTEM documentation master file, created by
   sphinx-quickstart on Wed Nov 30 18:15:47 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to SimpliPyTEM's documentation!
=======================================

SimpliPyTEM is a python package to make python-based analysis of Transmission electron microscopy images easier and more approachable. Although TEM is the focus, this could also easily be adapted to other microscopy images. 
Importantly, SimpliPyTEM is designed to make automated, basic work accessible for beginners (through a simple GUI), while more complicated methods can be accessed through simple python code. This package centers around the image data being held in a Numpy array which makes the image data easy to access for further analysis. 

SimpliPyTEM also has a modules designed for *in situ* TEM videos, easily altering the functions to include these. 

This project aims to make use of the rapid automation of image analysis methods available through python while making it approachable for the user.

Functions to generate pdf and html files containing images and videos are also included in this package. This allows easy viewing and sharing of all the images/videos taken in an imaging session, making experiment evaluation significantly easier. 

 

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   Micrograph_class
   MicroVideo_class
   PDF_generator
   html_writer
   Particle_analysis
   Previews_app

Installation
------------


``git clone https://github.com/gabriel-ing/Micrograph-analysis-scripts``

``conda create --name SimpliPyTEM python=3.10``

``conda activate SimpliPyTEM``

``cd Micrograph-analysis-scripts``

``pip install .``


Indices
-------


* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Licensing
---------
This project is licensed under the BSD license.
