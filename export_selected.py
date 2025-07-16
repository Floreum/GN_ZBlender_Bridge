import bpy
import os

class ExportSelectedToAssets(bpy.types.Operator):
    bl_idname = "object.export_selected_to_assets"
    bl_label = "Export Selected to Assets"
    bl_options = {'REGISTER', 'UNDO'}

    export_format: bpy.props.EnumProperty(
        name="Format",
        description="Choose which format to export. Only the selected format will be exported.",
        items=[('OBJ', "OBJ", "Export as Wavefront OBJ"), ('FBX', "FBX", "Export as FBX")],
        default='OBJ'
    )
    zbrush: bpy.props.BoolProperty(
        name="ZBrush",
        description="Set export scale to 100 for ZBrush compatibility",
        default=False
    )
    apply_modifiers: bpy.props.BoolProperty(
        name="Apply Modifiers",
        description="Apply modifiers before export",
        default=False
    )

    def invoke(self, context, event):
        # Show a confirmation dialog before executing
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "export_format")
        layout.prop(self, "zbrush")
        layout.prop(self, "apply_modifiers")

    def execute(self, context):
        blend_path = bpy.data.filepath
        if not blend_path:
            self.report({'ERROR'}, "Please save your Blender file before exporting.")
            return {'CANCELLED'}

        scenes_dir = os.path.dirname(blend_path)
        parent_dir = os.path.dirname(scenes_dir)
        assets_dir = os.path.join(parent_dir, "assets")
        os.makedirs(assets_dir, exist_ok=True)

        selected_objects = context.selected_objects
        if not selected_objects:
            self.report({'ERROR'}, "No objects selected for export.")
            return {'CANCELLED'}

        export_scale = 100 if self.zbrush else 1

        for obj in selected_objects:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj

            # Apply modifiers if requested, but skip if object has shape keys
            if self.apply_modifiers and obj.type == 'MESH':
                if not obj.data.shape_keys:
                    for mod in obj.modifiers:
                        bpy.ops.object.modifier_apply(modifier=mod.name)
                else:
                    self.report({'WARNING'}, f"Skipped applying modifiers for {obj.name} (has shape keys)")

            export_path = os.path.join(assets_dir, f"{obj.name}.{self.export_format.lower()}")
            if self.export_format == 'OBJ':
                result = bpy.ops.wm.obj_export(
                    filepath=export_path,
                    export_selected_objects=True,
                    global_scale=export_scale
                )
            elif self.export_format == 'FBX':
                result = bpy.ops.export_scene.fbx(
                    filepath=export_path,
                    use_selection=True,
                    global_scale=export_scale
                )
            else:
                self.report({'ERROR'}, f"Unsupported format: {self.export_format}")
                continue

            if result == {'FINISHED'}:
                self.report({'INFO'}, f"Exported {obj.name} to {export_path}")
            else:
                self.report({'WARNING'}, f"Failed to export {obj.name}")

        # Reselect original selection
        for obj in selected_objects:
            obj.select_set(True)

        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(ExportSelectedToAssets.bl_idname)

def register():
    bpy.utils.register_class(ExportSelectedToAssets)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    bpy.utils.unregister_class(ExportSelectedToAssets)

if __name__ == "__main__":
    register()