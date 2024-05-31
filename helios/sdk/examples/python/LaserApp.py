import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import QTimer

import numpy as np 

from LaserCore import LaserCore
from FFTEffect import FFT
from VectorRenderEffect import Camera, ShapeRendererEffect, Cube, Pyramid, Tetrahedron, Octahedron, Sphere, Torus, Star, Prism, Cylinder

#%%

class LaserShowApp(QWidget):
    def __init__(self):
        super().__init__()
        
        self.loop_cnt = 0
        self.angle_increment = 6*np.pi / 180  

        
        self.initUI()
        
        # Initialize laser and effects
        self.laser = LaserCore(".\\HeliosLaserDAC.dll", frame_size=4000)
        self.camera = Camera(position=(0, -800, -10), rotation=(0.0, 0.0, 0.0))
        self.angle_increment = 20*np.pi / 180  
        
        # FFT effects
        self.fft_effect1 = FFT(frame_size=1, num_points=64, point_color=(0,255,255,0), 
                               line_color=(0,0,255,0), chunk=4096, buckets=2048,
                               floor=0x400, decay=0.35, min_step=75, max_step=75,
                               trans_len=0, blanking_points=0, start_blanking_points=50,
                               brightness_multiplier=1)

        self.fft_effect2 = FFT(frame_size=1, num_points=16, point_color=(255,255,255,0), 
                               line_color=(0,0,0,0), chunk=2048, buckets=1024,
                               floor=0x400, decay=0.35, min_step=75, max_step=75,
                               trans_len=0, blanking_points=0, start_blanking_points=50,
                               brightness_multiplier=10)
        
        self.fft_effect3 = FFT(frame_size=1, num_points=16, point_color=(255,0,0,0), 
                               line_color=(0,0,0,0), chunk=2048, buckets=1024,
                               floor=0x400, decay=0.1, min_step=75, max_step=75,
                               trans_len=0, blanking_points=0, start_blanking_points=50,
                               brightness_multiplier=10)
        
        self.fft_effect4 = FFT(frame_size=1, num_points=16, point_color=(0,255,0,0), 
                               line_color=(0,0,0,0), chunk=2048, buckets=1024,
                               floor=0x400, decay=0.1, min_step=75, max_step=75,
                               trans_len=0, blanking_points=0, start_blanking_points=50,
                               brightness_multiplier=10)
        
        self.fft_effect5 = FFT(frame_size=1, num_points=64, point_color=(255,255,255,0), 
                               line_color=(255,255,255,0), chunk=4096, buckets=2048,
                               floor=0x400, decay=0.35, min_step=75, max_step=75,
                               trans_len=0, blanking_points=0, start_blanking_points=50,
                               brightness_multiplier=1)
        
        # Shape effects
        cube = Cube(center=(0, -1000, 0), size=500)
        pyramid = Pyramid(center=(-1000, 0, 0), base_size=500, height=500)
        tetra = Tetrahedron(center=(0, 500, 0), size=1500)
        octahedron = Octahedron(center=(0, 0, 0), size=2000)
        sphere = Sphere(center=(0, 1000, 0), radius=500, num_latitudes=8, num_longitudes=8) 
        torus  = Torus(center=(0, 0, 0), major_radius=500, minor_radius=250, num_circles=16, num_sides=3)
        star = Star(center=(0, 0, 0), inner_radius=0, outer_radius=800, num_points=16)
        cylinder = Cylinder(center=(0, 0, 0), radius=500, height=250, num_sides=8)
        prism = Prism(center=(0, 0, 0), num_sides=8, radius=500, height=250)
        
        self.shape_effect1 = ShapeRendererEffect(cube, point_color=(255,255,255,0), line_color=(255,0,0,0))
        self.shape_effect2 = ShapeRendererEffect(pyramid, point_color=(255,255,255,0), line_color=(0,0,255,0))
        self.shape_effect3 = ShapeRendererEffect(tetra, point_color=(255,255,255,0), line_color=(255,0,0,0), point_brightness=5, blanking_points=10)
        self.shape_effect4 = ShapeRendererEffect(torus, point_color=(255,0,255,0), line_color=(255,0,0,0))
        # self.shape_effect4 = ShapeRendererEffect(octahedron, point_color=(255,255,255,0), line_color=(0,255,0,0))
        self.shape_effect5 = ShapeRendererEffect(sphere, point_color=(255,255,255,0), line_color=(255,0,255,0))
        
        # self.shape_effect7 = ShapeRendererEffect(star, point_color=(255,255,255,0), line_color=(0,0,255,0))
        # self.shape_effect8 = ShapeRendererEffect(cylinder, point_color=(255,255,255,0), line_color=(0,255,0,0))
        # self.shape_effect9 = ShapeRendererEffect(prism, point_color=(255,255,255,0), line_color=(0,0,255,0))
        # self.shape_effect9.shape.rotate(np.pi/2, 0, 0)


        


        self.current_effect = self.fft_effect1

        # Set up a timer to update the laser frames
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(0)  # Approximately 30 FPS
        
        
    def initUI(self):
        self.setWindowTitle('Laser Show Controller')

        main_layout = QHBoxLayout()
        
        fft_layout = QVBoxLayout()
        shape_layout = QVBoxLayout()

        self.fft_effectAButton = QPushButton('FFT Effect A', self)
        self.fft_effectAButton.clicked.connect(self.switch_to_fft_effect_a)
        fft_layout.addWidget(self.fft_effectAButton)

        self.fft_effectBButton = QPushButton('FFT Effect B', self)
        self.fft_effectBButton.clicked.connect(self.switch_to_fft_effect_b)
        fft_layout.addWidget(self.fft_effectBButton)
        
        self.fft_effectCButton = QPushButton('FFT Effect C', self)
        self.fft_effectCButton.clicked.connect(self.switch_to_fft_effect_c)
        fft_layout.addWidget(self.fft_effectCButton)
        
        self.fft_effectDButton = QPushButton('FFT Effect D', self)
        self.fft_effectDButton.clicked.connect(self.switch_to_fft_effect_d)
        fft_layout.addWidget(self.fft_effectDButton)
        
        self.fft_effectEButton = QPushButton('FFT Effect E', self)
        self.fft_effectEButton.clicked.connect(self.switch_to_fft_effect_e)
        fft_layout.addWidget(self.fft_effectEButton)

        self.shape_effectAButton = QPushButton('Shape Effect A', self)
        self.shape_effectAButton.clicked.connect(self.switch_to_shape_effect_a)
        shape_layout.addWidget(self.shape_effectAButton)

        self.shape_effectBButton = QPushButton('Shape Effect B', self)
        self.shape_effectBButton.clicked.connect(self.switch_to_shape_effect_b)
        shape_layout.addWidget(self.shape_effectBButton)
        
        self.shape_effectCButton = QPushButton('Shape Effect C', self)
        self.shape_effectCButton.clicked.connect(self.switch_to_shape_effect_c)
        shape_layout.addWidget(self.shape_effectCButton)
        
        self.shape_effectDButton = QPushButton('Shape Effect D', self)
        self.shape_effectDButton.clicked.connect(self.switch_to_shape_effect_d)
        shape_layout.addWidget(self.shape_effectDButton)
        
        self.shape_effectEButton = QPushButton('Shape Effect E', self)
        self.shape_effectEButton.clicked.connect(self.switch_to_shape_effect_e)
        shape_layout.addWidget(self.shape_effectEButton)

        main_layout.addLayout(fft_layout)
        main_layout.addLayout(shape_layout)

        self.setLayout(main_layout)
        self.show()

    def switch_to_fft_effect_a(self):
        print("Switching to FFT Effect A")
        self.current_effect = self.fft_effect1

    def switch_to_fft_effect_b(self):
        print("Switching to FFT Effect B")
        self.current_effect = self.fft_effect2

    def switch_to_fft_effect_c(self):
        print("Switching to FFT Effect C")
        self.current_effect = self.fft_effect3

    def switch_to_fft_effect_d(self):
        print("Switching to FFT Effect D")
        self.current_effect = self.fft_effect4

    def switch_to_fft_effect_e(self):
        print("Switching to FFT Effect E")
        self.current_effect = self.fft_effect5

    def switch_to_shape_effect_a(self):
        print("Switching to Shape Effect A")
        self.current_effect = self.shape_effect1

    def switch_to_shape_effect_b(self):
        print("Switching to Shape Effect B")
        self.current_effect = self.shape_effect2

    def switch_to_shape_effect_c(self):
        print("Switching to Shape Effect C")
        self.current_effect = self.shape_effect3

    def switch_to_shape_effect_d(self):
        print("Switching to Shape Effect D")
        self.current_effect = self.shape_effect4

    def switch_to_shape_effect_e(self):
        print("Switching to Shape Effect E")
        self.current_effect = self.shape_effect5

    def update_frame(self):
        try:
            for device_index in range(self.laser.num_devices):
                self.camera.position[2] = -2000 + np.sin(self.loop_cnt/10) * 1000
                self.loop_cnt += 1
                self.shape_effect1.shape.rotate(0, self.angle_increment, 0)
                self.shape_effect2.shape.rotate(self.angle_increment, 0, 0)
                self.shape_effect3.shape.rotate(0, 0, self.angle_increment)
                self.shape_effect4.shape.rotate(0, self.angle_increment, self.angle_increment)
                self.shape_effect5.shape.rotate(0, self.angle_increment, 0)
                # self.shape_effect6.shape.rotate(self.angle_increment, self.angle_increment, self.angle_increment)
                # self.shape_effect7.shape.rotate(self.angle_increment, self.angle_increment, self.angle_increment)
                # self.shape_effect8.shape.rotate(0, self.angle_increment, 0)
                # self.shape_effect9.shape.rotate(0, -self.angle_increment, 0)

                
                self.current_effect.update_frame(self.laser.frame, clear=True, camera=self.camera)
                self.laser.write_frame(0, 40000, self.laser.frame.points, self.laser.frame.count)
        except Exception as e:
            print(f"Error updating frame: {e}")

    def closeEvent(self, event):
        self.laser.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    ex = LaserShowApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()