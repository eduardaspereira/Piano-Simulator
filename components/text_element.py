# text_element.py
from core_ext.mesh import Mesh
from geometry.screen import ScreenRectangleGeometry
from material.screen import ScreenMaterial  # Changed import
from extras.text_texture import TextTexture

class TextElement:
    def __init__(self, text, position, size, color=(255, 255, 255), font_size=32):
        self.text = text
        self.position = position  # [x, y] in NDC (-1 to 1)
        self.size = size          # [width, height] in NDC
        
        # Create text texture and mesh
        self.text_texture = TextTexture(
            text=text,
            font_size=font_size,
            font_color=color,
            background_color=(0, 0, 0, 0),  # Transparent background
            transparent=True
        )
        self.text_material = ScreenMaterial(texture=self.text_texture)  # Using ScreenMaterial
        self.text_geometry = ScreenRectangleGeometry(width=size[0], height=size[1])
        self.text_mesh = Mesh(self.text_geometry, self.text_material)
        self.text_mesh.set_position([position[0], position[1], 0])

    def check_click(self, mouse_pos_ndc, mouse_clicked):
        """Check if text is clicked"""
        x, y = mouse_pos_ndc
        left = self.position[0] - self.size[0]/2
        right = self.position[0] + self.size[0]/2
        bottom = self.position[1] - self.size[1]/2
        top = self.position[1] + self.size[1]/2
        
        return (left <= x <= right) and (bottom <= y <= top) and mouse_clicked