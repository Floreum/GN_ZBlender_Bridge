import bpy
import os
from bpy.types import Operator

bl_info = {
    "name": "Import/Export OBJ Bridge",
    "author": "Happy Customer. Edits by: Floreum",
    "version": (1, 3, 6),
    "blender": (4, 5, 0),
    "location": "File > Bridge Import / Bridge Export",
    "description": "Imports or Exports selected OBJ files from a fixed folder, with mesh-replace or shape-key bake",
    "category": "Import-Export",
}

FILE_PATH = "/home/floreum/Games/zbrush_2022-0-8/drive_c/temp"
OBJ_FILENAME = "exported.obj"
EXPORTED_FOLDER = os.path.join(FILE_PATH, "exported")  # The fallback folder

def self_report(context, level, message):
    context.window_manager.popup_menu(
        lambda self, ctx: self.layout.label(text=message),
        title=level,
        icon='ERROR' if level == 'ERROR' else 'INFO'
    )

def import_single_obj(context, obj_file):
    print(f"Bridge Import → {obj_file}")

    if not os.path.isfile(obj_file):
        self_report(context, 'ERROR', f"OBJ file not found: {obj_file}")
        return False

    targets = [o for o in context.selected_objects if o.type == 'MESH']
    before_objs = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=obj_file)
    after_objs = set(bpy.data.objects)
    imported_objs = [obj for obj in after_objs - before_objs if obj.type == 'MESH']

    if not imported_objs:
        self_report(context, 'ERROR', "Import failed: no mesh objects found after import")
        return False

    imported_obj = imported_objs[0]
    imported_mesh = imported_obj.data
    rot_mtx = imported_obj.rotation_euler.to_matrix().to_4x4()
    processed_any = False

    for tgt in targets:
        if len(imported_mesh.vertices) == len(tgt.data.vertices):
            sk = tgt.data.shape_keys
            if sk and "Basis" in sk.key_blocks:
                basis = sk.key_blocks["Basis"]
                for i, v in enumerate(imported_mesh.vertices):
                    basis.data[i].co = (rot_mtx @ v.co.to_4d()).to_3d()
                tgt.data.update()
                print(f"Baked into Basis shape key for: {tgt.name}")
            else:
                new_mesh = imported_mesh.copy()
                for v in new_mesh.vertices:
                    v.co = (rot_mtx @ v.co.to_4d()).to_3d()
                tgt.data = new_mesh
                print(f"Replaced mesh data for: {tgt.name}")
        else:
            new_mesh = imported_mesh.copy()
            for v in new_mesh.vertices:
                v.co = (rot_mtx @ v.co.to_4d()).to_3d()
            tgt.data = new_mesh
            if tgt.data.shape_keys:
                bpy.data.shape_keys.remove(tgt.data.shape_keys)
            print(f"Fully replaced mesh for: {tgt.name}")

        tgt.rotation_euler = (0.0, 0.0, 0.0)
        processed_any = True

    if processed_any:
        bpy.data.objects.remove(imported_obj, do_unlink=True)
        bpy.data.meshes.remove(imported_mesh, do_unlink=True)
        print("Removed imported object after replacement.")
    else:
        # Bake rotation directly into mesh coords when no target selected
        for v in imported_mesh.vertices:
            v.co = (rot_mtx @ v.co.to_4d()).to_3d()
        imported_obj.rotation_euler = (0.0, 0.0, 0.0)
        imported_obj.name = "BlenderBridge"
        print("No selection — imported object left in scene with baked rotation.")

    try:
        os.remove(obj_file)
        print(f"Deleted OBJ file: {obj_file}")
    except Exception as e:
        print(f"Could not delete OBJ file: {e}")

    return True

import time

def import_obj(context):
    # Try to import the single exported.obj first
    single_obj_path = os.path.join(FILE_PATH, OBJ_FILENAME)
    if os.path.isfile(single_obj_path):
        success = import_single_obj(context, single_obj_path)
        return {'FINISHED'} if success else {'CANCELLED'}
    
    # Otherwise import all OBJ files inside the fallback folder
    if os.path.isdir(EXPORTED_FOLDER):
        obj_files = [os.path.join(EXPORTED_FOLDER, f) for f in os.listdir(EXPORTED_FOLDER) if f.lower().endswith('.obj')]
        if not obj_files:
            self_report(context, 'WARNING', f"No OBJ files found in folder: {EXPORTED_FOLDER}")
            return {'CANCELLED'}
        
        print(f"Found OBJ files to import: {obj_files}")
        any_success = False
        for obj_file in obj_files:
            try:
                # Clear selection to avoid issues
                bpy.ops.object.select_all(action='DESELECT')
                context.view_layer.objects.active = None
                
                success = import_single_obj(context, obj_file)
                if success:
                    any_success = True
                else:
                    print(f"Failed to import: {obj_file}")
                # Short pause to let Blender process
                time.sleep(0.1)
            except Exception as e:
                print(f"Exception during import of {obj_file}: {e}")
                self_report(context, 'ERROR', f"Exception importing {obj_file}: {e}")
                
        return {'FINISHED'} if any_success else {'CANCELLED'}
    else:
        self_report(context, 'ERROR', f"Neither {single_obj_path} nor fallback folder {EXPORTED_FOLDER} exist.")
        return {'CANCELLED'}


def export_obj(context):
    print("Bridge Export →", FILE_PATH)
    os.makedirs(FILE_PATH, exist_ok=True)
    
    # Export each selected object as its own OBJ file named after the mesh
    selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
    if not selected_meshes:
        self_report(context, 'WARNING', "No mesh objects selected to export.")
        return {'CANCELLED'}
    
    for obj in selected_meshes:
        export_path = os.path.join(FILE_PATH, f"{obj.data.name}.obj")
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        bpy.ops.wm.obj_export(filepath=export_path)
        print(f"Exported {obj.name} as {export_path}")

    return {'FINISHED'}

class BridgeImport(Operator):
    bl_idname = "bridge.obj_import"
    bl_label = "Bridge Import"
    def execute(self, context):
        return import_obj(context)

class BridgeExport(Operator):
    bl_idname = "bridge.obj_export"
    bl_label = "Bridge Export"
    def execute(self, context):
        return export_obj(context)

def menu_func_import(self, context):
    self.layout.operator(BridgeImport.bl_idname, text="Bridge Import")

def menu_func_export(self, context):
    self.layout.operator(BridgeExport.bl_idname, text="Bridge Export")

def register():
    bpy.utils.register_class(BridgeImport)
    bpy.types.TOPBAR_MT_file.append(menu_func_import)
    bpy.utils.register_class(BridgeExport)
    bpy.types.TOPBAR_MT_file.append(menu_func_export)

def unregister():
    bpy.types.TOPBAR_MT_file.remove(menu_func_import)
    bpy.utils.unregister_class(BridgeImport)
    bpy.types.TOPBAR_MT_file.remove(menu_func_export)
    bpy.utils.unregister_class(BridgeExport)

if __name__ == "__main__":
    register()
