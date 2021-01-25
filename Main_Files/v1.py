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




###

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

    def __init__(self):
        super().__init__()
        self.w = None  # No external window yet.
        
        self.button1 = QPushButton("Push for Window")
        self.button1.clicked.connect(self.show_new_window)
        self.setCentralWidget(self.button1)

    def show_new_window(self):
        if self.w is None:
            #self.w = AnotherWindow()
            #self.w.show()
            
            stream1= 'rtsp://192.168.8.20/4'
            self.w = Ui_video_screen(stream1)
            self.w.show()            
            
        else:
            self.w.close()  # Close window.
            self.w = None  # Discard reference.


if __name__ == "__main__":

    #windowsize = app.desktop().availableGeometry().size()
    
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    #video_win = Ui_video_screen()
    #video_win.show()
    #app.exec_()
    sys.exit(app.exec_())
