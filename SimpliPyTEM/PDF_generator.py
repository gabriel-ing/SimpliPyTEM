
from fpdf import FPDF
import os
import itertools
import math



def pdf_generator(images, title, notes, directory='',max_num=9):
    '''
    Function for generating a pdf file showing images, this aims to make it easier to examine, evaluate and share images from a TEM session by putting them in a single document. 

    Parameters
    ----------

        images: list
            A list of images to place in the pdf document. This can be easily created with a generator function, eg. images = [x for x in os.listdir('PATH/TO/DIRECTORY') if x[-3:]=='jpg'] 
    
        title: str
            A title for the experiment

        notes: str
            Experimental notes, need to be kept fairly short (a few sentances max), these will be placed on the first page.

        directory: str
            If being run outside of the directory containing the images, the path to the directory needs to be included here, by default it assumes the same directory.

        max_num: int
            The maximum number of images to include on a single pdf page, this can be 1,4,6 or 9 (default). Smaller number means larger images (but longer document) 

    Output
    ------

        Saves a pdf document under the name {title}.pdf with the images contained within the list. 
    '''
    if ' ' in title: 
        filename = title.replace(' ', '_')+'.pdf'
    elif '_' in title:
        filename = str(title)+'.pdf'
        title = title.replace('_', ' ')
    elif title == '':
        filename = 'out.pdf'
    else: 
        filename = title+'.pdf' 

    pdf = FPDF(orientation='P',unit='pt', format='A4')
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(540, 10, title, align='C')
    pdf.set_font('Arial','', 10)
    pdf.set_xy(20, 50 )

    pdf.multi_cell(0, 12,notes)
    if directory:
        images = [directory+'/'+image for image in images]
    i = 0
    grouped_images = group_images(images)
    group_number = 0


    for prefix in grouped_images:
        i=0

        group = grouped_images[prefix]
        print(prefix)
        if group_number !=0:
            pdf.add_page()

        #pdf.set_xy(10, 100)
        #pdf.set_font('Arial', 'B', 14)
        #xsample_name = 'Sample name: {}'.format(' '.join(prefix.split('_')))
        #pdf.cell(540, 10, sample_name, align='C')
        pagenum =0

        group_size= len(group)

        
        # this if group decides how many images to put per page based on the number of images total.

        if group_size<2:
            num = 1
        elif group_size<5 or group_size==7 or group_size ==8:
            num =4 
        elif group_size<7 or group_size ==10 or group_size==11 or group_size==12:
            num=6
        else:
            num=9   

        
        if num==6:
            pdf.set_xy(10, 100)
        else:
            pdf.set_xy(10,120)          
        pdf.set_font('Arial', 'B', 14)
        sample_name = 'Sample name: {}'.format(' '.join(prefix.split('_')))
        pdf.cell(540, 10, sample_name, align='C')   
        #This line gets the coordinates using the  
        
        image_coords, cap_coords, size = return_coords(num)
        print(image_coords, cap_coords, size)

        for i in range(len(group)):
                    
            j =i-(pagenum*num)

            pdf.image(group[i],image_coords[j][0], image_coords[j][1], size )
                   

            im_id, im_preview = find_number(group[i])
            pdf.set_xy(cap_coords[j][0],cap_coords[j][1])
            pdf.cell(10,10,im_id )
            #pdf.cell
                #i+=1
                #print(j)
    
            #this deals with making a new page when all the images are on the previous page.

            if (i+1)%num==0 and num!=1 and i+1!=group_size:
                print('yes')
                pagenum+=1
                pdf.add_page()
                pdf.set_xy(10, 100)
                pdf.cell(540, 10, sample_name, align='C')

        group_number+=1
    pdf.output(filename,'F')

    print('PDF generated!')

def find_number(string):
    '''
    Function to find the idenfication number of the images so they can be  labelled in the pdf. 

    Parameters
    ----------
        string: str
            Filename which contains the image number

    Returns
    -------

        im_id:str
            The ID number of the image 

        prefix:str
            The prefix to the image id - normally contains details about the sample. 

    
    '''
    lstring = string.split('_')

    success = False
    for item in lstring:
        if len(item)==4 and item.isdigit:
                im_id = item
                ind = lstring.index(im_id)
                #print(ind)
                success=True
    if success==False:
        ind = -2
        im_id = lstring[ind]

    prefix = ' '.join(lstring[:ind])
    return im_id, prefix
#print(im_prefix)

def group_images(images):
    '''
    Sorts a number of images into a dictionary with images separated by the sample name, these can then be separated onto different pages. 

    Parameters
    ----------

        images:list
            List of images (by filename)

    Returns 
    -------

        organised_dict:dict
            Dictionary containing the sample names (image prefixes) as the keys and a list of images with  that name as the value.
    '''

    prefixes = []
    prefix_set=set()
    images.sort()
    tups = []
    for image in images:
        im_id, im_prefix = find_number(image)
        
        prefix_set.add(im_prefix)
        tup = image, im_id, im_prefix
        tups.append(tup)

    organised_dict= {}
    prefix_set = sorted(prefix_set)
    for prefix in prefix_set:

        #im_id, im_prefix = find_number(image)

        images_per_prefix =[x[0] for x in tups if x[2]==prefix]
        organised_dict[prefix]=images_per_prefix
  
    return organised_dict

def return_coords(max_num):
    '''
    Gives the coordinates for the images & captions, and the size of the images depending on the number per page.

    Parameters
    ----------
        max_num:int
            The number of images per page.

    Returns
    -------
        Image_coords:list
            The coordinates for each image on the page

        cap_coords:list
            The coordinates for each caption on the page

        size:int 
            The size of the images.
    '''
    if max_num==1:
        imx = [15]
        imy = [178]
        capx = [271]
        capy = [755]
        size = 570
    
    elif max_num==4:
        imx = [10, 300]
        imy = [149, 475]
       
        capx = [123,431]
        capy = [442,768]
        size = 280
        #capy = [422,754]
#        size = 284

    elif max_num==6:
        imx = [68,358]
        imy = [123,360, 598]
        capx = [13, 307]
        capy = [255, 463, 700]
        size = 227
    elif max_num==9:
        
        imx = [12, 205, 398]
        imy= [146, 361, 576]
        

        capx = [85,280, 473]
        capy = [335, 550, 764]
        size = 180
    else: 
        print('Input not valid, returning default')
                
        imx = [12, 205, 398]
        imy= [146, 361, 576]
        capx = [85,280, 473]
        capy = [335, 550, 764]
        size = 180
    cap_coords=list(itertools.product(capx, capy))
    image_coords = list(itertools.product(imx,imy))
    return image_coords, cap_coords, size 

if __name__=='__main__':
    images = [x for x in os.listdir('.') if x[-3:]=='jpg']      

    pdf_generator(images, 'New_attempt', 'Hello world')


