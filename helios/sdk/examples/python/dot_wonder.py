# -*- coding: utf-8 -*-
"""
Example for using Helios DAC libraries in python (using C library with ctypes)
for simulating a random walk with N points and precomputing frames with unconnected points
"""

import ctypes
import numpy as np
import random
import time

# Define point structure
class HeliosPoint(ctypes.Structure):
    _fields_ = [('x', ctypes.c_uint16),
                ('y', ctypes.c_uint16),
                ('r', ctypes.c_uint8),
                ('g', ctypes.c_uint8),
                ('b', ctypes.c_uint8),
                ('i', ctypes.c_uint8)]

# Load and initialize library
HeliosLib = ctypes.cdll.LoadLibrary(".\\HeliosLaserDAC.dll")
numDevices = HeliosLib.OpenDevices()
print("Found ", numDevices, "Helios DACs")

# Constants
NUM_POINTS = 2  # Number of points to track
NUM_POINTS_FRAME = NUM_POINTS * 2  # Actual points and blank points
MAX_X = 0xFFF    # Maximum x-coordinate
MAX_Y = 0xFFF    # Maximum y-coordinate
FRAME_RATE = 100
TOTAL_FRAMES = 10000  # Total number of frames to precompute

# Initialize frame buffer
frameType = HeliosPoint * NUM_POINTS_FRAME
frames = [frameType() for _ in range(TOTAL_FRAMES)]

# Initialize points
points = [(random.randint(0, MAX_X), random.randint(0, MAX_Y)) for _ in range(NUM_POINTS)]
colors = [(random.randint(0, 1)*255, random.randint(0, 1)*255, random.randint(0, 1)*255) for _ in range(NUM_POINTS)]

# Function to update points
def update_points():
    for index, (x, y) in enumerate(points):
        rand_x = random.randint(-250, 250)
        rand_y = random.randint(-250, 250)
        new_x = max(0, min(MAX_X, x + rand_x))
        new_y = max(0, min(MAX_Y, y + rand_y))
        points[index] = (new_x, new_y)

# Precompute all frames
for i in range(TOTAL_FRAMES):
    update_points()
    for j, ((x, y), (r, g, b)) in enumerate(zip(points, colors)):
        # Set the actual point
        frames[i][2*j] = HeliosPoint(x, y, r, g, b, 255)
        # Set the blank point
        frames[i][2*j+1] = HeliosPoint(x, y, 0, 0, 0, 0)  # Black point to disconnect

# Play frames on DAC
for i in range(TOTAL_FRAMES):
    for j in range(numDevices):
        for k in range(NUM_POINTS_FRAME):  # Ensure you loop through all points including blank ones
            statusAttempts = 0
            while (statusAttempts < 512 and HeliosLib.GetStatus(j) != 1):
                statusAttempts += 1
            HeliosLib.WriteFrame(j, FRAME_RATE, 0b10, ctypes.pointer(frames[i % TOTAL_FRAMES][k]), 1)  # Send the frame

HeliosLib.CloseDevices()



#%%
HeliosLib.CloseDevices()
