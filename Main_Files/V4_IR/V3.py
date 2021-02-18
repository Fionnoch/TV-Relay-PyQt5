# feature test using threads and thread events rather than gpio.event
# WORKS!!!
# Using queue to communicate which page the user is currently on (relevant as commands are in different classes)
##
# V1 - a window with a button which opens up another window with a video playing 
# V2 - the basic interface works with buttons which link to video streams
#    - way found to change button focus
# V3 - added keyboard navigation
# V4 - need to create IR interface - Opi-gpio
# V4-ir - IR Commands feature tests only 
# V5 - need ip connection - 
# V6 - need to add style (stylesheets)

import OPi.GPIO as GPIO
from time import sleep
from time import perf_counter
import threading
import numpy
from queue import Queue

LED_gpio = 7 # pin name = PA6 wPi = 2 GPIO = 6 
ir_gpio = 5 # pin name = SCL.0 wPi = 1 GPIO = 11

GPIO.setmode(GPIO.BOARD)  # set up BOARD BCM SUNXI numbering
#GPIO.setup(LED_gpio, GPIO.OUT)    # set pin as an output (LED)

GPIO.setup(ir_gpio, GPIO.IN)

# ===================================================================================================
# IR controls

#wait_time = 4523982e-9 * 1.5 # 60e-3 # in seconds should be just higher than the longest wait. think longest is about 5ms. noted from looking theough sky remote commands
wait_time = 6e-3 # in seconds should be just higher than the longest wait. think longest is about 5ms. noted from looking theough sky remote commands

ir_keys_dict = { # in nanosecs
    'down' : numpy.array([0.004283, 0.004550, 0.000543, 0.001578, 0.000513, 0.001692, 0.000649, 0.001594, 0.000513, 0.000588, 0.000662, 0.000485, 0.000484, 0.000617, 0.000567, 0.000519, 0.000568, 0.000509, 0.000566, 0.001751, 0.000541, 0.001657, 0.000485, 0.001736, 0.000489, 0.000604, 0.000567, 0.000562, 0.000499, 0.000485, 0.000729, 0.000488, 0.000497, 0.000496, 0.000638, 0.001626, 0.000650, 0.000479, 0.000497, 0.000642, 0.000564, 0.000503, 0.000561, 0.000659, 0.000485, 0.001689, 0.000498, 0.001710, 0.000598, 0.000490, 0.000561, 0.000511, 0.000643, 0.001634, 0.000573, 0.001625, 0.000628, 0.001652, 0.000480, 0.001717, 0.000618, 0.000522, 0.000665, 0.000479, 0.000477, 0.001691, 0.000502]), 
    'up' :   numpy.array([0.004288, 0.004426, 0.000647, 0.001535, 0.000654, 0.001583, 0.000607, 0.001568, 0.000646, 0.000572, 0.000502, 0.000524, 0.000615, 0.000494, 0.000654, 0.000489, 0.000597, 0.000466, 0.000613, 0.001711, 0.000514, 0.001665, 0.000554, 0.001641, 0.000568, 0.000521, 0.000586, 0.000543, 0.000509, 0.000579, 0.000655, 0.000484, 0.000583, 0.000415, 0.000721, 0.000511, 0.000581, 0.000489, 0.000569, 0.000487, 0.000673, 0.000543, 0.000506, 0.000489, 0.000644, 0.001623, 0.000598, 0.001611, 0.000504, 0.000730, 0.000498, 0.001597, 0.000655, 0.001596, 0.000595, 0.001588, 0.000651, 0.001574, 0.000528, 0.001732, 0.000564, 0.000562, 0.000509, 0.000509, 0.000670, 0.001537, 0.000645]), 
    'right': numpy.array([0.004273, 0.004527, 0.000435, 0.001788, 0.000553, 0.001568, 0.000650, 0.001661, 0.000498, 0.000498, 0.000651, 0.000486, 0.000564, 0.000620, 0.000599, 0.000496, 0.000490, 0.000487, 0.000694, 0.001671, 0.000442, 0.001704, 0.000644, 0.001608, 0.000577, 0.000570, 0.000493, 0.000566, 0.000567, 0.000518, 0.000588, 0.000491, 0.000646, 0.000565, 0.000484, 0.000487, 0.000733, 0.001488, 0.000646, 0.000484, 0.000565, 0.000604, 0.000535, 0.000579, 0.000566, 0.001605, 0.000673, 0.001552, 0.000568, 0.000566, 0.000565, 0.001646, 0.000566, 0.000483, 0.000644, 0.001573, 0.000752, 0.001458, 0.000726, 0.001658, 0.000499, 0.000496, 0.000647, 0.000484, 0.000565, 0.001636, 0.000581]), 
    'left' : numpy.array([0.004381, 0.004456, 0.000502, 0.001620, 0.000570, 0.001685, 0.000605, 0.001628, 0.000533, 0.000601, 0.000520, 0.000524, 0.000587, 0.000568, 0.000491, 0.000566, 0.000607, 0.000514, 0.000587, 0.001682, 0.000514, 0.001677, 0.000520, 0.001691, 0.000519, 0.000582, 0.000586, 0.000590, 0.000493, 0.000486, 0.000649, 0.000579, 0.000502, 0.000519, 0.000509, 0.001704, 0.000591, 0.000488, 0.000716, 0.001613, 0.000573, 0.000520, 0.000520, 0.000603, 0.000497, 0.001645, 0.000623, 0.001688, 0.000506, 0.000489, 0.000567, 0.000643, 0.000523, 0.001666, 0.000576, 0.000491, 0.000567, 0.001599, 0.000679, 0.001665, 0.000439, 0.000667, 0.000509, 0.000504, 0.000581, 0.001731, 0.000496]),
    'exit':  numpy.array([0.004383, 0.004593, 0.000486, 0.001635, 0.000487, 0.001646, 0.000673, 0.001685, 0.000485, 0.000515, 0.000626, 0.000412, 0.000731, 0.000481, 0.000486, 0.000638, 0.000596, 0.000499, 0.000509, 0.001728, 0.000500, 0.001665, 0.000569, 0.001675, 0.000502, 0.000604, 0.000670, 0.000485, 0.000487, 0.000664, 0.000557, 0.000446, 0.000531, 0.000612, 0.000504, 0.001715, 0.000587, 0.000544, 0.000524, 0.001671, 0.000637, 0.001564, 0.000644, 0.000514, 0.000428, 0.001779, 0.000538, 0.000513, 0.000650, 0.000484, 0.000484, 0.000560, 0.000654, 0.001689, 0.000547, 0.000430, 0.000743, 0.000507, 0.000501, 0.001644, 0.000584, 0.000485, 0.000570, 0.001711, 0.000567, 0.001685, 0.000510]),
    'enter' :numpy.array([0.004291, 0.004423, 0.000652, 0.001543, 0.000591, 0.001699, 0.000569, 0.001668, 0.000520, 0.000576, 0.000595, 0.000495, 0.000564, 0.000558, 0.000560, 0.000516, 0.000576, 0.000595, 0.000486, 0.001727, 0.000540, 0.001636, 0.000485, 0.001676, 0.000745, 0.000482, 0.000500, 0.000482, 0.000721, 0.000482, 0.000479, 0.000599, 0.000569, 0.000589, 0.000486, 0.000560, 0.000565, 0.000638, 0.000545, 0.000414, 0.000747, 0.001520, 0.000632, 0.000519, 0.000490, 0.001703, 0.000643, 0.001622, 0.000498, 0.000650, 0.000562, 0.001622, 0.000601, 0.001602, 0.000567, 0.001720, 0.000485, 0.000507, 0.000566, 0.001676, 0.000678, 0.000532, 0.000511, 0.000490, 0.000645, 0.001650, 0.000573]), 
    'return':numpy.array([0.004415, 0.004415, 0.000515, 0.001658, 0.000700, 0.001538, 0.000517, 0.001694, 0.000580, 0.000528, 0.000570, 0.000516, 0.000569, 0.000560, 0.000482, 0.000662, 0.000592, 0.000494, 0.000583, 0.001670, 0.000505, 0.001686, 0.000589, 0.001619, 0.000646, 0.000419, 0.000578, 0.000511, 0.000570, 0.000564, 0.000538, 0.000598, 0.000591, 0.000490, 0.000585, 0.000569, 0.000486, 0.000565, 0.000670, 0.000511, 0.000574, 0.001635, 0.000483, 0.001727, 0.000590, 0.000491, 0.000645, 0.001560, 0.000591, 0.000578, 0.000500, 0.001681, 0.000608, 0.001649, 0.000492, 0.001758, 0.000523, 0.000494, 0.000668, 0.000491, 0.000482, 0.001730, 0.000489, 0.000503, 0.000732, 0.001629, 0.000505])
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

    def change_screen(self, message): 
        self.q.put(message)

    def wait_for_falling_edge(self):

        while thread_flag_event.is_set() : #uses threading event to dictate when the loop should be killed
            if GPIO.input(ir_gpio) == 0:
                self.read_command(0)
                
            if self.q.full():
                print("queue message detected the message was:")
                mesg = self.q.get()
                #print(mesg)
                if mesg == 'main screen':
                    print('main screen message detected ')
                elif mesg == 'menu screen':
                    print('menu screen message detected ')
                elif mesg == 'video screen':
                    print('video screen message detected ')
                
    def wait_for_rising_edge(self):
        while thread_flag_event.is_set() :
            if GPIO.input(ir_gpio) == 1:
                self.read_command(1)
            
    def stop_detection(self):
        self.run_in_background == False

    def read_command(self, start_val):
        print("input detected")
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
          
        if min(ir_keys_length.values()) == len_command:
            self.translate_command(command) #compare value
        
        #if min(ir_keys_length['down']) == len_command: #check if the lengths are the same, all the commands are the same 
        #    self.translate_command(command) #compare value

    def translate_command(self, command):
        np_command = numpy.asarray(command, dtype=numpy.float32) # dtype=numpy.uintc)
        #print("checking command translation ")
        #for i in ir_keys_dict: #scroll though the list >> just idea not finished
        #    if numpy.allclose(np_command, ir_keys_dict[i], rtol=1 , atol= ir_keys_tolerance_dict[i]): #checks if the arrays are the same within a tolerance
        #        #check what command the match worked with 
        #        #excecute the command
        #        #break for loop 
                
        if numpy.allclose(np_command, ir_keys_dict['up'], rtol=1 , atol= ir_keys_tolerance_dict['up']): #checks if the arrays are the same within a tolerance
            print("up button pressed")
            #self.screen_choice_class.navigation_control('up')
            #self.MainScreen_class.navigation_control('up')

        if numpy.allclose(np_command, ir_keys_dict['down'], rtol=1 , atol= ir_keys_tolerance_dict['down']): #down
            print('down remote button pressed')
            #self.screen_choice_class.navigation_control('down')   ####

        if numpy.allclose(np_command, ir_keys_dict['left'], rtol=1 , atol= ir_keys_tolerance_dict['left']):  #left
            print('left remote button pressed')
            #self.screen_choice_class.navigation_control('left')

        if numpy.allclose(np_command, ir_keys_dict['right'], rtol=1 , atol= ir_keys_tolerance_dict['right']): #right
            print('right remote button pressed')
            #self.screen_choice_class.navigation_control('right')

        if numpy.allclose(np_command, ir_keys_dict['enter'], rtol=1 , atol= ir_keys_tolerance_dict['enter']): #enter button
            print ("enter remote button pressed")
            #self.screen_choice_class.navigation_control('enter')

        if numpy.allclose(np_command, ir_keys_dict['return'], rtol=1 , atol= ir_keys_tolerance_dict['return']): #backup button not needed for main screen
            print ("backup remote button pressed")
            #self.screen_choice_class.navigation_control('return')

        if numpy.allclose(np_command, ir_keys_dict['exit'], rtol=1 , atol= ir_keys_tolerance_dict['exit']): #backup button not needed for main screen
            print ("exit button pressed")
            #self.screen_choice_class.navigation_control('exit')         
    

try:
    gpio_input = IR_reciever(ir_gpio, wait_time)  #initialte the function by inputting the input pin number and the wait time (longest time between individual pulses

    thread_flag_event = threading.Event() 
    thread_flag_event.set()
    thread = threading.Thread(target = gpio_input.wait_for_falling_edge) #place this into a thread so that it can run in parallel with the 
    thread.start() 
    
    test_number = 0
    print("running program press ctrl+c to stop")
    while 1:
        sleep(10)
        if test_number == 0:
            gpio_input.change_screen('main screen')
            test_number = test_number+1
        elif test_number == 1:
            gpio_input.change_screen('menu screen')
            test_number = test_number+1
        else:
            gpio_input.change_screen('video screen')
            test_number = 0
                    
 
except KeyboardInterrupt:
    thread_flag_event.clear() #tell the thread to shut down
    print("")
    print("program stopping") 
    GPIO.cleanup()
