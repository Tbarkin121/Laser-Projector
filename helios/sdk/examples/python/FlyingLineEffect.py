from LaserCore import HeliosPoint, Frame, LaserCore
from LaserEffects import LaserEffect

import numpy as np
import math
import time 

class MovingLinesEffect(LaserEffect):
    def __init__(self, frame_size=1000, num_lines=10, line_length=100, max_x=0xFFF, max_y=0xFFF, velocity=5):
        super().__init__(frame_size)
        self.num_lines = num_lines
        self.line_length = line_length
        self.max_x = max_x
        self.max_y = max_y
        self.velocity = velocity
        self.theta = 0  # Initial angle in radians
        self.lines = self.initialize_lines()
        self.line_color = (255,0,0,0)

    def initialize_lines(self):
        lines = []
        for _ in range(self.num_lines):
            start_x = np.random.randint(0, self.max_x)
            start_y = np.random.randint(0, self.max_y)
            end_x = start_x + self.line_length * np.cos(self.theta)
            end_y = start_y + self.line_length * np.sin(self.theta)
            lines.append((start_x, start_y, end_x, end_y))
        return lines

    def update_lines(self):
        new_lines = []
        for (start_x, start_y, end_x, end_y) in self.lines:
            # Update start and end points based on velocity and angle
            start_x += self.velocity * np.cos(self.theta)
            start_y += self.velocity * np.sin(self.theta)
            end_x += self.velocity * np.cos(self.theta)
            end_y += self.velocity * np.sin(self.theta)
            
            # Check if the line is still within bounds, if not, reinitialize or remove
            if 0 <= start_x <= self.max_x and 0 <= start_y <= self.max_y:
                new_lines.append((start_x, start_y, end_x, end_y))
            else:
                # Reinitialize line at opposite boundary or remove
                # Implement logic based on specific needs, e.g., wrap around
                pass
        
        self.lines = new_lines

    def update_frame(self, frame, clear):
        if clear:
            frame.clear()
        
        for (start_x, start_y, end_x, end_y) in self.lines:
            start_point = HeliosPoint(int(start_x), int(start_y), 255, 255, 255, 0)
            end_point = HeliosPoint(int(end_x), int(end_y), 255, 255, 255, 0)
            frame.add_line(start_point, end_point, self.line_color, self.max_step_size)

    def change_angle(self, new_theta):
        self.theta = new_theta
        self.lines = self.initialize_lines()  # Reinitialize lines with new angle


#%%
laser = LaserCore(".\\HeliosLaserDAC.dll", frame_size=3000)
effect = MovingLinesEffect()



try:
    while True:
        start_time = time.perf_counter()
        for device_index in range(laser.num_devices):
            effect.update_lines()
            effect.update_frame(laser.frame, clear=True)
            laser.write_frame(0, 30000, laser.frame.points, laser.frame.count)

            dt = time.perf_counter() - start_time
            print(f'fps = {1/dt}, pt_count = {laser.frame.count}')
            
        # time.sleep(1 / 30)  # 30 FPS
finally:
    laser.close()
