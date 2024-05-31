# -*- coding: utf-8 -*-
"""
Created on Fri May 10 20:52:34 2024

@author: Plutonium
"""
from LaserCore import HeliosPoint, Frame, LaserCore
from LaserEffects import LaserEffect

import numpy as np
import pyaudio
import random
import math
import time


class LineTravelEffect(LaserEffect):
    def __init__(self, line_length, vel_x, vel_y, point_color=(255, 255, 255, 0), line_color=(0,0,0,0), blanking_points=10, start_blanking_points=50, brightness_multiplier=0, max_x=0xFFF, max_y=0xFFF, edge_spawn=-1):
        
        super().__init__(frame_size=1000, min_step=10, max_step=50, trans_len=1000, 
                         blanking_points=blanking_points, 
                         start_blanking_points = start_blanking_points, 
                         brightness_multiplier=brightness_multiplier, 
                         max_x=max_x, max_y=max_y)
        
        self.line_length = line_length
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.point_color = point_color
        self.line_color = line_color
        self.edge_spawn = edge_spawn
        self.reset_line()
        
        
    def reset_line(self):
        # Roll a new starting point on the edge
        if(self.edge_spawn == -1):
            edge = random.randint(1, 4)
        else:
            edge = self.edge_spawn
        if edge == 1:  # Top edge
            self.start_x = random.randint(0, self.max_x)
            self.start_y = 0
        elif edge == 2:  # Bottom edge
            self.start_x = random.randint(0, self.max_x)
            self.start_y = self.max_y
        elif edge == 3:  # Left edge
            self.start_x = 0
            self.start_y = random.randint(0, self.max_y)
        else:  # Right edge
            self.start_x = self.max_x
            self.start_y = random.randint(0, self.max_y)

        self.current_x = self.start_x
        self.current_y = self.start_y

    def update_position(self):
        # Update line position
        self.current_x += self.vel_x
        self.current_y += self.vel_y
    
        # Expanded boundary conditions to allow the line to move completely off the screen
        if not (-self.line_length <= self.current_x <= self.max_x + self.line_length and -self.line_length <= self.current_y <= self.max_y + self.line_length):
            self.reset_line()  # Reset if the line has exited
            
            
    # def calculate_visible_segment(self, start_x, start_y, end_x, end_y):
    #     """Adjust the line endpoints to ensure they are within the screen boundaries."""
    #     # Create a lambda function to clamp values within the screen boundary
    #     clamp = lambda val, min_val, max_val: max(min(val, max_val), min_val)
    
    #     # Clamping the start and end points to the screen boundary
    #     visible_start_x = clamp(start_x, 0, self.max_x)
    #     visible_start_y = clamp(start_y, 0, self.max_y)
    #     visible_end_x = clamp(end_x, 0, self.max_x)
    #     visible_end_y = clamp(end_y, 0, self.max_y)
    
    #     return visible_start_x, visible_start_y, visible_end_x, visible_end_y
    
    def calculate_visible_segment(self, start_x, start_y, end_x, end_y):
        """Calculate intersections with screen boundaries to ensure the line stays within the view."""
        dx = end_x - start_x
        dy = end_y - start_y
        points = []
    
        # Functions to check if coordinates are within bounds
        within_x_bounds = lambda x: 0 <= x <= self.max_x
        within_y_bounds = lambda y: 0 <= y <= self.max_y
    
        # Check intersections with each boundary
        if dx != 0:
            # Intersection with left boundary (x=0)
            t = -start_x / dx
            y = start_y + t * dy
            if within_y_bounds(y) and 0 <= t <= 1:
                points.append((0, y))
            
            # Intersection with right boundary (x=max_x)
            t = (self.max_x - start_x) / dx
            y = start_y + t * dy
            if within_y_bounds(y) and 0 <= t <= 1:
                points.append((self.max_x, y))
    
        if dy != 0:
            # Intersection with top boundary (y=0)
            t = -start_y / dy
            x = start_x + t * dx
            if within_x_bounds(x) and 0 <= t <= 1:
                points.append((x, 0))
            
            # Intersection with bottom boundary (y=max_y)
            t = (self.max_y - start_y) / dy
            x = start_x + t * dx
            if within_x_bounds(x) and 0 <= t <= 1:
                points.append((x, self.max_y))
    
        # Include original points if they are within bounds
        if within_x_bounds(start_x) and within_y_bounds(start_y):
            points.append((start_x, start_y))
        if within_x_bounds(end_x) and within_y_bounds(end_y):
            points.append((end_x, end_y))
    
        # Select the two points that form the longest visible segment
        if len(points) >= 2:
            max_dist = 0
            best_pair = (start_x, start_y, end_x, end_y)
            for i in range(len(points)):
                for j in range(i + 1, len(points)):
                    px, py = points[i]
                    qx, qy = points[j]
                    dist = (px - qx) ** 2 + (py - qy) ** 2
                    if dist > max_dist:
                        max_dist = dist
                        best_pair = (px, py, qx, qy)
            return best_pair
        return start_x, start_y, end_x, end_y  # Return original line if no intersections are useful

    def update_frame(self, frame, clear=True):
        if clear:
            frame.clear()
        
        # Calculate the actual endpoint of the line
        end_x = int(self.current_x - self.line_length * math.cos(math.atan2(self.vel_y, self.vel_x)))
        end_y = int(self.current_y - self.line_length * math.sin(math.atan2(self.vel_y, self.vel_x)))
    
        # Adjust line endpoints to stay within the visible area
        visible_start_x, visible_start_y, visible_end_x, visible_end_y = self.calculate_visible_segment(self.current_x, self.current_y, end_x, end_y)
        
        visible_start_x = int(max(0, min(self.max_x, visible_start_x)))
        visible_start_y = int(max(0, min(self.max_y, visible_start_y)))
        visible_end_x = int(max(0, min(self.max_x, visible_end_x)))
        visible_end_y = int(max(0, min(self.max_y, visible_end_y)))
    
        start_point = HeliosPoint(visible_start_x, visible_start_y, self.point_color[0], self.point_color[1], self.point_color[2])
        end_point = HeliosPoint(visible_end_x, visible_end_y, self.line_color[0], self.line_color[1], self.line_color[2])
        
        
        
        # Initial blanking move to the start position
        start_blank_point = HeliosPoint(visible_start_x, visible_start_y, 0, 0, 0)
        frame.move_head_to_point(start_blank_point, self.max_step_size)
        
        for _ in range(self.starting_blanking_points):
            frame.add_point(start_blank_point)
        
        for _ in range(self.blanking_points):
            frame.add_point(start_blank_point)
        
        for _ in range(self.brightness_multiplier):
            frame.add_point(start_point)
            
        frame.add_line_smooth(start_point, end_point, color=self.line_color, min_step_size=self.min_step_size, max_step_size=self.max_step_size, transition_length=self.transition_length)
        
        # Adding a blanking point at the end of the line
        end_blank_point = HeliosPoint(visible_end_x, visible_end_y, 0, 0, 0)
        for _ in range(self.blanking_points):
            frame.add_point(end_blank_point)
            
            
            

    
                
        
            
       

            
            
#%%
laser = LaserCore(".\\HeliosLaserDAC.dll", frame_size=10000)

line_effect1 = LineTravelEffect(line_length=1000, vel_x=-100, vel_y=0, point_color=(255, 0, 0, 0), line_color=(255,0,0,0), blanking_points=10, start_blanking_points=50, brightness_multiplier=2, edge_spawn=0 )
line_effect2 = LineTravelEffect(line_length=2000, vel_x=-100, vel_y=0, point_color=(255, 0, 0, 0), line_color=(255,0,0,0), blanking_points=10, start_blanking_points=50, brightness_multiplier=2, edge_spawn=0 )
line_effect3 = LineTravelEffect(line_length=1000, vel_x=0, vel_y=100, point_color=(0, 0, 255, 0), line_color=(0,0,255,0), blanking_points=10, start_blanking_points=50, brightness_multiplier=2, edge_spawn=1 )
line_effect4 = LineTravelEffect(line_length=4000, vel_x=0, vel_y=100, point_color=(0, 0, 255, 0), line_color=(0,0,255,0), blanking_points=10, start_blanking_points=50, brightness_multiplier=2, edge_spawn=1 )
line_effect5 = LineTravelEffect(line_length=250, vel_x=100, vel_y=0, point_color=(0, 255, 0, 0), line_color=(0,255,0,0), blanking_points=10, start_blanking_points=50, brightness_multiplier=2, edge_spawn=3 )
line_effect6 = LineTravelEffect(line_length=500, vel_x=100, vel_y=0, point_color=(0, 255, 0, 0), line_color=(0,255,0,0), blanking_points=10, start_blanking_points=50, brightness_multiplier=2, edge_spawn=3 )
line_effect7 = LineTravelEffect(line_length=250, vel_x=0, vel_y=-100, point_color=(255, 0, 255, 0), line_color=(0, 0, 0, 0), blanking_points=10, start_blanking_points=50, brightness_multiplier=10, edge_spawn=2 )
line_effect8 = LineTravelEffect(line_length=500, vel_x=0, vel_y=-100, point_color=(255, 0, 255, 0), line_color=(0, 0, 0, 0), blanking_points=10, start_blanking_points=50, brightness_multiplier=10, edge_spawn=2 )

line_effect9 = LineTravelEffect(line_length=1000, vel_x=0, vel_y=100, point_color=(0, 0, 255, 0), line_color=(0,0,255,0), blanking_points=10, start_blanking_points=50, brightness_multiplier=2, edge_spawn=1 )
line_effect10 = LineTravelEffect(line_length=4000, vel_x=0, vel_y=100, point_color=(0, 0, 255, 0), line_color=(0,0,255,0), blanking_points=10, start_blanking_points=50, brightness_multiplier=2, edge_spawn=1 )
line_effect11 = LineTravelEffect(line_length=1000, vel_x=0, vel_y=100, point_color=(0, 0, 255, 0), line_color=(0,0,255,0), blanking_points=10, start_blanking_points=50, brightness_multiplier=2, edge_spawn=1 )
line_effect12 = LineTravelEffect(line_length=4000, vel_x=0, vel_y=100, point_color=(0, 0, 255, 0), line_color=(0,0,255,0), blanking_points=10, start_blanking_points=50, brightness_multiplier=2, edge_spawn=1 )


try:
    loop_count = 0
    while True:
        start_time = time.perf_counter()
        for device_index in range(laser.num_devices):
            # Then in your loop, update and draw:
            line_effect1.update_position()
            line_effect2.update_position()
            line_effect3.update_position()
            line_effect4.update_position()
            line_effect5.update_position()
            line_effect6.update_position()
            line_effect7.update_position()
            line_effect8.update_position()
            line_effect9.update_position()
            line_effect10.update_position()
            line_effect11.update_position()
            line_effect12.update_position()
            
            line_effect1.update_frame(laser.frame, clear=True)
            line_effect2.update_frame(laser.frame, clear=False)
            line_effect3.update_frame(laser.frame, clear=False)
            line_effect4.update_frame(laser.frame, clear=False)
            line_effect6.update_frame(laser.frame, clear=False)
            line_effect7.update_frame(laser.frame, clear=False)
            # line_effect11.update_frame(laser.frame, clear=False)
            # line_effect12.update_frame(laser.frame, clear=False)
            # line_effect5.update_frame(laser.frame, clear=False)
            # line_effect6.update_frame(laser.frame, clear=False)
            # line_effect7.update_frame(laser.frame, clear=False)
            # line_effect8.update_frame(laser.frame, clear=False)
            
            laser.write_frame(0, 30000, laser.frame.points, laser.frame.count)
            dt = time.perf_counter() - start_time
            print(f'fps = {1/dt}, pt_count = {laser.frame.count}')
            
        # time.sleep(1 / 30)  # 30 FPS
finally:
    laser.close()



