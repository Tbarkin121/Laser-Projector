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


class DynamicCircleEffect(LaserEffect):
    def __init__(self, initial_x, initial_y, radius, num_points=100, point_color=(255, 0, 0, 0), line_color=(0,0,0,0), spring_constant=0.001, damping=0.01, point_brightness=1, blanking_points=1, target_x=0x7FF, target_y=0x7FF, max_x=0xFFF, max_y=0xFFF):
        super().__init__(frame_size=1000, 
                            min_step=10, 
                            max_step=200, 
                            trans_len=600, 
                            blanking_points=blanking_points, 
                            start_blanking_points=30, 
                            brightness_multiplier=point_brightness, 
                            max_x=0xFFF,  # Up to 0xFFF
                            max_y=0xFFF)
                        
        self.center_x = initial_x
        self.center_y = initial_y
        self.radius = radius
        self.num_points = num_points
        self.point_color = point_color
        self.line_color = line_color
        self.spring_constant = spring_constant
        self.damping = damping
        self.target_x = target_x
        self.target_y = target_y
        self.velocity_x = 10
        self.velocity_y = 10
        self.circle_entry_angle = 0
        self.circle_entry_rate = 0.001
    
    def update_target_position(self, new_x, new_y):
        self.target_x = new_x
        self.target_y = new_y
    
    def update_center_position(self):
        # Calculate the spring force
        force_x = -self.spring_constant * (self.center_x - self.target_x)
        force_y = -self.spring_constant * (self.center_y - self.target_y)

        # Update velocities
        self.velocity_x += force_x
        self.velocity_y += force_y

        # Apply damping
        self.velocity_x *= (1 - self.damping)
        self.velocity_y *= (1 - self.damping)

        # Update positions
        self.center_x += self.velocity_x
        self.center_y += self.velocity_y

        # Check for boundary collision and reflect if needed
        if self.center_x <= 0 or self.center_x >= self.max_x:
            self.velocity_x = -self.velocity_x
            self.center_x = max(0, min(self.max_x, int(self.center_x)))

        if self.center_y <= 0 or self.center_y >= self.max_y:
            self.velocity_y = -self.velocity_y
            self.center_y = max(0, min(self.max_y, int(self.center_y)))
            
        
    def update_circle(self):
        self.points = []
        for i in range(self.num_points):
            angle = self.circle_entry_angle + ( 2 * math.pi * i) / self.num_points
            self.circle_entry_angle += self.circle_entry_rate
            x = int(self.center_x + self.radius * math.cos(angle))
            y = int(self.center_y + self.radius * math.sin(angle))
            x = max(0, min(self.max_x, x))
            y = max(0, min(self.max_y, y))
            self.points.append({'pos': (x, y), 'color': self.point_color})

    def update_frame(self, frame, clear):
        if clear:
            frame.clear()
        
        start_blank_point = HeliosPoint(self.points[0]['pos'][0], self.points[0]['pos'][1], 0, 0, 0)
        frame.move_head_to_point(start_blank_point, self.min_step_size)
        
        
        for _ in range(self.starting_blanking_points):
            frame.add_point(start_blank_point)
            
        for i in range(self.num_points+1): #+1 for wrap around
            
            current_point = self.points[i % self.num_points]
            next_point = self.points[(i + 1) % self.num_points]  # wrap around to the start
            start_point = HeliosPoint(current_point['pos'][0], current_point['pos'][1], self.point_color[0], self.point_color[1], self.point_color[2])
            end_point = HeliosPoint(next_point['pos'][0], next_point['pos'][1], self.line_color[0], self.line_color[1], self.line_color[2])
            start_blank_point = HeliosPoint(current_point['pos'][0], current_point['pos'][1], 0, 0, 0)
            end_blank_point = HeliosPoint(next_point['pos'][0], next_point['pos'][1], 0, 0, 0)
            
            
            for _ in range(self.blanking_points):
                frame.add_point(start_blank_point)
            
            for _ in range(self.brightness_multiplier):
                frame.add_point(start_point)
                
            frame.add_line_smooth(start_point, end_point, color=self.line_color, min_step_size=self.min_step_size, max_step_size=self.max_step_size, transition_length=self.transition_length)
            
            for _ in range(self.blanking_points):
                frame.add_point(end_blank_point)
                
                
        # for _ in range(self.starting_blanking_points):
        #     frame.add_point(end_blank_point)
                
    
                
        
            
       

            
            
#%%
laser = LaserCore(".\\HeliosLaserDAC.dll", frame_size=10000)
dynamic_circle1 = DynamicCircleEffect(initial_x=0x7FF, initial_y=0x7FF, radius=1000, num_points=10, 
                                      point_color=(255, 255, 255, 0), line_color=(0,0,0,0), point_brightness=10, blanking_points=2,
                                      spring_constant=0.01, damping=0.05)

dynamic_circle2 = DynamicCircleEffect(initial_x=0x7FF, initial_y=0x7FF, radius=750, num_points=10, 
                                      point_color=(0, 255, 0, 0), line_color=(0,0,255,0), point_brightness=1, blanking_points=0,
                                      spring_constant=0.01, damping=0.05)

dynamic_circle3 = DynamicCircleEffect(initial_x=0x7FF, initial_y=0x7FF, radius=500, num_points=10, 
                                      point_color=(0, 0, 255, 0), line_color=(255,0,0,0), point_brightness=1, blanking_points=0,
                                      spring_constant=0.1, damping=0.05)
# Update the target position here
dynamic_circle1.update_target_position(random.randint(0, 0xFFF), random.randint(0, 0xFFF))
dynamic_circle2.update_target_position(random.randint(0, 0xFFF), random.randint(0, 0xFFF))
dynamic_circle3.update_target_position(random.randint(0, 0xFFF), random.randint(0, 0xFFF))


try:
    loop_count = 0
    while True:
        start_time = time.perf_counter()
        for device_index in range(laser.num_devices):
            if(loop_count % 100 == 0):
                dynamic_circle1.update_target_position(random.randint(0, 0xFFF), random.randint(0, 0xFFF))
                dynamic_circle2.update_target_position(random.randint(0, 0xFFF), random.randint(0, 0xFFF))
                dynamic_circle3.update_target_position(random.randint(0, 0xFFF), random.randint(0, 0xFFF))
            loop_count += 1
                
            dynamic_circle1.update_center_position()
            dynamic_circle1.update_circle()
            dynamic_circle1.update_frame(laser.frame, clear=True)
            
            # dynamic_circle2.update_center_position()
            # dynamic_circle2.update_circle()
            # dynamic_circle2.update_frame(laser.frame, clear=False)
            
            # dynamic_circle3.update_center_position()
            # dynamic_circle3.update_circle()
            # dynamic_circle3.update_frame(laser.frame, clear=False)
            
            laser.write_frame(0, 30000, laser.frame.points, laser.frame.count)
            dt = time.perf_counter() - start_time
            print(f'fps = {1/dt}, pt_count = {laser.frame.count}')
            
        # time.sleep(1 / 30)  # 30 FPS
finally:
    laser.close()



