import ctypes
import random
import math
import time

from LaserCore import HeliosPoint, Frame, LaserCore


class LaserEffect:
    def __init__(self, 
                 frame_size=1000, 
                 min_step=1, 
                 max_step=100, 
                 trans_len=500, 
                 blanking_points=8, 
                 start_blanking_points=20, 
                 brightness_multiplier=10, 
                 max_x=0xFFF,  # Up to 0xFFF
                 max_y=0xFFF): # Up to 0xFFF
        
        self.frame = Frame(frame_size)
        self.min_step_size = min_step
        self.max_step_size = max_step
        self.transition_length = trans_len
        self.blanking_points = blanking_points
        self.starting_blanking_points = start_blanking_points
        self.brightness_multiplier = brightness_multiplier
        self.max_x = max_x             
        self.max_y = max_y            
       
        

    def update_frame(self):
        """Update the frame with new points. This method should be overridden by subclasses."""
        raise NotImplementedError("This method should be overridden by subclasses")

    def apply_to_device(self, device):
        """Send the current frame to the device."""
        device.write_frame(0, self.frame_rate, self.frame.points, self.frame.count)

    def stop(self):
        """Stop the effect."""
        self.active = False
        

