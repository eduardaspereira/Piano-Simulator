from geometry.geometry import Geometry
from core.obj_reader import my_obj_reader, my_mtl_reader

class CustomGeometry:
    def __init__(self, obj_file, mtl_file=None):
        vertices, texture_coords, normals, objects = my_obj_reader(obj_file)
        materials = my_mtl_reader(mtl_file) if mtl_file else {}

        self.meshes = []
        self.objects = objects     
        self.materials = materials 

        for object_name, obj_data in objects.items():
            geometry = Geometry()
            
            geometry.attribute_data = {"object_names": [object_name]}

            position_data = []
            color_data = []
            uv_data = []
            normal_data = []

            for (face, uv_face, normal_face), material_name in zip(obj_data['faces'], obj_data['material_indices']):
                material = materials.get(material_name, {
                    'diffuse': [0.8, 0.8, 0.8]
                })

                for j, vertex_idx in enumerate(face):
                    position_data.append(vertices[vertex_idx])
                    color_data.append(material['diffuse'])

                    if uv_face and j < len(uv_face) and uv_face[j] is not None:
                        uv_data.append(texture_coords[uv_face[j]])
                    else:
                        uv_data.append([0.0, 0.0])

                    if normal_face and j < len(normal_face) and normal_face[j] is not None:
                        normal_data.append(normals[normal_face[j]])
                    else:
                        normal_data.append([0.0, 0.0, 0.0])

            geometry.add_attribute("vec3", "vertexPosition", position_data)
            geometry.add_attribute("vec3", "vertexColor", color_data)
            geometry.add_attribute("vec2", "vertexUV", uv_data)
            geometry.add_attribute("vec3", "vertexNormal", normal_data)
            geometry.count_vertices()

            self.meshes.append(geometry)
