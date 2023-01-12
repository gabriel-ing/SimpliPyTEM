import os
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtWidgets import (QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout,
                             QFileDialog, QTextEdit, QTextBrowser, QComboBox, QCheckBox, QMainWindow,QGridLayout,QFileDialog,QLineEdit,QButtonGroup)
from PyQt5.QtGui import QFont
import sys
from App_functions import * 
from SimpliPyTEM.PDF_generator import *
from html_writer import *


class MainApplication(QWidget):
    def __init__(self):
        super().__init__()
        #Qt.AlignHCenter

        self.setGeometry(500, 500, 100,400)
        self.setWindowTitle('Micrograph Previews App')
        
        self.title = QLabel('Make Preview Images',self)
        #app.setStyleSheet("QLabel, QCheckBox{font-size: 16pt;}")




        self.folderlabel = QLabel('Choose whether to process a folder,\n a file or liveprocessing a folder:')
        #label.setLayout(layout)
        #self.label2 = QLabel('Choose whether to process a file, a folder, or live during an imaging session',self)
        self.title.setAlignment(Qt.AlignCenter)
        #Live
        self.live = 'Folder'
        self.live_choice = QComboBox(self)
        #live_button.clicked.connect(self.liveCommand)
        choices = ['Folder', 'File', 'Live Processing']
        self.folder_option=choices[0]
        self.live_choice.addItems(['Folder', 'File', 'Live Processing'])
        self.live_choice.currentTextChanged.connect(self.text_changed)
        #live_choice.setLayout(layout)


        self.folderpath = None
        #Checkbox for median filter
        self.med_check = QCheckBox('Median filter',self)
        #self.med_check.setEnabled(True)
        self.med_check.toggled.connect(self.updateMed)
        self.Med_state=True
        self.med_check.setChecked(True)
        #Value choicec for median filter
        self.med_filter_value= 3
        self.med_choice = QComboBox(self)
        self.med_choice.addItems(['3', '5', '7','9','11'])
        self.med_choice.currentTextChanged.connect(self.med_int_changed)


        #Checkbox for gaussian filter
        self.gauss_check = QCheckBox('Gaussian Filter', self)
        self.gauss_check.toggled.connect(self.updateGauss)
        self.gauss_check.setChecked(False)
        self.Gauss_state=False

        #value for gaussian filter
        self.gauss_filter_value= 3
        self.gauss_choice = QComboBox(self)
        self.gauss_choice.addItems(['3', '5', '7','9','11'])
        self.gauss_choice.currentTextChanged.connect(self.gauss_int_changed)

        # Checkbox for bin 
        self.bin_check = QCheckBox('Bin image', self)
        self.bin_check.toggled.connect(self.updateBin)
        self.bin_check.setChecked(True)
        self.Bin_state=True

        #Value for bin
        self.bin_value = 2
        self.bin_choice=QComboBox(self)
        self.bin_choice.addItems(['2','4','8'])
        self.bin_choice.currentTextChanged.connect(self.gauss_int_changed)

        #Checkbox for scalebar
        self.scalebar_on = True
        self.scalebar_check = QCheckBox('Scalebar', self)
        self.scalebar_check.toggled.connect(self.updateScalebar)
        self.scalebar_check.setChecked(True)


        self.output_folder_label = QLabel('Give the output folder a name:')
        self.output_folder_box =  QLineEdit(self)




        #Video options checkboxes:
        self.video_group = QButtonGroup()
        self.video_label =  QLabel('If there are videos, choose how video files are handled, else ignore: ')
        



        self.video_option1 = QCheckBox('Save Average', self)
        self.video_option2 = QCheckBox('Save Video as mp4', self)
        self.video_option3 = QCheckBox('Save Tif Stack', self)
        self.video_option4 = QCheckBox('Save MotionCorrected average', self)
        self.video_group.buttonClicked.connect(self.video_group_func)
        self.video_status='Save Averages'
        self.video_group.addButton(self.video_option1)
        self.video_group.addButton(self.video_option2)
        self.video_group.addButton(self.video_option3)
        self.video_group.addButton(self.video_option4)

        self.doc_label1 = QLabel('Document Section')
        
        self.doc_label1.setAlignment(Qt.AlignCenter)

        self.doc_label=QLabel('Following generation of images/videos, use this section to create \n an html or pdf file to display the resulting images:')
        self.title_box_label = QLabel('Give a title for the experiment:')
        self.title_box = QLineEdit()
        self.notes_box_label=  QLabel('Add some notes here:')
        self.notes_box = QTextEdit()



        #Layoutsss
        self.make_buttons()
        self.set_fonts()
        self.set_layouts()
        self.add_styles()

        self.show()

    def make_buttons(self):
        #folder browse button
        self.FolderBrowse_button = QPushButton('Choose Folder', self)
        self.FolderBrowse_button.clicked.connect(self.FileFolderChooser)

        #self.FolderBrowse_button.setStyleSheet("background-color : White")

        #Run button 
        self.Run_button = QPushButton('Run!', self)
        self.Run_button.clicked.connect(self.RunCommand)

        #html button
        self.html_button = QPushButton('Make HTML!')
        self.html_button.clicked.connect(self.html_command)

        #pdf button
        self.pdf_button  = QPushButton('Made PDF!')
        self.pdf_button.clicked.connect(self.pdf_command)

    def add_styles(self):
        #app.setStyleSheet(" QCheckBox{font-size: 14pt;}")
        #app.setStyleSheet("QPushButton{background-color:White;font-size:16pt;font-weight:500;}")
        app.setStyleSheet('''QWidget{background-color:#C2E4E9;} \
            QPushButton:hover{background-color: #D8BBEA; color:black;} \
            QPushButton{background-color:white;font-size:16pt;font-weight:500;}  \
            QPushButton.active{background-color:#502673}
            QCheckBox{font-size: 14pt; } \
            QComboBox{background-color:white;font-size:14px}\
            QTextEdit{background-color:white;} \
            QLineEdit{background-color:white}''')

    def set_fonts(self):
        #define title font
        self.titlefont = QFont()
        self.titlefont.setPointSize(20)
        self.titlefont.setBold(True)
        # add title font to title and doc section title
        self.title.setFont(self.titlefont)
        self.doc_label1.setFont(self.titlefont)


        #define and set video label font 
        self.video_labelfont = QFont()
        self.video_labelfont.setPointSize(16)
        self.video_labelfont.setItalic(True)
        self.video_label.setFont(self.video_labelfont)

        #define button font - Easier done in the add_styles method
 

        #self.button_font = QFont()
        #self.button_font.setPointSize(16)
        #self.button_font.setBold(True) 
        #self.button_font.setItalic(True)

        #set button fonts
        #self.FolderBrowse_button.setFont(self.button_font)
        #self.Run_button.setFont(self.button_font)
        #self.html_button.setFont(self.button_font)
        #self.pdf_button.setFont(self.button_font)



    def set_layouts(self):
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.title,0,0, 1,2)
        self.layout.addWidget(self.folderlabel,1,0,1,1)
        self.layout.addWidget(self.live_choice,1,1,1,1)
        self.layout.addWidget(self.FolderBrowse_button, 2,0,1,2)
        self.layout.addWidget(self.med_check,3,0,1,1)
        self.layout.addWidget(self.med_choice,3,1,1,1)

        self.layout.addWidget(self.gauss_check,4,0,1,1)
        self.layout.addWidget(self.gauss_choice,4,1,1,1)
        self.layout.addWidget(self.bin_check,5,0,1,1)
        self.layout.addWidget(self.bin_choice,5,1,1,1)

        self.layout.addWidget(self.scalebar_check, 6,0,1,2)
        self.layout.addWidget(self.output_folder_label, 7,0,1,1)
        self.layout.addWidget(self.output_folder_box,7,1,1,1)

        self.layout.addWidget(self.video_label, 8,0,1,2)
        self.layout.addWidget(self.video_option1,9,0,1,1)
        self.layout.addWidget(self.video_option2,9,1,1,1)
        self.layout.addWidget(self.video_option3,10,0,1,1)
        self.layout.addWidget(self.video_option4,10,1,1,1)
        self.layout.addWidget(self.Run_button, 11,0,1,2)
        self.layout.addWidget(self.doc_label1, 12,0,1,2)
        self.layout.addWidget(self.doc_label, 13, 0,1,2)
        self.layout.addWidget(self.title_box_label, 14, 0,1,1)
        self.layout.addWidget(self.title_box,15,0,1,2)
        self.layout.addWidget(self.notes_box_label, 16,0,1,1)
        self.layout.addWidget(self.notes_box, 17,0,1,3)

        self.layout.addWidget(self.html_button, 21,0,1,1)
        self.layout.addWidget(self.pdf_button, 21,1,1,1)

        

    def text_changed(self, s): # i is an int
        self.folder_option=s 
    def med_int_changed(self,i):
        self.med_filter_value=int(i)
    def gauss_int_changed(self,i):
        self.gauss_filter_value=int(i)
    def bin_int_changed(self,i):
        self.bin_value=int(i)
    def updateGauss(self,state):
        self.Gauss_state=state
    def updateMed(self,state):
        self.Med_state=state
    def updateBin(self,state):
        self.Bin_state = state
    def updateScalebar(self,state):
        self.scalebar_on=state
    def video_group_func(self, but):
        self.videostatus = (but.text())

    def FileFolderChooser(self):
        if self.folder_option=='Folder' or self.folder_option=='Live Processing':
            self.folderpath = QFileDialog.getExistingDirectory(self, 'Select a Folder')
        else:
            self.folderpath = QFileDialog.getOpenFileName(self, 'Select a File')[0]

    def html_command(self):
        outdir = self.output_folder_box.text()
        if outdir=='':
            outdir='.'

        cwd = os.getcwd()
        os.chdir(self.folderpath+'/'+outdir)

        title = self.title_box.text()
        notes = self.notes_box.toPlainText()
        print('Writing html and css files')
        image_files, video_files = get_files('Images', 'Videos')
        write_html(image_files, video_files, title, notes)
        write_css()
        print('Done!')
        os.chdir(cwd)

    def pdf_command(self):
        outdir = self.output_folder_box.text()
        if outdir=='':
            outdir='.'

        cwd = os.getcwd()
        os.chdir(self.folderpath+'/'+outdir)


        title = self.title_box.text()
        notes = self.notes_box.toPlainText()
        
        print(os.getcwd())
        print(os.listdir('.'))

        images = ['Images/'+x for x in os.listdir('Images')]
        print(images)
        pdf_generator(images, title, notes)

        os.chdir(cwd)

    def RunCommand(self):
        #print('Gauss=', self.Gauss_state)
        #print('Med=',self.Med_state)
        #print('med_value',self.med_filter_value)
        #print('Bin=',self.Bin_state)
        #print('Folder:' ,self.folder_option)
        
        
        outdir = self.output_folder_box.text()
        if outdir=='':
            outdir='.'
        elif '\n' in outdir:
            outdir.replace('\n','')


        if self.Med_state==False:
            self.med_filter_value=0
        if self.Gauss_state==False:
            self.gauss_filter_value=0
        if self.Bin_state==False:
            self.bin_value=0

        if self.folderpath=='' or self.folderpath==None:
            print('Please select a folder/file')
            return 1
        print(self.folderpath)
        if self.live=='Folder':
            print('Running folder?')
            process_folder(self.folderpath, outdir, self.bin_value, self.med_filter_value, self.gauss_filter_value,self.video_status )
        elif self.live=='File':
            print(self.live)    
            process_file(self.folderpath, outdir, self.bin_value, self.med_filter_value, self.gauss_filter_value,self.video_status )
        elif self.live =='Live Processing':
            live_process_folder(self.folderpath, outdir, self.bin_value, self.med_filter_value, self.gauss_filter_value,self.video_status )




#MainApplication.show()
#application.exec()
app = QApplication(sys.argv)
ex = MainApplication()
sys.exit(app.exec_())
