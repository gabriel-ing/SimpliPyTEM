# Create previews of digital micrograph images
### Image_previews_openCV.py

This python script will open all the digital micrograph .dm3 files in a folder, median filter, gaussian blur, bin the image by 2 and add a scalebar of a suitable size and save the file as a .jpg in a separate folder. 

Hasn't been extensively tested but should be very useful at creating a low resolution, small size preview of the micrographs to examine, if you want higher resolution or no filtering, commands can be commented out. By using this script, all the scale bars should match on the images  

Usage: *python Image_previews_openCV.py*

Dependancies :

numpy (*pip install numpy*) - array handling 

opencv (*pip install opencv-python*) - image handling and filtering 

ncempy (*pip install ncempy*) - .dm3 parser 

matplotlib (*pip install matplotlib*) - Not needed unless you want to plot the images 

os (*pip install os_sys*) - handling operating system functions (create directory to save files in, list files in the directory etc) 
