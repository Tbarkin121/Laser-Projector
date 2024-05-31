# -*- coding: utf-8 -*-
"""
Created on Fri May 10 20:50:35 2024

@author: Plutonium
"""
from LaserCore import HeliosPoint, Frame, LaserCore
from LaserEffects import LaserEffect

class BouncingBallEffect(LaserEffect):
    def __init__(self, frame_size=1000):
        super().__init__(frame_size)
        self.position = 0
        self.velocity = 10
        self.direction = 1
        
        self.min_step_size = 5
        self.max_step_size = 100
        self.transition_length = 500
        self.blanking_points = 8
        self.starting_blanking_points = 20
        self.brightness_multiplier = 10


    def update_frame(self, frame, clear):
        if(clear):
            frame.clear()
        if self.position + self.velocity >= self.max_x or self.position + self.velocity <= 0:
            self.direction *= -1  # Reverse direction at boundaries
            self.velocity *= self.direction
        self.position += self.velocity
        # Update position based on possibly inverted velocity
        self.position = max(0, min(self.max_x, self.position))
        
        start_point = HeliosPoint(self.position, self.max_y // 2, 255, 0, 0, 0)
        end_point = HeliosPoint(self.position, self.max_y // 3, 255, 0, 0, 0)
        start_blank_point = HeliosPoint(self.position, self.max_y // 2, 0, 0, 0, 0)
        end_blank_point = HeliosPoint(self.position, self.max_y // 3, 0, 0, 0, 0)
        
        frame.move_head_to_point(start_blank_point, self.max_step_size)
        
        if(clear):
            for _ in range(self.starting_blanking_points):
                frame.add_point(start_blank_point)
                
        for _ in range(self.blanking_points):
            frame.add_point(start_blank_point)
        
        for _ in range(self.brightness_multiplier):
            frame.add_point(start_point)
    
        frame.add_line_smooth(start_point, end_point, (0,255,0,0), self.min_step_size, self.max_step_size, self.transition_length)
        
        for _ in range(self.blanking_points):
            frame.add_point(end_blank_point)
            
        for _ in range(self.brightness_multiplier):
            frame.add_point(end_point)
        
        for _ in range(self.blanking_points):
            frame.add_point(end_blank_point)

      
class BouncingBallEffect2(LaserEffect):
    def __init__(self, frame_size=1000):
        super().__init__(frame_size)
        self.position = 0
        self.velocity = 40
        self.direction = 1
        self.min_step_size = 5
        self.max_step_size = 100
        self.transition_length = 400
        self.blanking_points = 8
        self.starting_blanking_points = 20
        self.brightness_multiplier = 10
        
    def update_frame(self, frame, clear):
        if(clear):
            frame.clear()

            
        if self.position + self.velocity >= self.max_x or self.position + self.velocity <= 0:
            self.direction *= -1  # Reverse direction at boundaries
            self.velocity *= self.direction
        self.position += self.velocity
        # Update position based on possibly inverted velocity
        self.position = max(0, min(self.max_x, self.position))
        
        start_point = HeliosPoint(self.max_x // 2, self.position, 0, 0, 255, 0)
        end_point = HeliosPoint(self.max_x // 3, self.position, 0, 0, 255, 0)
        start_blank_point = HeliosPoint(self.max_y // 2, self.position, 0, 0, 0, 0)
        end_blank_point = HeliosPoint(self.max_y // 3, self.position, 0, 0, 0, 0)
        
        frame.move_head_to_point(start_blank_point, self.max_step_size)
        
        if(clear):
            for _ in range(self.starting_blanking_points):
                frame.add_point(start_blank_point)
                
        for _ in range(self.blanking_points):
            frame.add_point(start_blank_point)
            
        for _ in range(self.brightness_multiplier):
            frame.add_point(start_point)
        
        frame.add_line_smooth(start_point, end_point, (0,255,0,0), self.min_step_size, self.max_step_size, self.transition_length)
        
        for _ in range(self.blanking_points):
            frame.add_point(end_blank_point)
        
        for _ in range(self.brightness_multiplier):
            frame.add_point(end_point)

            
#%%
laser = LaserCore(".\\HeliosLaserDAC.dll", frame_size=2000)
effect = BouncingBallEffect()
effect2 = BouncingBallEffect2()
try:
    while True:
        for device_index in range(laser.num_devices):
            effect.update_frame(laser.frame, clear=True)
            # effect.apply_to_device(laser)
            effect2.update_frame(laser.frame, clear=False)
            # effect2.apply_to_device(laser)
            laser.write_frame(0, 30000, laser.frame.points, laser.frame.count)
        # time.sleep(1 / 30)  # 30 FPS
finally:
    laser.close()




