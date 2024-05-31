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
NUM_POINTS = 5  # Number of main points
MAX_STEP_SIZE = 40  # Maximum distance allowed between points
FRAME_RATE = 30000
MAX_X = 0xFFF
MAX_Y = 0xFFF
BRIGHTNESS_MULTIPLIER = 10  # Number of times to repeat each main point for increased brightness
BLANKING_FRAMES = 5
START_BLANKING_FRAMES = 10

# Initialize velocities and main points with random positions and velocities
main_points = [{
    'pos': (random.randint(0, MAX_X), random.randint(0, MAX_Y)),
    'vel': (random.randint(-80, 80), random.randint(-80, 80)),
    'color': (255,255,255)
} for _ in range(NUM_POINTS)]

# Append the first point to the end to close the loop
# main_points[0]['color'] = (255,0,0)
# main_points[1]['color'] = (0,255,0)
# main_points[2]['color'] = (0,0,255)
# main_points[3]['color'] = (255,255,0)
# main_points[4]['color'] = (0,255,255)

# main_points[0]['pos'] = (0xFF,0xFF)
# main_points[1]['pos'] = (0x5FF,0xFF)
# main_points[2]['pos'] = (0x5FF,0x5FF)
# main_points[3]['pos'] = (0xFF,0x5FF)
# main_points[4]['pos'] = (0xFFF,0xFFF)

main_points.append(main_points[0].copy())  # Make a copy to avoid issues with mutable dictionaries

NUM_POINTS = NUM_POINTS+1

# Initialize frame buffer
frameType = HeliosPoint * (400 * NUM_POINTS)  # Large enough buffer for interpolated points
frame = frameType()


def interpolate_points(start, end):
    """ Interpolates points between start and end if distance is greater than MAX_STEP_SIZE """
    points = []
    dx, dy = end[0] - start[0], end[1] - start[1]
    distance = math.sqrt(dx**2 + dy**2)
    if distance > MAX_STEP_SIZE:
        num_steps = int(distance / MAX_STEP_SIZE)
        for step in range(1, num_steps + 1):
            fraction = step / num_steps
            intermediate_x = round(start[0] + fraction * dx)
            intermediate_y = round(start[1] + fraction * dy)
            points.append((intermediate_x, intermediate_y))
    return points

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

for _ in range(10000):
    point_index = 0
    
    for _ in range(START_BLANKING_FRAMES):
       frame[point_index] = HeliosPoint(*main_points[0]['pos'], 0, 0, 0, 0)  # Position at start, but laser off
       point_index += 1
       
    for i in range(NUM_POINTS - 1):
        start = main_points[i]['pos']
        end = main_points[i + 1]['pos']
        color = main_points[i]['color']
        
        # Insert blanking points before the start point
        for _ in range(BLANKING_FRAMES):
           frame[point_index] = HeliosPoint(*start, 0, 0, 0, 0)  # Position at start, but laser off
           point_index += 1
        # Repeat start point for increased brightness
        for _ in range(BRIGHTNESS_MULTIPLIER):
            frame[point_index] = HeliosPoint(*start, *color, 255)
            point_index += 1

        # Calculate path with interpolated points (laser off)
        interpolated_points = interpolate_points(start, end)
        for x, y in interpolated_points:
            frame[point_index] = HeliosPoint(x, y, 255, 0, 255, 0)
            point_index += 1
            
    # Insert blanking points before the last main point
    last_point = main_points[-1]['pos']
    last_color = main_points[-1]['color']
    for _ in range(BLANKING_FRAMES):
        frame[point_index] = HeliosPoint(*last_point, 0, 0, 0, 0)  # Position at last point, but laser off
        point_index += 1
        
    # Repeat end point of the last segment for increased brightness
    for _ in range(BRIGHTNESS_MULTIPLIER):
        frame[point_index] = HeliosPoint(*last_point, *last_color, 255)
        point_index += 1

    # Send the current frame to DAC
    for device_index in range(numDevices):
        while HeliosLib.GetStatus(device_index) != 1:
            pass  # Wait for DAC to be ready
        HeliosLib.WriteFrame(device_index, FRAME_RATE, 0, ctypes.pointer(frame), point_index + 1)

    # Update points for next frame
    for point in main_points:
        update_points(point)
        pass

    time.sleep(1.0 / FRAME_RATE)  # Sleep to maintain approximate frame rate

HeliosLib.CloseDevices()

#%%
HeliosLib.CloseDevices()

#%%

for i in range(10):
    print(frames[i][0].x)
    
