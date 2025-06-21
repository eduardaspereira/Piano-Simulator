from typing import List, Tuple, Dict

def my_obj_reader(filename: str) -> Tuple[List, List, List, Dict]:
    """Get vertices, texture coordinates, normals and faces grouped by object"""
    vertices = []
    texture_coords = []
    normals = []
    objects = {}  
    current_object = None
    current_material = None

    with open(filename, 'r') as in_file:
        for line in in_file:
            if line.startswith('o '):
                current_object = line.strip().split()[1]
                objects[current_object] = {'faces': [], 'material_indices': [], 'name': current_object}  # Store name
            elif line.startswith('v '):
                point = [float(value) for value in line.strip().split()[1:]]
                vertices.append(point)
            elif line.startswith('vt '):
                uv = [float(value) for value in line.strip().split()[1:]]
                texture_coords.append(uv)
            elif line.startswith('vn '):
                normal = [float(value) for value in line.strip().split()[1:]]
                normals.append(normal)
            elif line.startswith('f '):
                if current_object is None:
                    current_object = "default"
                    objects[current_object] = {'faces': [], 'material_indices': []}
                
                face = []
                uv_face = []
                normal_face = []
                for vertex in line.strip().split()[1:]:
                    indices = vertex.split('/')
                    
                    v_index = int(indices[0]) - 1
                    face.append(v_index)
                    
                    if len(indices) > 1 and indices[1] != '':
                        vt_index = int(indices[1]) - 1
                        uv_face.append(vt_index)
                    else:
                        uv_face.append(None)

                    if len(indices) > 2 and indices[2] != '':
                        vn_index = int(indices[2]) - 1
                        normal_face.append(vn_index)
                    else:
                        normal_face.append(None)

                objects[current_object]['faces'].append((face, uv_face, normal_face))
                objects[current_object]['material_indices'].append(current_material)
            elif line.startswith('usemtl '):
                current_material = line.strip().split()[1]

    return vertices, texture_coords, normals, objects


def my_mtl_reader(filename: str) -> Dict:
    materials = {}
    current_material = None

    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if not parts:
                continue

            if parts[0] == 'newmtl':
                current_material = parts[1]
                materials[current_material] = {
                    'diffuse': [0.8, 0.8, 0.8],
                    'ambient': [0.2, 0.2, 0.2],
                    'specular': [0.0, 0.0, 0.0],
                    'shininess': 0.0,
                    'texture': None  # <- novo campo para textura
                }
            elif current_material:
                if parts[0] == 'Kd':
                    materials[current_material]['diffuse'] = [float(x) for x in parts[1:4]]
                elif parts[0] == 'Ka':
                    materials[current_material]['ambient'] = [float(x) for x in parts[1:4]]
                elif parts[0] == 'Ks':
                    materials[current_material]['specular'] = [float(x) for x in parts[1:4]]
                elif parts[0] == 'Ns':
                    materials[current_material]['shininess'] = float(parts[1])
                elif parts[0] == 'map_Kd':
                    materials[current_material]['texture'] = parts[1]  # caminho da textura

    return materials

