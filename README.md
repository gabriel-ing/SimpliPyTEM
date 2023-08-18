# SimpliPyTEM: an open source project to simplify Python-based analysis of electron microscopy data with added focus on in situ videos 

<img src=docs/Media/Images/SimpliPyTEM_figures.001.png width=700px, alt='Figure showing effect of SimpliPyTEM-GUI'>

Please see full documentation at https://simplipytem.readthedocs.io/en/latest/

## Installation

Install SimpliPyTEM using pip: 

  `pip install SimpliPyTEM`

This is best done using a clean environment to ensure there are no clashes with existing installs: 

```
conda create --name SimpliPyTEM python=3.8
conda activate SimpliPyTEM
pip install SimpliPyTEM
```

The **library** is then available in Python code using standard imports, eg: 

`from SimpliPyTEM.Micrograph_class import Micrograph`

The **GUI** can be opened from the terminal (assuming the correct conda environment is activated) with the command: 

`SimpliPyTEM-GUI`

### Installation from github

To install from github, first download the repository, either using the *Download Zip* option after clicking the green `<> Code` button, or use the command: 

`git clone https://github.com/gabriel-ing/SimpliPyTEM.git`

Then, in the command line enter the SimpliPyTEM folder (if the zip folder was downloaded, this needs to be unzipped first) and use the command:

`pip install .`

pip is used again here as it will ensure that all the dependencies are installed.


## Intro

SimpliPyTEM introduces the Micrograph and MicroVideo classes to process images and videos respectively. These aim to make many basic functions incredibly simple, without the need for knowledge of more complex libraries which are performing the functions. Functions included are adding a scalebar, enhancing contrast and equalising histogram, converting to 8bit images, binning, and filtering with many common filters (Median, gaussian, low-pass, weiner and non-local means). Video frames can easily be averaged together in both simple averaging and running averaging ways. 

The image data within these classes are kept in numpy arrays, which is the most common format for using images in other applications, which makes it easy to use the files for downstream processes like thresholding and particle analysis. 

On top of the simplified Python functions, I have also implemented an app to automate the image analysis - this allows all the files in a directory to be processed (eg. filtered, contrast-enhanced, add scalebar, save as jpg) to make looking at, presenting and downloaded images much faster and the filesizes much smaller. This is also combined with outputting the images onto a pdf document or an html file which then allows for viewing images and videos as a webpage. This type of automation is designed to make viewing the results of an experiment a rapid and straightforward process 

If there are any features that you would like to be added - for example compatibility with other filetypes, or if things aren't working as you expect them to, please feel free to open an issue and I will do my best to sort it for you! Please also be aware that I am a final year PhD student with my own research so I will help when I can find the time...

I would also like to welcome any additions from potential contributors, whether it is practical examples of code being used, bugs being fixedd or the introduction of new functionalities. Again, feel free to raise an issue or contact me directly if you would like help with these things .
