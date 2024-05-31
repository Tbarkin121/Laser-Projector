# -*- coding: utf-8 -*-
"""
Example for using Helios DAC libraries in python (using C library with ctypes)
for drawing connected lines with maximum step size respected.
"""

import ctypes
import random
import math

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
NUM_POINTS = 10  # Define how many main points you want
MAX_STEP_SIZE = 50  # Maximum distance allowed between points
FRAME_RATE = 30000
TOTAL_FRAMES = 200  # Total number of frames to precompute
MAX_X = 0xFFF
MAX_Y = 0xFFF

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

# Initialize main points with random positions and random colors
# Initialize velocities and main points with random positions and velocities
main_points = [{
    'pos': (random.randint(0, MAX_X), random.randint(0, MAX_Y)),
    'vel': (random.randint(-100, 100), random.randint(-100, 100)),
    'color': (random.randint(0, 1)*255, random.randint(0, 1)*255, random.randint(0, 1)*255)
} for _ in range(NUM_POINTS)]

main_points[0]['color'] = (255,0,0)

# Initialize frame buffer
frameType = HeliosPoint * (75 * NUM_POINTS)  # Large enough buffer for interpolated points
frames = [frameType() for _ in range(TOTAL_FRAMES)]


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


def generate_path(frames):
    """ Generates the path including interpolated points """
    for frame_index in range(TOTAL_FRAMES):
        point_index = 0
        for i in range(NUM_POINTS - 1):
            start = main_points[i]['pos']
            end = main_points[i + 1]['pos']
            color = main_points[i]['color']
            # Print the current start position to debug
            # print(f"Frame {frame_index}, Point {point_index}: Start = {start}")
            # Start point (laser on)
            frames[frame_index][point_index] = HeliosPoint(*start, *color, 255)
            point_index += 1

            # Calculate path with interpolated points (laser off)
            interpolated_points = interpolate_points(start, end)
            for x, y in interpolated_points:
                frames[frame_index][point_index] = HeliosPoint(x, y, 0, 0, 0, 0)
                point_index += 1

        # End point of the last segment (laser on)
        last_point = main_points[-1]['pos']
        last_color = main_points[-1]['color']
        frames[frame_index][point_index] = HeliosPoint(*last_point, *last_color, 255)
        # print(f"Frame {frame_index}, Last Point: End = {last_point}")

        # Update points for next frame
        for point in main_points:
            update_points(point)

        # Optionally, reset the point index if using a static array size
        # This is crucial if your frame buffer size doesn't dynamically match the number of points
        point_index = 0  # Reset index if necessary, depending on buffer size handling
        
        print("{}, {}".format(frames[frame_index][0].x, frames[frame_index][0].y))

# Generate the path
generate_path(frames)

# Play frames on DAC
for frame in frames:
    for device_index in range(numDevices):
        while HeliosLib.GetStatus(device_index) != 1:
            pass  # Wait for DAC to be ready
        HeliosLib.WriteFrame(device_index, FRAME_RATE, 0, ctypes.pointer(frame), len(frame))
        # pass

HeliosLib.CloseDevices()

#%%

for i in range(200):
    print('---')
    for j in range(1):
        print("{}, {}, ({},{},{}) ".format(frames[i][j].x, frames[i][j].y, frames[i][j].r, frames[i][j].g, frames[i][j].b))
    
#%%

# for _ in range(10):
#     print('---')
#     for point in main_points:
#         update_points(point)        
#         print(point)
        
#%%
HeliosLib.CloseDevices()     
            
            