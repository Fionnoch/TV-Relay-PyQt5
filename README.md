# TV-Relay-PyQt5
This is a python video streaming program which runs on a cheap single board computer (developed primarily on the orange pi one) but which also uses the GPIO's to detect an IR remote in order to send the commands to another device which will relay them. 

The use case of this is that you have 1 satellite tv source which is broadcast over the local network using a video capture device. The singleboard computers can then be used anywhere in the house as if the satellite box was there. 

This is the 3rd itteration of this project. The first 2 utilised Kivy and Tkinter as the GUI however getting a media player to work through them caused major difficulties. As the goal is to use cheap single board computers performance and efficiency is very important and as such the aim is to not use a desktop enviorment only a CLI with potentially a window manager. 

After the other failed attempts I've learnt that MPV player is best suited for perfomance however it can be difficult to run in conjunction with another program or when not in a desktop enviornment. However it can tie in with pyqt5 quite nicely so the aim will be to use that as the gui
