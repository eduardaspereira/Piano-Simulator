# components/button.py
from core_ext.mesh import Mesh
from geometry.screen import ScreenRectangleGeometry
from material.screen import ScreenMaterial
from material.texture import TextureMaterial
from extras.text_texture import TextTexture  # Your custom text texture class

class Button:
    def __init__(self, text, position, size, color, hover_color):
        self.text = text
        self.position = position  # [x, y] in NDC (-1 to 1)
        self.size = size          # [width, height] in NDC
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
        # Create button background mesh (colored rectangle)
        self.geometry = ScreenRectangleGeometry(width=size[0], height=size[1])
        self.material = ScreenMaterial()
        self.material.uniform_dict["color"].data = color
        self.mesh = Mesh(self.geometry, self.material)
        self.mesh.set_position([position[0], position[1], 0])

        # Create text texture and mesh - IMPORTANT: Set is_screen_space=True
        self.text_texture = TextTexture(
            text=text,
            font_size=32,
            font_color=(255, 255, 255),
            background_color=(0, 0, 0, 0),
            transparent=True
        )
        self.text_material = TextureMaterial(texture=self.text_texture, is_screen_space=True)  # Add this parameter
        self.text_geometry = ScreenRectangleGeometry(width=size[0] * 0.8, height=size[1] * 0.5)
        self.text_mesh = Mesh(self.text_geometry, self.text_material)
        self.text_mesh.set_position([position[0], position[1], 0.1])

    def check_hover(self, mouse_pos_ndc):
        """Check if mouse is hovering over the button"""
        x, y = mouse_pos_ndc
        left = self.position[0] - self.size[0]/2
        right = self.position[0] + self.size[0]/2
        bottom = self.position[1] - self.size[1]/2
        top = self.position[1] + self.size[1]/2
        
        self.is_hovered = (left <= x <= right) and (bottom <= y <= top)
        self.material.uniform_dict["color"].data = self.hover_color if self.is_hovered else self.color
        return self.is_hovered

    def is_clicked(self, mouse_pos_ndc, mouse_clicked):
        """Check if button is clicked"""
        return self.check_hover(mouse_pos_ndc) and mouse_clicked