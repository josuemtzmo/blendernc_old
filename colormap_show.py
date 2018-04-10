import bpy
import cmocean
import numpy as np

availcmaps=cmocean.cm.cmapnames

def create_obj_cmap(nodes,context,mymat,cmap,flip=False,node='Diffuse'):
    
    
    if 'ColorRamp' not in nodes:
        nodes.new(type="ShaderNodeValToRGB")
    else:
        nodes.remove(nodes["ColorRamp"])
        nodes.new(type="ShaderNodeValToRGB")
    if node+' BSDF' not in nodes:
        nodes.new(type="ShaderNodeBsdf"+node)
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
    Math0.inputs[1].default_value=context.object.scale[2]
    Math1 = nodes['Math.001']
    Math1.operation='DIVIDE'
    Math1.inputs[1].default_value=context.object.dimensions[2]
    
    TexCoord = nodes['Texture Coordinate']
    
    SeparateXYZ = nodes['Separate XYZ']
        
    DiffuseBSDF = nodes[node + " BSDF"]
    MaterialOut = nodes["Material Output"]
    
    mymat.node_tree.links.new(TexCoord.outputs[3], SeparateXYZ.inputs[0])
    mymat.node_tree.links.new(SeparateXYZ.outputs[2], Math0.inputs[0])
    mymat.node_tree.links.new(Math0.outputs[0], Math1.inputs[0])
    mymat.node_tree.links.new(Math1.outputs[0], ColorRamp.inputs[0])
    mymat.node_tree.links.new(ColorRamp.outputs[0], DiffuseBSDF.inputs[0])
    mymat.node_tree.links.new(DiffuseBSDF.outputs[0], MaterialOut.inputs[0])
    
    if flip==False:
        ColorRamp.color_ramp.elements[0].color[0:3]=getattr(cmocean.cm, cmap)(int(0))[0:3]
        ColorRamp.color_ramp.elements[1].color[0:3]=getattr(cmocean.cm, cmap)(int(256))[0:3]
        for i in range(1,16):
            ColorRamp.color_ramp.elements.new(i/16)
            ColorRamp.color_ramp.elements[i].color[0:3]=getattr(cmocean.cm, cmap)(int(i*16))[0:3]
    else:
        ColorRamp.color_ramp.elements[1].color[0:3]=getattr(cmocean.cm, cmap)(int(0))[0:3]
        ColorRamp.color_ramp.elements[0].color[0:3]=getattr(cmocean.cm, cmap)(int(256))[0:3]
        for i in range(1,16):
            ColorRamp.color_ramp.elements.new(i/16)
            ColorRamp.color_ramp.elements[i].color[0:3]=getattr(cmocean.cm, cmap)(int((16-i)*16))[0:3]
    if context.object.data.materials:
        context.object.data.materials[0]=mymat
    else:
        context.object.data.materials.append(mymat)
    return mymat

obj=[]
material=['Diffuse','Glossy','Glass','Hair']
for i in range(0,17):
    for j in range(0,len(material)):
        bpy.ops.mesh.primitive_uv_sphere_add(location=((i*2.5)-(16*2.5)/2,(j*2.5)-(len(material)*2.5)/2, 0),rotation=(0,0,0))
        mymat = bpy.data.materials.get(bpy.context.object.name)
        bpy.context.object.rotation_euler[0] = np.pi/2
        bpy.context.object.rotation_euler[0] = 1.60919
        bpy.ops.object.shade_smooth()
        if not mymat:
            mymat = bpy.data.materials.new(bpy.context.object.name)
        mymat.use_nodes = True
        nodes = mymat.node_tree.nodes
        mymat=create_obj_cmap(nodes,bpy.context,mymat,availcmaps[i],node=material[j])    

    
    
