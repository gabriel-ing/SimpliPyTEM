from setuptools import setup 

setup(
	name='SimpliPyTEM',
	version='1.0.10',
	description='A python package to simplify the processing and analysis of TEM and in situ TEM images and videos',
	long_description='''SimpliPyTEM is a python package to make python-based analysis of Transmission electron microscopy images easier and more approachable. Although TEM is the focus, this could also easily be adapted to other microscopy images. Importantly, SimpliPyTEM is designed to make automated, basic work accessible for beginners (through a simple GUI), while more complicated methods can be accessed through simple python code. This package centers around the image data being held in a Numpy array which makes the image data easy to access for further analysis.
	This project aims to make use of the rapid automation of image analysis methods available through python while making it approachable for the user.
	Functions to generate pdf and html files containing images and videos are also included in this package. This allows easy viewing and sharing of all the images/videos taken in an imaging session, making experiment evaluation significantly easier. 
	For more info, please see: https://micrograph-analysis-scripts.readthedocs.io/en/latest/''',
	url='https://github/gabriel-ing/Micrograph-analysis-scripts',
	author='Gabriel Ing',
	author_email='ucbtgrb@ucl.ac.uk',
	license = 'GPL-3.0',
	packages =['SimpliPyTEM'],
	install_requires=['numpy',
	 'ncempy==1.10.0',
	 'Pillow==10.2.0',
	 'mrcfile==1.4.3',
	 'moviepy==1.0.3',
	 'airium==0.2.5',
	 'matplotlib',
	 'opencv-python==4.7.0.72',
	 'tifffile==2023.3.21',
	 'notebook==7.0.0b2',
	 'scikit-image==0.20.0',
	 'imutils==0.5.4',
	 'fpdf2==2.7.5',
	 'PyQt6==6.5.0',
	 'sphinx',
	 'sphinx_rtd_theme',
	 'nbsphinx',
	 'pandas==1.5.3',
	 'seaborn==0.12.2',
	 'hyperspy==1.7.5',
	 'cherrypicker==0.4.0',
     'imagecodecs'],
	entry_points={'console_scripts':['SimpliPyTEM-GUI = SimpliPyTEM.SimpliPyTEM_GUI:main']},
	classifiers=[
		'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',     
        'Programming Language :: Python :: 3',
		'Topic :: Scientific/Engineering :: Image Processing'],


)
