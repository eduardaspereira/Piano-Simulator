import time
import pygame
from core_ext.object3d import Object3D
from core_ext.mesh import Mesh
from geometry.custom import CustomGeometry
from material.phong import PhongMaterial
from core_ext.texture import Texture

class Cenario(Object3D):
    def __init__(self, number_of_lights):
        super().__init__()
        
        # Cria um objeto pai para o cenário
        self.cenario_parent = Object3D()
        self.add(self.cenario_parent)
        
        # Fator de escala para o cenário
        scale_factor = 2.0
        self.cenario_parent.scale(scale_factor)
        
        # Variáveis para animação das cortinas
        self.curtain_meshes = {}  # Armazena as cortinas
        self.curtain_animation_start_time = 1.0  # Começa após 1 segundo
        self.curtain_animation_duration = 5.0  # Duração total da animação (3 segundos)
        self.curtain_animation_started = False
        pygame.mixer.init()
        self.curtain_sound = pygame.mixer.Sound("sounds/cortina.wav")

        # Carrega os modelos do cenário principal
        self.load_main_scene(number_of_lights)
        
        # Carrega as cortinas separadamente
        self.load_curtains(number_of_lights)
    
    def load_main_scene(self, number_of_lights):
        """Carrega o cenário principal sem as cortinas"""
        cenario_data = CustomGeometry('models/cenarioFinal.obj', 'models/cenarioFinal.mtl')
        
        # Pré-carrega todas as texturas que vamos usar
        self.gold_texture = Texture("images/blackkeys.png")
        self.sky_texture = Texture("images/palco.jpg") 
        self.crate_texture = Texture("images/blackkeys.png")
        self.solid_black = Texture("images/solidblack.png")
        
        # Cria os materiais que serão usados
        self.gold_material = PhongMaterial(
            texture=self.gold_texture,
            number_of_light_sources=number_of_lights,
            use_shadow=True,
            property_dict={
                "specularStrength": 0.8,
                "shininess": 128.0
            }
        )
        
        self.sky_material = PhongMaterial(
            texture=self.sky_texture,
            number_of_light_sources=number_of_lights,
            use_shadow=True,
            property_dict={
                "specularStrength": 0.5,
                "shininess": 64.0
            }
        )
        
        self.crate_material = PhongMaterial(
            texture=self.crate_texture,
            number_of_light_sources=number_of_lights,
            use_shadow=True,
            property_dict={
                "specularStrength": 0.3,
                "shininess": 32.0
            }
        )
        
        self.black_material = PhongMaterial(
            texture=self.solid_black,
            number_of_light_sources=number_of_lights,
            use_shadow=True
        )
        
        # Processa cada mesh do cenário principal
        for geometry in cenario_data.meshes:
            object_names = geometry.attribute_data.get("object_names", [])
            
            # Determina qual material usar baseado no nome do objeto
            if any("parede" in name.lower() or "wall" in name.lower() for name in object_names):
                mesh = Mesh(geometry, self.gold_material)
            elif any("palco" in name.lower() or "stage" in name.lower() for name in object_names):
                mesh = Mesh(geometry, self.sky_material)
            elif any("chão" in name.lower() or "floor" in name.lower() or "ground" in name.lower() for name in object_names):
                mesh = Mesh(geometry, self.black_material)
            else:
                # Material padrão para outros objetos
                mesh = Mesh(geometry, self.crate_material)
            
            self.cenario_parent.add(mesh)
    
    def load_curtains(self, number_of_lights):
        """Carrega e configura as cortinas para animação"""
        curtain_data = CustomGeometry('models/curtain.obj')
        self.curtain_texture = Texture("images/cortina.jpg")
        
        self.curtain_material = PhongMaterial(
            texture=self.curtain_texture,
            number_of_light_sources=number_of_lights,
            use_shadow=True,
            property_dict={
                "specularStrength": 0.4,
                "shininess": 48.0
            }
        )
        
        # Configuração das cortinas
        curtain_config = {
            "Curtain.001": {
                "target_x": 5.0,
                "speed": 5.0 / self.curtain_animation_duration  # Distância / tempo = unidades por segundo
            },
            "Curtain.002": {
                "target_x": -6.0,
                "speed": 6.0 / self.curtain_animation_duration  # Distância / tempo = unidades por segundo
            }
        }
        
        # Cria e configura cada cortina
        for geometry in curtain_data.meshes:
            object_names = geometry.attribute_data.get("object_names", [])
            
            for name in object_names:
                name_lower = name.lower()
                if "curtain.001" in name_lower or "curtain.002" in name_lower:
                    mesh = Mesh(geometry, self.curtain_material)
                    self.cenario_parent.add(mesh)
                    
                    # Armazena informações para animação
                    curtain_id = "Curtain.001" if "curtain.001" in name_lower else "Curtain.002"
                    config = curtain_config[curtain_id]
                    
                    self.curtain_meshes[curtain_id] = {
                        "mesh": mesh,
                        "original_x": mesh.local_position[0],
                        "target_x": config["target_x"],
                        "speed": config["speed"],
                        "current_x": mesh.local_position[0]
                    }
        
    def update(self, delta_time, player_has_moved=False):
        # Só começa a contar quando o player se mover
        if not player_has_moved:
            return
        
        # Inicia o timer no primeiro movimento
        if not hasattr(self, 'movement_start_time'):
            self.movement_start_time = time.time()
        
        current_time = time.time() - self.movement_start_time
        
        # Verifica se já é hora de começar a animação
        if not self.curtain_animation_started and current_time > self.curtain_animation_start_time:
            self.curtain_animation_started = True
            self.animation_start_time = current_time
            self.curtain_sound.play()
        
        # Restante da animação (mantido igual)
        if self.curtain_animation_started:
            animation_progress = (current_time - self.animation_start_time) / self.curtain_animation_duration
            
            if animation_progress < 1.0:
                for curtain_id, curtain_data in self.curtain_meshes.items():
                    mesh = curtain_data["mesh"]
                    original_x = curtain_data["original_x"]
                    target_x = curtain_data["target_x"]
                    new_x = original_x + (target_x - original_x) * animation_progress
                    current_pos = mesh.local_position
                    mesh.set_position([new_x, current_pos[1], current_pos[2]])
            else:
                for curtain_id, curtain_data in self.curtain_meshes.items():
                    mesh = curtain_data["mesh"]
                    target_x = curtain_data["target_x"]
                    current_pos = mesh.local_position
                    mesh.set_position([target_x, current_pos[1], current_pos[2]])