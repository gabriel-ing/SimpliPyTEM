import tkinter as tk
from tkinter import ttk, filedialog
#from tkinter import 

import os
from Micrograph_editing_functions import *
from PDF_generator import pdf_generator 
import subprocess as sb

class MainApplication(tk.Tk):
	def __init__(self):
		super().__init__()
		#self.parent = parent
		#self.label
		self.geometry('600x600')
		self.title('Micrograph Previews App')
		ttk.Label(self,text='Program for generating small filesize previews of micrographs', wraplength=550).pack()
		ttk.Label(self,text='Choose whether to process a file, a folder, or live during an imaging session', wraplength=550).pack()
		#self.label = ttk.Label(self, text ='Hello').pack()
		#self.geometry('400x300')

		self.live='Folder'
		self.liveButton = ttk.Button(self, text='Process Folder', command=self.liveCommand,)
		self.liveButton.pack()

		ttk.Label(self, text='Choose folder or file:').pack()
		
		self.folder = ''
		self.browsebutton=ttk.Button(self, text='Browse', command=self.BrowseCommand)
		self.browsebutton.pack()

		self.folderLabel = ttk.Label(self, text=self.folder)
		self.folderLabel.pack()

		ttk.Label(self, text='Choose output image options:').pack()
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
		self.textoff = 'On'
		self.textbutton = ttk.Button(self, text='Scalebar text: On', command=self.TextoffCommand)
		self.textbutton.pack()

		self.motioncor = 'Off'
		self.motioncorbutton = ttk.Button(self, text='Motion Correct videos: Off', command=self.MotioncorCommand)
		self.motioncorbutton.pack()
		
		self.quality = tk.DoubleVar()
		self.qualitySlider=ttk.Scale(self, variable=self.quality,from_=10, to=100, orient=tk.HORIZONTAL, command=self.getQuality)
		self.qualitySlider.pack()

		self.output_folder_name = 'Previews'
		ttk.Label(self, text='Choose output folder name (default=Previews)').pack()
		self.outfolder_box = tk.Text(self, height=1)
		self.outfolder_box.pack()

		self.runButton = ttk.Button(self, text='RUN!', command=self.runCommand)
		self.runButton.pack()

		ttk.Label(self, text='This section allows writing all micrographs into a formatted PDF document.').pack()
		ttk.Label(self, text='Experiment title:').pack()
		self.title_box = tk.Text(self, height=1)
		self.title_box.pack()
		ttk.Label(self, text='Add notes here:').pack()
		self.notes_box = tk.Text(self, height=5)
		self.notes_box.pack()
		self.pdf_on_button = ttk.Button(self, text='Generate PDF', command=self.pdf_command)
		self.pdf_on_button.pack()

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
	
	def	TextoffCommand(self):
		self.textoff = self.cycle_options(['On', 'Off'], self.textoff)
		self.textbutton.config(text='Scalebar text: {}'.format(self.textoff))

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
		print(os.getcwd())
		os.chdir(self.folder)
		os.chdir(self.output_folder_name)
		print(os.getcwd())
		images = [x for x in os.listdir('.') if x[-4:]=='.jpg']
		print(images)
		self.Retrive_title()
		self.Retrive_notes()
		pdf_generator(images, title=self.title, notes=self.notes)
		print('Done!')
		os.chdir(self.folder)

	def process_folder(self):
		os.chdir(self.folder)
		dm_files = [x for x in os.listdir('.') if x[-4:-1]=='.dm']
		dm_vids = [x for x in dm_files if os.path.getsize(x)>230165776 and x[-3:]=='dm4']
		dm_ims = [x for x in dm_files if x not in dm_vids]	
		print(dm_vids)
		for file in dm_vids:
			print(file)
			outfile_aligned = motioncorrect_video(file)
			Generate_preview_dm(outfile_aligned,textoff=self.textoff,xybin=self.bin,quality=80,foldername=self.output_folder_name)			
			try:
				pass
				#outfile_aligned = motioncorrect_video(file)
				#Generate_preview_dm(outfile_aligned,textoff=self.textoff,xybin=self.bin,quality=80,foldername=self.output_folder_name)
			except Exception:
				print('Exception!')
				pass
		for file in dm_ims:
			Generate_preview_dm(file, textoff=self.textoff,xybin=self.bin, quality=80,foldername=self.output_folder_name)
	
	def process_file(self):
		file=self.folder
		print(file)
		if file[-3:]=='dm4' and os.path.getsize(file)>230165776:
			outfile_aligned = motioncorrect_video(file)
			Generate_preview_dm(outfile_aligned, textoff=self.textoff, xybin=self.bin, quality=80,foldername=self.output_folder_name)
		elif file[-3:]=='dm3':
			Generate_preview_dm(file, textoff=self.textoff,xybin=self.bin, quality=80,foldername=self.output_folder_name)
			#print('working')	

	def live_process(self):
		os.chdir(self.folder)
		files = os.listdir('.')
		file_set = set(files)
		start_time = time.time()
		max_running_time = 3600
		while True:
			for file in os.listdir('.'):
				if file not in file_set:
					if file[-3:]=='dm4':
						try:
							outfile_aligned = motioncorrect_video(file)
							print(file)
							Generate_preview_dm(outfile_aligned,textoff=self.textoff,xybin=self.bin,quality=80, foldername=self.output_folder_name)
						except: 
							Generate_preview_dm(file)
					elif file[-3:]=='dm3':
						#try:
						Generate_preview_dm(file,textoff=self.textoff,xybin=self.bin,quality=80,foldername=self.output_folder_name)
						#except Exception:
					#		print('Exception')
						#	time.sleep(100)
						#try:	
							#Generate_preview_dm(file,textoff=self.textoff,xybin=self.xybin,quality=80,foldername=self.output_folder_name)
						#except:
							#pass	
					print(file)
					file_set.add(file)
            
			running_time = time.time() - start_time
			print(running_time)
			if running_time>max_running_time:
				break
			time.sleep(30)    		


	def getQuality(self):
		print(self.qualitySlider.get())

	def cycle_options(self, options, current): #cycle through the options
		#print(options)

		ind = options.index(current)
		if ind==len(options)-1:
			ind = 0
		else:
			ind +=1	
		return options[ind]

	def Retrive_folder(self):
		self.output_folder_name = self.outfolder_box.get('1.0', tk.END)
		self.output_folder_name=self.output_folder_name.strip('\n')
		if self.output_folder_name == '':
			self.output_folder_name='.'
		print(self.output_folder_name)

	def Retrive_title(self):
		self.title = self.title_box.get('1.0', tk.END)
		self.title=self.title.strip('\n')
		print(self.title)

	def Retrive_notes(self):
		self.notes = self.notes_box.get('1.0', tk.END)
		self.notes=self.notes.strip('\n')
		print(self.notes)


if __name__=="__main__":
	root = MainApplication()
	#MainApplication(root).pack(side='top', fill='both', expand=True)
	root.mainloop()

#MainApplication()
