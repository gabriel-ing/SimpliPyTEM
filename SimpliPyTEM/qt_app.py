from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtWidgets import (QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout,
                             QFileDialog, QTextEdit, QTextBrowser, QComboBox, QCheckBox, QMainWindow,QGridLayout,QFileDialog,QLineEdit,QButtonGroup)
import sys
from App_functions import * 

class MainApplication(QWidget):
    def __init__(self):
        super().__init__()
        #Qt.AlignHCenter
        layout = QGridLayout()
        self.setLayout(layout)
        self.setGeometry(500, 500, 100,400)
        self.setWindowTitle('Micrograph Previews App')
        
        title = QLabel('Program for generating small filesize previews of micrographs',self)
        app.setStyleSheet("QLabel, QCheckBox{font-size: 16pt;}")
        #font = QFont("Helvetica [Cronyx]", 12)
        #title.setFont(font)
        folderlabel = QLabel('Choose whether to process a folder,\n a file or liveprocessing a folder:')
        #label.setLayout(layout)
        #self.label2 = QLabel('Choose whether to process a file, a folder, or live during an imaging session',self)
        title.setAlignment(Qt.AlignCenter)
        #Live
        self.live = 'Folder'
        self.live_choice = QComboBox(self)
        #live_button.clicked.connect(self.liveCommand)
        choices = ['Folder', 'File', 'Live Processing']
        self.folder_option=choices[0]
        self.live_choice.addItems(['Folder', 'File', 'Live Processing'])
        self.live_choice.currentTextChanged.connect(self.text_changed)
        #live_choice.setLayout(layout)

        FolderBrowse_button = QPushButton('Choose Folder', self)
        FolderBrowse_button.clicked.connect(self.FileFolderChooser)
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


        Run_button = QPushButton('Run!', self)
        Run_button.clicked.connect(self.RunCommand)

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

        #Layoutss
        layout.addWidget(title,0,0, 1,2)
        layout.addWidget(folderlabel,1,0,1,1)
        layout.addWidget(self.live_choice,1,1,1,1)
        layout.addWidget(FolderBrowse_button, 2,0,1,2)
        layout.addWidget(self.med_check,3,0,1,1)
        layout.addWidget(self.med_choice,3,1,1,1)

        layout.addWidget(self.gauss_check,4,0,1,1)
        layout.addWidget(self.gauss_choice,4,1,1,1)
        layout.addWidget(self.bin_check,5,0,1,1)
        layout.addWidget(self.bin_choice,5,1,1,1)

        layout.addWidget(self.scalebar_check, 6,0,1,2)
        layout.addWidget(self.output_folder_label, 7,0,1,1)
        layout.addWidget(self.output_folder_box,7,1,1,1)

        layout.addWidget(self.video_label, 8,0,1,2)
        layout.addWidget(self.video_option1,9,0,1,1)
        layout.addWidget(self.video_option2,9,1,1,1)
        layout.addWidget(self.video_option3,10,0,1,1)
        layout.addWidget(self.video_option4,10,1,1,1)
        layout.addWidget(Run_button, 11,0,1,2)
        
        self.show()

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

    def RunCommand(self):
        #print('Gauss=', self.Gauss_state)
        #print('Med=',self.Med_state)
        #print('med_value',self.med_filter_value)
        #print('Bin=',self.Bin_state)
        #print('Folder:' ,self.folder_option)
        
        
        outdir = self. output_folder_box.text()
        if outdir=='':
            outdir='Images'
        elif '\n' in outdir:
            outdir.replace('\n','')

        if self.Med_state==False:
            self.med_filter_value=0
        if self.Gauss_state==False:
            self.gauss_filter_value=0
        if self.Bin_state==False:
            self.bin_value=0

        if self.folderpath==None:
            print('Please select a folder/file')
            return 1

        if self.live=='Folder':
            print('calling?')
            process_folder(self.folderpath, outdir, self.bin_value, self.med_filter_value, self.gauss_filter_value,self.video_status )
        else:
            print(self.live)





#MainApplication.show()
#application.exec()
app = QApplication(sys.argv)
ex = MainApplication()
sys.exit(app.exec_())