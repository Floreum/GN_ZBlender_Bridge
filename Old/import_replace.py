import bpy
import os
import mathutils

obj_filepath = r"C:\Users\Floreum\Documents\export_test.obj"
target_name = "Mesh_A"

if not os.path.isfile(obj_filepath):
    print(f"File not found: {obj_filepath}")
else:
    bpy.ops.wm.obj_import(filepath=obj_filepath)
    imported_obj = bpy.context.selected_objects[0] if bpy.context.selected_objects else None

    if not imported_obj:
        print("No object imported.")
    else:
        print(f"Imported object rotation: {imported_obj.rotation_euler}")

        target_obj = bpy.data.objects.get(target_name)
        if not target_obj:
            print(f"Target object '{target_name}' not found.")
            bpy.data.objects.remove(imported_obj, do_unlink=True)
        else:
            if len(imported_obj.data.vertices) != len(target_obj.data.vertices):
                print(f"Vertex count mismatch: source={len(imported_obj.data.vertices)}, target={len(target_obj.data.vertices)}")
                bpy.data.objects.remove(imported_obj, do_unlink=True)
            else:
                basis = target_obj.data.shape_keys.key_blocks.get("Basis")
                if not basis:
                    print("BASIS shape key not found!")
                    bpy.data.objects.remove(imported_obj, do_unlink=True)
                else:
                    # Get rotation matrix from imported object
                    rot_matrix = imported_obj.rotation_euler.to_matrix().to_4x4()

                    for i, v in enumerate(imported_obj.data.vertices):
                        # Convert vertex coord to 4D vector
                        vec = v.co.to_4d()
                        # Apply imported rotation matrix to vertex
                        transformed_vec = rot_matrix @ vec
                        basis.data[i].co = transformed_vec.to_3d()

                    target_obj.data.update()
                    target_obj.data.shape_keys.key_blocks.update()

                    # Reset target object rotation to identity
                    target_obj.rotation_euler = (0.0, 0.0, 0.0)

                    bpy.data.objects.remove(imported_obj, do_unlink=True)

                    print(f"BASIS shape key replaced with rotation baked into vertices; target rotation reset.")
