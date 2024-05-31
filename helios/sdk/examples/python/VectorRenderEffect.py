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


class Camera:
    def __init__(self, position, rotation):
        self.position = np.array(position)  # Position as (x, y, z)
        self.rotation = np.array(rotation)  # Rotation as (pitch, yaw, roll) in radians

    def get_view_matrix(self):
        # Create rotation matrices for each axis with 4x4 dimension for homogeneous coordinates
        Rx = np.array([
            [1, 0, 0, 0],
            [0, np.cos(self.rotation[0]), -np.sin(self.rotation[0]), 0],
            [0, np.sin(self.rotation[0]), np.cos(self.rotation[0]), 0],
            [0, 0, 0, 1]
        ])
        
        Ry = np.array([
            [np.cos(self.rotation[1]), 0, np.sin(self.rotation[1]), 0],
            [0, 1, 0, 0],
            [-np.sin(self.rotation[1]), 0, np.cos(self.rotation[1]), 0],
            [0, 0, 0, 1]
        ])
        
        Rz = np.array([
            [np.cos(self.rotation[2]), -np.sin(self.rotation[2]), 0, 0],
            [np.sin(self.rotation[2]), np.cos(self.rotation[2]), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

        # Combine rotations to a single rotation matrix
        R = Rz @ Ry @ Rx
        
        # Create translation matrix
        T = np.array([
            [1, 0, 0, -self.position[0]],
            [0, 1, 0, -self.position[1]],
            [0, 0, 1, -self.position[2]],
            [0, 0, 0, 1]
        ])

        # The view matrix is the product of translation and rotation matrices
        view_matrix = R @ T
        return view_matrix

    def apply_view_transformation(self, vertices):
        # Apply view transformation to a list of vertices
        transformed_vertices = []
        view_matrix = self.get_view_matrix()
        for vertex in vertices:
            homogeneous_vertex = np.array([*vertex, 1])  # Convert to homogeneous coordinates
            transformed_vertex = view_matrix @ homogeneous_vertex
            transformed_vertices.append(transformed_vertex[:3])
        return transformed_vertices
    
class Shape:
    def __init__(self, vertices, edges, center):
        self.vertices = vertices  # List of tuples (x, y, z)
        self.edges = edges        # List of tuples (start_vertex_idx, end_vertex_idx)
        self.center = center
        self.rot_rate_x = 0
        self.rot_rate_y = 0
        self.rot_rate_z = 0

    def project_vertices(self, screen_width, screen_height, camera, fov=1250, viewer_distance=0):
        # Apply camera transformations
        transformed_vertices = camera.apply_view_transformation(self.vertices)
    
        # Project transformed vertices into 2D coordinates
        projected_vertices = []
        for vertex in transformed_vertices:
            x, y, z = vertex
            factor = fov / (viewer_distance + z)
            x_proj = screen_width // 2 + int(x * factor)
            y_proj = screen_height // 2 - int(y * factor)
            projected_vertices.append((x_proj, y_proj))
        return projected_vertices
    
    def rotate_x(self, vertices, angle, center):
        cx, cy, cz = center
        cos_angle = np.cos(angle)
        sin_angle = np.sin(angle)
        matrix = np.array([
            [1, 0, 0, 0],
            [0, cos_angle, -sin_angle, 0],
            [0, sin_angle, cos_angle, 0],
            [0, 0, 0, 1]
        ])
        translation_matrix1 = np.array([
            [1, 0, 0, -cx],
            [0, 1, 0, -cy],
            [0, 0, 1, -cz],
            [0, 0, 0, 1]
        ])
        translation_matrix2 = np.array([
            [1, 0, 0, cx],
            [0, 1, 0, cy],
            [0, 0, 1, cz],
            [0, 0, 0, 1]
        ])
        vertices = [(x, y, z, 1) for x, y, z in vertices]
        vertices = [np.dot(translation_matrix1, vertex) for vertex in vertices]
        vertices = [np.dot(matrix, vertex) for vertex in vertices]
        vertices = [np.dot(translation_matrix2, vertex) for vertex in vertices]
        return [(x, y, z) for x, y, z, w in vertices]
    
    def rotate_y(self, vertices, angle, center):
        cx, cy, cz = center
        cos_angle = np.cos(angle)
        sin_angle = np.sin(angle)
        matrix = np.array([
            [cos_angle, 0, sin_angle, 0],
            [0, 1, 0, 0],
            [-sin_angle, 0, cos_angle, 0],
            [0, 0, 0, 1]
        ])
        translation_matrix1 = np.array([
            [1, 0, 0, -cx],
            [0, 1, 0, -cy],
            [0, 0, 1, -cz],
            [0, 0, 0, 1]
        ])
        translation_matrix2 = np.array([
            [1, 0, 0, cx],
            [0, 1, 0, cy],
            [0, 0, 1, cz],
            [0, 0, 0, 1]
        ])
        vertices = [(x, y, z, 1) for x, y, z in vertices]
        vertices = [np.dot(translation_matrix1, vertex) for vertex in vertices]
        vertices = [np.dot(matrix, vertex) for vertex in vertices]
        vertices = [np.dot(translation_matrix2, vertex) for vertex in vertices]
        return [(x, y, z) for x, y, z, w in vertices]
    
    def rotate_z(self, vertices, angle, center):
        cx, cy, cz = center
        cos_angle = np.cos(angle)
        sin_angle = np.sin(angle)
        matrix = np.array([
            [cos_angle, -sin_angle, 0, 0],
            [sin_angle, cos_angle, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        translation_matrix1 = np.array([
            [1, 0, 0, -cx],
            [0, 1, 0, -cy],
            [0, 0, 1, -cz],
            [0, 0, 0, 1]
        ])
        translation_matrix2 = np.array([
            [1, 0, 0, cx],
            [0, 1, 0, cy],
            [0, 0, 1, cz],
            [0, 0, 0, 1]
        ])
        vertices = [(x, y, z, 1) for x, y, z in vertices]
        vertices = [np.dot(translation_matrix1, vertex) for vertex in vertices]
        vertices = [np.dot(matrix, vertex) for vertex in vertices]
        vertices = [np.dot(translation_matrix2, vertex) for vertex in vertices]
        return [(x, y, z) for x, y, z, w in vertices]
    
    def rotate(self, angle_x, angle_y, angle_z):
        self.rot_rate_x = angle_x
        self.rot_rate_y = angle_y
        self.rot_rate_z = angle_z
        self.vertices = self.rotate_x(self.vertices, self.rot_rate_x, self.center)
        self.vertices = self.rotate_y(self.vertices, self.rot_rate_y, self.center)
        self.vertices = self.rotate_z(self.vertices, self.rot_rate_z, self.center)


class Cube(Shape):
    def __init__(self, center, size):
        # Define vertices relative to the center
        cx, cy, cz = center
        s = size / 2
        self.vertices = np.array([
            [cx + s, cy + s, cz + s], [cx + s, cy + s, cz - s],
            [cx + s, cy - s, cz + s], [cx + s, cy - s, cz - s],
            [cx - s, cy + s, cz + s], [cx - s, cy + s, cz - s],
            [cx - s, cy - s, cz + s], [cx - s, cy - s, cz - s]
        ])
        self.edges = [(0, 1), (1, 3), (3, 2), (2, 0), (4, 5), (5, 7), (7, 6), (6, 4),
                 (0, 4), (1, 5), (2, 6), (3, 7)]
        self.faces = [
            [0, 1, 3, 2], [4, 5, 7, 6],  # Front and back face
            [0, 4, 6, 2], [1, 5, 7, 3],  # Right and left face
            [0, 4, 5, 1], [2, 6, 7, 3]   # Top and bottom face
        ]
        super().__init__(self.vertices, self.edges, center)

    def face_normals(self):
        normals = []
        for face in self.faces:
            v0, v1, v2 = self.vertices[face[0]], self.vertices[face[1]], self.vertices[face[2]]
            # Calculate normal using the cross product of vectors within the face
            normal = np.cross(np.array(v1) - np.array(v0), np.array(v2) - np.array(v0))
            normal = normal / np.linalg.norm(normal)  # Normalize the vector
            normals.append(normal)
        return normals

    def face_centers(self):
        centers = []
        for face in self.faces:
            # Calculate the centroid of each face
            face_vertices = np.array(self.vertices)[face]
            center = np.mean(face_vertices, axis=0)
            centers.append(center)
        return np.array(centers)
        
        
class Pyramid(Shape):
    def __init__(self, center, base_size, height):
        # Define vertices relative to the center
        cx, cy, cz = center
        s = base_size / 2
        h = height / 2
        vertices = [
            (cx - s, cy - s, cz - h),  # Base bottom left
            (cx + s, cy - s, cz - h),  # Base bottom right
            (cx + s, cy + s, cz - h),  # Base top right
            (cx - s, cy + s, cz - h),  # Base top left
            (cx, cy, cz + h)          # Apex
        ]
        # Edges: each tuple represents a connection between two vertices
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Base
            (0, 4), (1, 4), (2, 4), (3, 4)   # Sides
        ]
        super().__init__(vertices, edges, center)
class Tetrahedron(Shape):
    def __init__(self, center, size):
        cx, cy, cz = center
        s = size / 2
        vertices = [
            (cx, cy, cz + s * np.sqrt(2/3)),  # Top vertex
            (cx - s, cy - s/np.sqrt(3), cz - s/3),
            (cx + s, cy - s/np.sqrt(3), cz - s/3),
            (cx, cy + 2*s/np.sqrt(3), cz - s/3)
        ]
        edges = [(0, 1), (0, 2), (0, 3), (1, 2), (2, 3), (3, 1)]
        super().__init__(vertices, edges, center)
class Octahedron(Shape):
    def __init__(self, center, size):
        # Center coordinates and half-size
        cx, cy, cz = center
        s = size / 2

        # Vertices of the Octahedron
        vertices = [
            (cx, cy, cz + s),  # Top vertex
            (cx, cy, cz - s),  # Bottom vertex
            (cx + s, cy, cz),  # Front vertex on XY plane
            (cx - s, cy, cz),  # Back vertex on XY plane
            (cx, cy + s, cz),  # Right vertex on XY plane
            (cx, cy - s, cz)   # Left vertex on XY plane
        ]

        # Edges between vertices
        edges = [
            (0, 2), (0, 3), (0, 4), (0, 5),  # Top vertex to sides
            (1, 2), (1, 3), (1, 4), (1, 5),  # Bottom vertex to sides
            (2, 4), (4, 3), (3, 5), (5, 2)   # Edges on the base
        ]

        super().__init__(vertices, edges, center)
class Sphere(Shape):
    def __init__(self, center, radius, num_latitudes=10, num_longitudes=20):
        # Center coordinates
        cx, cy, cz = center
        
        # Generate vertices
        vertices = []
        for i in range(num_latitudes + 1):
            # Latitude angle varies from -π/2 to π/2
            theta = np.pi * (i / num_latitudes - 0.5) 
            z = cz + radius * np.sin(theta)
            r_xy = radius * np.cos(theta)
            
            for j in range(num_longitudes):
                # Longitude angle varies from 0 to 2π
                phi = 2 * np.pi * j / num_longitudes
                x = cx + r_xy * np.cos(phi)
                y = cy + r_xy * np.sin(phi)
                vertices.append((x, y, z))

        # Generate edges
        edges = []
        # Add latitude lines (horizontal circles)
        for i in range(num_latitudes + 1):
            for j in range(num_longitudes):
                next_j = (j + 1) % num_longitudes
                edges.append((i * num_longitudes + j, i * num_longitudes + next_j))
        
        # Add longitude lines (vertical lines)
        for j in range(num_longitudes):
            for i in range(num_latitudes):
                edges.append((i * num_longitudes + j, (i + 1) * num_longitudes + j))

        super().__init__(vertices, edges, center)
class Torus(Shape):
    def __init__(self, center, major_radius, minor_radius, num_circles=20, num_sides=20):
        # Center coordinates
        cx, cy, cz = center
        
        # Generate vertices
        vertices = []
        for i in range(num_circles):
            theta = 2 * np.pi * i / num_circles  # Angle for the main circle
            cos_theta = np.cos(theta)
            sin_theta = np.sin(theta)
            for j in range(num_sides):
                phi = 2 * np.pi * j / num_sides  # Angle for the tube circle
                x = cx + (major_radius + minor_radius * np.cos(phi)) * cos_theta
                y = cy + (major_radius + minor_radius * np.cos(phi)) * sin_theta
                z = cz + minor_radius * np.sin(phi)
                vertices.append((x, y, z))

        # Generate edges
        edges = []
        # Add edges along the circles
        for i in range(num_circles):
            for j in range(num_sides):
                next_j = (j + 1) % num_sides
                current_index = i * num_sides + j
                next_index = i * num_sides + next_j
                edges.append((current_index, next_index))
        
        # Add edges between the circles
        for i in range(num_circles):
            next_i = (i + 1) % num_circles
            for j in range(num_sides):
                current_index = i * num_sides + j
                next_circle_index = next_i * num_sides + j
                edges.append((current_index, next_circle_index))

        super().__init__(vertices, edges, center)
class Star(Shape):
    def __init__(self, center, inner_radius, outer_radius, num_points):
        cx, cy, cz = center

        # Generate vertices for the central sphere
        vertices = [(cx, cy, cz)]  # Central point

        # Calculate the vertices on the sphere using the golden spiral
        offset = 2 / num_points
        increment = np.pi * (3 - np.sqrt(5))  # Golden angle in radians

        for i in range(num_points):
            y = ((i * offset) - 1) + (offset / 2)
            r = np.sqrt(1 - y * y)  # Radius at y

            phi = i * increment  # Angle along the spiral

            x = np.cos(phi) * r
            z = np.sin(phi) * r

            # Extend the points from the sphere surface to create the star points
            vertices.append((cx + outer_radius * x, cy + outer_radius * y, cz + outer_radius * z))

        # Generate edges: Connect the center to each point on the sphere
        edges = [(0, i + 1) for i in range(num_points)]

        super().__init__(vertices, edges, center)
class Cylinder(Shape):
    def __init__(self, center, radius, height, num_sides):
        cx, cy, cz = center
        h = height / 2  # Half height to center the cylinder at the center point

        # Generate vertices for the top and bottom circles
        vertices = []
        for z in [cz + h, cz - h]:  # Top and bottom z-coordinates
            for i in range(num_sides):
                angle = 2 * np.pi * i / num_sides
                x = cx + radius * np.cos(angle)
                y = cy + radius * np.sin(angle)
                vertices.append((x, y, z))

        # Generate edges
        edges = []
        # Connect vertices within each circle
        for i in range(num_sides):
            top_i = i
            bottom_i = i + num_sides
            next_top_i = (top_i + 1) % num_sides
            next_bottom_i = (bottom_i + 1) % num_sides if (bottom_i + 1) % num_sides != 0 else num_sides

            # Connect top circle points
            edges.append((top_i, next_top_i))
            # Connect bottom circle points
            edges.append((bottom_i, next_bottom_i))
            # Connect corresponding top and bottom points
            edges.append((top_i, bottom_i))

        super().__init__(vertices, edges, center)
class Prism(Shape):
    def __init__(self, center, num_sides, radius, height):
        cx, cy, cz = center
        h = height / 2  # Half height for symmetry around the center

        # Generate vertices for the bottom and top polygonal faces
        vertices = []
        angle_increment = 2 * np.pi / num_sides
        for z in [cz - h, cz + h]:  # Bottom and top z-coordinates
            for i in range(num_sides):
                angle = i * angle_increment
                x = cx + radius * np.cos(angle)
                y = cy + radius * np.sin(angle)
                vertices.append((x, y, z))

        # Generate edges
        edges = []
        # Connect vertices within each face
        for i in range(num_sides):
            bottom_i = i
            top_i = i + num_sides
            next_bottom_i = (bottom_i + 1) % num_sides
            next_top_i = (top_i + 1) % num_sides + num_sides

            # Connect bottom face points
            edges.append((bottom_i, next_bottom_i))
            # Connect top face points
            edges.append((top_i, next_top_i))
            # Connect corresponding top and bottom points to form the sides
            edges.append((bottom_i, top_i))

        super().__init__(vertices, edges, center)
        
class ShapeRendererEffect(LaserEffect):
    def __init__(self, shape, point_color=(255, 0, 0, 0), line_color=(0,0,0,0), point_brightness=5, blanking_points=1, max_x=0xFFF, max_y=0xFFF): #brightness 3 blanking 13 is good
        super().__init__(frame_size=1000, 
                            min_step=5, 
                            max_step=150, 
                            trans_len=800, 
                            blanking_points=blanking_points, 
                            start_blanking_points=20, 
                            brightness_multiplier=point_brightness, 
                            max_x=max_x,  # Up to 0xFFF
                            max_y=max_y)
                        
       
        self.point_color = point_color
        self.line_color = line_color
        
        self.shape = shape
    
    
            

    def update_frame(self, frame, clear, camera):
        
        if clear:
            frame.clear()
        

            
        projected_vertices = self.shape.project_vertices(self.max_x, self.max_y, camera)
        
        current_point = (max(0, min(self.max_x, projected_vertices[0][0])), max(0, min(self.max_y, projected_vertices[0][1])))
        start_blank_point = HeliosPoint(current_point[0], current_point[1], 0, 0, 0)
        frame.move_head_to_point(start_blank_point, self.min_step_size)
        
        
        for _ in range(self.starting_blanking_points):
            frame.add_point(start_blank_point)
        
        
        for start_idx, end_idx in self.shape.edges:
            current_point = (max(0, min(self.max_x, projected_vertices[start_idx][0])), max(0, min(self.max_y, projected_vertices[start_idx][1])))
            next_point = (max(0, min(self.max_x, projected_vertices[end_idx][0])), max(0, min(self.max_y, projected_vertices[end_idx][1])))
            
            start_point = HeliosPoint(current_point[0], current_point[1], self.point_color[0], self.point_color[1], self.point_color[2])
            end_point = HeliosPoint(next_point[0], next_point[1], self.line_color[0], self.line_color[1], self.line_color[2])
            start_blank_point = HeliosPoint(current_point[0], current_point[1], 0, 0, 0)
            end_blank_point = HeliosPoint(next_point[0], next_point[1], 0, 0, 0)
            
            frame.move_head_to_point(start_blank_point, self.max_step_size)
            for _ in range(self.blanking_points):
                frame.add_point(start_blank_point)
            
            for _ in range(self.brightness_multiplier):
                frame.add_point(start_point)
                
            frame.add_line_smooth(start_point, end_point, color=self.line_color, min_step_size=self.min_step_size, max_step_size=self.max_step_size, transition_length=self.transition_length)

            for _ in range(self.blanking_points):
                frame.add_point(end_blank_point)
    
            
            
#%%
laser = LaserCore(".\\HeliosLaserDAC.dll", frame_size=4000)

cube = Cube(center=(0, -1000, 0), size=500)
effectCube = ShapeRendererEffect(cube, point_color=(255,255,255,0), line_color=(255,0,0,0))

pyramid = Pyramid(center=(-1000, 0, 0), base_size=500, height=500)
effectPyramid = ShapeRendererEffect(pyramid, point_color=(255,255,255,0), line_color=(0,0,255,0))

tetra = Tetrahedron(center=(0, 500, 0), size=1500)
effectTetra = ShapeRendererEffect(tetra, point_color=(255,255,255,0), line_color=(255,0,0,0), point_brightness=5, blanking_points=10)

octahedron = Octahedron(center=(0, 0, 0), size=2000)
effectOcto = ShapeRendererEffect(octahedron, point_color=(255,255,255,0), line_color=(0,255,0,0))

sphere = Sphere(center=(0, 1000, 0), radius=500, num_latitudes=8, num_longitudes=8) 
effectSphere = ShapeRendererEffect(sphere, point_color=(255,255,255,0), line_color=(255,0,255,0))

torus  = Torus(center=(0, 0, 0), major_radius=500, minor_radius=250, num_circles=16, num_sides=3)
effectTorus = ShapeRendererEffect(torus, point_color=(255,0,255,0), line_color=(255,0,0,0))

star = Star(center=(0, 0, 0), inner_radius=0, outer_radius=800, num_points=16)
effectStar = ShapeRendererEffect(star, point_color=(255,255,255,0), line_color=(0,0,255,0))

cylinder = Cylinder(center=(0, 0, 0), radius=500, height=250, num_sides=8)
effectCylinder = ShapeRendererEffect(cylinder, point_color=(255,255,255,0), line_color=(0,255,0,0))

prism = Prism(center=(0, 0, 0), num_sides=8, radius=500, height=250)
effectPrism = ShapeRendererEffect(prism, point_color=(255,255,255,0), line_color=(0,0,255,0))
effectPrism.shape.rotate(np.pi/2, 0, 0)

camera = Camera(position=(0, 0, -10), rotation=(0.0, 0.0, 0.0))
angle_increment = 6*np.pi / 180  


#%%


# try:
#     loop_cnt = 0
#     while True:
#         start_time = time.perf_counter()
        
#         for device_index in range(laser.num_devices):
#             camera.position[2] = -2000 + np.sin(loop_cnt/10) * 1000
#             # print(camera.position[2])
#             effectCube.update_frame(laser.frame, clear=True, camera=camera)
#             # effectPrism.update_frame(laser.frame, clear=False, camera=camera)
#             # effectSphere.update_frame(laser.frame, clear=True, camera=camera)
#             # effectPyramid.update_frame(laser.frame, clear=False, camera=camera)
#             # effectTetra.update_frame(laser.frame, clear=True, camera=camera)
#             # effectOcto.update_frame(laser.frame, clear=True, camera=camera)
#             # effectTorus.update_frame(laser.frame, clear=True, camera=camera)
#             # effectStar.update_frame(laser.frame, clear=True, camera=camera)
#             # effectCylinder.update_frame(laser.frame, clear=False, camera=camera)

            
#             laser.write_frame(0, 30000, laser.frame.points, laser.frame.count)
#             dt = time.perf_counter() - start_time
#             print(f'fps = {1/dt}, pt_count = {laser.frame.count}')
#             loop_cnt += 1
            

            
            
#         effectCube.shape.rotate(0, angle_increment, 0)
#         effectPyramid.shape.rotate(angle_increment, 0, 0)
#         effectTetra.shape.rotate(0, 0, angle_increment)
#         effectOcto.shape.rotate(0, angle_increment, angle_increment)
#         effectSphere.shape.rotate(0, angle_increment, 0)
#         effectTorus.shape.rotate(angle_increment, angle_increment, angle_increment)
#         effectStar.shape.rotate(angle_increment, angle_increment, angle_increment)
#         effectCylinder.shape.rotate(0, angle_increment, 0)
#         effectPrism.shape.rotate(0, -angle_increment, 0)
        
#         effectStar.shape.center = (np.sin(loop_cnt/50) * 500, np.cos(loop_cnt/30) * 500, np.cos(loop_cnt/100) * 500)
#         effectCube.shape.center = (np.cos(loop_cnt/25) * 1000, np.cos(loop_cnt/10) * 2000, 0)

            
#         # time.sleep(1 / 30)  # 30 FPS
# finally:
#     laser.close()

#%%
# laser = LaserCore(".\\HeliosLaserDAC.dll", frame_size=4000)
# camera = Camera(position=(0, -800, -10), rotation=(0.0, 0.0, 0.0))
# angle_increment = 20*np.pi / 180  

# star1 = Star(center=(0, 0, 0), inner_radius=0, outer_radius=500, num_points=8)
# star2 = Star(center=(800, 0, 0), inner_radius=0, outer_radius=500, num_points=8)
# star3 = Star(center=(-800, 0, 0), inner_radius=0, outer_radius=500, num_points=8)
# star4 = Star(center=(0, 0, 400), inner_radius=0, outer_radius=500, num_points=8)
# star5 = Star(center=(0, 0, -400), inner_radius=0, outer_radius=500, num_points=8)

# effect1 = ShapeRendererEffect(star1, point_color=(255,255,255,0), line_color=(0,255,0,0))
# effect2 = ShapeRendererEffect(star2, point_color=(255,255,255,0), line_color=(255,0,0,0))
# effect3 = ShapeRendererEffect(star3, point_color=(255,255,255,0), line_color=(0,0,255,0))
# effect4 = ShapeRendererEffect(star4, point_color=(255,255,255,0), line_color=(0,0,255,0))
# effect5 = ShapeRendererEffect(star5, point_color=(255,255,255,0), line_color=(0,0,255,0))

# try:
#     loop_cnt = 0
#     while True:
#         start_time = time.perf_counter()
        
#         for device_index in range(laser.num_devices):
#             camera.position[2] = -2000 + np.sin(loop_cnt/10) * 1000
#             # camera.rotation[2] = 5*2*np.pi*np.sin(loop_cnt/100)
           
#             effect1.update_frame(laser.frame, clear=True, camera=camera)
#             effect2.update_frame(laser.frame, clear=False, camera=camera)
#             effect3.update_frame(laser.frame, clear=False, camera=camera)
#             # effect4.update_frame(laser.frame, clear=False, camera=camera)
#             # effect5.update_frame(laser.frame, clear=False, camera=camera)
            
            
#             laser.write_frame(0, 20000, laser.frame.points, laser.frame.count)
#             dt = time.perf_counter() - start_time
#             print(f'fps = {1/dt}, pt_count = {laser.frame.count}')
#             loop_cnt += 1
            

            
            
#         effect1.shape.rotate(0, -angle_increment, 0)
#         effect2.shape.rotate(angle_increment, 0, 0)
#         effect3.shape.rotate(-angle_increment, 0, angle_increment)


            
#         # time.sleep(1 / 30)  # 30 FPS
# finally:
#     laser.close()
    

