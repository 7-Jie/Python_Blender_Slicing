import bpy
import os

# Function to set up the environment and paths
def setup_paths():
    # Use placeholder paths; users should update these paths
    path_in = r"/path/to/your/input/directory"
    filename_in = "Assembly.stl"
    path_out = r"/path/to/your/output/directory"
    filename_out = "Assembly_{}.tif"
    
    filepath = os.path.join(path_in, filename_in)
    
    return filepath, path_out, filename_out

# Function to import STL file
def import_stl(filepath):
    bpy.ops.import_mesh.stl(filepath=filepath)
    obj = bpy.context.selected_objects[0]
    return obj

# Function to set up the object and plane
def setup_object_and_plane(obj):
    obj.rotation_euler = (0, 0, 0)
    obj.rotation_mode = 'XYZ'
    obj.data.transform(obj.matrix_world)

    bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
    bpy.context.scene.cursor.location = (0, 0, 0)

    bpy.ops.transform.rotate(value=1.5708, orient_axis='Y', orient_type='LOCAL')

    bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
    obj.location = (15, -15, 0)

    bpy.ops.object.mode_set(mode='OBJECT')

    if bpy.context.space_data.type == 'VIEW_3D':
        bpy.ops.view3d.snap_cursor_to_center()

    bpy.ops.mesh.primitive_plane_add()
    plane = bpy.context.object
    plane.scale = (30, 30, 0.06)
    
    return plane

# Function to apply boolean modifier
def apply_boolean_modifier(plane, stl_object):
    mod = plane.modifiers.new(type='BOOLEAN', name='Boolean')
    mod.object = stl_object
    mod.operation = 'INTERSECT'

# Function to set materials and background
def set_materials_and_background(plane):
    cross_section_material = bpy.data.materials.new(name="CrossSectionMaterial")
    plane.data.materials.append(cross_section_material)
    cross_section_material.diffuse_color = (0.01, 0.01, 0.01, 1)

    bpy.context.scene.world.use_nodes = True
    bg_node = bpy.context.scene.world.node_tree.nodes.new("ShaderNodeBackground")
    bg_node.inputs[0].default_value = (0.9, 0.9, 0.9, 1)

    world_output = bpy.context.scene.world.node_tree.nodes.get("World Output")
    bpy.context.scene.world.node_tree.links.new(bg_node.outputs[0], world_output.inputs[0])

# Function to set up the camera
def setup_camera():
    bpy.ops.object.camera_add(location=(0, 0, 60))
    bpy.data.cameras['Camera'].type = 'ORTHO'
    bpy.context.scene.camera = bpy.context.object
    bpy.data.objects["Camera"].location = (0, 0, 50)
    bpy.data.cameras['Camera'].ortho_scale = 2

# Function to render cross-sectional images
def render_cross_sections(plane, path_out, filename_out):
    bpy.context.scene.render.resolution_x = 350
    bpy.context.scene.render.resolution_y = 350

    for i in range(350):
        slice_L = 30
        slice_n = 350
        slice_dx = slice_L / (slice_n - 1)
        plane.location.z = i * slice_dx
        bpy.ops.object.modifier_apply(modifier='Boolean')
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        bpy.data.objects["Camera"].location = (0, 0, 50 + plane.location.z)
        bpy.data.cameras['Camera'].ortho_scale = 2

        file_path = os.path.join(path_out, filename_out.format(i))
        bpy.ops.render.render()
        bpy.data.images['Render Result'].save_render(file_path)

# Main function
def main():
    filepath, path_out, filename_out = setup_paths()
    
    try:
        obj = import_stl(filepath)
        plane = setup_object_and_plane(obj)
        apply_boolean_modifier(plane, obj)
        set_materials_and_background(plane)
        setup_camera()
        render_cross_sections(plane, path_out, filename_out)
        print("Rendering completed successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
