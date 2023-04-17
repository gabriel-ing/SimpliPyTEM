from SimpliPyTEM.Micrograph_class import * 
from SimpliPyTEM.MicroVideo_class import * 
import os
import re
'''
def process_folder(folder, output_folder_name,xybin, medfilter, gaussian_filter, video_status):
    print('Processing folder!')
    print('Here')
    cwd = os.getcwd()

    os.chdir(folder)

    dm_files = [x for x in os.listdir('.') if x[-4:-1]=='.dm']
    dm_vids = [x for x in dm_files if isvideo(x)]
    dm_frames = [x for x in dm_files if x[-9]=='-' and x[-13:-9].isdigit() and x[-8:-4].isdigit()]
    dm_ims = [x for x in dm_files if x not in dm_vids and x not in dm_frames]   

    if output_folder_name not in os.listdir('.') and output_folder_name!='.':
        os.mkdir(output_folder_name)

    print('OUTPUTFOLDERNAME===='+output_folder_name)
    for file in dm_vids:
        print('Processing: ', file)
        video_processing(file,output_folder_name,xybin, medfilter, gaussian_filter, video_status)

    for  file in dm_ims:
        default_image_pipeline(file, xybin = xybin, medfilter=medfilter, gaussfilter=gaussian_filter,outdir=output_folder_name)
    if len(dm_frames)!=0: 
        print(dm_frames)
        frames_processing(dm_frames,output_folder_name,xybin, medfilter, gaussian_filter, video_status )



    print('All files in folder complete!')  
    os.chdir(cwd)
'''
'''
def process_folder_original(folder, output_folder_name,xybin, medfilter, gaussian_filter, video_status):

    ##deal with videostatus
    print('Processing folder!')
    cwd = os.getcwd()
    os.chdir(folder)

    dm_files = [x for x in os.listdir('.') if x[-4:-1]=='.dm']
    dm_vids = [x for x in dm_files if os.path.getsize(x)>230165776 and x[-3:]=='dm4']
    dm_frames = [x for x in dm_files if x[-9]=='-' and x[-13:-9].isdigit() and x[-8:-4].isdigit()]
    dm_ims = [x for x in dm_files if x not in dm_vids and x not in dm_frames]   

    micrograph = Micrograph()
    #micrograph.set_foldername(self.output_folder_name)

    for file in dm_vids:
        print('Runnning file: {}....'.format(file))
        #if self.motioncor=='On':
            #These are here for debugging purposes, if you want to find the error uncomment:  
        #   micrograph.motioncorrect_video(file)
        #   default_pipeline_class(micrograph, outdir=output_folder_name)
            #try:

                #   micrograph.motioncorrect_video(file)
                #   default_pipeline(micrograph, xybin = self.bin, texton=self.texton, color=self.color, medfilter=self.median)
                #except:
                #   print('There is an error with {}'.format(file) )
                #   print('Skipping file and continuing. If this is a common occurance debug or contact Gabriel')

        #else: 
            
        micrograph.open_dm(file)
        default_pipeline_class(micrograph, outdir=output_folder_name)
    for file in dm_ims:
        print('Runnning file: {}....'.format(file))
            #micrograph.motioncorrect_video(file)
        micrograph.open_dm(file)
        default_pipeline_class(micrograph, outdir=output_folder_name)
            #try:
            #   micrograph.open_dm(file)
            #   default_pipeline(micrograph, xybin = self.bin, texton=self.texton, color=self.color,medfilter=self.median)
            #except:
            #       print('There is an error with {}'.format(file) )
            #       print('Skipping file and continuing. If this is a common occurance debug or contact Gabriel')

            
    if dm_frames:
        dm_frames = group_frames(dm_frames)
        for vid in dm_frames:
            #if self.motioncor=='Off':
                     
                print(dm_frames[vid])
                frames = dm_frames[vid]
                micrograph.open_dm(frames[0])
                micrograph.add_frames(frames[1:])
                default_pipeline_class(micrograph, xybin = xybin, medfilter=medfilter, gaussfilter=gaussian_filter,outdir=output_folder_name)
            #else:
            #   print('Motion correcting frames!')
            #   micrograph.motioncor_frames(dm_frames)
            #   default_image_pipeline(micrograph, xybin = self.bin, texton=self.texton, color=self.color,medfilter=self.median, outdir=self.output_folder_name)
    print('All files in folder complete!')  
    os.chdir(cwd)

'''
'''
def process_file(filename, output_folder_name,xybin, medfilter, gaussian_filter, video_status):

    if isvideo(file):
        if video_status=='Save Average':
            default_image_pipeline(filename, xybin = xybin, medfilter=medfilter, gaussfilter=gaussian_filter,outdir=output_folder_name)
        else:
            print('This isnt coded in yet!')

    else:
        default_image_pipeline(filename,output_type=video_status, xybin = xybin, medfilter=medfilter, gaussfilter=gaussian_filter,outdir=output_folder_name)

def live_process(filename, output_folder_name,xybin, medfilter, gaussian_filter, video_status):
    cwd = os.getcwd()
    os.chdir(self.folder)
    files = os.listdir('.')
    file_set = set(files)
    start_time = time.time()
    max_running_time = 3600
    Micrograph()
    micrograph.set_foldername(self.output_folder_name)
    while True:
        for file in os.listdir('.'):
            if file not in file_set:
                currentsize = os.path.getsize(file)
                time.sleep(1)
                if os.path.getsize(file)==currentsize:
                    break
                if file[-4:-1]=='.dm':

                    if os.path.getsize(file)>230165776 and file[-3:]=='dm4' and self.motioncor=='On':
                            
                        micrograph.motioncorrect_video(file)
                        default_pipeline_class(micrograph, xybin = self.bin, texton=self.texton, color=self.color,medfilter=self.median)

                    elif x[-9]=='-' and file[-13:-9].isdigit() and file[-8:-4].isdigit():
                            
                            pass
                            #wait = 1
                            #time.sleep(60)
                            #if self.motioncor=='Off':
                            #   dm_frames = [x for x in dm_files if x[-9]=='-' and x[-13:-9].isdigit() and x[-8:-4].isdigit()]

                    else:
                        micrograph.open_dm(file)
                        default_pipeline_class(micrograph, xybin = self.bin, texton=self.texton, color=self.color,medfilter=self.median)

                    print(file)
                    file_set.add(file)
            
            running_time = time.time() - start_time
            print(running_time)
            if running_time>max_running_time:
                break
            time.sleep(30)      

    os.chdir(cwd)

'''
def video_processing(filename, output_folder_name,xybin, medfilter, gaussian_filter,scalebar_on, video_status, topaz_denoise, denoise_with_cuda):
    if video_status=='Save Average':

        default_image_pipeline(filename, xybin = xybin, medfilter=medfilter, gaussfilter=gaussian_filter,scalebar=scalebar_on, outdir=output_folder_name, topaz_denoise=topaz_denoise, denoise_with_cuda=denoise_with_cuda)
    else:
        default_video_pipeline(filename,output_type=video_status, xybin = xybin, medfilter=medfilter, gaussfilter=gaussian_filter,outdir=output_folder_name, scalebar=scalebar_on,topaz_denoise=topaz_denoise, denoise_with_cuda=denoise_with_cuda) #output folder = output_folder+videos
     



def isvideo(dmfile):
    try:
        f = nci.dm.fileDM(dmfile)
        if f.zSize[1]>1:
            return True
        else:
            return False
    except OSError as e:
        print(e)

def frames_processing(dm_frames,output_folder_name,xybin, medfilter, gaussian_filter, video_status):
    dm_frames = group_frames(dm_frames)
    for vid in dm_frames:
            #if self.motioncor=='Off':
            print(dm_frames[vid])
            frames = dm_frames[vid]
            micrograph = Micrograph()
            micrograph.open_dm(frames[0])
            micrograph.add_frames(frames[1:])
            default_pipeline_class(micrograph, xybin = xybin, medfilter=medfilter, gaussfilter=gaussian_filter,outdir=output_folder_name)
            

def get_files_from_pattern(pattern):
    '''
    Imports all the files in the current directory that fits the defined pattern and returns them into lists of images, videos and digital micrograph frames
    The pattern allows for use of * for anything and ? for any single charactor, so for all tif files in the directory, one can use `*.tif` or give files with the same prefix but different number: filenumber00??.tif
    
    '''

    dirfiles = os.listdir('.')
    files = []
    if '*' in pattern:
        pattern = pattern.replace('*', '.+')
        pattern = pattern.replace('?', '.')
        for file in dirfiles:
            if re.search(pattern, file):
                #print(file)
                files.append(file)
    im_files = []
    video_files = []
    frames = []
    #print(files)
    for file in files: 
        if file[-4:-1]=='.dm':
            if isvideo(file):
                video_files.append(file)
            elif file[-9]=='-' and file[-13:-9].isdigit() and file[-8:-4].isdigit():
                frames.append(file)
            else:
                im_files.append(file)
        elif file[-4:]=='.avi' or file[-4:]=='mp4':
            video_files.append(file)
        elif file[-4:].lower() in ['.tif', '.jpg', '.png', 'tiff']:
            im_files.append(file)
        else:
            print('{} file not included as not a known image/video format, if this is unexpected please raise an issue on github'.format(file))

    return im_files, video_files, frames



'''
            if '/' in outdir:
                if outdir.split('/')[-1] not in os.listdir('/'.join(outdir.split('/')[:-1])):
                    os.mkdir(outdir)
            elif outdir not in os.listdir('.') and outdir!='.' and outdir!='.':
                print(outdir)
                #print(os.listdir('.'))
                os.mkdir(outdir)

            if len(name.split('/'))>1:
                name=name.split('/')[:-1]+outdir+'/'+name
            else:
                name =outdir+'/'+name  
'''