from material.material import Material

class ScreenMaterial(Material):
    def __init__(self, color=[1, 1, 1], alpha=1, texture=None):
        vertex_shader = """
        in vec3 vertexPosition;
        in vec2 vertexUV;
        uniform vec3 position;
        out vec2 UV;
        void main() {
            gl_Position = vec4(vertexPosition + position, 1.0);
            UV = vertexUV;
        }
        """
        fragment_shader = """
        in vec2 UV;
        uniform vec3 baseColor;
        uniform float alpha;
        uniform sampler2D textureSampler;
        out vec4 fragColor;
        void main() {
            vec4 texColor = texture(textureSampler, UV);
            // Discard fully transparent fragments
            if (texColor.a == 0.0) {
                discard;
            }
            fragColor = texColor * vec4(baseColor, alpha);
        }
        """
        super().__init__(vertex_shader, fragment_shader)
        self.add_uniform("vec3", "baseColor", color)
        self.add_uniform("float", "alpha", alpha)
        self.add_uniform("sampler2D", "textureSampler", [texture.texture_ref, 0] if texture else [-1, 0])
        self.add_uniform("vec3", "position", [0, 0, 0])