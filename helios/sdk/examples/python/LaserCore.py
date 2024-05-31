# -*- coding: utf-8 -*-
"""
Created on Thu May  9 20:57:18 2024

@author: Plutonium
"""


import ctypes
import random
import math
import time

#%%
class HeliosPoint(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_uint16),
        ('y', ctypes.c_uint16),
        ('r', ctypes.c_uint8),
        ('g', ctypes.c_uint8),
        ('b', ctypes.c_uint8),
        ('i', ctypes.c_uint8)  # Intensity
    ]

class Frame:
    def __init__(self, size=1000):
        self.points = (HeliosPoint * size)()  # Allocate space for points
        self.size = size                      # Max points a frame can contain
        self.count = 0                        # current frame point count

    # This should call add line if the previous point is greater than step size away
    # Maybe add repeat and blanking to the add point function
    
    def add_point(self, point):
        if self.count < self.size:                
            self.points[self.count] = point
            self.count += 1
        else:
            pass
            # print('Frame Point Capacity Reached')
            
    def add_line(self, start_point, end_point, color=(0,0,0,0), step_size=10):
        dx, dy = end_point.x - start_point.x, end_point.y - start_point.y
        distance = math.sqrt(dx**2 + dy**2)
        if distance > step_size:
            num_steps = int(distance / step_size)
            for step in range(1, num_steps + 1):
                fraction = step / num_steps
                intermediate_x = round(start_point.x + fraction * dx)
                intermediate_y = round(start_point.y + fraction * dy)
                
                intermediate_point = HeliosPoint(intermediate_x, intermediate_y, color[0], color[1], color[2], color[3])
                self.add_point(intermediate_point)
                

    def add_line_smooth(self, start_point, end_point, color=(0,0,0,0), min_step_size=1, max_step_size=50, transition_length=100, max_iterations=1000):
        """ Incrementally moves from start_point to end_point by step_size until close enough or max_iterations reached. """
        current_x, current_y = start_point.x, start_point.y
        dx, dy = end_point.x - start_point.x, end_point.y - start_point.y
        total_distance = math.sqrt(dx**2 + dy**2)
        iteration = 0
    
        while iteration < max_iterations:
                dist_to_end = math.sqrt((end_point.x - current_x)**2 + (end_point.y - current_y)**2)
                
                if dist_to_end < min_step_size:
                    break  # Close enough to target point
                
                # Calculate distance from the closest endpoint
                dist_from_start = math.sqrt((current_x - start_point.x)**2 + (current_y - start_point.y)**2)
                dist_to_closest_endpoint = min(dist_from_start, dist_to_end)
        
                # Determine step size based on the distance from the closest endpoint
                if dist_to_closest_endpoint < transition_length:
                    # Linear interpolation between min_step_size and max_step_size
                    step_size = min_step_size + (max_step_size - min_step_size) * (dist_to_closest_endpoint / transition_length)
                else:
                    step_size = max_step_size
                
                # print(step_size)
                # Update step direction
                step_x = dx / total_distance * step_size
                step_y = dy / total_distance * step_size
                
                # Move the point
                current_x += step_x
                current_y += step_y
        
                # Clip current_x and current_y to not exceed end_point
                if (step_x > 0 and current_x > end_point.x) or (step_x < 0 and current_x < end_point.x):
                    current_x = end_point.x
                if (step_y > 0 and current_y > end_point.y) or (step_y < 0 and current_y < end_point.y):
                    current_y = end_point.y
        
                intermediate_point = HeliosPoint(round(current_x), round(current_y), color[0], color[1], color[2], color[3])
                self.add_point(intermediate_point)
        
                iteration += 1
    
        # Add the final point to ensure the line reaches the end_point
        final_point = HeliosPoint(end_point.x, end_point.y, color[0], color[1], color[2], color[3])
        self.add_point(final_point)
                
    def move_head_to_point(self, point, min_step_size=10, max_step_size=50, transition_length=100):
        if(self.count > 0):
            self.add_line(self.points[self.count-1], point, (0,0,0,0), min_step_size)
            # self.add_line_smooth(self.points[self.count-1], point, (0,0,0,0), min_step_size=min_step_size, max_step_size=max_step_size, transition_length=transition_length)
        
            
            
    def clear(self):
        self.count = 0

    
            
class LaserCore:
    def __init__(self, dll_path, frame_size=1000):
        self.lib = ctypes.cdll.LoadLibrary(dll_path)
        self.num_devices = self.lib.OpenDevices()
        self.frame = Frame(frame_size)
        print("Found", self.num_devices, "Helios DACs")
    
    def write_frame(self, device_index, frame_rate, frame, point_count):
        while self.lib.GetStatus(device_index) != 1:
            pass
        self.lib.WriteFrame(device_index, frame_rate, 0, ctypes.pointer(frame), point_count)


    def close(self):
        self.lib.CloseDevices()



   
#%%


