from geometry.rectangle import RectangleGeometry

class ScreenRectangleGeometry(RectangleGeometry):
    def __init__(self, width=1, height=1):
        super().__init__()  # Skip parent init
        
        # Define vertices for a full quad (6 vertices for GL_TRIANGLES)
        position_data = [
            [0, 0, 0],       # Bottom-left
            [width, 0, 0],   # Bottom-right
            [width, height, 0],  # Top-right
            [0, 0, 0],       # Bottom-left (reused)
            [width, height, 0],  # Top-right (reused)
            [0, height, 0]   # Top-left
        ]
        
        # UV coordinates
        uv_data = [
            [0, 0], [1, 0], [1, 1],  # First triangle
            [0, 0], [1, 1], [0, 1]   # Second triangle
        ]
        
        self.add_attribute("vec3", "vertexPosition", position_data)
        self.add_attribute("vec2", "vertexUV", uv_data)
        self.count_vertices()