from SimpliPyTEM.Micrograph_class import * 
from SimpliPyTEM.MicroVideo_class import * 
import os

def process_folder(folder, output_folder_name,xybin, medfilter, gaussian_filter, video_status):
    print('Processing folder!')
    cwd = os.getcwd()

    os.chdir(folder)

    dm_files = [x for x in os.listdir('.') if x[-4:-1]=='.dm']
    dm_vids = [x for x in dm_files if isvideo(x)]
    dm_frames = [x for x in dm_files if x[-9]=='-' and x[-13:-9].isdigit() and x[-8:-4].isdigit()]
    dm_ims = [x for x in dm_files if x not in dm_vids and x not in dm_frames]   

    if output_folder_name not in os.listdir('.') and output_folder_name!='.':
        os.mkdir(output_folder_name)

    for file in dm_vids:
        print('Processing: ', file)
        video_processing(file,output_folder_name,xybin, medfilter, gaussian_filter, video_status)

    for  file in dm_ims:
        default_image_pipeline(file, xybin = xybin, medfilter=medfilter, gaussfilter=gaussian_filter,outdir=output_folder_name+'/Images')
    if len(dm_frames)!=0: 
        print(dm_frames)
        frames_processing(dm_frames,output_folder_name+'/Images',xybin, medfilter, gaussian_filter, video_status )



    print('All files in folder complete!')  
    os.chdir(cwd)


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

def video_processing(filename, output_folder_name,xybin, medfilter, gaussian_filter, video_status):
    if video_status=='Save Average':

        default_image_pipeline(filename, xybin = xybin, medfilter=medfilter, gaussfilter=gaussian_filter,outdir=output_folder_name+'/Images')
    else:
        default_video_pipeline(filename,output_type=video_status, xybin = xybin, medfilter=medfilter, gaussfilter=gaussian_filter,outdir=output_folder_name) #output folder = output_folder+videos
     



def isvideo(file):
    if os.path.getsize(file)>230165776:
        print('Large_file, probably video')
        return True
    else:
        return False

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
            

