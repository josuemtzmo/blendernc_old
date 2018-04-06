import bpy
import cmocean
import struct

bl_info = {
    "name": "NETcdf blender",
    "author": "Josue Martinez Moreno",
    "version": (0, 0, 0),
    "blender": (2, 7, 9),
    "category": "Data",
    "wiki_url": "",
    "tracker_url": ""
}

availcmaps=cmocean.cm.cmapnames

from bpy.props import (StringProperty,
                       PointerProperty,
                       )
                       
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )
    
def create_cmap(nodes,context,mymat,flip=False):

    if 'ColorRamp' not in nodes:
        nodes.new(type="ShaderNodeValToRGB")
    else:
        nodes.remove(nodes["ColorRamp"])
        nodes.new(type="ShaderNodeValToRGB")
    if 'Diffuse BSDF' not in nodes:
        nodes.new(type="ShaderNodeBsdfDiffuse")
    if 'Material Output' not in nodes:    
        nodes.new(type="ShaderNodeOutputMaterial")
    if 'Texture Coordinate' not in nodes:
        nodes.new('ShaderNodeTexCoord')
    if 'Separate XYZ' not in nodes:
        nodes.new('ShaderNodeSeparateXYZ')
    if 'Math' not in nodes:
        nodes.new('ShaderNodeMath')
        nodes.new('ShaderNodeMath')
        
    ColorRamp = nodes['ColorRamp']
    Math0 = nodes['Math']
    Math0.operation='ADD'
    Math0.inputs[1].default_value=5.5#context.object.dimensions[2]
    Math1 = nodes['Math.001']
    Math1.operation='DIVIDE'
    Math1.inputs[1].default_value=5.5#context.object.dimensions[2]
    
    TexCoord = nodes['Texture Coordinate']
    
    SeparateXYZ = nodes['Separate XYZ']
        
    DiffuseBSDF = nodes["Diffuse BSDF"]
    MaterialOut = nodes["Material Output"]
    
    mymat.node_tree.links.new(TexCoord.outputs[3], SeparateXYZ.inputs[0])
    mymat.node_tree.links.new(SeparateXYZ.outputs[2], Math0.inputs[0])
    mymat.node_tree.links.new(Math0.outputs[0], Math1.inputs[0])
    mymat.node_tree.links.new(Math1.outputs[0], ColorRamp.inputs[0])
    mymat.node_tree.links.new(ColorRamp.outputs[0], DiffuseBSDF.inputs[0])
    mymat.node_tree.links.new(DiffuseBSDF.outputs[0], MaterialOut.inputs[0])
    
    if flip==False:
        ColorRamp.color_ramp.elements[0].color[0:3]=getattr(cmocean.cm, availcmaps[int(context.scene.gradients_props.selected_mode)])(int(0))[0:3]
        ColorRamp.color_ramp.elements[1].color[0:3]=getattr(cmocean.cm, availcmaps[int(context.scene.gradients_props.selected_mode)])(int(256))[0:3]
        for i in range(1,16):
            ColorRamp.color_ramp.elements.new(i/16)
            ColorRamp.color_ramp.elements[i].color[0:3]=getattr(cmocean.cm, availcmaps[int(context.scene.gradients_props.selected_mode)])(int(i*16))[0:3]
    else:
        ColorRamp.color_ramp.elements[1].color[0:3]=getattr(cmocean.cm, availcmaps[int(context.scene.gradients_props.selected_mode)])(int(0))[0:3]
        ColorRamp.color_ramp.elements[0].color[0:3]=getattr(cmocean.cm, availcmaps[int(context.scene.gradients_props.selected_mode)])(int(256))[0:3]
        for i in range(1,16):
            ColorRamp.color_ramp.elements.new(i/16)
            ColorRamp.color_ramp.elements[i].color[0:3]=getattr(cmocean.cm, availcmaps[int(context.scene.gradients_props.selected_mode)])(int((16-i)*16))[0:3]
    context.object.data.materials[0]=mymat
    return mymat


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
        scn = context.scene
        row = layout.row()
        row.label(text="This Add-on will allow you to import and plot netCDF files!")
        
        if obj.name!="wave":
            row = layout.row()
            col = layout.column(align=True)
            row.label(text="Select netcdf file:")
            col.prop(scn.LOADNETCDF, "path", text="")
        else:
            row = layout.row()
            row.label(text="Active nefCDF loaded: " + obj.name)
            layout.label(text="Pick a gradient")

            r = layout.row(align=True)
            for i in range(16):
                r.prop(scn.gradients_props, 'color_' + str(i), text='')

            r = layout.row()
            r.prop(scn.gradients_props, 'selected_mode', text='')
            r = layout.row()
            r.operator('scene.gradient_apply', text='Apply Gradient').origin = 'button'
            r.operator('scene.gradient_flip_apply', text='', icon='ARROW_LEFTRIGHT').origin = 'button'
            

class CmoceanOps(bpy.types.Operator):
    bl_label = "Gradient Operator"
    bl_idname = "scene.gradient_apply"

    origin = bpy.props.StringProperty(default='search')
    scripted = bpy.props.BoolProperty(default=False)
    
    def execute(self, context):
        try:
            space = context.space_data
            node_tree = space.node_tree
            nodes = node_tree.nodes
            make_slices(context, nodes, self.origin)
        except:
            driver_namespace = bpy.app.driver_namespace
            mymat = bpy.data.materials.get(context.object.name+'.0000')
            if not mymat:
                mymat = bpy.data.materials.new(context.object.name+'.0000')
            mymat.use_nodes = True
            nodes = mymat.node_tree.nodes
            mymat=create_cmap(nodes,context,mymat)
        return {'FINISHED'}
    
class CmoceanOpsFlip(bpy.types.Operator):
    bl_label = "Gradient Operator"
    bl_idname = "scene.gradient_flip_apply"

    origin = bpy.props.StringProperty(default='search')
    scripted = bpy.props.BoolProperty(default=False)
    
    def execute(self, context):
        try:
            space = context.space_data
            node_tree = space.node_tree
            nodes = node_tree.nodes
            make_slices(context, nodes, self.origin)
        except:
            driver_namespace = bpy.app.driver_namespace
            mymat = bpy.data.materials.get(context.object.name+'.0000')
            if not mymat:
                mymat = bpy.data.materials.new(context.object.name+'.0000')
            mymat.use_nodes = True
            nodes = mymat.node_tree.nodes
            mymat=create_cmap(nodes,context,mymat,flip=True)
        return {'FINISHED'}

class CmoceanProperties(bpy.types.PropertyGroup):

    @classmethod
    def register(cls):
        Scn = bpy.types.Scene
        
        Scn.gradients_props = PointerProperty(
            name="internal global properties",
            description="shared properties between operators",
            type=cls,
        )

        def updateColors(self, context):
            print(context)
            props = context.scene.gradients_props
            key = int(props.selected_mode)
            for i in range(0,16):        
                currentmap=availcmaps[key]
                exec('props.color_' + str(i) + ' = getattr(cmocean.cm, currentmap)(int(i*16))[0:3]')
            
        for i in range(len(availcmaps)):
            k = " = bpy.props.FloatVectorProperty(subtype='COLOR', min=0.0, max=1.0)"
            exec('cls.color_' + str(i) + k)

        mode_options = [(str(i), availcmaps[i], "", i) for i in range(len(availcmaps))]
        
        cls.selected_mode = bpy.props.EnumProperty(
            items=mode_options,
            description="offers....",
            default="0",
            update=updateColors)

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.gradients_props       
            
def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.LOADNETCDF = PointerProperty(type=LoadFile)
    bpy.types.Scene.CUSTOMCMAP = bpy.props.StringProperty()


def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.LOADNETCDF
    del bby.types.Scene.CUSTOMCMAP


if __name__ == "__main__":
    register()