from SimpliPyTEM.Micrograph_class import *
from SimpliPyTEM.MicroVideo import *
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
    MajorMinorRatio = []

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
        MajMinRat = height/width
        MajorMinorRatio.append(MajMinRat)
        ((cx, cy), radius) = cv.minEnclosingCircle(c)
        radius_particle.append(radius*pixelSize)
        #circularity_particle.append(area/(np.pi*radius*radius))
        aspect_ratio_particle[i, 0] = width/height
        box = cv.boxPoints(min_rectangle)
        box=np.int0(box)

    particle_data = {'Max_length':max_length_particle, 'Area':area_particle, 'Centroid':centroid_particle, 
                     'Aspect_ratio':aspect_ratio_particle, 'Perimeter':perimeter_particle, 'Circularity':circularity_particle, 
                     'Width':width_particle, 'Height':height_particle, 'Radius':radius_particle, 'Major-Minor Ratio':MajorMinorRatio}    
    #print(particle_data)
    return particle_data

#particle_data=  Collect_particle_data(contours_im, 0.112)
#print(particle_data['Height'])
#print(np.mean(particle_data['Height']))


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
    

def save_videos_sidebyside(Video1, Video2):
    #Videos need to be the same shape. Add video as numpy stack (Z,Y,X ) 
    print(Video1.shape)
    z1,y1,x1 = Video1.shape
    z2, y2, x2=Video2.shape
    sidebyside = np.zeros((z, y, x*2),dtype='uint8')
    # this was put here to invert the masked video, DO this BEFORE calling function. 
    #masksinv=cv.bitwise_not(np.array(masks))
    sidebyside[:, :, :x] =Video1

    sidebyside[:, :, x:] =Video2[:,:,:]
    plt.imshow(sidebyside[0], cmap='magma')
    plt.show()
    return sidebyside