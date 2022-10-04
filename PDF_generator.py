from fpdf import FPDF
import os
import itertools
import math

def find_number(string):
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
    for prefix in prefix_set:

        im_id, im_prefix = find_number(image)
        images_per_prefix =[x[0] for x in tups if x[2]==prefix]
        organised_dict[prefix]=images_per_prefix
  
    return organised_dict

def return_coords(max_num):
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
        capy = [422,754]
        size = 284
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

def pdf_generator(images, title, notes, max_num=9):
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
	pdf.set_font('Arial','', 12)
	pdf.set_xy(20, 60 )
	pdf.multi_cell(0, 12,notes)


	i = 0
	grouped_images = group_images(images)
	group_number = 0


	for prefix in grouped_images:
		i=0
		group = grouped_images[prefix]
		print(prefix)
		if group_number !=0:
			pdf.add_page()
		pdf.set_xy(10, 100)
		pdf.set_font('Arial', 'B', 14)
		sample_name = 'Sample name: {}'.format(' '.join(prefix.split('_')))
		pdf.cell(540, 10, sample_name, align='C')
	    


		pagenum =0

		group_size= len(group)
		if group_size<2:
			num = 1
		elif group_size<5 or group_size==7 or group_size ==8:
			num =4 
		elif group_size<7 or group_size ==10 or group_size==11 or group_size==12:
			num=6
		else:
			num=9   
		image_coords, cap_coords, size = return_coords(num)
		for i in range(len(group)):

	                
			j =i-(pagenum*9)
			#print(i, j, pagenum)
	            #pdf.set_xy(coordinates[i])
	            #print(image)
			#print('i', i)
			#print('j',j)

			#print('len:',len(group))

			pdf.image(group[i],image_coords[j][0], image_coords[j][1], size )
	               

			im_id, im_preview = find_number(group[i])
			pdf.set_xy(cap_coords[j][0],cap_coords[j][1])
			pdf.cell(10,10,im_id )
			#pdf.cell
	            #i+=1
	            #print(j)
			if (i+1)%num==0 and num!=1 and i+1!=group_size:
				print('yes')
				pagenum+=1
				pdf.add_page()
				pdf.set_xy(10, 100)
				pdf.cell(540, 10, sample_name, align='C')

		group_number+=1
	pdf.output(filename,'F')
images = [x for x in os.listdir('.') if x[-3:]=='jpg']	    
pdf_generator(images, 'New_attempt', 'Hello world')


