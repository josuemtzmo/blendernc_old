import bpy

class FILE_EXISTS_OT_file_exists(bpy.types.Operator):
    bl_idname = "blendernc.file_error"
    bl_label = "File error"
    bl_description = "File error"

    def execute(self, context):
        self.report({"ERROR_INVALID_INPUT"}, "File doesn't exist or it's not a netCDF")
        return {'FINISHED'}

class LARGE_DATASET_OT_report(bpy.types.Operator):
    bl_idname = "blendernc.large_dataset"
    bl_label = "Large dataset"
    bl_description = "Large dataset warning"

    def execute(self, context):
        self.report({"WARNING"}, "Large dataset, automatic texture gereration disabled")
        return {'FINISHED'}

class SAVE_FILE_OT_file_is_saved(bpy.types.Operator):
    bl_idname = "blendernc.file_is_saved"
    bl_label = "File is saved"
    bl_description = "File is not saved"

    def execute(self, context):
        self.report({"WARNING"}, "Save the file")
        return {'FINISHED'}