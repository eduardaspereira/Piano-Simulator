import math
import random
import pygame
from core.matrix import Matrix
from extras.movement_rig import MovementRig
from core_ext.cameraPlayer import Camera

class Player(MovementRig):
    def __init__(self):
        super().__init__(units_per_second=5, degrees_per_second=180, mouse_sensitivity=0.002)
        
        # Spawn configuration - easily editable
        self.spawn_position = [4.5, 0.93, 4]  # [x, y, z] - set y to 1.7 for eye level
        self.camera_offset = [0, 0, 0]     # [x, y, z] - camera position relative to player (Cabeça)
        self.has_moved = False
        
        self.footstep_sounds = [
            pygame.mixer.Sound("sounds/footstep1.wav"),
            pygame.mixer.Sound("sounds/footstep2.wav"),
            pygame.mixer.Sound("sounds/footstep3.wav"),
            pygame.mixer.Sound("sounds/footstep4.wav"),
        ]

        self.footstep_sounds[0].set_volume(1.5)
        self.footstep_sounds[0].set_volume(1.5)
        self.footstep_sounds[0].set_volume(1.5)
        self.footstep_sounds[0].set_volume(1.5)

        self.footstep_cooldown = 0.8  
        self._footstep_timer = 0
        
        # Set initial position
        self.translate(*self.spawn_position)
        self._current_yaw = math.pi / 1.55
        
        # Setup camera
        self.camera = Camera(aspect_ratio=800/600)
        self._update_camera_transform()
        
        # Initialize mouse control
        self._center_mouse()

    def _update_camera_transform(self):
        """Update camera transform without recursion"""
        # Combine transformations manually:
        # 1. Player position
        position = Matrix.make_translation(*self.local_position)
        
        # 2. Yaw rotation (from MovementRig)
        yaw_rot = Matrix.make_rotation_y(self._current_yaw)
        
        # 3. Pitch rotation (from pitch node)
        pitch_rot = Matrix.make_rotation_x(self._current_pitch)
        height_offset = Matrix.make_translation(0, 1.7, 0)  # Eye level
        
        # Combine all transformations
        camera_transform = position @ yaw_rot @ height_offset @ pitch_rot
        self.camera.set_transform(camera_transform)

    def update(self, input_object, delta_time):
        if input_object is not None:
            moving = (
                input_object.is_key_pressed("w") or
                input_object.is_key_pressed("a") or
                input_object.is_key_pressed("s") or
                input_object.is_key_pressed("d")
            )

            if moving:
                self.has_moved = True
                self._footstep_timer -= delta_time
                if self._footstep_timer <= 0:
                    random.choice(self.footstep_sounds).play()
                    self._footstep_timer = self.footstep_cooldown
            else:
                self._footstep_timer = 0  # para que o som dispare imediatamente ao voltar a andar
            super().update(input_object, delta_time)
            
        self._update_camera_transform()
        
        if hasattr(input_object, 'mouse_rel') and input_object.mouse_rel != (0, 0):
            self._center_mouse()

    def get_camera(self):
        return self.camera

    def _center_mouse(self):
        if pygame.display.get_init():
            window_size = pygame.display.get_surface().get_size()
            pygame.mouse.set_pos(window_size[0]//2, window_size[1]//2)
    
    # Proper property implementation
    @property
    def mouse_sensitivity(self):
        return self._mouse_sensitivity

    @mouse_sensitivity.setter
    def mouse_sensitivity(self, value):
        self._mouse_sensitivity = value