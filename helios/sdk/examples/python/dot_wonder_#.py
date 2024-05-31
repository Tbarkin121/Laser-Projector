# -*- coding: utf-8 -*-
"""
Created on Sun May  5 02:36:08 2024

@author: Plutonium
"""

# -*- coding: utf-8 -*-
"""
Example for using Helios DAC libraries in python (using C library with ctypes)
for dynamic real-time drawing with particle simulation.
"""

import ctypes
import random
import math
import time

# Define point structure
class HeliosPoint(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_uint16),
        ('y', ctypes.c_uint16),
        ('r', ctypes.c_uint8),
        ('g', ctypes.c_uint8),
        ('b', ctypes.c_uint8),
        ('i', ctypes.c_uint8)  # Intensity of the laser
    ]

# Load and initialize library
HeliosLib = ctypes.cdll.LoadLibrary(".\\HeliosLaserDAC.dll")
numDevices = HeliosLib.OpenDevices()
print("Found", numDevices, "Helios DACs")

# Constants
NUM_POINTS = 2  # Number of main points
MAX_STEP_SIZE = 5  # Maximum distance allowed between points
FRAME_RATE = 30000
MAX_X = 0xFFF
MAX_Y = 0xFFF

# Initialize velocities and main points with random positions and velocities
main_points = [{
    'pos': (random.randint(0, MAX_X), random.randint(0, MAX_Y)),
    'vel': (random.randint(-10, 10), random.randint(-10, 10)),
    'color': (0, 0, 255)
} for _ in range(NUM_POINTS)]

# Initialize frame buffer
frameType = HeliosPoint * (500 * NUM_POINTS)  # Large enough buffer for interpolated points
frame = frameType()

def update_points(point):
    """ Updates the position of the point based on velocity and handles reflection at boundaries """
    x, y = point['pos']
    vx, vy = point['vel']
    x_new = x + vx
    y_new = y + vy

    # Reflect off boundaries
    if x_new < 0 or x_new > MAX_X:
        vx *= -1
    if y_new < 0 or y_new > MAX_Y:
        vy *= -1

    # Update position based on possibly inverted velocity
    x_new = max(0, min(MAX_X, x_new))
    y_new = max(0, min(MAX_Y, y_new))

    point['pos'] = (x_new, y_new)
    point['vel'] = (vx, vy)

while True:
    point_index = 0
    for i in range(NUM_POINTS - 1):
        start = main_points[i]['pos']
        end = main_points[i + 1]['pos']
        color = main_points[i]['color']
        # Start point (laser on)
        frame[point_index] = HeliosPoint(*start, *color, 255)
        point_index += 1

        # Calculate path with interpolated points (laser off)
        interpolated_points = interpolate_points(start, end)
        for x, y in interpolated_points:
            frame[point_index] = HeliosPoint(x, y, 0, 0, 0, 0)
            point_index += 1

    # End point of the last segment (laser on)
    frame[point_index] = HeliosPoint(*main_points[-1]['pos'], *main_points[-1]['color'], 255)

    # Send the current frame to DAC
    for device_index in range(numDevices):
        while HeliosLib.GetStatus(device_index) != 1:
            pass  # Wait for DAC to be ready
        HeliosLib.WriteFrame(device_index, FRAME_RATE, 0, ctypes.pointer(frame), point_index + 1)

    # Update points for next frame
    for point in main_points:
        update_points(point)

    time.sleep(1.0 / FRAME_RATE)  # Sleep to maintain approximate frame rate

HeliosLib.CloseDevices()
