import math
import pygame
from components.player import Player
from core.base import Base
from core.matrix import Matrix
from core_ext.mesh import Mesh
from core_ext.renderer import Renderer
from core_ext.scene import Scene
from core_ext.texture import Texture
from extras.directional_light import DirectionalLightHelper
from geometry.cenario import Cenario
from geometry.piano import Piano
from geometry.rectangle import RectangleGeometry
from geometry.sphere import SphereGeometry
from light.ambient import AmbientLight
from light.directional import DirectionalLight
from light.point import PointLight
from material.phong import PhongMaterial
from material.texture import TextureMaterial

# main.py
class Example(Base):
    def __init__(self, screen_size=None, screen=None):
        super().__init__(screen_size, screen)
        self.screen_size = screen_size
        self.game_active = False

    def initialize(self):
        print("Initializing program...")
        self.renderer = Renderer()
        self.scene = Scene()
        self.number_of_lights = 3
        
        ambient_light = AmbientLight(color=[0.1, 0.1, 0.1])
        self.scene.add(ambient_light)
        
        self.directional_light = DirectionalLight(color=(0.2, 0.2, 0.2), direction=(-1, -1, -1))
        self.directional_light.set_position([4, 10, 4])
        self.directional_light.rotate_y(-math.pi/1.8, False)
        self.scene.add(self.directional_light)

        self.pointLight = PointLight(color=(1.3, 1.15, 1.0), position=(4, 10, -2), attenuation=(1.0,0.05,0.005))
        self.pointLight.rotate_y(3)
        self.pointLight.rotate_x(1.9)
        self.scene.add(self.pointLight)
        
        #direct_helper = DirectionalLightHelper(self.directional_light)
        #self.directional_light.add(direct_helper)
        #direct_helperp = DirectionalLightHelper(self.pointLight)
        #self.pointLight.add(direct_helperp)
        
        self.player = Player()
        self.player.set_position([15,3,-8])
        self.player.mouse_sensitivity = 0.004
        
        self.piano = Piano(self.number_of_lights)
        self.piano.set_position([4, 2.93, -4])
        self.piano.scale(1.2)
        
        pygame.mouse.set_pos(400, 300)
        self.create_environment()
        self.renderer.enable_shadows(self.directional_light, resolution=(1024,1024))
        self.start_game()

    def create_environment(self):
        # Sky
        sky_material = PhongMaterial(
            texture=Texture("images/solidblack.jpg"),
            number_of_light_sources=self.number_of_lights,
            use_shadow=True,
        )

        sky_geometry = SphereGeometry(radius=200)
        self.sky = Mesh(sky_geometry, sky_material)
        self.scene.add(self.sky)
        
        # Carrega o cenário
        self.cenario = Cenario(self.number_of_lights)
        self.cenario.rotate_y(90)
        self.scene.add(self.cenario)

    def start_game(self):
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
        self.scene.add(self.player)
        self.scene.add(self.piano)
        self.game_active = True

    def update(self):
        camera = self.player.get_camera()
        
        using_piano, near_piano = self.piano.check_interaction(self.player, self.input, camera)

        if not using_piano:
            self.player.update(self.input, self.delta_time)
        else:
            self.player.update(None, self.delta_time)

        self.piano.update(self.input if using_piano else None, self.delta_time)
        self.cenario.update(self.delta_time, self.player.has_moved)
        self.renderer.render(self.scene, camera)

Example(screen_size=[1920, 1080]).run()