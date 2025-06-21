import math
from core_ext.texture import Texture
from geometry.custom import CustomGeometry
from core_ext.object3d import Object3D
from core_ext.mesh import Mesh
from material.phong import PhongMaterial
import pygame
import time

class Piano(Object3D):
    def __init__(self, number_of_lights):
        super().__init__()
        
        # Interaction properties
        self.interaction_radius = 2.0
        self.interaction_pos = [0.70, 0, 2.0]
        self.using_piano = False
        self.original_mouse_grab = True
        self.number_of_lights=number_of_lights
        
        # Animation properties
        self.animating_to_piano = False
        self.animation_start_time = 0
        self.animation_duration = 0.5
        self.player_start_pos = None
        self.player_target_pos = None
        self.player_ref = None
        self.player_start_yaw = None
        self.player_target_yaw = None
        self.player_start_pitch = None
        self.player_target_pitch = None

        
        pygame.mixer.init()
        pygame.mixer.set_num_channels(32)
        self.sound_notes = {}
        self.sound_channels = {}
        self.release_duration = 1.0
        
        self.load_sounds()
        
        geometry = CustomGeometry("models/Piano.obj", "models/Piano.mtl")
        bench_data = CustomGeometry('models/BancoPiano.obj', 'models/BancoPiano.mtl')
        
        self.key_mapping = {
            'a': ('White_Keys.019', 'F4'),
            's': ('White_Keys.020', 'G4'),
            'd': ('White_Keys.021', 'A4'),
            'f': ('White_Keys.022', 'B4'),
            'g': ('White_Keys.023', 'C5'),
            'h': ('White_Keys.024', 'D5'),
            'j': ('White_Keys.025', 'E5'),
            'k': ('White_Keys.026', 'F5'),
            'l': ('White_Keys.027', 'G5'),
            'ç': ('White_Keys.028', 'A5'),
            'º': ('White_Keys.029', 'B5'),
            '~': ('White_Keys.030', 'C6'),
            
            'w': ('Black_Keys.013', 'Gb4'),
            'e': ('Black_Keys.014', 'Ab4'),
            'r': ('Black_Keys.015', 'Bb4'),
            't': ('Black_Keys.016', 'Db5'),
            'y': ('Black_Keys.017', 'Eb5'),
            'i': ('Black_Keys.018', 'Gb5'),
            'o': ('Black_Keys.019', 'Ab5'),
            'p': ('Black_Keys.020', 'Bb5'),
        }

        self.initialize_piano(geometry)
        self.initialize_bench(bench_data)
         

    def initialize_bench(self, bench_data):
        self.bench_parent = Object3D()
        self.add(self.bench_parent)
        scale_factor = 2.0
        self.bench_parent.scale(scale_factor)
        bench_position = [0.1, -0.95, 2.2]
        self.bench_parent.set_position(bench_position)

        # Define materials
        body_material = PhongMaterial(
            texture=Texture("images/solidblack.png"),
            number_of_light_sources=self.number_of_lights,
            use_shadow=True
        )
        
        gold_material = PhongMaterial(
            texture=Texture("images/gold.jpg"),
            number_of_light_sources=self.number_of_lights,
            use_shadow=True,
            property_dict={
                "specularStrength": 0.8,
                "shininess": 128.0
            }
        )
        
        leather_material = PhongMaterial(
            texture=Texture("images/blackkeys.png"),
            number_of_light_sources=self.number_of_lights,
            use_shadow=True,
            property_dict={
                "specularStrength": 0.3,
                "shininess": 32.0
            }
        )

        for geometry in bench_data.meshes:
            object_names = geometry.attribute_data.get("object_names", [])
            
            if any("foot" in name.lower() for name in object_names):
                mesh = Mesh(geometry, gold_material)
            elif any("leather" in name.lower() for name in object_names):
                mesh = Mesh(geometry, leather_material)
            else:
                mesh = Mesh(geometry, body_material)
                
            self.bench_parent.add(mesh)

    def initialize_piano(self, geometry):
        self.key_meshes = {}
        self.key_targets = {}
        self.key_speeds = {}
        self.key_original_positions = {}
        self.key_press_times = {}
        self.key_release_times = {}

        # Define all materials
        body_material = PhongMaterial(
            texture=Texture("images/solidblack.png"),
            number_of_light_sources=self.number_of_lights,
            use_shadow=True
        )
        
        whitekey_material = PhongMaterial(
            property_dict={
                "useVertexColors": True,
                "doubleSide": True,
                "specularStrength": 0.5,
                "shininess": 64.0,
            },
            number_of_light_sources=self.number_of_lights,
            use_shadow=True
        )

        blackkey_material = PhongMaterial(
            texture=Texture("images/blackkeys.png"),
            number_of_light_sources=self.number_of_lights,
            use_shadow=True
        )

        gold_material = PhongMaterial(
            texture=Texture("images/gold.jpg"),
            number_of_light_sources=self.number_of_lights,
            use_shadow=True,
            property_dict={
                "specularStrength": 0.8,
                "shininess": 128.0
            }
        )

        for i, mesh_geom in enumerate(geometry.meshes):
            object_names = mesh_geom.attribute_data.get("object_names", [])
            
            # Check for special gold parts first
            if "Pedals" in object_names or "Plane.001" in object_names:
                mesh = Mesh(mesh_geom, gold_material)
            # Then check for keys
            elif any("White_Keys" in name for name in object_names):
                mesh = Mesh(mesh_geom, whitekey_material)
                # Add to key mapping if it's a mapped white key
                self._add_to_key_mapping(mesh_geom, mesh, object_names)
            elif any("Black_Keys" in name for name in object_names):
                mesh = Mesh(mesh_geom, blackkey_material)
                # Add to key mapping if it's a mapped black key
                self._add_to_key_mapping(mesh_geom, mesh, object_names)
            else:
                mesh = Mesh(mesh_geom, body_material)

            self.add(mesh)

    def _add_to_key_mapping(self, mesh_geom, mesh, object_names):
        """Helper method to add keys to the mapping dictionary"""
        for key_name, (mesh_name, note) in self.key_mapping.items():
            if mesh_name in object_names:
                self.key_meshes[key_name] = mesh
                self.key_targets[key_name] = -0.025
                self.key_speeds[key_name] = 0.6
                self.key_original_positions[key_name] = mesh.local_position.copy()
                self.key_press_times[key_name] = 0
                self.key_release_times[key_name] = 0

    def load_sounds(self):
        notes = ['F4', 'G4', 'A4', 'B4', 'C5', 'D5', 'E5', 'F5', 'G5', 'A5', 'B5', 'C6',
             'Gb4', 'Ab4', 'Bb4', 'Db5', 'Eb5', 'Gb5', 'Ab5', 'Bb5']
        for note in notes:
            try:
                sound = pygame.mixer.Sound(f'sounds/{note}.wav')
                sound.set_volume(1.0)
                self.sound_notes[note] = sound
                self.sound_channels[note] = pygame.mixer.Channel(notes.index(note))
            except Exception as e:
                print(f"Error loading sound {note}: {str(e)}")
                self.sound_notes[note] = None

    def check_interaction(self, player, input_object, camera):
        player_pos = player.local_position
        bench_global_pos = (self.global_matrix @ [*self.interaction_pos, 1])[:3]
        near_piano = (player_pos[0]-bench_global_pos[0])**2 + (player_pos[2]-bench_global_pos[2])**2 < self.interaction_radius**2

        if input_object.is_key_down(' ') and near_piano:
            self.using_piano = not self.using_piano
            if self.using_piano:
                self.animating_to_piano   = True
                self.animation_start_time = time.time()
                self.player_start_pos     = player_pos.copy()
                self.player_target_pos    = [bench_global_pos[0] - 0.08, bench_global_pos[1], bench_global_pos[2]]
                direction_x = self.player_target_pos[0] - player_pos[0]
                direction_z = self.player_target_pos[2] - player_pos[2]
                angle_radians = math.atan2(direction_z, direction_x)
                self.player_target_yaw = 0.0                 
                self.player_ref           = player 
                self.player_start_yaw = player._current_yaw
                self.player_start_pitch = self.player_ref._current_pitch
                self.player_target_pitch = -math.radians(45) 
                self.original_mouse_grab  = pygame.event.get_grab()
                pygame.event.set_grab(False)
                pygame.mouse.set_visible(True)
            else:
                pygame.event.set_grab(self.original_mouse_grab)
                pygame.mouse.set_visible(False)


        return self.using_piano, near_piano

    def update(self, input_object, delta_time):
        if input_object is None:
            return
        current_time = time.time()

        if self.animating_to_piano and self.player_ref:
            elapsed = current_time - self.animation_start_time
            t = min(elapsed / self.animation_duration, 1.0) 

            # Posição do Player
            new_x = (1 - t) * self.player_start_pos[0] + t * self.player_target_pos[0]
            new_y = (1 - t) * self.player_start_pos[1] + t * self.player_target_pos[1]
            new_z = (1 - t) * self.player_start_pos[2] + t * self.player_target_pos[2]
            self.player_ref.set_position([new_x, new_y, new_z])

            # Camera Posição Horizontal
            start_yaw = self.player_start_yaw
            end_yaw = self.player_target_yaw
            delta_yaw = (end_yaw - start_yaw + math.pi) % (2 * math.pi) - math.pi
            current_yaw = start_yaw + delta_yaw * t
            self.player_ref._current_yaw = current_yaw
            
            # Camera Posição Vertical
            start_pitch = self.player_start_pitch
            end_pitch = self.player_target_pitch
            delta_pitch = end_pitch - start_pitch
            current_pitch = start_pitch + delta_pitch * t
            self.player_ref._current_pitch = current_pitch

            if t >= 1.0:
                self.animating_to_piano = False

        for key_name, mesh in self.key_meshes.items():
            mesh_name, note = self.key_mapping[key_name]
            current_pos = mesh.local_position

            if input_object.is_key_pressed(key_name):
                target_y = self.key_original_positions[key_name][1] + self.key_targets[key_name]
                if current_pos[1] > target_y:
                    new_y = max(target_y, current_pos[1] - self.key_speeds[key_name] * delta_time)
                    mesh.set_position([current_pos[0], new_y, current_pos[2]])

                if self.key_press_times[key_name] == 0:
                    self.key_press_times[key_name] = current_time
                    if self.sound_notes.get(note):
                        if self.sound_channels[note].get_busy():
                            self.sound_channels[note].stop()
                        self.sound_channels[note].play(self.sound_notes[note])
            else:
                original_y = self.key_original_positions[key_name][1]
                if current_pos[1] < original_y:
                    new_y = min(original_y, current_pos[1] + self.key_speeds[key_name] * delta_time)
                    mesh.set_position([current_pos[0], new_y, current_pos[2]])

                if self.key_press_times[key_name] > 0:
                    self.key_release_times[key_name] = current_time
                    self.key_press_times[key_name] = 0

                if (self.key_release_times[key_name] > 0 and
                    current_time - self.key_release_times[key_name] > self.release_duration and
                    self.sound_channels[note].get_busy()):
                    self.sound_channels[note].fadeout(1000)
                    self.key_release_times[key_name] = 0