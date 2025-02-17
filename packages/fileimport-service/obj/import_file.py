
import json
from specklepy.objects import Base
from specklepy.objects.other import RenderMaterial
from specklepy.objects.geometry import Mesh, Point, Line
from specklepy.transports.server import ServerTransport
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.api import operations

import sys, os

from obj_file import ObjFile

TMP_RESULTS_PATH = '/tmp/import_result.json'
DEFAULT_BRANCH = 'uploads'

def convert_material(obj_mat):
    speckle_mat = RenderMaterial()
    speckle_mat.name = obj_mat['name']
    if 'diffuse' in obj_mat:
        argb = [1,] + obj_mat['diffuse']
        speckle_mat.diffuse = int.from_bytes([int(val * 255) for val in argb], byteorder="big", signed=True)
    if 'dissolved' in obj_mat:
        speckle_mat.opacity = obj_mat['dissolved']
    return speckle_mat

def import_obj():
    file_path, user_id, stream_id, branch_name, commit_message = sys.argv[1:]
    print(f'ImportOBJ argv[1:]: {sys.argv[1:]}')

    # Parse input
    obj = ObjFile(file_path)
    print(f'Parsed obj with {len(obj.faces)} faces ({len(obj.vertices) * 3} vertices)')

    speckle_root = Base()
    speckle_root['@objects'] = []

    for objname in obj.objects:
        print(f'  Converting {objname}...')

        speckle_obj = Base()
        speckle_obj.name = objname
        speckle_obj['@displayValue'] = []
        speckle_root['@objects'].append(speckle_obj)
        
        for obj_mesh in obj.objects[objname]:
            speckle_vertices = [coord for point in obj_mesh['vertices'] for coord in point]
            speckle_faces = []
            for obj_face in obj_mesh['faces']:
                if len(obj_face) == 3:
                    speckle_faces.append(0)
                elif len(obj_face) == 4:
                    speckle_faces.append(1)
                else:
                    speckle_faces.append(len(obj_face))
                speckle_faces.extend(obj_face)

            has_vertex_colors = False
            for vc in obj_mesh['vertex_colors']:
                if vc is not None:
                    has_vertex_colors = True
            colors = []
            if has_vertex_colors:
                for vc in obj_mesh['vertex_colors']:
                    if vc is None:
                        r, g, b = (1.0, 1.0, 1.0)
                    else:
                        r, g, b = vc
                    argb = (1.0, r, g, b)
                    color = int.from_bytes([int(val * 255) for val in argb], byteorder="big", signed=True)
                    colors.append(color)

            speckle_mesh = Mesh(
                vertices=speckle_vertices,
                faces=speckle_faces,
                colors=colors,
                textureCoordinates=[]
            )

            obj_material = obj_mesh['material']
            if obj_material:
                speckle_mesh['renderMaterial'] = convert_material(obj_material)

            speckle_obj['@displayValue'].append(speckle_mesh)

    # Commit

    client = SpeckleClient(host=os.getenv('SPECKLE_SERVER_URL', 'localhost:3000'), use_ssl=False)
    client.authenticate(os.environ['USER_TOKEN'])

    if not client.branch.get(stream_id, branch_name):
        client.branch.create(stream_id, branch_name, 'File upload branch' if branch_name == 'uploads' else '')

    transport = ServerTransport(client=client, stream_id=stream_id)
    id = operations.send(base=speckle_root, transports=[transport])

    commit_id = client.commit.create(
        stream_id=stream_id,
        object_id=id,
        branch_name=(branch_name or DEFAULT_BRANCH),
        message=(commit_message or 'OBJ file upload'),
        source_application='OBJ'
    )

    return commit_id


if __name__ == '__main__':
    try:
        commit_id = import_obj()
        if not commit_id:
            raise Exception("Can't create commit")
        results = {'success': True, 'commitId': commit_id}
    except Exception as ex:
        print('ERROR: ' + str(ex))
        results = {'success': False, 'error': str(ex)}

    with open(TMP_RESULTS_PATH, 'w') as f:
        json.dump(results, f)
