# Create previews of digital micrograph images
### Image_previews_openCV.py

This python script will open all the digital micrograph .dm3 files in a folder, median filter, bin the image by 2 and add a scalebar of a suitable size and save the file as a .jpg in a separate folder. 

The script should be very useful at creating a low resolution, small size preview of the micrographs to examine, if you want higher resolution or no filtering, commands can be commented out. By using this script, all the scale bars should match on the images (in height, position and labelling). It will also process images very quickly (my macbook pro 2017 can process an image in 0.5s)

The script can also handle micrograph stacks (assuming your computer has the memory to do so). For image stacks it will save an average of all the individual images, again by default this is binned, median filtered and scalebar added, the same arguments should work with stacks. This method is significantly faster at processing image stacks than imageJ (for 25-frame, 1.5gb image stack it took less than 10 seconds to generate a preview on my workstation). 


I wrote this script for personal use as my previous method using imageJ gave inconsistent scalebars, was considerably slower, and often required manual repeating to get it looking good. Feel free to use, adapt, ask questions if it would be useful to you. 


### Usage: 

process all .dm3 files in directory:

 *python Image_previews_openCV.py*

process a single file 

*python Image_previews_OpenCV.py --file filename*

add additional flag arguments: 

*--color {white, black or  grey}* -override default scale bar color choosing to make scale bar this color
*--quality {int}* -choose quality of jpg image when saving from 1-95 (default 80), lower reduces filesize
*--xybin {int}* - choose level of xybinning, this is 2 by default (output image size = x/2 y/2), put 1 for no binning, more for more binning (smaller file) 
*--textoff {}* - set this to anything other than 0 (easiest is 1) to remove the text from the scalebar, scale bar size can be seen in filename.
 
 
 Before use, you need to download or locate a font .ttf file and add the path to this file on your computer to line 94:
  
  *font = ImageFont.truetype('/path/to/font.ttf', fontsize)*

### Dependancies :

numpy (*pip install numpy*) - array handling 

opencv (*pip install opencv-python*) - image handling and filtering 

ncempy (*pip install ncempy*) - .dm3 parser 

matplotlib (*pip install matplotlib*) - Not needed unless you want to plot the images while running, will signficantly increase running time. (uncomment import and lines of code)

os (*pip install os_sys*) - handling operating system functions (create directory to save files in, list files in the directory etc) should be installed by default

pillow (pip install Pillow) - adding text, image handling

argsparse - adding arguments, should be installed by default

### Things to do :

- Test with more files: including choosing color and different magnifications (DONE) 
- Implement with Dm4 files   (DONE) 
- Use args-parser to change options without editting file (DONE) 
- Break up into different functions, allow some functions to be used on any images (e.g. add scalebar) (DONE) 
- Implement with videos (i.e import image stack, save average of stack) (DONE)

