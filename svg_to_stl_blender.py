import bpy
import os
import sys
from mathutils import Color, Vector

# Change this item to increase the embossing of the symbols.
FOREGROUND_DEPTH_MM = 0.5

# Change this item to increase the thickness of the baseplate of the symbols.
BACKGROUND_DEPTH_MM = 1

# Don't edit below this line
# -------------------------------------

SCALE_FACTOR = 0.5
STL_EXPORT_SCALE = 1.0

def color_equal(color_a, color_b, epsilon=0.001):
    for component in [0, 1, 2]:
        if abs(color_a[component] - color_b[component]) > epsilon:
            return False
    return True

def create_stl(svg_filename, background_depth=BACKGROUND_DEPTH_MM/1000.0, foreground_depth=FOREGROUND_DEPTH_MM/1000.0, output_filename=None, scale_factor=SCALE_FACTOR, halo_radius=0.001):
    # Delete old collection
    for c in [c for c in bpy.context.scene.collection.children if c.name.startswith(os.path.splitext(svg_filename)[0])]:
        for obj in c.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(c)
    
    old_collections = [c for c in bpy.context.scene.collection.children]
    
    # Import SVG file
    bpy.ops.import_curve.svg(filepath=svg_filename, filter_glob='*.svg')
        
    new_collection = [c for c in bpy.context.scene.collection.children if c not in old_collections][0]
        
    # Get collection name
    new_collection.name = os.path.splitext(new_collection.name)[0]
    bg_object = None
    
    # Get curves
    for curve in new_collection.objects:
        if len(curve.data.materials) < 1 or curve.data.materials[0] is None:
            continue
        
        mat = curve.data.materials[0]
        
        if color_equal(mat.diffuse_color, Color((0, 0, 0))):
            # This is black
            curve.data.extrude = (foreground_depth + background_depth) * 0.5
            curve.location += Vector((0, 0, (foreground_depth + background_depth) * 0.5))
        else:
            # This is not black
            curve.data.extrude = background_depth * 0.5
            curve.location += Vector((0, 0, background_depth * 0.5))
            bg_object = curve
            pass
        
    # Offset to the origin
    bpy.ops.object.select_all(action='DESELECT')
    for obj in new_collection.objects:
        obj.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
    
    offset = (
        bg_object.location[0] if bg_object else 0,
        bg_object.location[1] if bg_object else 0,
        0.0
    )
        
    # new_collection.instance_offset = offset
    
    # Move to the offset and scale appropriately
    for obj in new_collection.objects:
        obj.location -= Vector((offset[0], offset[1], 0))
        
    bpy.ops.transform.resize(value=(SCALE_FACTOR, SCALE_FACTOR, 1.0))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    create_box=False

    if create_box:
        # Create bounding frame
        min_box = Vector((0, 0, 0))
        max_box = Vector((0, 0, 0))
        
        for obj in new_collection.objects:
            obj_min = Vector((obj.location[i] - (obj.dimensions[i] * 0.5) for i in range(3)))
            obj_max = Vector((obj.location[i] + (obj.dimensions[i] * 0.5) for i in range(3)))
            
            min_box=Vector((min(min_box[i], obj_min[i]) for i in range(3)))
            max_box=Vector((max(max_box[i], obj_max[i]) for i in range(3)))
            
        cube_size = max_box - min_box
            
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0), scale=(cube_size*1.0 + Vector((halo_radius * 2, halo_radius * 2, 0))))
        cube = bpy.context.active_object
        
        for other_col in cube.users_collection:
            other_col.objects.unlink(cube)
        new_collection.objects.link(cube)
        

        print(f'Cube size: {cube_size}')
        
        cube.dimensions[0] = cube_size[0]
        cube.dimensions[1] = cube_size[1]
        cube.dimensions[2] = background_depth
            
        cube.location = min_box + (cube_size * 0.5)
        cube.location[2] = background_depth * 0.5
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Export as an STL
    
    bpy.ops.object.select_all(action='DESELECT')
    for obj in new_collection.objects:
        obj.select_set(True)

    cwd = os.path.dirname(__file__)
    if not os.path.exists(os.path.join(cwd, 'STLs')):
        os.makedirs(os.path.join(cwd, 'STLs'), exist_ok=True)

    bpy.ops.wm.stl_export(
        filepath=os.path.join(cwd, 'STLs', output_filename if output_filename is not None else f'{new_collection.name}.stl'),
        check_existing=False,
        export_selected_objects=True,
        global_scale=STL_EXPORT_SCALE)
    

if __name__ == '__main__':
    if len(sys.argv) > 1:
        create_stl(svg_filename=sys.argv[-1])
    else:
        create_stl(svg_filename='enemy_artillery_regiment_STL.svg')