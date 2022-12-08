import tkinter as tk
from tkinter import ttk, filedialog
#from tkinter import 

import os
from Micrograph_class import *
from PDF_generator import pdf_generator 
from html_writer import * 
class MainApplication(tk.Tk):
	def __init__(self):
		super().__init__()
		#self.parent = parent
		#self.label
		self.geometry('600x700')
		self.title('Micrograph Previews App')
		ttk.Label(self,text='\nProgram for generating small filesize previews of micrographs', wraplength=550).pack()
		ttk.Label(self,text='Choose whether to process a file, a folder, or live during an imaging session', wraplength=550).pack()
		#self.label = ttk.Label(sel, text ='Hello').pack()
		#self.geometry('400x300')

		self.live='Folder'
		self.liveButton = ttk.Button(self, text='Process Folder', command=self.liveCommand,)
		self.liveButton.pack()

		ttk.Label(self, text='\nChoose folder or file:').pack()
		
		self.folder = 'Images'
		self.browsebutton=ttk.Button(self, text='Browse', command=self.BrowseCommand)
		self.browsebutton.pack()

		self.folderLabel = ttk.Label(self, text=self.folder)
		self.folderLabel.pack()

		ttk.Label(self, text='Choose output image options:\n').pack()
		#Add the options of binning the image 0, 2, 4 or 6 times
		self.bin = 2
		self.binbutton = ttk.Button(self, text='Bin: 2', command=self.BinCommand)
		self.binbutton.pack()
		self.resizable(True,True)
		#message = tk.Label(root, text="Live processing").pack()
		

		#Add the option to choose colour
		self.color='Auto'
		self.colorbutton = ttk.Button(self, text='Scalebar colour: Auto', command=self.ColorCommand)
		self.colorbutton.pack()

		#choose to remove scalebar text
		self.texton = True
		self.textbutton = ttk.Button(self, text='Scalebar text: On', command=self.TextoffCommand)
		self.textbutton.pack()

		#choose median filter
		self.median = 3
		ttk.Label(self,text='\nMEDIAN FILTER? 0 for no, otherwise enter an odd integer for filter kernal size (strength). default is 3 (leave blank for default)', wraplength=555).pack()
		self.median_box = tk.Text(self, height =1, width =4)
		self.median_box.pack()

		self.motioncor = 'Off'
		self.motioncorbutton = ttk.Button(self, text='Motion Correct videos: Off', command=self.MotioncorCommand)
		self.motioncorbutton.pack()
		
		#self.quality = tk.DoubleVar()
		#self.qualitySlider=ttk.Scale(self, variable=self.quality,from_=10, to=100, orient=tk.HORIZONTAL, command=self.getQuality)
		#self.qualitySlider.pack()

		self.output_folder_name = './'
		ttk.Label(self, text='\n\nChoose output folder name (default is same folder)').pack()
		self.outfolder_box = tk.Text(self, height=1)
		self.outfolder_box.pack()

		self.runButton = ttk.Button(self, text='RUN!', command=self.runCommand)
		self.runButton.pack()

		ttk.Label(self, text='\n\nThis section allows writing all micrographs into a formatted PDF document.').pack()
		ttk.Label(self, text='\n\nExperiment title:').pack()
		self.title_box = tk.Text(self, height=1)
		self.title_box.pack()
		ttk.Label(self, text='\nAdd notes here:').pack()
		self.notes_box = tk.Text(self, height=5)
		self.notes_box.pack()
		self.pdf_on_button = ttk.Button(self, text='Generate PDF', command=self.pdf_command)
		self.pdf_on_button.pack()

		self.html_button = ttk.Button(self, text='Generate HTML', command= self.html_command)
		self.html_button.pack()
		
		
		self.med = True
		self.gauss = False
		self.medkernal=3
		self.gauss_kernal = 0
		
		self.quality=90
		







	def cycle_options(self, options, current): #cycle through the options
		#print(options)

		ind = options.index(current)
		if ind==len(options)-1:
			ind = 0
		else:
			ind +=1	
		return options[ind]




	'''----------------------------------------------------------------------------------
	SECTION: BUTTON COMMANDS 
	'''
	def BrowseCommand(self):
		if self.live=='File':
			self.folder = filedialog.askopenfilename()
		else:	
			self.folder = filedialog.askdirectory()
		self.folderLabel.config(text=self.folder)  

	def liveCommand(self):
		self.live = self.cycle_options(['File', 'Folder', 'Folder Live'], self.live)
		self.liveButton.config(text='Process {}'.format(self.live))

	def BinCommand(self):
		self.bin = self.cycle_options([0, 2,4,6], self.bin)
		self.binbutton.config(text='Bin: {}'.format(self.bin))

	def ColorCommand(self):
		#colors=['Auto', 'Black', 'White']

		self.color=self.cycle_options(['Auto', 'Black', 'White'], self.color)
		self.colorbutton.config(text='Scalebar colour: {}'.format(self.color))
	
	def TextoffCommand(self):
		self.texton = self.cycle_options([True, False], self.texton)
		self.textbutton.config(text='Scalebar text: {}'.format(self.texton))

	def MotioncorCommand(self):
		self.motioncor = self.cycle_options(['On', 'Off'], self.motioncor)
		self.motioncorbutton.config(text='Motion Correct videos: {}'.format(self.motioncor))

	def runCommand(self):
		print(self.live)
		self.Retrive_folder()
		if self.live=='File':
			self.process_file()
		elif self.live=='Folder':
			self.process_folder()
		else:
			self.live_process()

	def pdf_command(self):
		self.Retrive_folder()
		if self.folder !=os.getcwd():
			os.chdir(self.folder)
			print(os.getcwd())

		os.chdir(self.output_folder_name)
		print(os.getcwd())
		images = [x for x in os.listdir('.') if x[-4:]=='.jpg']
		print(images)
		self.Retrive_title()
		self.Retrive_notes()
		pdf_generator(images, title=self.title, notes=self.notes)
		print('Done!')
		os.chdir(self.folder)


	def html_command(self):
		images = [x for x in os.listdir('.') if x[-4:]=='.jpg']
		self.Retrive_title()
		write_html(images, videos=[], title=self.title)
		write_css()
	'''-------------------------------------------------------------------------------------
	SECTION: RETREVERS
	'''

	def Retrive_folder(self):
		self.output_folder_name = self.outfolder_box.get('1.0', tk.END)
		self.output_folder_name=self.output_folder_name.strip('\n')
		if self.output_folder_name == '':
			self.output_folder_name='Images'
		print(self.output_folder_name)

	def Retrive_title(self):
		self.title = self.title_box.get('1.0', tk.END)
		self.title=self.title.strip('\n')
		print(self.title)

	def Retrive_notes(self):
		self.notes = self.notes_box.get('1.0', tk.END)
		self.notes=self.notes.strip('\n')
		print(self.notes)

	#NOT CURRENTLY FUNCTIONING BUT NOR IS THE SAVE QUALITY FUNCTION - DELETE
	def getQuality(self):
		print(self.qualitySlider.get())


	def Retrive_median(self):
		self.median = self.median_box.get('1.0', tk.END)
		self.median=self.median.strip('\n')
		try:
			self.median=int(self.median)
		except:
			self.median=3


	'''-----------------------------------------------------------------------------------------
	SECTION: RUNNING 

	'''
	def process_folder(self):
		os.chdir(self.folder)

		dm_files = [x for x in os.listdir('.') if x[-4:-1]=='.dm']
		dm_vids = [x for x in dm_files if os.path.getsize(x)>230165776 and x[-3:]=='dm4']
		dm_frames = [x for x in dm_files if x[-9]=='-' and x[-13:-9].isdigit() and x[-8:-4].isdigit()]
		dm_ims = [x for x in dm_files if x not in dm_vids and x not in dm_frames]	

		micrograph = Micrograph()
		#micrograph.set_foldername(self.output_folder_name)

		for file in dm_vids:
			print('Runnning file: {}....'.format(file))
			if self.motioncor=='On':
				#These are here for debugging purposes, if you want to find the error uncomment:  
				micrograph.motioncorrect_video(file)
				default_pipeline_class(micrograph, outdir=self.output_folder_name)
				#try:

				#	micrograph.motioncorrect_video(file)
				#	default_pipeline(micrograph, xybin = self.bin, texton=self.texton, color=self.color, medfilter=self.median)
				#except:
				#	print('There is an error with {}'.format(file) )
				#	print('Skipping file and continuing. If this is a common occurance debug or contact Gabriel')

			else: 
				micrograph.open_dm(file)
				default_pipeline_class(micrograph, outdir=self.output_folder_name)
		for file in dm_ims:
			print('Runnning file: {}....'.format(file))
			#micrograph.motioncorrect_video(file)
			micrograph.open_dm(file)
			default_pipeline_class(micrograph, outdir=self.output_folder_name)
			#try:
			#	micrograph.open_dm(file)
			#	default_pipeline(micrograph, xybin = self.bin, texton=self.texton, color=self.color,medfilter=self.median)
			#except:
			#		print('There is an error with {}'.format(file) )
			#		print('Skipping file and continuing. If this is a common occurance debug or contact Gabriel')

			
		if dm_frames:
			dm_frames = group_frames(dm_frames)
			for vid in dm_frames:
				if self.motioncor=='Off':
					 
					    print(dm_frames[vid])
					    frames = dm_frames[vid]
					    micrograph.open_dm(frames[0])
					    micrograph.add_frames(frames[1:])
					    default_pipeline_class(micrograph, xybin = self.bin, texton=self.texton, color=self.color,medfilter=self.median, outdir=self.output_folder_name)
				else:
					print('Motion correcting frames!')
					micrograph.motioncor_frames(dm_frames)
					default_image_pipeline(micrograph, xybin = self.bin, texton=self.texton, color=self.color,medfilter=self.median, outdir=self.output_folder_name)
		print('All files in folder complete!')	


	def process_file(self):
		file=self.folder
		print(file)
		micrograph = Micrograph()
		#micrograph.set_foldername(self.output_folder_name)
		if file[-4:-1]=='.dm':
			micrograph.open_dm(file)
			default_pipeline_class(micrograph, outdir=self.output_folder_name)

		

	def live_process(self):
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
							#	dm_frames = [x for x in dm_files if x[-9]=='-' and x[-13:-9].isdigit() and x[-8:-4].isdigit()]

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


if __name__=="__main__":
	root = MainApplication()
	#MainApplication(root).pack(side='top', fill='both', expand=True)
	root.mainloop()

#MainApplication()
