##
# V1 - a window with a button which opens up another window with a video playing 
# V2 - the basic interface works with buttons which link to video streams
#    - way found to change button focus
# V3 - need to add in a scrolling capability
# V4 - need to create IR interface - micropython
# V5 - need ip connection - 
# V6 - need to add style (stylesheets)


from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget

import sys

from random import randint

import mpv
import sys
import time

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from PyQt5.QtWidgets import QWidget
from PyQt5 import QtWidgets

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_video_screen(QWidget):
    
    def __init__(self, video_stream_address):
        super(Ui_video_screen, self).__init__()
        
        print("")
        print("")
        print("went into init")
        print("")
        print("")
        
        self.video_stream_address = video_stream_address
        
        windowsize = app.desktop().availableGeometry().size()
        xpos = 200 
        ypos = 200
        self.width = windowsize.width()*.5 
        self.height = windowsize.height()*.5 
        self.setGeometry(xpos, ypos, self.width, self.height)
        self.setWindowTitle("Test window Title")
        self.setObjectName("video_screen")
        self.resize(self.width, self.height)
        self.initUI()
        self.start_vid()
    
    def initUI(self):
        self.video_widget = QtWidgets.QWidget(self)
        self.video_widget.setGeometry(QtCore.QRect(0, 0, self.width, self.height))
        self.video_widget.setObjectName("video_window")
        
        self.button_widget = QtWidgets.QWidget(self)
        self.button_widget.setGeometry(QtCore.QRect(0, 0, self.width, self.height*.30))
        self.button_widget.setObjectName("button_widget")       
        
        self.verticalLayout = QtWidgets.QVBoxLayout(self.button_widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(self.button_widget)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.return_button = QtWidgets.QPushButton(self.groupBox)
        font.setPointSize(30)
        self.return_button.setFont(font)
        self.return_button.setObjectName("return_button")
        self.horizontalLayout.addWidget(self.return_button)
        self.refresh_button = QtWidgets.QPushButton(self.groupBox)
        self.refresh_button.setFont(font)
        self.refresh_button.setObjectName("refresh_button")
        self.horizontalLayout.addWidget(self.refresh_button)
        self.reboot_button = QtWidgets.QPushButton(self.groupBox)
        self.reboot_button.setFont(font)
        self.reboot_button.setObjectName("reboot_button")
        self.horizontalLayout.addWidget(self.reboot_button)
        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox.setTitle("Options")
        self.return_button.setText("Return")
        self.refresh_button.setText("Refresh")
        self.reboot_button.setText("Reboot")
        self.setWindowTitle("Stream")
        
        self.return_button.clicked.connect(self.return_func)
        self.refresh_button.clicked.connect(self.refresh_func)
        self.reboot_button.clicked.connect(self.reboot_func)     
        
        #self.button_widget.hide()
        
    def start_vid(self):
        print("starting video")
        self.video_widget.setAttribute(Qt.WA_DontCreateNativeAncestors)
        self.video_widget.setAttribute(Qt.WA_NativeWindow)
        self.player = mpv.MPV(wid=str(int(self.video_widget.winId())),
                #vo='x11', # You may not need this
                log_handler=print,
                loglevel='debug'
                )  
        self.player.play(self.video_stream_address)  
        
    def return_func(self):
        print("pressed return button")
        #Ui_video_screen
        self.player.stop()
        self.close()
    
    def refresh_func(self):
        print("pressed refresh button")
        #print("self.w = ", self.w)
        #self.w = None
        self.player.stop()
        time.sleep(2)
        self.player.play(self.video_stream_address)
    
    def reboot_func(self):
        print("pressed reboot button")   

class SettingsWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("Another Window % d" % randint(0,100))
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        self.button_hide = QPushButton("Hide", self) 
        self.button_hide.setGeometry(0, 150, 200, 40) 
        self.button_hide.clicked.connect(self.hidebutton) 
        
        self.button_show = QPushButton("show", self) 
        self.button_show.setGeometry(200, 150, 200, 40) 
        self.button_show.clicked.connect(self.showbutton) 
        
        self.button_close = QPushButton("close window", self) 
        self.button_close.setGeometry(400, 150, 200, 40) 
        self.button_close.clicked.connect(self.close_window) 
        
        self.show() 

    def hidebutton(self): 
		# hiding the button 
        self.button_hide.hide() 
		# printing pressed 
        print("hiding button") 
        
    def showbutton(self): 
		# hiding the button 
        self.button_hide.show() 
		# printing pressed 
        print("showing button") 
        
    def close_window(self):
        print("closing window") 
        self.close() 

class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.w = None  # No external window yet.
        
        self.setObjectName("MainWindow")
        self.resize(910, 665)
        self.setAutoFillBackground(True)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_buttons = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_buttons.sizePolicy().hasHeightForWidth())
        self.groupBox_buttons.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(30)
        
        self.groupBox_buttons.setFont(font)
        self.groupBox_buttons.setTitle("")
        self.groupBox_buttons.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_buttons.setFlat(False)
        self.groupBox_buttons.setObjectName("groupBox_buttons")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_buttons)
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.gridLayout.setObjectName("gridLayout")
        self.vid_button_1 = QtWidgets.QPushButton(self.groupBox_buttons)
        self.vid_button_1.setObjectName("vid_button_1")        
        self.vid_button_1.setSizePolicy(sizePolicy)
        self.gridLayout.addWidget(self.vid_button_1, 0, 0, 1, 1)
        
        self.vid_button_2 = QtWidgets.QPushButton(self.groupBox_buttons)
        self.vid_button_2.setObjectName("vid_button_2")
        self.vid_button_2.setSizePolicy(sizePolicy)
        self.gridLayout.addWidget(self.vid_button_2, 0, 1, 1, 1)
        
        self.vid_button_3 = QtWidgets.QPushButton(self.groupBox_buttons)
        self.vid_button_3.setObjectName("vid_button_3")
        self.vid_button_3.setSizePolicy(sizePolicy)
        self.gridLayout.addWidget(self.vid_button_3, 1, 0, 1, 1)
        
        self.vid_button_4 = QtWidgets.QPushButton(self.groupBox_buttons)
        self.vid_button_4.setObjectName("vid_button_4")
        self.vid_button_4.setSizePolicy(sizePolicy)
        self.gridLayout.addWidget(self.vid_button_4, 1, 1, 1, 1)
        
        self.verticalLayout.addWidget(self.groupBox_buttons)
        self.setting_button = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(30)
        self.setting_button.setFont(font)
        self.setting_button.setObjectName("setting_button")
        self.verticalLayout.addWidget(self.setting_button)
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.vid_button_1.setText("Video 1")
        self.vid_button_2.setText("Video 2")
        self.vid_button_3.setText("Video 3")
        self.vid_button_4.setText("Video 4")
        self.setting_button.setText("Settings")          

        #lambda: calluser(name)
        streams = ['rtsp://192.168.8.20/0', 'rtsp://192.168.8.20/4', 'rtsp://192.168.8.20/8', 'rtsp://192.168.8.20/12']

        self.vid_button_1.clicked.connect( lambda: self.show_new_window(streams[0]) )
        self.vid_button_2.clicked.connect( lambda: self.show_new_window(streams[1]) )
        self.vid_button_3.clicked.connect( lambda: self.show_new_window(streams[2]) )
        self.vid_button_4.clicked.connect( lambda: self.show_new_window(streams[3]) )
        self.setting_button.clicked.connect( self.test )
        
        self.vid_button_2.setDefault(True) #test but set focus to button2
        QtCore.QTimer.singleShot(0, self.vid_button_2.setFocus) # works!!!
        
        #time.sleep(15)
        #self.vid_button_2.setFocus()
        #print("set focus to button 2")
        #time.sleep(15)
        #print("pressing button automatically")
        #self.vid_button_2.click()

    def show_new_window(self, stream):
        if self.w is None:          
            self.w = Ui_video_screen(stream)
            self.w.show()            
            
        else:
            self.w.close()  # Close window.
            self.w = None  # Discard reference.
            
    def test(self):
        self.vid_button_2.setDefault(True)
        QtCore.QTimer.singleShot(0, self.vid_button_2.setFocus) # works!!!
        #self.vid_button_2.setFocus() ## doesn't work!!
        print("pressing button automatically")
        time.sleep(10)
        self.vid_button_2.click() # works!!!
        

if __name__ == "__main__":

    #windowsize = app.desktop().availableGeometry().size()
    
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
