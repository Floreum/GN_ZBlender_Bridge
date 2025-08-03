import bpy
import os


# This is a better approach
# Path to the OBJ file
obj_filepath = r"C:\Users\Floreum\Documents\export_test.obj"

# Get the mesh datablock to modify (the one with shape keys)
mesh_b = bpy.data.meshes.get("Mesh_B")

if not mesh_b:
    print("Mesh_B not found.")
elif not os.path.isfile(obj_filepath):
    print(f"File not found: {obj_filepath}")
else:
    # Import the OBJ using Blender 4.4's built-in importer
    bpy.ops.wm.obj_import(filepath=obj_filepath)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Get the imported mesh object
    imported_obj = bpy.context.selected_objects[0] if bpy.context.selected_objects else None

    if not imported_obj or imported_obj.type != 'MESH':
        print("No valid mesh object was imported.")
    else:
        imported_mesh = imported_obj.data

        # Check vertex count compatibility
        if len(imported_mesh.vertices) != len(mesh_b.vertices):
            print("ERROR: Imported mesh and Mesh_B have different vertex counts.")
        else:
            # Get the object that uses Mesh_B
            target_obj = next((o for o in bpy.data.objects if o.data == mesh_b), None)

            if not target_obj:
                print("No object found using Mesh_B.")
            else:
                # Make sure Mesh_B has shape keys
                if not mesh_b.shape_keys:
                    target_obj.shape_key_add(name="Basis", from_mix=False)

                basis_key = mesh_b.shape_keys.key_blocks["Basis"]

                # Copy vertex positions from imported mesh to Basis of Mesh_B
                for i, vert in enumerate(imported_mesh.vertices):
                    basis_key.data[i].co = vert.co

                print(f"Successfully replaced geometry of Mesh_B using imported OBJ.")

        # Clean up: remove the imported temporary object and mesh
        bpy.data.objects.remove(imported_obj, do_unlink=True)
        bpy.data.meshes.remove(imported_mesh, do_unlink=True)
