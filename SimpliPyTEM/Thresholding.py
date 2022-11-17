from Downloads.Micrograph_analysis_scripts_master.Micrograph_class import *
from Downloads.Micrograph_analysis_scripts_master.MicroVideo import *
from ipyfilechooser import FileChooser
from moviepy.editor import ImageSequenceClip
from skimage import measure
from imutils import contours
import imutils

'''
MAIN FUNCTIONS
'''

def Threshold(image, threshold):
    imG=cv.GaussianBlur(image, (5,5),0)
    #croppedThresh[croppedThresh<90] = 0
    #croppedThresh[croppedThresh>90]=255
    ret, cvThresh = cv.threshold(imG, threshold, 255, cv.THRESH_BINARY)
    cvThresh = cv.erode(cvThresh, None,iterations=1)
    cvThresh = cv.dilate(cvThresh, None,iterations=1)
    cvThresh = cvThresh.astype('uint8')
    #print(cvThresh.dtype)plt.imshow(mask)
    #print(des)
    #print(des)
    #plt.imshow(des)
    #contour, hier = cv.findContours(cvThresh, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)
    #for cont in contour:
     #   cv.drawContours(des,[cont], 0, 255,-1)
    #plt.imshow(cvThresh[0])
    thresh = cvThresh
    thresh=cv.bitwise_not(thresh)
    #new lines
    #kernal  = cv.getStructuringElement(cv.MORPH_ELLIPSE, (3,3))
    #res=cv.morphologyEx(thresh, cv.MORPH_OPEN,kernal)
   
    return thresh#,res


def Find_contours(thresh, min_size=200):
    cnts, hier = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    for cnt in cnts:
        cv.drawContours(thresh, [cnt], 0,255,-1)
    #plt.imshow(thresh)
    #plt.show()
    labels =measure.label(thresh, neighbors=8, background=0)
    mask = np.zeros(thresh.shape, dtype='uint8')
    
    

    for label in np.unique(labels):
        if label==0:
            continue
        label_mask = np.zeros(thresh.shape, dtype='uint8')
        label_mask[labels==label]=255
        #particle_data['Radius']=255
        num_pixels = cv.countNonZero(label_mask)
        if num_pixels>min_size:
            mask = cv.add(mask, label_mask)
    
    contours_im = cv.findContours(mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    #for cnt in contours_im:
    #print(contours_im)
    contours_im = imutils.grab_contours(contours_im)
    contours_im = contours.sort_contours(contours_im)[0]
    #print(contours_im)
    #plt.imshow(labels)
    #for labell in np.unique(labels)
    return contours_im, mask



    
def Collect_particle_data(contours_im, pixelSize):    
    num_particle= len(contours_im)
    #print(num_particle)


    # this parameter computes the maximum length of a particle i.e. maximum distance between two point of a contour
    max_length_particle = np.zeros([num_particle, 1], dtype=float)
    # this parameter computes the areas of  particles
    #area_particle = np.zeros([num_particle, 1], dtype=float)
    area_particle=[]
    # this parameter computes the center of the mass of  particles
    centroid_particle = np.zeros([num_particle, 2], dtype=float)
    # this parameter computes the ratio between maximum and minimum length of a particle
    aspect_ratio_particle = np.zeros([num_particle, 1], dtype=float)
    # this parameter computes the perimeter of particles
    perimeter_particle = np.zeros([num_particle, 1], dtype=float)
    # this parameter computes the perimeter of particles
    #circularity_particle = np.zeros([num_particle, 1], dtype=float)
    circularity_particle=[]
    #width_particle =np.zeros([num_particle, 1], dtype = float)
    #height_particle = np.zeros([num_particle, 1], dtype = float)
    width_particle = []
    height_particle = []
    radius_particle= []
    #meanradius_particle=np.zeros([num_particle, 1],dtype = float)

    for (i, c) in enumerate(contours_im):
        #print(i,c)
        moment_contour = cv.moments(c)
        centroid_particle[i, 0] = moment_contour['m10']/moment_contour['m00']
        centroid_particle[i, 1] = moment_contour['m01']/moment_contour['m00']

        area = cv.contourArea(c)*pixelSize**2
        area_particle.append(area)
        #meanradius_particle = area__particle[i, 0]


        perimeter_particle[i, 0] = cv.arcLength(c, True)*pixelSize
        min_rectangle = cv.minAreaRect(c)
        #print(min_rectangle)
        #circularity_particle = 
        width_height = min_rectangle[1]
        #print(width, height)
        #width_particle[i, 0]= width*pixelSize
        #height_particle[i, 0] = height*pixelSize
        height = max(width_height)
        width = min(width_height)
        width_particle.append(width*pixelSize)
        height_particle.append(height*pixelSize)
        ((cx, cy), radius) = cv.minEnclosingCircle(c)
        radius_particle.append(radius*pixelSize)
        #circularity_particle.append(area/(np.pi*radius*radius))
        aspect_ratio_particle[i, 0] = width/height
        box = cv.boxPoints(min_rectangle)
        box=np.int0(box)

    particle_data = {'Max_length':max_length_particle, 'Area':area_particle, 'Centroid':centroid_particle, 
                     'Aspect_ratio':aspect_ratio_particle, 'Perimeter':perimeter_particle, 'Circularity':circularity_particle, 
                     'Width':width_particle, 'Height':height_particle, 'Radius':radius_particle}    
    #print(particle_data)
    return particle_data

#particle_data=  Collect_particle_data(contours_im, 0.112)
#print(particle_data['Height'])
#print(np.mean(particle_data['Height']))

'''-------------------------------------------
EXTRACT DATA FROM VIDEO 

'''

widths = []
heights = []
masks = []
circularity=[]
radius=[]
vid.convert_to_8bit()
for frame in vid.frames:
    thresh= Threshold(frame, 90)
    contours_im, mask= Find_contours(thresh)
    particle_data=Collect_particle_data(contours_im, 0.112)
    widths.append(particle_data['Width'])
    heights.append(particle_data['Height'])
    masks.append(mask)
    circularity.append(particle_data['Circularity'])
    radius.append(particle_data['Radius'])
                       
        

'''
----------------------------------------------------
PLOT RADIUS DATA
'''
#print(np.array(widths))
#widths_list = [x for i in widths for x in i]
def flatten_list(l):
    return [x for i in l for x in i]
    
def plot_histogram(data):
    plt.style.use('seaborn-whitegrid')
    plt.hist(data, color =(0.9,0.9,1), edgecolor='black', bins=50)
    
    plt.xlabel('Particle size (nm)')
    plt.ylabel('Frequency')
    plt.show()
    
print(particle_data['Radius'])    
height_data= flatten_list(heights)
width_data= flatten_list(widths)
#circularity_data = flatten_list(circularity)
radius_data = flatten_list(radius)
colors = [(0.9,0.9,1), (1,0.9,0.9), (0.9,1,0.9)]

fig, ax = plt.subplots(1,3,figsize=(40,10))
print(ax)
ax[0].hist(height_data, color =colors[0], edgecolor='black', bins=50)
ax[0].set_xlabel('Major axis size (nm)', fontsize=20)
ax[0].set_xticks(list(range(0,int(max(height_data)+2),2)))
ax[0].set_xticklabels(list(range(0,int(max(height_data)+2),2)),fontsize=15)
ax[0].set_title('Major axis size',fontsize=25)
ax[1].set_ylabel('Frequency')

ax[1].hist(width_data, color = colors[1], edgecolor='black', bins=50)
ax[1].set_xlabel('Minor axis size (nm)', fontsize=20)
ax[1].set_xticks(list(range(0,int(max(height_data)+2),2)))
ax[1].set_xticklabels(list(range(0,int(max(height_data)+2),2)),fontsize=15)
ax[1].set_ylabel('Frequency')
ax[1].set_title('Minor axis size',fontsize=25)

ax[2].hist(radius_data, color = colors[2], edgecolor='black', bins=50)
ax[2].set_xlabel('Bounding circle radius', fontsize=20)
ax[2].set_xticks(list(range(0,int(max(height_data)+2),2)))
ax[2].set_xticklabels(list(range(0,int(max(height_data)+2),2)),fontsize=15)
ax[2].set_title('Bounding circle radius',fontsize=25)
ax[1].set_ylabel('Frequency')
#ax[1,1].hist(circularity_data, color = (0.9,0.9,1), edgecolor='black', bins=50)
#ax[1,1].set_xlabel('Circularity', fontsize=20)

#ax[1].set_xticks(list(range(0,int(max(height_data)+2),2)))
#ax[1].set_xticklabels(list(range(0,int(max(height_data)+2),2)),fontsize=15)

plt.savefig('Top_fibrils_80thresh.jpg'))




'''
----------------------------------------------
SAVE VIDEOS SIDE BY SIDE
this is the bit to save the video side by side

'''
print(vid.frames.shape)
z,y,x = vid.frames.shape

sidebyside = np.zeros((z, y, x*2),dtype='uint8')
masksinv=cv.bitwise_not(np.array(masks))
#print(sidebyside.shape)
vid.convert_to_8bit()
vid.make_scalebar()
sidebyside[:, :, :x] =vid.frames

sidebyside[:, :, x:] =masksinv[:,:,:]
#print(vid)

#sidebyside = np.hstack((vid.frames,masksinv))
plt.imshow(sidebyside[0], cmap='magma')
print(sidebyside.shape)

video = []
for frame in sidebyside:
        
        frame = cv.cvtColor(frame, cv.COLOR_GRAY2BGR)
        video.append(frame)
video = np.array(video)

clip = ImageSequenceClip(list(video), fps=5)
clip.write_videofile('Top_crop_Horsidebyside80thresh_inv_.mp4')



'''
--------------------------------------------
Frame by frame analysis (widths and radius)
'''

num_particles= [len(x) for x in widths]
mean_radius = [np.mean(x) for x in radius]

fig, ax=plt.subplots(1,2, figsize=(20,10))
xticks = list(range(0,90,10))


ax[0].plot(range(len(num_particles)),num_particles )
ax[0].set_xlim(0,80)
ax[0].set_title('Number of particles by frame', fontsize=25)
ax[0].set_ylabel('Number of particles', fontsize=20)
ax[0].set_xlabel('Frame number', fontsize=20)
ax[0].set_xticks(xticks)
ax[0].set_xticklabels(xticks, fontsize=15)
#plt.show()

#print(mean_radius)
ax[1].plot(range(len(mean_radius)), mean_radius)
ax[1].set_xlim(0,80)
ax[1].set_title('Mean radius by frame', fontsize=25)
ax[1].set_ylabel('Mean particle radius', fontsize=20)
ax[1].set_xlabel('Frame number', fontsize=20)
ax[1].set_xticks(xticks)
ax[1].set_xticklabels(xticks, fontsize=15)
plt.savefig('Top_fibrils_number_of_particles_and_radius.png')