import bpy
from . core import BlenderncEngine


blendernc_core = BlenderncEngine()

# class LoadFile(bpy.types.PropertyGroup):
#     path = bpy.types.StringProperty(
#         name="",
#         description="Path to Directory",
#         default="",
#         maxlen=1024,
#         subtype='DIR_PATH')


class netCDF_Var(bpy.types.Operator):
    bl_idname = "blendernc.cursor_center"
    bl_label = "Simple Operator"
    bl_description = "Center 3d cursor"

    def execute(self, context):
        bpy.ops.view3d.snap_cursor_to_center()
        bpy.ops.blendernc.button_file_off()
        return {'FINISHED'}


class netCDF_exists(bpy.types.Operator):
    bl_idname = "blendernc.file_error"
    bl_label = "File error"
    bl_description = "File error"

    def execute(self, context):
        self.report({"ERROR_INVALID_INPUT"}, "File doesn't exist or it's not a netCDF")
        return {'FINISHED'}

class netCDF_load(bpy.types.Operator):
    bl_idname = "blendernc.netcdf_load"
    bl_label = "Simple Operator"
    bl_description = "Center 3d cursor"

    def execute(self, context):
        file_path=context.scene.blendernc_file
        try:
            blendernc_core.check_files_netcdf(file_path)
            var_names = blendernc_core.netcdf_var()
        except:
            self.report({"ERROR"}, "File doesn't exist or it's not a netCDF")

        bpy.types.Scene.blendernc_netcdf_vars = bpy.props.EnumProperty(items=var_names,
                                                                name="")

        #[ items.insert(var_n, (var_names[var_n]) ) for var_n in range(len(var_names))]
        return {'FINISHED'}

class netCDF_vars(bpy.types.Operator):
    bl_idname = "blendernc.netcdf_vars"
    bl_label = "Simple Operator"
    bl_description = "Center 3d cursor"

    def execute(self, context):
        file_path=context.scene.blendernc_proxy_library
        try:
            blendernc_core.check_files_netcdf(file_path)
        except:
            self.report({"ERROR"}, "File doesn't exist or it's not a netCDF")
        return {'FINISHED'}

        