#this is a feature test using only the gpio library
# issues with timing with the gpio add_event as such it wasn't used in future versions
#
##
# V1 - a window with a button which opens up another window with a video playing 
# V2 - the basic interface works with buttons which link to video streams
#    - way found to change button focus
# V3 - added keyboard navigation
# V4 - need to create IR interface - Opi-gpio
# V4-ir - IR Commands only 
# V5 - need ip connection - 
# V6 - need to add style (stylesheets)

import OPi.GPIO as GPIO
from time import sleep
from time import perf_counter

LED_gpio = 7 # pin name = PA6 wPi = 2 GPIO = 6 
ir_gpio = 5 # pin name = SCL.0 wPi = 1 GPIO = 11

#GPIO.setboard(GPIO.PCPCPLUS)
GPIO.setmode(GPIO.BOARD)  # set up BOARD BCM SUNXI numbering
#GPIO.setup(LED_gpio, GPIO.OUT)    # set pin as an output (LED)

GPIO.setup(ir_gpio, GPIO.IN)

wait_time = 4523982e-9 * 1.1 #60e-3 # in seconds should be just higher than the longest wait. think longest is about 5ms. noted from looking theough sky remote commands


def inputChange_rpi(channel):
    print("input detected")
    #GPIO.remove_event_detect(ir_gpio) #remove event detect so that it doesn't get called again
    command = []
    start_of_event = perf_counter()
    IR_timer = start_of_event + wait_time #make it extra long to stop the loop exiting premiturely. value will be reset inside loop
    
    previousValue = bool(0)
    
    while perf_counter() < IR_timer: #waits until a timer expires. the timer refers to the time after a command has not been passed. this is readjusted instide the code to make sure the entire command is captured
        print(GPIO.input(ir_gpio))
        if GPIO.input(ir_gpio) != previousValue:  # Waits until change in state occurs.
			# Records the current time              maybe change to just record microseconds
            end_of_event = perf_counter() #records the end time of a signal change. the first start_of_event is above the while loop so from here out we need to record just hte$
			# Calculate time in between pulses
            command_length = end_of_event - start_of_event
            #print(command_length)
            start_of_event = perf_counter() #Resets the start time

            command.append(command_length)

            IR_timer = perf_counter() + wait_time #resets counter

            # Reads values again
            #value = GPIO.input(ir_gpio) #reads new value
            previousValue = not previousValue #value #changes previous value to current value to see if there is a change
            
    #GPIO.add_event_detect(ir_gpio, GPIO.FALLING, callback = inputChange) #, bouncetime = 3)
    print("finished event detect, command recorded = ")
    print(command)

GPIO.add_event_detect(ir_gpio, GPIO.FALLING, callback = inputChange_rpi) #, bouncetime = 30)

try:
    print("running program press ctrl+c to stop")
    while 1:
        sleep(5)
        
except KeyboardInterrupt:
    print("")
    print("program stopping")
    #p.stop()
    #GPIO.output(LED_gpio, 0)  
    GPIO.cleanup()
