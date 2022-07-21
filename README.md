# Create previews of digital micrograph images
### Image_previews_openCV.py

This python script will open all the digital micrograph .dm3 files in a folder, median filter, gaussian blur, bin the image by 2 and add a scalebar of a suitable size and save the file as a .jpg in a separate folder. 

Hasn't been extensively tested but should be very useful at creating a low resolution, small size preview of the micrographs to examine, if you want higher resolution or no filtering, commands can be commented out. By using this script, all the scale bars should match on the images  

Usage: 
process all .dm3 files in directory:

 *python Image_previews_openCV.py*

process a single file 

*python Image_previews_OpenCV.py --file filename*

add additional flag arguments: 

*--color {white, black or  grey}* -override default scale bar color choosing to make scale bar this color
*--quality {int}* -choose quality of jpg image when saving from 1-95 (default 80), lower reduces filesize
*--xybin {int}* - choose level of xybinning, this is 2 by default (output image size = x/2 y/2), put 1 for no binning, more for more binning (smaller file) 
*--textoff {}* - set this to anything other than 0 (easiest is 1) to remove the text from the scalebar, scale bar size can be seen in filename.
 
 

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
- Implement with Dm4 files   (   ) 
- Use args-parser to change options without editting file (DONE) 
- Break up into different functions, allow some functions to be used on any images (e.g. add scalebar) (   ) 

