# -*- coding: utf-8 -*-
"""
Created on Wed May  1 01:00:33 2024

@author: Plutonium
"""

# -*- coding: utf-8 -*-
"""
Example for using Helios DAC libraries in python (using C library with ctypes)
"""

import ctypes
import numpy as np

MAX_X = 0xFFF    # Maximum x-coordinate
MAX_Y = 0xFFF    # Maximum y-coordinate

#Define point structure
class HeliosPoint(ctypes.Structure): 
    #_pack_=1
    _fields_ = [('x', ctypes.c_uint16),
                ('y', ctypes.c_uint16),
                ('r', ctypes.c_uint8),
                ('g', ctypes.c_uint8),
                ('b', ctypes.c_uint8),
                ('i', ctypes.c_uint8)]

#Load and initialize library
HeliosLib = ctypes.cdll.LoadLibrary(".\HeliosLaserDAC.dll")
numDevices = HeliosLib.OpenDevices()
print("Found ", numDevices, "Helios DACs")

#Create sample frames
frames = [0 for x in range(30)]
frameType = HeliosPoint * 1000

x = 0
y = 0
r_val = 0
g_val = 0
b_val = 0
angle_val = 0
angle_inc = 2*np.pi/30
for i in range(30):
    y = round(i * 0xFFF / 30)
    frames[i] = frameType()
    r_val = int(255*(np.cos(angle_val)/2+0.5))
    g_val = int(255*(np.cos(angle_val+(2*np.pi/3))/2+0.5))
    b_val = int(255*(np.cos(angle_val+(4*np.pi/3))/2+0.5))
    angle_val += angle_inc
    for j in range(500):
        if (j < 500):
            x = round(j * 0xFFF / 500)
        else:
            x = round(0xFFF - ((j - 500) * 0xFFF / 500))
        
        y_adjust = int(np.cos(j * 2 * np.pi / 100)*500)
        y_new = max(0, min(MAX_Y, y + y_adjust))
        
        x_adjust = int(np.cos(j * 2 * np.pi / 25)*250)
        x_new = max(0, min(MAX_Y, x + x_adjust))
        
        frames[i][j] = HeliosPoint(x_new,y_new,r_val,g_val,b_val,130)
        
        print(r_val)
        print(g_val)
        print(b_val)
        print('---')

#Play frames on DAC
for i in range(1500):
    for j in range(numDevices):
        statusAttempts = 0
        # Make 512 attempts for DAC status to be ready. After that, just give up and try to write the frame anyway
        while (statusAttempts < 512 and HeliosLib.GetStatus(j) != 1):
            statusAttempts += 1
        HeliosLib.WriteFrame(j, 20000, 0, ctypes.pointer(frames[i % 30]), 500) #Send the frame


HeliosLib.CloseDevices()

#%%

HeliosLib.CloseDevices()