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
import pygame

class SecondaryParticle:
    def __init__(self, position, velocity, drag_coefficient):
        self.position = position
        self.velocity = velocity
        self.drag_coefficient = drag_coefficient

    def update(self):
        """Update particle position and velocity considering drag."""
        self.velocity = (self.velocity[0] * (1 - self.drag_coefficient), 
                         self.velocity[1] * (1 - self.drag_coefficient))
        self.position = (self.position[0] + self.velocity[0], 
                         self.position[1] + self.velocity[1])
        
class ParticleEffect(LaserEffect):
    def __init__(self, initial_x, initial_y, num_trail_points=30, num_sparks=10, point_color=(0,255,255,0), line_color=(255,0,0,0), spark_color=(255,255,255,0), drag_coefficient=0.001, spark_drag=0.1, max_x=0xFFF, max_y=0xFFF):
        super().__init__(max_x=max_x, max_y=max_y)
        self.position = (initial_x, initial_y)
        self.velocity = (0, 0)
        self.acceleration = (0, 0)
        self.drag_coefficient = drag_coefficient
        self.points = []
        self.sparks = []
        self.num_trail_points = num_trail_points
        self.num_sparks = num_sparks
        self.point_color = point_color
        self.line_color = line_color
        self.spark_color = spark_color
        self.spark_drag = spark_drag
        
        self.brightness_multiplier=10
        self.blanking_points=5
        self.starting_blanking_points=20
        self.min_step_size=20
        self.max_step_size=150
        self.transition_length=200
        
        # Constants
        self.format = pyaudio.paInt16  # Audio format (16-bit PCM)
        self.channels = 1  # Mono audio
        self.rate = 192000  # Sample rate
        self.chunk = 1024  # Number of audio samples per frame
        self.buckets = 16  # Number of frequency buckets
        self.num_points = 16
        
        
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        
        # Open stream
        self.stream = p.open(format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.chunk)
        print("Streaming started")
        
        
    def spawn_spark(self):
        """Spawn a spark with a random velocity and position close to the main particle."""
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 5)
        velocity = (speed * math.cos(angle), speed * math.sin(angle))
        position = (self.position[0] + random.gauss(0, 3), self.position[1] + random.gauss(0, 3))
        new_spark = SecondaryParticle(position, velocity, self.spark_drag)
        self.sparks.append(new_spark)
        if len(self.sparks) > self.num_sparks:
            self.sparks.pop(0)
            
    def apply_force(self, force_x, force_y):
        """Apply a force to the particle, changing its acceleration."""
        self.acceleration = (self.acceleration[0] + force_x, self.acceleration[1] + force_y)
        # print(self.acceleration)

    def update(self):
        
        data = self.stream.read(self.chunk, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        fft_data = np.fft.fft(audio_data)
        freqs = np.fft.fftfreq(len(fft_data), 1 / self.rate)
        # y_data = 2 / CHUNK * np.abs(fft_data[0:CHUNK // 2])
        mag = np.abs(fft_data)**2 / (self.chunk**2)


        bucket_width = len(freqs) // 2 // self.buckets
        energy_buckets = np.array([np.sum(mag[i*bucket_width:(i+1)*bucket_width]) for i in range(self.num_points)]) 
        
        # force_level_1 = np.mean(energy_buckets[1:3])
        # force_level_2 = np.mean(energy_buckets[3:7])
        # x_force = 0
        # y_force = 0
        # if(force_level_1 > 50):
        #     x_force = -np.sign(particle.velocity[0])*force_level_1 / 10
        
        # if(force_level_2 > 50):
        #     y_force  = -np.sign(particle.velocity[1])*force_level_2/2
        # print(x_force)
        # self.apply_force(x_force, y_force)
        
        
        
        
        """Update the particle's velocity, position, and trail based on its acceleration and drag."""
        # Apply drag to velocity before updating it with acceleration
        self.velocity = (
            self.velocity[0] * (1 - self.drag_coefficient),
            self.velocity[1] * (1 - self.drag_coefficient)
        )
        
        # Update velocity with current acceleration
        self.velocity = (
            self.velocity[0] + self.acceleration[0],
            self.velocity[1] + self.acceleration[1]
        )
        
        # Predict next position
        next_position = (
            self.position[0] + self.velocity[0],
            self.position[1] + self.velocity[1]
        )
        
        # Reflect velocity at boundaries
        if next_position[0] <= 0 or next_position[0] >= self.max_x:
            self.velocity = (-self.velocity[0], self.velocity[1])  # Reflect horizontal velocity
        if next_position[1] <= 0 or next_position[1] >= self.max_y:
            self.velocity = (self.velocity[0], -self.velocity[1])  # Reflect vertical velocity
        
        # Update position with reflected velocity
        self.position = (
            self.position[0] + self.velocity[0],
            self.position[1] + self.velocity[1]
        )
        
        # Update trail
        self.points.append({'pos': (int(self.position[0]), int(self.position[1]))})
        if len(self.points) > self.num_trail_points:
            self.points.pop(0)

        # Reset acceleration after applying it
        self.acceleration = (0, 0)
        
        # if random.random() < 0.1:  # Low probability to spawn a spark
        #     self.spawn_spark()
        # for spark in self.sparks:
        #     spark.update()

    def update_frame(self, frame, clear=True):
        if clear:
            frame.clear()
        
        start_blank_point = HeliosPoint(self.points[0]['pos'][0], self.points[0]['pos'][1], 0, 0, 0)
        frame.move_head_to_point(start_blank_point, self.min_step_size)
        self.num_points=len(self.points)
        
        for _ in range(self.starting_blanking_points):
            frame.add_point(start_blank_point)
            
        for i in range(0, self.num_points-1):
            
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
                
        for spark in self.sparks:
            spark_point = HeliosPoint(int(spark.position[0]), int(spark.position[1]),  self.spark_color[0], self.spark_color[1], self.spark_color[2])
            spark_point_blank = HeliosPoint(int(spark.position[0]), int(spark.position[1]), 0, 0, 0)
            frame.move_head_to_point(spark_point_blank, self.min_step_size)
            for _ in range(self.blanking_points):
                frame.add_point(start_blank_point)
            
            for _ in range(self.brightness_multiplier*2):
                frame.add_point(start_point)
            
            for _ in range(self.blanking_points):
                frame.add_point(start_blank_point)
                

class Paddle(LaserEffect):
    def __init__(self, x, y, height, max_y, max_x, point_color=(255,255,255,0), line_color=(0,0,255,0)):
        super().__init__(max_x=max_x, max_y=max_y)
        self.x = x
        self.y = y
        self.height = height
        self.max_y = max_y
        self.update_endpoints()
        self.point_color=point_color
        self.line_color=line_color
        
        self.brightness_multiplier=10
        self.blanking_points=0
        self.starting_blanking_points=20
        self.min_step_size=20
        self.max_step_size=100
        self.transition_length=250

    def update_endpoints(self):
        """Update the top and bottom endpoints of the paddle."""
        self.top_endpoint = (self.x, self.y)
        self.bottom_endpoint = (self.x, self.y + self.height)

    def move(self, dy):
        """Move paddle vertically within frame boundaries and update endpoints."""
        new_y = max(0, min(self.max_y - self.height, self.y + dy))
        if new_y != self.y:
            self.y = new_y
            self.update_endpoints()

    def update_frame(self, frame, clear=True):
        if clear:
            frame.clear()
        """Render the paddle as a rectangle on the frame."""
        start_point = HeliosPoint(self.top_endpoint[0], self.top_endpoint[1], self.point_color[0], self.point_color[1], self.point_color[2])
        end_point = HeliosPoint(self.bottom_endpoint[0], self.bottom_endpoint[1], self.line_color[0], self.line_color[1], self.line_color[2])
        start_blank_point = HeliosPoint(self.top_endpoint[0], self.top_endpoint[1], 0, 0, 0)
        end_blank_point = HeliosPoint(self.bottom_endpoint[0], self.bottom_endpoint[1], 0, 0, 0)
        
        for _ in range(self.starting_blanking_points):
            frame.add_point(start_blank_point)
            
        for _ in range(self.blanking_points):
            frame.add_point(start_blank_point)
        
        for _ in range(self.brightness_multiplier):
            frame.add_point(start_point)
            
        frame.add_line_smooth(start_point, end_point, color=self.line_color, min_step_size=self.min_step_size, max_step_size=self.max_step_size, transition_length=self.transition_length)
        
        for _ in range(self.blanking_points):
            frame.add_point(end_blank_point)
            
        for _ in range(self.brightness_multiplier):
            frame.add_point(end_point)
        
       


class PongGame:
    def __init__(self, frame_width, frame_height):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.ball = ParticleEffect(initial_x=frame_width // 2, initial_y=frame_height // 3, num_trail_points=10, drag_coefficient=0.00, point_color=(255,0,0,0), max_x=frame_width, max_y=frame_height)
        self.paddle1 = Paddle(x=250, y=frame_height // 2 - 20, height=500, max_y=frame_height, max_x=frame_width)
        self.paddle2 = Paddle(x=frame_width - 250, y=frame_height // 2 - 20, height=500, max_y=frame_height, max_x=frame_width)
        self.score1 = 0
        self.score2 = 0
        self.reset_ball()
        # Initialize Pygame
        pygame.init()
        
        # Set up the display
        screen_width, screen_height = 800, 600
        screen = pygame.display.set_mode((screen_width, screen_height))
        
        # Game settings
        running = True
        fps = 60
        clock = pygame.time.Clock()

    def update(self):
        """Update game state including ball and paddle positions."""
        # Check pressed keys
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.paddle1.move(50)  # Move paddle 1 up
        if keys[pygame.K_s]:
            self.paddle1.move(-50)   # Move paddle 1 down
        if keys[pygame.K_UP]:
            self.paddle2.move(50)  # Move paddle 2 up
        if keys[pygame.K_DOWN]:
            self.paddle2.move(-50)   # Move paddle 2 down
            
            
        self.ball.update()

        # Prepare for collision detection
        next_ball_position = (
            self.ball.position[0] + self.ball.velocity[0],
            self.ball.position[1] + self.ball.velocity[1]
        )

        # Collision detection with paddles
        if self.check_collision(self.paddle1, next_ball_position):
            print('hit 1')
            self.ball.velocity = (-self.ball.velocity[0], self.ball.velocity[1])
        elif self.check_collision(self.paddle2, next_ball_position):
            print('hit 2')
            self.ball.velocity = (-self.ball.velocity[0], self.ball.velocity[1])

        # Scoring
        print(self.ball.position)
        if self.ball.position[0] < 150:
            print('score 1')
            self.score2 += 1
            self.reset_ball()
        elif self.ball.position[0] > self.frame_width - 150:
            print('score 2')
            self.score1 += 1
            self.reset_ball()

    def check_collision(self, paddle, ball_position):
        """Check if the ball collides with a given paddle."""
        paddle_top = paddle.y
        paddle_bottom = paddle.y + paddle.height
        paddle_left = paddle.x
        paddle_right = paddle.x + 10  # Assuming the paddle width is 10

        ball_x, ball_y = ball_position
        ball_radius = 5  # Assuming the ball has a radius of 5 for collision detection

        # Check if the ball's next position is within the paddle's area
        return (paddle_left - ball_radius <= ball_x <= paddle_right + ball_radius) and \
               (paddle_top - ball_radius <= ball_y <= paddle_bottom + ball_radius)
               
    def reset_ball(self):
        """Reset the ball to the center with a random initial velocity."""
        self.ball.position = (self.frame_width // 2, self.frame_height // 2)
        self.ball.velocity = (random.choice([-1, 1]) * 25, random.choice([-1, 1]) * 25)

    def update_frame(self, frame, clear=True):
        if clear:
            frame.clear()
        """Draw the game state to the frame."""
        self.ball.update_frame(frame, clear=False)
        self.paddle1.update_frame(frame, clear=False)
        self.paddle2.update_frame(frame, clear=False)           
            
#%%
# laser = LaserCore(".\\HeliosLaserDAC.dll", frame_size=10000)
# particle = ParticleEffect(0xA00, 0xC00)
# pong = PongGame(0xFFF,0xFFF)

# try:
#     loop_count = 0
#     while True:
#         start_time = time.perf_counter()
#         for device_index in range(laser.num_devices):

#             # particle.apply_force(3*math.sin(loop_count/10), 3*math.cos(loop_count/10))
#             # print(particle.velocity)
#             loop_count += 1

#             # particle.update()
#             # particle.update_frame(laser.frame, clear=True)
#             # pong.paddle1.move(int(250*math.sin(loop_count/10)))
#             # pong.paddle2.move(int(250*math.cos(loop_count/10)))
#             pong.update()
#             pong.update_frame(laser.frame, clear=True)

            
#             laser.write_frame(0, 30000, laser.frame.points, laser.frame.count)
#             dt = time.perf_counter() - start_time
#             print(f'fps = {1/dt}, pt_count = {laser.frame.count}')
            
#         # time.sleep(1 / 30)  # 30 FPS
# finally:
#     laser.close()

#%%
laser = LaserCore(".\\HeliosLaserDAC.dll", frame_size=10000)
particle = ParticleEffect(0xA00, 0xC00)
pong = PongGame(0xFFF,0xFFF)

try:
    loop_count = 0
    while True:
        start_time = time.perf_counter()
        for device_index in range(laser.num_devices):

            particle.apply_force(5*math.sin(loop_count/10), 5*math.cos(loop_count/10))
            # print(particle.velocity)
            loop_count += 1

            particle.update()
            particle.update_frame(laser.frame, clear=True)

            # pong.update()
            # pong.update_frame(laser.frame, clear=True)

            
            laser.write_frame(0, 30000, laser.frame.points, laser.frame.count)
            dt = time.perf_counter() - start_time
            print(f'fps = {1/dt}, pt_count = {laser.frame.count}')
            
        # time.sleep(1 / 30)  # 30 FPS
finally:
    laser.close()



