import OpenGL.GL as GL
from material.material import Material


class HybridMaterial(Material):
    def __init__(self, texture, property_dict={}, use_vertex_colors=True):
        vertex_shader_code = """
        uniform mat4 projectionMatrix;
        uniform mat4 viewMatrix;
        uniform mat4 modelMatrix;
        in vec3 vertexPosition;
        in vec3 vertexColor;
        in vec2 vertexUV;

        uniform vec2 repeatUV;
        uniform vec2 offsetUV;

        out vec2 UV;
        out vec3 color;

        void main()
        {
            gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(vertexPosition, 1.0);
            UV = vertexUV * repeatUV + offsetUV;
            color = vertexColor;
        }
        """

        fragment_shader_code = """
        uniform vec3 baseColor;
        uniform sampler2D texture;
        uniform bool useVertexColors;
        in vec2 UV;
        in vec3 color;
        out vec4 fragColor;

        void main()
        {
            vec4 texColor = texture2D(texture, UV);
            vec4 base = vec4(baseColor, 1.0);

            if (useVertexColors) {
                base *= vec4(color, 1.0);
            }

            fragColor = base * texColor;

            if (fragColor.a < 0.1) discard;
        }
        """

        super().__init__(vertex_shader_code, fragment_shader_code)

        self.add_uniform("vec3", "baseColor", [1.0, 1.0, 1.0])
        self.add_uniform("sampler2D", "texture", [texture.texture_ref, 1])
        self.add_uniform("vec2", "repeatUV", [1.0, 1.0])
        self.add_uniform("vec2", "offsetUV", [0.0, 0.0])
        self.add_uniform("bool", "useVertexColors", use_vertex_colors)
        
        self.locate_uniforms()
        
        self.setting_dict["doubleSide"] = True
        self.setting_dict["wireframe"] = False
        self.setting_dict["lineWidth"] = 1
        self.set_properties(property_dict)

    def update_render_settings(self):
        if self.setting_dict["doubleSide"]:
            GL.glDisable(GL.GL_CULL_FACE)
        else:
            GL.glEnable(GL.GL_CULL_FACE)
        
        if self.setting_dict["wireframe"]:
            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
        else:
            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        
        GL.glLineWidth(self.setting_dict["lineWidth"])
