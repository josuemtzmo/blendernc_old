import bpy
from bpy.props import (StringProperty,
                       PointerProperty,
                       )
                       
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )
                       
class LoadFile(PropertyGroup):
    path = StringProperty(
        name="",
        description="Path to Directory",
        default="",
        maxlen=1024,
        subtype='DIR_PATH')

class BlenderncPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Blendernc"
    bl_idname = "OBJECT_PT_netcdf"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.label(text="This Add-on will allow you to import and plot netCDF files!")
        
        if obj.name!="wave":
            row = layout.row()
            scn = context.scene
            col = layout.column(align=True)
            row.label(text="Select netcdf file:")
            col.prop(scn.loadnetcdf, "path", text="")
        else: 
            row = layout.row()
            row.label(text="Active nefCDF loaded: " + obj.name)

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.loadnetcdf = PointerProperty(type=LoadFile)


def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.loadnetcdf


if __name__ == "__main__":
    register()