# -*- coding: utf-8 -*-
"""
Example for using Helios DAC libraries in python (using C library with ctypes)
for dynamic real-time drawing with particle simulation.
"""

import ctypes
import random
import math
import time
import pyaudio
import numpy as np

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
NUM_POINTS = 128  # Number of main points
MAX_STEP_SIZE = 50  # Maximum distance allowed between points
FRAME_RATE = 40000
MAX_X = 0xFFF
MAX_Y = 0xFFF
BRIGHTNESS_MULTIPLIER = 1  # Number of times to repeat each main point for increased brightness
BLANKING_FRAMES = 1
START_BLANKING_FRAMES = 1

main_points = [{
    'pos': (i * MAX_X // (NUM_POINTS - 1), MAX_Y // 2),
    'vel': (random.randint(-80, 80), 0),  # Set vertical velocity to 0 if not needed
    'color': (255,255,255)
} for i in range(NUM_POINTS)]

# An extra point for wrapping around to close the shape
main_points.append(main_points[0].copy())  # Make a copy to avoid issues with mutable dictionaries
NUM_POINTS = NUM_POINTS+1


# Constants
FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1  # Mono audio
# RATE = 44100  # Sample rate
RATE = 96000  # Sample rate
CHUNK = 1024*4  # Number of audio samples per frame
N_BUCKETS = 1024  # Number of frequency buckets

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)


print("Streaming started")

#%%


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

def update_points(point, energy_level):    
    Y_FLOOR = 0x400
    decay_factor = 0.25
    target = int(np.sqrt(energy_level*100))
    
    x, y = point['pos']
    x_new = x
   
    
    
    if( target > y):
        y_new = target
    else:
        y_new = int(y - decay_factor * (y-Y_FLOOR))
        y_new = max(y_new, Y_FLOOR)

    # Update position based on possibly inverted velocity
    x_new = max(0, min(MAX_X, x_new))
    y_new = max(0, min(MAX_Y, y_new))

    point['pos'] = (x_new, y_new)


for _ in range(10000):
    point_index = 0
    start_t = time.perf_counter()
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
            if(i !=(NUM_POINTS-2) ):
                frame[point_index] = HeliosPoint(x, y, 255, 0, 255, 0)
            else:
                frame[point_index] = HeliosPoint(x, y, 0, 0, 0, 0)
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
    
    data = stream.read(CHUNK, exception_on_overflow=False)
    audio_data = np.frombuffer(data, dtype=np.int16)
    fft_data = np.fft.fft(audio_data)
    freqs = np.fft.fftfreq(len(fft_data), 1 / RATE)
    # y_data = 2 / CHUNK * np.abs(fft_data[0:CHUNK // 2])
    mag = np.abs(fft_data)**2 / (CHUNK**2)
     
    bucket_width = len(freqs) // 2 // N_BUCKETS
    energy_buckets = np.array([np.sum(mag[i*bucket_width:(i+1)*bucket_width]) for i in range(NUM_POINTS)]) 
    
    i = 0    
    for point in main_points:
        update_points(point, int(energy_buckets[i]))
        i = (i + 1) % (NUM_POINTS-1) # Hacky for now... i know. its to deal with the point wrap on the closed shapes
 
    time_diff =  time.perf_counter()-start_t
    print(f'{1/time_diff} Hz, pt_count = {point_index+1}')
     # time.sleep(1.0 / FRAME_RATE)  # Sleep to maintain approximate frame rate

HeliosLib.CloseDevices()

#%%
HeliosLib.CloseDevices()

#%%

for i in range(10):
    print(frames[i][0].x)
    
