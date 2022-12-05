from setuptools import setup 

setup(
	name='SimpliPyTEM',
	version='0.1.0',
	discription='A python package to simplify the processing and analysis of TEM and in situ TEM images and videos',
	url='https://github/gabriel-ing/Micrograph-analysis-scripts',
	author='Gabriel Ing',
	author_email='ucbtgrb@ucl.ac.uk',
	license = 'BSD 2-clause',
	packages =['SimpliPyTEM'],
	install_requires=['numpy', 'ncempy', 'pillow', 'mrcfile', 'moviepy', 'airium', 'matplotlib', 'opencv-python', 'pillow', 'tifffile', 'notebook','scikit-image', 'imutils'],
	classifiers=[
		'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',     
        'Programming Language :: Python :: 3'],


)
