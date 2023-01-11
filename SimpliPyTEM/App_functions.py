from SimpliPyTEM.Micrograph_class import * 
from SimpliPyTEM.MicroVideo_class import * 
import os


def process_folder(folder, output_folder_name,xybin, medfilter, gaussian_filter, video_status):

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
		#	micrograph.motioncorrect_video(file)
		#	default_pipeline_class(micrograph, outdir=output_folder_name)
			#try:

				#	micrograph.motioncorrect_video(file)
				#	default_pipeline(micrograph, xybin = self.bin, texton=self.texton, color=self.color, medfilter=self.median)
				#except:
				#	print('There is an error with {}'.format(file) )
				#	print('Skipping file and continuing. If this is a common occurance debug or contact Gabriel')

		#else: 
			
		micrograph.open_dm(file)
		default_pipeline_class(micrograph, outdir=output_folder_name)
	for file in dm_ims:
		print('Runnning file: {}....'.format(file))
			#micrograph.motioncorrect_video(file)
		micrograph.open_dm(file)
		default_pipeline_class(micrograph, outdir=output_folder_name)
			#try:
			#	micrograph.open_dm(file)
			#	default_pipeline(micrograph, xybin = self.bin, texton=self.texton, color=self.color,medfilter=self.median)
			#except:
			#		print('There is an error with {}'.format(file) )
			#		print('Skipping file and continuing. If this is a common occurance debug or contact Gabriel')

			
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
			#	print('Motion correcting frames!')
			#	micrograph.motioncor_frames(dm_frames)
			#	default_image_pipeline(micrograph, xybin = self.bin, texton=self.texton, color=self.color,medfilter=self.median, outdir=self.output_folder_name)
	print('All files in folder complete!')	
	os.chdir(cwd)


def process_file(filename, output_folder_name,xybin, medfilter, gaussian_filter, video_status):
	if os.path.getsize(x)>230165776:
		video = True
	else:
		video =False

	if video:
		if video_status=='Save Average':

		    default_image_pipeline(micrograph, xybin = xybin, medfilter=medfilter, gaussfilter=gaussian_filter,outdir=output_folder_name)

		else:
			print('This isnt coded in yet!')

	else:
		default_image_pipeline(filename, xybin = xybin, medfilter=medfilter, gaussfilter=gaussian_filter,outdir=output_folder_name)

	dm_files = [x for x in os.listdir('.') if x[-4:-1]=='.dm']
	dm_vids = [x for x in dm_files if os.path.getsize(x)>230165776 and x[-3:]=='dm4']
	dm_frames = [x for x in dm_files if x[-9]=='-' and x[-13:-9].isdigit() and x[-8:-4].isdigit()]
	dm_ims = [x for x in dm_files if x not in dm_vids and x not in dm_frames]	


