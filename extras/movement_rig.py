import math
import pygame
from core_ext.cameraPlayer import Camera
from core_ext.object3d import Object3D
from core.matrix import Matrix

class MovementRig(Object3D):
    """
    First-person movement rig with proper mouse look
    """
    def __init__(self, units_per_second=5, degrees_per_second=60, mouse_sensitivity=0.002):
        super().__init__()
        self._units_per_second = units_per_second
        self._degrees_per_second = degrees_per_second
        self._mouse_sensitivity = mouse_sensitivity
        self._max_pitch = math.pi/2 * 0.95 
        
        # Create pitch node (for up/down rotation)
        self._pitch_node = Object3D()
        self.add(self._pitch_node)
        
        # Track current pitch
        self._current_pitch = 0
        self._current_yaw = 0  # Track yaw separately
        self._current_pitch = 0

    @property
    def mouse_sensitivity(self):
        return self._mouse_sensitivity

    @mouse_sensitivity.setter
    def mouse_sensitivity(self, value):
        self._mouse_sensitivity = value

    def add(self, child):
        """Add objects to the pitch node"""
        self._pitch_node.add(child)

    def update(self, input_object, delta_time):
        move_amount = self._units_per_second * delta_time
        
        # Calculate movement direction based on yaw only
        forward = [0, 0, -1]  # -Z in world space
        right = [1, 0, 0]     # +X in world space
        
        # Apply movement
        if input_object.is_key_pressed("w"):
            self.translate(forward[0]*move_amount, forward[1]*move_amount, forward[2]*move_amount)
        if input_object.is_key_pressed("s"):
            self.translate(-forward[0]*move_amount, -forward[1]*move_amount, -forward[2]*move_amount)
        if input_object.is_key_pressed("a"):
            self.translate(-right[0]*move_amount, -right[1]*move_amount, -right[2]*move_amount)
        if input_object.is_key_pressed("d"):
            self.translate(right[0]*move_amount, right[1]*move_amount, right[2]*move_amount)

        
        # Mouse look
        if hasattr(input_object, 'mouse_rel'):
            self._handle_mouse_look(input_object.mouse_rel)

    def _handle_mouse_look(self, mouse_rel):
        dx, dy = mouse_rel

        # Yaw rotation
        self._current_yaw -= dx * self._mouse_sensitivity
        # FIX: Preserve translation
        position = self.local_position
        self._matrix = Matrix.make_rotation_y(self._current_yaw)
        self.set_position(position)

        # Pitch rotation
        pitch_amount = -dy * self._mouse_sensitivity
        self._current_pitch = max(-self._max_pitch, min(self._max_pitch, self._current_pitch + pitch_amount))
        self._pitch_node._matrix = Matrix.make_rotation_x(self._current_pitch)
