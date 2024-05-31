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


class FFT(LaserEffect):
    def __init__(self,
                 frame_size=1000,
                 num_points=16,
                 point_color = (255,0,0,0),
                 line_color = (0,0,255,0),
                 chunk = 4096,
                 buckets = 2048,
                 floor = 0x400,
                 decay = 0.5,
                 min_step=50, 
                 max_step=50, 
                 trans_len=0, 
                 blanking_points=0, 
                 start_blanking_points=50, 
                 brightness_multiplier=1, 
                 max_x=0xFFF,  # Up to 0xFFF
                 max_y=0xFFF): # Up to 0xFFF):
        super().__init__(frame_size, min_step, max_step, trans_len, blanking_points, start_blanking_points, brightness_multiplier, max_x, max_y)
        # Constants
        self.format = pyaudio.paInt16  # Audio format (16-bit PCM)
        self.channels = 1  # Mono audio
        self.rate = 192000  # Sample rate
        self.chunk = chunk  # Number of audio samples per frame
        self.buckets = buckets  # Number of frequency buckets
        self.num_points = num_points
        self.y_floor = floor
        self.decay_factor = decay
        self.point_color = point_color
        self.line_color = line_color
        #target point array
        self.points = [{
            'pos': (i * self.max_x // (self.num_points - 1), self.max_y // 2),
            'vel': (random.randint(-80, 80), 0),  
            'color': (255,255,255)
        } for i in range(self.num_points)]
        
        
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        
        # Open stream
        self.stream = p.open(format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.chunk)
        print("Streaming started")
        

    def log_spaced_indices(self):
        nyquist = self.rate / 2
        min_freq = self.rate / self.chunk
        max_freq = nyquist
        frequencies = np.logspace(np.log10(min_freq), np.log10(max_freq), self.num_points)
        indices = np.floor((frequencies / nyquist) * (self.chunk / 2)).astype(int)
        return indices
        
    def update_fft(self):
        data = self.stream.read(self.chunk, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        fft_data = np.fft.fft(audio_data)
        freqs = np.fft.fftfreq(len(fft_data), 1 / self.rate)
        # y_data = 2 / CHUNK * np.abs(fft_data[0:CHUNK // 2])
        mag = np.abs(fft_data)**2 / (self.chunk**2)


        bucket_width = len(freqs) // 2 // self.buckets
        energy_buckets = np.array([np.sum(mag[i*bucket_width:(i+1)*bucket_width]) for i in range(self.num_points)]) 

        
        # log_indices = self.log_spaced_indices()
        # print(log_indices)
        # energy_buckets = energy_buckets[log_indices]

        for idx, point in enumerate(self.points):
            target = int(np.sqrt(energy_buckets[idx]*50))
            
            x, y = point['pos']
            x_new = x
           
            if( target > y):
                y_new = int(target)
            else:
                y_new = int(y - self.decay_factor * (y-self.y_floor))
                y_new = max(y_new, self.y_floor)
        
            # Update position based on possibly inverted velocity
            x_new = max(0, min(self.max_x, x_new))
            y_new = max(0, min(self.max_y, y_new))
        
            point['pos'] = (x_new, y_new)
            

        
        
    def update_frame(self, frame, clear, camera):
        self.update_fft()
        if(clear):
            frame.clear()
            start_blank_point = HeliosPoint(self.points[0]['pos'][0], self.points[0]['pos'][1], 0, 0, 0, 0)
            for _ in range(self.starting_blanking_points):
                frame.add_point(start_blank_point)
        
        for i in range(self.num_points-1):
            
            start = self.points[i]['pos']
            end = self.points[i + 1]['pos']
            
            start_point = HeliosPoint(start[0], start[1], self.point_color[0], self.point_color[1], self.point_color[2])
            end_point = HeliosPoint(end[0], end[1], 0, 0, 0, 0)
            start_blank_point = HeliosPoint(start[0], start[1], 0, 0, 0, 0)
            end_blank_point = HeliosPoint(end[0], end[1], 0, 0, 0, 0)
                    
            for _ in range(self.blanking_points):
                frame.add_point(start_blank_point)
            
            for _ in range(self.brightness_multiplier):
                frame.add_point(start_point)
        
            frame.add_line_smooth(start_point, end_point, self.line_color, self.min_step_size, self.max_step_size, self.transition_length)
            # frame.add_line(start_point, end_point, self.line_color, self.max_step_size)
            for _ in range(self.brightness_multiplier):
                frame.add_point(end_point)
            
            for _ in range(self.blanking_points):
                frame.add_point(end_blank_point)
            
        # Wrapping around to the first point
        start = self.points[-1]['pos']
        end = self.points[0]['pos']        
        start_blank_point = HeliosPoint(start[0], start[1], 0, 0, 0, 0)
        end_blank_point = HeliosPoint(end[0], end[1], 0, 0, 0, 0)
        # frame.add_line_smooth(start_blank_point, end_blank_point, (0,0,0,0), self.min_step_size, self.max_step_size, self.transition_length)
        frame.add_line(start_point, end_point, self.line_color, self.max_step_size)

            
            
#%%
# laser = LaserCore(".\\HeliosLaserDAC.dll", frame_size=3000)
# effect = FFT(frame_size = 1,
#               num_points=16, 
#               point_color = (255,255,255,0), 
#               line_color = (0,0,0,0),
#               chunk=2048, 
#               buckets=1024,
#               floor = 0x400,
#               decay = 0.1,
#               min_step=50, 
#               max_step=50, 
#               trans_len=0, 
#               blanking_points=0, 
#               start_blanking_points=50, 
#               brightness_multiplier=20)

# effect2 = FFT(frame_size = 1,
#               num_points=64, 
#               point_color = (0,255,255,0), 
#               line_color = (0,0,255,0),
#               chunk=4096, 
#               buckets=2048,
#               floor = 0x400,
#               decay = 0.35,
#               min_step=75, 
#               max_step=75, 
#               trans_len=0, 
#               blanking_points=0, 
#               start_blanking_points=50, 
#               brightness_multiplier=1)

# try:
#     while True:
#         start_time = time.perf_counter()
#         for device_index in range(laser.num_devices):
#             if(0):
#                 effect.update_frame(laser.frame, clear=True)
#                 laser.write_frame(0, 30000, laser.frame.points, laser.frame.count)
#             else:
#                 effect2.update_frame(laser.frame, clear=True)
#                 laser.write_frame(0, 30000, laser.frame.points, laser.frame.count)
#             dt = time.perf_counter() - start_time
#             print(f'fps = {1/dt}, pt_count = {laser.frame.count}')
            
#         # time.sleep(1 / 30)  # 30 FPS
# finally:
#     laser.close()



# #%%
# import matplotlib.pyplot as plt
# x = np.arange(0,effect.num_points)

# y = np.log(x) 
# y = y/np.max(y)*effect.chunk

# plt.plot(y,x)
# plt.grid(True)
# plt.show()


# #%%


# nyquist = effect.rate / 2
# min_freq = effect.rate / effect.chunk
# max_freq = nyquist
# frequencies = np.logspace(np.log10(min_freq), np.log10(max_freq), effect.num_points)
# indices = np.floor((frequencies / nyquist) * (effect.chunk / 2)).astype(int)
    
    
