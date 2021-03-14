##
# V1 - a window with a button which opens up another window with a video playing 
# V2 - the basic interface works with buttons which link to video streams
#    - way found to change button focus
# V3 - added keyboard navigation
# V4 - need to create IR interface - Opi-gpio + thread + queue 
# V5 - Intergrate pyqt5 with IR commands 
# V6 - need ip connection 
# V7 - need to add style (stylesheets)

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

import OPi.GPIO as GPIO
from time import sleep
from time import perf_counter
import threading
import multiprocessing
import numpy
from queue import Queue
import locale

LED_gpio = 7 # pin name = PA6 wPi = 2 GPIO = 6 
ir_gpio = 5 # pin name = SCL.0 wPi = 1 GPIO = 11

GPIO.setmode(GPIO.BOARD)  # set up BOARD BCM SUNXI numbering
#GPIO.setup(LED_gpio, GPIO.OUT)    # set pin as an output (LED)

GPIO.setup(ir_gpio, GPIO.IN)

# ===================================================================================================
# IR controls

#wait_time = 4523982e-9 * 1.5 # 60e-3 # in seconds should be just higher than the longest wait. think longest is about 5ms. noted from looking theough sky remote commands
wait_time = 6e-3 # in seconds should be just higher than the longest wait. think longest is about 5ms. noted from looking theough sky remote commands
wait_time = 1e-2

ir_keys_dict = { # in nanosecs
    'right': numpy.array([0.004273, 0.004527, 0.000435, 0.001788, 0.000553, 0.001568, 0.000650, 0.001661, 0.000498, 0.000498, 0.000651, 0.000486, 0.000564, 0.000620, 0.000599, 0.000496, 0.000490, 0.000487, 0.000694, 0.001671, 0.000442, 0.001704, 0.000644, 0.001608, 0.000577, 0.000570, 0.000493, 0.000566, 0.000567, 0.000518, 0.000588, 0.000491, 0.000646, 0.000565, 0.000484, 0.000487, 0.000733, 0.001488, 0.000646, 0.000484, 0.000565, 0.000604, 0.000535, 0.000579, 0.000566, 0.001605, 0.000673, 0.001552, 0.000568, 0.000566, 0.000565, 0.001646, 0.000566, 0.000483, 0.000644, 0.001573, 0.000752, 0.001458, 0.000726, 0.001658, 0.000499, 0.000496, 0.000647, 0.000484, 0.000565, 0.001636, 0.000581]), 
    'left' : numpy.array([0.004381, 0.004456, 0.000502, 0.001620, 0.000570, 0.001685, 0.000605, 0.001628, 0.000533, 0.000601, 0.000520, 0.000524, 0.000587, 0.000568, 0.000491, 0.000566, 0.000607, 0.000514, 0.000587, 0.001682, 0.000514, 0.001677, 0.000520, 0.001691, 0.000519, 0.000582, 0.000586, 0.000590, 0.000493, 0.000486, 0.000649, 0.000579, 0.000502, 0.000519, 0.000509, 0.001704, 0.000591, 0.000488, 0.000716, 0.001613, 0.000573, 0.000520, 0.000520, 0.000603, 0.000497, 0.001645, 0.000623, 0.001688, 0.000506, 0.000489, 0.000567, 0.000643, 0.000523, 0.001666, 0.000576, 0.000491, 0.000567, 0.001599, 0.000679, 0.001665, 0.000439, 0.000667, 0.000509, 0.000504, 0.000581, 0.001731, 0.000496]),
    'enter' :numpy.array([0.004291, 0.004423, 0.000652, 0.001543, 0.000591, 0.001699, 0.000569, 0.001668, 0.000520, 0.000576, 0.000595, 0.000495, 0.000564, 0.000558, 0.000560, 0.000516, 0.000576, 0.000595, 0.000486, 0.001727, 0.000540, 0.001636, 0.000485, 0.001676, 0.000745, 0.000482, 0.000500, 0.000482, 0.000721, 0.000482, 0.000479, 0.000599, 0.000569, 0.000589, 0.000486, 0.000560, 0.000565, 0.000638, 0.000545, 0.000414, 0.000747, 0.001520, 0.000632, 0.000519, 0.000490, 0.001703, 0.000643, 0.001622, 0.000498, 0.000650, 0.000562, 0.001622, 0.000601, 0.001602, 0.000567, 0.001720, 0.000485, 0.000507, 0.000566, 0.001676, 0.000678, 0.000532, 0.000511, 0.000490, 0.000645, 0.001650, 0.000573]), 
    'return':numpy.array([0.004415, 0.004415, 0.000515, 0.001658, 0.000700, 0.001538, 0.000517, 0.001694, 0.000580, 0.000528, 0.000570, 0.000516, 0.000569, 0.000560, 0.000482, 0.000662, 0.000592, 0.000494, 0.000583, 0.001670, 0.000505, 0.001686, 0.000589, 0.001619, 0.000646, 0.000419, 0.000578, 0.000511, 0.000570, 0.000564, 0.000538, 0.000598, 0.000591, 0.000490, 0.000585, 0.000569, 0.000486, 0.000565, 0.000670, 0.000511, 0.000574, 0.001635, 0.000483, 0.001727, 0.000590, 0.000491, 0.000645, 0.001560, 0.000591, 0.000578, 0.000500, 0.001681, 0.000608, 0.001649, 0.000492, 0.001758, 0.000523, 0.000494, 0.000668, 0.000491, 0.000482, 0.001730, 0.000489, 0.000503, 0.000732, 0.001629, 0.000505]),
    'down' : numpy.array([0.004283, 0.004550, 0.000543, 0.001578, 0.000513, 0.001692, 0.000649, 0.001594, 0.000513, 0.000588, 0.000662, 0.000485, 0.000484, 0.000617, 0.000567, 0.000519, 0.000568, 0.000509, 0.000566, 0.001751, 0.000541, 0.001657, 0.000485, 0.001736, 0.000489, 0.000604, 0.000567, 0.000562, 0.000499, 0.000485, 0.000729, 0.000488, 0.000497, 0.000496, 0.000638, 0.001626, 0.000650, 0.000479, 0.000497, 0.000642, 0.000564, 0.000503, 0.000561, 0.000659, 0.000485, 0.001689, 0.000498, 0.001710, 0.000598, 0.000490, 0.000561, 0.000511, 0.000643, 0.001634, 0.000573, 0.001625, 0.000628, 0.001652, 0.000480, 0.001717, 0.000618, 0.000522, 0.000665, 0.000479, 0.000477, 0.001691, 0.000502]), 
    'up' :   numpy.array([0.004288, 0.004426, 0.000647, 0.001535, 0.000654, 0.001583, 0.000607, 0.001568, 0.000646, 0.000572, 0.000502, 0.000524, 0.000615, 0.000494, 0.000654, 0.000489, 0.000597, 0.000466, 0.000613, 0.001711, 0.000514, 0.001665, 0.000554, 0.001641, 0.000568, 0.000521, 0.000586, 0.000543, 0.000509, 0.000579, 0.000655, 0.000484, 0.000583, 0.000415, 0.000721, 0.000511, 0.000581, 0.000489, 0.000569, 0.000487, 0.000673, 0.000543, 0.000506, 0.000489, 0.000644, 0.001623, 0.000598, 0.001611, 0.000504, 0.000730, 0.000498, 0.001597, 0.000655, 0.001596, 0.000595, 0.001588, 0.000651, 0.001574, 0.000528, 0.001732, 0.000564, 0.000562, 0.000509, 0.000509, 0.000670, 0.001537, 0.000645]), 
    'exit':  numpy.array([0.004383, 0.004593, 0.000486, 0.001635, 0.000487, 0.001646, 0.000673, 0.001685, 0.000485, 0.000515, 0.000626, 0.000412, 0.000731, 0.000481, 0.000486, 0.000638, 0.000596, 0.000499, 0.000509, 0.001728, 0.000500, 0.001665, 0.000569, 0.001675, 0.000502, 0.000604, 0.000670, 0.000485, 0.000487, 0.000664, 0.000557, 0.000446, 0.000531, 0.000612, 0.000504, 0.001715, 0.000587, 0.000544, 0.000524, 0.001671, 0.000637, 0.001564, 0.000644, 0.000514, 0.000428, 0.001779, 0.000538, 0.000513, 0.000650, 0.000484, 0.000484, 0.000560, 0.000654, 0.001689, 0.000547, 0.000430, 0.000743, 0.000507, 0.000501, 0.001644, 0.000584, 0.000485, 0.000570, 0.001711, 0.000567, 0.001685, 0.000510]),
}

ir_keys_tolerance_dict = {
    'up' : 0.000187,
    'down' : 0.000309,
    'left' : 0.000237,
    'right' : 0.000253,
    'exit' : 0.000271,
    'enter' : 0.000235,
    'return' : 0.000246
}

ir_keys_length = {
    'up' : len(ir_keys_dict['up']),
    'down' : len(ir_keys_dict['down']),
    'left' : len(ir_keys_dict['left']),
    'right' : len(ir_keys_dict['right']),
    'exit' : len(ir_keys_dict['exit']),
    'enter' : len(ir_keys_dict['enter']),
    'return' : len(ir_keys_dict['return'])    
}

class IR_reciever:
    
    def __init__(self, pin_num, delay_time):
        self.pin_num = pin_num
        self.delay_time = delay_time
        self.q = Queue(maxsize = 1) #create queue for communicating with ir thread. this will allow changing remote functions
        #print(q.qsize())

    def change_screen(self, screen_class): 
        self.q.put(screen_class) #this puts the sceen class into the queue so that it will be detected 

    def wait_for_falling_edge(self):

        while thread_flag_event.is_set() : #uses threading event to dictate when the loop should be killed
            if GPIO.input(ir_gpio) == 0:
                self.read_command(0)
                
            if self.q.full():
                print("queue message detected the message was:")
                self.screen_choice_class = self.q.get()
                #print(mesg)
                #if mesg == 'main screen':
                #    print('main screen message detected ')
                #elif mesg == 'menu screen':
                #    print('menu screen message detected ')
                #elif mesg == 'video screen':
                #    print('video screen message detected ')
                
    def wait_for_rising_edge(self):
        while thread_flag_event.is_set() :
            if GPIO.input(ir_gpio) == 1:
                self.read_command(1)
            
    def stop_detection(self):
        self.run_in_background == False

    def read_command(self, start_val):
        #print("input detected")
        command = []
        start_of_event = perf_counter()
        IR_timer = start_of_event + wait_time #make it extra long to stop the loop exiting premiturely. value will be reset inside loop
        
        previousValue = bool(start_val)
        
        while perf_counter() < IR_timer: #waits until a timer expires. the timer refers to the time after a command has not been passed. this is readjusted instide the code to make sure the entire command is captured
            #print(GPIO.input(ir_gpio)) #dont debug with this, it slows everything down too much and it misses all the inputs
            if GPIO.input(ir_gpio) != previousValue:  # Waits until change in state occurs.
                # Records the current time              maybe change to just record microseconds
                end_of_event = perf_counter() #records the end time of a signal change. the first start_of_event is above the while loop so from here out we need to record just hte$
                # Calculate time in between pulses
                command_length = end_of_event - start_of_event
                #print(command_length)
                start_of_event = perf_counter() #Resets the start time

                command.append(command_length)

                IR_timer = perf_counter() + wait_time #resets counter

                previousValue = not previousValue #value #changes previous value to current value to see if there is a change
                
        #print("finished event detect, lengh of command = ", len(command), "  command recorded = ")
        #print(command)
        #print("")
        
        len_command = len(command)
        #print("length of command = ", len_command)
          
        if min(ir_keys_length.values()) == len_command:
            self.translate_command(command) #compare value
        
    def translate_command(self, command):
        np_command = numpy.asarray(command, dtype=numpy.float32) # dtype=numpy.uintc)
        #print("checking command translation ")
        for i in ir_keys_dict: #scroll though the list >> just idea not finished
            if numpy.allclose(np_command, ir_keys_dict[i], rtol=1 , atol= ir_keys_tolerance_dict[i]): #checks if the arrays are the same within a tolerance
                self.screen_choice_class.button_control(i)
                break      

class Ui_video_screen(QWidget):
    
    def __init__(self, video_stream_address, gpio_input, main_screen_class):
        super(Ui_video_screen, self).__init__()
        
        self.gpio_input = gpio_input
        self.link_ir()
        
        self.main_screen_class = main_screen_class
        
        print("")
        print("")
        print("went into Video init")
        print("")
        print("")
        
        self.video_stream_address = video_stream_address
        
        windowsize = app.desktop().availableGeometry().size()
        xpos = 0 # 200 
        ypos = 0 # 200
        self.width = windowsize.width()* 1.0 #.5 
        self.height = windowsize.height()* 1.0 # .5 
        self.setGeometry(xpos, ypos, self.width, self.height)
        self.setWindowTitle("Test window Title")
        self.setObjectName("video_screen")
        self.resize(self.width, self.height)
        
        #QtCore.QTimer.singleShot(500, self.initUI)
        self.initUI()        
        
        self.q_core = multiprocessing.Queue(maxsize = 1)
        self.vid_core = multiprocessing.Process(target = self.start_vid)
        
        #self.vid_core.start()
        #self.start_vid() #current
        #=================================================
        # Current issue: the UI is being created after mpv starts, as mpv has no where to generate it isn't formed and neither is the ui
        #                   the UI is inly spawned when this function exits and as such the start_vid() function needs to be called after 
        #                   this is created 

    def link_ir(self):
        self.gpio_input.change_screen(self) # tell the button that you are in in the mainscreen 
      
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
        
        self.button_ids = []
        self.button_ids.append(self.return_button) 
        self.button_ids.append(self.refresh_button) 
        self.button_ids.append(self.reboot_button)   
        
        self.setFocusPolicy(Qt.StrongFocus) #!!! needed to change focus and use arrows when multiple widgets 
        self.button_navigator = 1
        self.return_button.setDefault(True) #test but set focus to button2      
        
        self.video_widget.setAttribute(Qt.WA_DontCreateNativeAncestors)
        self.video_widget.setAttribute(Qt.WA_NativeWindow)
        
        print("UI Created")  #
        
        #self.button_widget.hide()
        
    def start_vid(self):    #issue with mpv and ir reader. When both run at same time the thread is shared between the ir and mpv meaning that the remote doesn't detect a command as 1 whole command
                            # to resolve \i think either play mpv is a different core (multiprocessing.Process(target =...)) and shut down using queue from multiprocessing.Queue(maxsize = 1),
                            # note not the same queue as thread queue.
                            #option 2: stop mpv running in its own thread using start_event_thread=False and _loop but not sure how to shut off loop. think multicore the best option 
        print("starting video")
        #print("window id = ", str(int(self.video_widget.winId())) )
            
        self.player = mpv.MPV(
                wid=str(int(self.video_widget.winId()))
                , vo='x11' # You may not need this
                #, log_handler=print
                #, loglevel='debug'
                )
        #--vo=opengl --hwdec=vaapi
        #--vo=wayland --hwdec=vaapi
        #self.player.fullscreen = True
        self.player.play(self.video_stream_address)  
        self.player.wait_until_playing()
        self.q_core.get() #method will wait here until a user inputs something into q_core meaning the video will play here
        self.player.stop()
        print("ending mpv function")
        
    def return_func(self):
        print("pressed return button")
        self.main_screen_class.link_ir() #tell the IR function to link back to the main screen (done here as init isn't run when the screen opens)
        self.q_core.put("stop player")
        print("stopping video")        
        self.close()
    
    def refresh_func(self):
        print("pressed refresh button")
        self.q_core.put("stop player")
        time.sleep(1)
        self.q_core.get()
        self.vid_core.start()
    
    def reboot_func(self):
        print("pressed reboot button")   

    def button_control(self, command):
        print("video button changing function")
        old_num = self.button_navigator
        
        if command in ['up', 'down', 'right', 'left']:
            
            if command == 'up':
                if self.button_navigator == len(self.button_ids) -1:
                    self.button_navigator = 0 
                else:
                    self.button_navigator = self.button_navigator + 1 

            if command == 'right':
                if self.button_navigator == len(self.button_ids) -1:
                    self.button_navigator = 0 
                else:
                    self.button_navigator = self.button_navigator + 1 

            elif command == 'down':
                if self.button_navigator == 0:
                    self.button_navigator = len(self.button_ids) -1
                else:
                    self.button_navigator = self.button_navigator - 1
            else:
                if self.button_navigator == 0:
                    self.button_navigator = len(self.button_ids) -1
                else:
                    self.button_navigator = self.button_navigator - 1  

            self.button_ids[self.button_navigator].setDefault(True) #test but set focus to button2

            self.button_ids[old_num].setDefault(False) #test but set focus to button2
            
        elif command == "enter":
            self.button_ids[self.button_navigator].click() 
            
        elif command in ["return", 'exit']:
            self.q_core.put("stop player")
            self.close()

class SettingsWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self, gpio_input, main_screen_class):
        super().__init__()
        
        self.main_screen_class = main_screen_class
        
        self.gpio_input = gpio_input
        self.link_ir() #link ir commands to this page
        
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

    def link_ir(self):
        self.gpio_input.change_screen(self) # tell the button that you are in in the mainscreen 

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
        self.main_screen_class.link_ir() #tell the IR function to link back to the main screen (done here as init isn't run when the screen opens)
        self.close() 

class MainWindow(QMainWindow):

    def __init__(self, gpio_input):
        super(MainWindow, self).__init__()
        self.w = None  # No external window yet.
        self.button_navigator = 0
        
        self.gpio_input = gpio_input
        self.link_ir()

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
        
        self.button_ids = []
        self.button_ids.append(self.vid_button_1) 
        self.button_ids.append(self.vid_button_2) 
        self.button_ids.append(self.vid_button_3) 
        self.button_ids.append(self.vid_button_4) 
        self.button_ids.append(self.setting_button)         

        streams = ['rtsp://192.168.8.20/0', 'rtsp://192.168.8.20/4', 'rtsp://192.168.8.20/8', 'rtsp://192.168.8.20/12']

        self.vid_button_1.clicked.connect( lambda: self.show_new_window(streams[0]) )
        self.vid_button_2.clicked.connect( lambda: self.show_new_window(streams[1]) )
        self.vid_button_3.clicked.connect( lambda: self.show_new_window(streams[2]) )
        self.vid_button_4.clicked.connect( lambda: self.show_new_window(streams[3]) )
        self.setting_button.clicked.connect( self.settings )
        
        self.setFocusPolicy(Qt.StrongFocus) #!!! needed to change focus and use arrows when multiple widgets 
        self.button_navigator = 1
        self.vid_button_2.setDefault(True) #test but set focus to button2
        #QtCore.QTimer.singleShot(0, self.vid_button_2.setFocus) # works!!!
        
        #time.sleep(15)
        #self.vid_button_2.setFocus()
        #print("set focus to button 2")
        #time.sleep(15)
        #print("pressing button automatically")
        #self.vid_button_2.click()

    def show_new_window(self, stream):
        if self.w is None:          
            self.w = Ui_video_screen(stream, self.gpio_input, self) #the stream you want to play, the gpio link class to control the remote, the current class - this is needed to needed as the link_ir function needs to be called each time this screen enters this. main screen is particular as it is always open so init only ever gets called once. this will allow it to be called from a seperate class
            self.w.show()            
            
        else:
            self.w.close()  # Close window.
            self.w = None  # Discard reference.
            
    def link_ir(self):
        self.gpio_input.change_screen(self) # tell the button that you are in in the mainscreen 
        print("linked ir to main screen")
        
    def settings(self):
        #self.vid_button_2.setDefault(True)
        #QtCore.QTimer.singleShot(0, self.vid_button_2.setFocus) # works!!!
        #self.vid_button_2.setFocus() ## doesn't work!!
        #print("pressing button automatically")
        #time.sleep(10)
        #self.vid_button_2.click() # works!!!
        print("pressed settings button")
        
    def keyPressEvent(self, e):
        print("key pressed = ", e.key())
        if e.key() == Qt.Key_Up:
            print("up button pressed")
            self.button_control("up")
        elif e.key() == Qt.Key_Down:
            print("down button pressed")
            self.button_control("down")
        elif e.key() == Qt.Key_Left:
            print("left button pressed")
            self.button_control("left")
        elif e.key() == Qt.Key_Right:
            print("right button pressed")
            self.button_control("right")
        elif e.key() == Qt.Key_Enter:
            print("enter button pressed") #not working need to use return on windows laptop keyboard
            self.button_control("enter")
            #self.button_ids[self.button_navigator].click() 
        elif e.key() == Qt.Key_Return:
            print("enter/return button pressed")
            self.button_control("return")
            #self.button_ids[self.button_navigator].click() 
        elif e.key() == Qt.Key_Escape:
            print("exit button pressed")
            self.close()
            
    def button_control(self, command):
        
        print("changing button function")
        old_num = self.button_navigator
        
        if command in ['up', 'down', 'right', 'left']:
              
            if command =='up':
                if self.button_navigator == len(self.button_ids) -2:
                    self.button_navigator = 0
                elif self.button_navigator == len(self.button_ids) -1:
                    self.button_navigator = 1
                else:
                    self.button_navigator = self.button_navigator + 2

            elif command == 'down':
                if self.button_navigator == 0 :
                    self.button_navigator = len(self.button_ids) - 2
                elif self.button_navigator == 1 :
                    self.button_navigator = len(self.button_ids) -1
                else:
                    self.button_navigator = self.button_navigator - 2

            elif command == 'right':
                if self.button_navigator == len(self.button_ids) -1:
                    self.button_navigator = 0 
                else:
                    self.button_navigator = self.button_navigator + 1 

            else: # direction == 'left':
                if self.button_navigator == 0:
                    self.button_navigator = len(self.button_ids) -1
                else:
                    self.button_navigator = self.button_navigator - 1  

            self.button_ids[self.button_navigator].setDefault(True) #test but set focus to button2

            self.button_ids[old_num].setDefault(False) #test but set focus to button2
            
        elif command == "enter":
            self.button_ids[self.button_navigator].click() 
            
        elif command in ["return", 'exit']:
            self.close()
               
if __name__ == "__main__":

    try:
        #-------initialise IR remote
        gpio_input = IR_reciever(ir_gpio, wait_time)  #initialte the function by inputting the input pin number and the wait time (longest time between individual pulses
        thread_flag_event = threading.Event() 
        thread_flag_event.set()
        thread = threading.Thread(target = gpio_input.wait_for_falling_edge) #place this into a thread so that it can run in parallel with the 
        thread.start() 

        #--------start pyqt5 app
        #windowsize = app.desktop().availableGeometry().size()
        
        app = QtWidgets.QApplication(sys.argv)
        locale.setlocale(locale.LC_NUMERIC, 'C') #needs to be after app is created
        main_window = MainWindow(gpio_input)
        main_window.show()
        print("running program press ctrl+c to stop")
        sys.exit(app.exec_())
                        
    
    except KeyboardInterrupt:
        thread_flag_event.clear() #tell the thread to shut down
        print("")
        print("program stopping") 
        GPIO.cleanup()
        
