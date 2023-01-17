# SimpliPyTEM: an open source project to simplify python-based analysis of electron microscopy data with added focus on in situ videos 

<img src=docs/Media/Images/SimpliPyTEM_figures.001.png width=700px, alt='Figure showing effect of SimpliPyTEM-GUI'>

Please see full documentation at https://micrograph-analysis-scripts.readthedocs.io/en/latest/ 

SimpliPyTEM introduces the Micrograph and MicroVideo classes to process images and videos respectively. These aim to make many basic functions incredibly simple, without the need for knowledge of more complex libraries which are performing the functions. Functions included are adding scalebar, enhancing contrast and equalising histogram, converting to 8bit images, binning, filtering with many common filters (Median, gaussian, low-pass, weiner and non-local means). Video frames can easily be averaged together in both simple averaging and running averging ways. 

The image data within these classes are kept in numpy arrays, which is the most common format for using images in other applications, which makes it easy to use the files for downstream processes like thresholding and particle analysis. 

On top of the simplified python functions, I have also implemented an app to automate the image analysis - this allows all the files in a directory to be processed (eg. filtered, contrast enhanced, add scalebar, save as jpg) to make looking at, presenting and downloaded images much faster and the filesizes much smaller. This is also combined with outputting the images onto a pdf document or an html file which then allows for viewing images and videos as a webpage. This type of automation is designed to make viewing the results of an experiment a rapid and straightforward process 

