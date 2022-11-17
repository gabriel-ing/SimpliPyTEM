# SimpliPyTEM: an open source project to simplify python-based analysis of electron microscopy data with added focus on in situ videos 

SimpliPyTEM introduces the Micrograph and MicroVideo classes to process images and videos respectively. These aim to make many basic functions incredibly simple, without the need for knowledge of more complex libraries which are performing the functions. Functions included are adding scalebar, enhancing contrast and equalising histogram, converting to 8bit images, binning, filtering with many common filters (Median, gaussian, low-pass, weiner and non-local means). Video frames can easily be averaged together in both simple averaging and running averging ways. 

The image data within these classes are kept in numpy arrays, which is the most common format for using images in other applications, which makes it easy to use the files for downstream processes like thresholding and particle analysis. 

On top of the simplified python functions, I have also implemented an app to automate the image analysis - this allows all the files in a directory to be processed (eg. filtered, contrast enhanced, add scalebar, save as jpg) to make looking at, presenting and downloaded images much faster and the filesizes much smaller. This is also combined with outputting the images onto a pdf document or an html file which then allows for viewing images and videos as a webpage. This type of automation is designed to make viewing the results of an experiment a rapid and straightforward process 

### Dependancies :

numpy (*pip install numpy*) - array handling 

opencv (*pip install opencv-python*) - image handling and filtering 

ncempy (*pip install ncempy*) - .dm3 parser 

matplotlib (*pip install matplotlib*) - Not needed unless you want to plot the images while running, will signficantly increase running time. (uncomment import and lines of code)

os (*pip install os_sys*) - handling operating system functions (create directory to save files in, list files in the directory etc) should be installed by default

pillow (pip install Pillow) - adding text, image handling

argsparse - adding arguments, should be installed by default

mrcfile - parsing mrc files 

copy - copying objects effectively 

moviepy - saving movie files 

airium - html file writing 

(skimage, imutils - not currently implemented here but for thresholding 


