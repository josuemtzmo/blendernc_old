import bpy
import cmocean
import struct
import xarray as xr
import dask as ds
import numpy as np

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
    Math0.inputs[1].default_value=context.object.dimensions[2]#scale[2]
    Math1 = nodes['Math.001']
    Math1.operation='DIVIDE'
    Math1.inputs[1].default_value=context.object.dimensions[2]
    
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
    if context.object.data.materials:
        context.object.data.materials[0]=mymat
    else:
        context.object.data.materials.append(mymat)
    return mymat

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
        row = layout.row()
        row.label(text="Select netcdf file:")
        row = layout.row()
        row.prop(scn.load_file,'get_path', text='Dataset Path',icon='FILESEL')
        row = layout.row()
        row.prop(scn.load_file,'selected_var', text='Select Variable')
        row = layout.row(align=True)
        row.label(text='Scale Ratio (i.e. |x|/|z|):')
        row.prop(scn.load_file,'float_prop',text='')
        row = layout.row()
        row.operator('scene.load_netcdf', text='Load netCDF').origin = 'button'  
        row = layout.row()
        #row.label(text="Active nefCDF loaded: " + obj.name)
        layout.label(text="Pick a gradient")
        row = layout.row(align=True)
        for i in range(16):
            row.prop(scn.gradients_props, 'color_' + str(i), text='')
        row = layout.row()
        row.prop(scn.gradients_props, 'selected_mode', text='')
        row = layout.row() 
        row.operator('scene.gradient_apply', text='Apply Gradient').origin = 'button'
        row.operator('scene.gradient_flip_apply', text='', icon='ARROW_LEFTRIGHT').origin = 'button'
        


class CmoceanOps(bpy.types.Operator):
    bl_label = "Gradient Operator"
    bl_idname = "scene.gradient_apply"

    origin = bpy.props.StringProperty(default='search')
    scripted = bpy.props.BoolProperty(default=False)
    
    def execute(self, context):
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
        Scn.gradients_props = bpy.props.PointerProperty(
            name="internal global properties",
            description="shared properties between operators",
            type=cls,
        )
        def updateColors(self, context):
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
            description="Color list",
            default="0",
            update=updateColors)
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.gradients_props    
        
class LoadNetcdf(bpy.types.Operator):
    bl_label = "Load Netcdf"
    bl_idname = "scene.load_netcdf"

    origin = bpy.props.StringProperty(default='search')
    scripted = bpy.props.BoolProperty(default=False)
    
    def execute(self, context):
        filepath=context.scene.load_file.get_path.title()
        #Test that it's a netcdf
        filename=filepath.split("/")[-1]
        extension=filename.split(".")[-1]
        #print(filename)
        #print(extension)
        if extension=='Nc':
            data=xr.open_dataset(filepath)
            dimensions=[i for i in data.coords.dims.keys()]
            variable = list(data.variables.keys() - dimensions)
            xrdataset=data[variable[int(bpy.context.scene.load_file.selected_var)]]
            #data[]
            if len(xrdataset.shape) == 2:
                #print('Surface variable loading')
                staticsurface(xrdataset)
            if len(xrdataset.shape) == 3:
                #print('Surface variable loading')
                dynamicsurface(xrdataset)    
            #if variable
            #layout = self.layout
            #row = layout.row
            #row.prop(scn.gradients_props, 'selected_mode', text='')
        else:
            self.report({'ERROR'}, "The file selected is not a netCDF.")
        
        return {'FINISHED'}
    
def staticsurface(xarraydataset):
    verts = []
    faces = []
    # mesh variables
    numX = xarraydataset.shape[0]
    numY = xarraydataset.shape[1]
    dd=xarraydataset[0,:,:].values

    xx=xarraydataset[xarraydataset.dims[0]].values
    yy=xarraydataset[xarraydataset.dims[1]].values
    print(xx)
    # wave variables
    scale = 10/numX
    zscale = 1/abs(dd).max()*round(bpy.context.scene.load_file.float_prop,2)
    #fill verts array
    for i in range (0, numX):
        for j in range(0,numY):
            x = scale * xx[i]/abs(xx).max()
            y = scale * yy[j]/abs(yy).max()
            z = zscale * -dd[i,j]
            vert = (x,y,z)
            verts.append(vert)
    #fill faces array
    count = 0
    for i in range (0, numY *(numX-1)):
        if count < numY-1:
            A = i
            B = i+1
            C = (i+numY)+1
            D = (i+numY)
            face = (A,B,C,D)
            faces.append(face)
            count = count + 1
        else:
            count = 0
    #create mesh and object
    mesh = bpy.data.meshes.new(xarraydataset.name)
    object = bpy.data.objects.new(xarraydataset.name,mesh)
    #set mesh location
    object.location = (-scale*numX/2,-scale*numX/2,0)
    bpy.context.scene.objects.link(object)
    #create mesh from python data
    mesh.from_pydata(verts,[],faces)
    mesh.update(calc_edges=True)
    object.select = True
    bpy.context.scene.objects.active = object
    
def dynamicsurface(xarraydataset):
    verts = []
    faces = []
    # mesh variables
    numX = xarraydataset.shape[1]
    numY = xarraydataset.shape[2]
    dd=xarraydataset[0,:,:].values

    xx=xarraydataset[xarraydataset.dims[1]].values
    yy=xarraydataset[xarraydataset.dims[2]].values
    print(xx)
    # wave variables
    scale = round(bpy.context.scene.load_file.float_prop,2)
    zscale = (abs(dd).max()*round(bpy.context.scene.load_file.float_prop,2))/10
    #fill verts array
    for i in range (0, numX):
        for j in range(0,numY):
            x = scale * xx[i]
            y = scale * yy[j]
            z = zscale * -dd[i,j]
            if z!=0:
                vert = (x,y,z)
                verts.append(vert)
            else:
                vert = (np.nan,np.nan,np.nan)
                verts.append(vert)
    #fill faces array
    count = 0
    for i in range (0, numY *(numX-1)):
        if count < numY-1:
            A = i
            B = i+1
            C = (i+numY)+1
            D = (i+numY)
            face = (A,B,C,D)
            faces.append(face)
            count = count + 1
        else:
            count = 0
    #create mesh and object
    mesh = bpy.data.meshes.new(xarraydataset.name)
    object = bpy.data.objects.new(xarraydataset.name,mesh)
    #set mesh location
    object.location = (0,0,0)
    bpy.context.scene.objects.link(object)
    #create mesh from python data
    mesh.from_pydata(verts,[],faces)
    mesh.update(calc_edges=True)
    object.select = True
    bpy.context.scene.objects.active = object

class netCDFProperties(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        Scn = bpy.types.Scene
        Scn.load_file = bpy.props.PointerProperty(
            name="internal global properties",
            description="shared properties between operators",
            type=cls)
        
        def get_properties(self,context):
            filepath=bpy.context.scene.load_file.get_path.title()
            filename=filepath.split("/")[-1]
            extension=filename.split(".")[-1]
            if extension=='Nc':
                data=xr.open_dataset(filepath)
                dimensions=[i for i in data.coords.dims.keys()]
                variable = list(data.variables.keys() - dimensions)
                vardic = [('%d' %i,variable[i],variable[i]) for i in range(0,len(variable))]
                bpy.types.Object.Enum = vardic
            else:
                bpy.types.Object.Enum = [('0','File is not a netCDF','File is not a netCDF')]
                self.report({'ERROR'}, "The file selected is not a netCDF.")
            return bpy.types.Object.Enum
        cls.get_path = bpy.props.StringProperty(
            subtype="FILE_PATH",
            default = bpy.path.abspath("//"))
        cls.selected_var = bpy.props.EnumProperty(
            items=get_properties,
            description="Variable list")
        cls.float_prop = bpy.props.FloatProperty(
            name = "Float Value",
            description = "A float property",
            default = 0.1,
            min = 0.0,
            max = 1.0
            )
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.load_file 
        
def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()