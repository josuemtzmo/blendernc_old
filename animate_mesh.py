import bpy
from mathutils import Vector
from numpy import *
import xarray as xr
import cmocean as cm
from pylab import *
import math
import numpy as np 

def surface(data,xx,yy):
    verts = []
    faces = []
    # mesh variables
    numX = np.shape(data)[1]
    numY = np.shape(data)[2]
    dd=data[0,:,:]

    # wave variables
    scale = 10
    zscale = 1
    #fill verts array
    for i in range (0, numX):
        for j in range(0,numY):
            x = scale * xx[i]/abs(xx).max()
            y = scale * yy[j]/abs(yy).max()
            z = zscale * -dd[i,j]
            vert = (x,y,z)
            verts.append(vert)
    #fill faces arrayp
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
    mesh = bpy.data.meshes.new('test')
    object = bpy.data.objects.new('test',mesh)
    #set mesh location
    object.location = (0,0,0)
    bpy.context.scene.objects.link(object)
    #create mesh from python data
    mesh.from_pydata(verts,[],faces)
    mesh.update(calc_edges=True)
    object.select = True
    bpy.context.scene.objects.active = object
    return verts
    

x=np.linspace(0,2*np.pi,100)
y=np.linspace(0,2*np.pi,100)

X,Y=np.meshgrid(x,y)

Z=zeros([25,len(x),len(y)])
for t in range(0,25):
    Z[t,:,:]=np.sin(X+t)*np.cos(y) + np.cos(y) 

print(np.shape(Z))
verts=surface(Z,x,y)

def insert_keyframe(fcurves, frame, values):
    for fcu, val in zip(fcurves, values):
        fcu.keyframe_points.insert(frame, val, {'FAST'})

obj = bpy.context.active_object
mesh = obj.data
action = bpy.data.actions.new("MeshAnimation")

mesh.animation_data_create()
mesh.animation_data.action = action

data_path = "vertices[%d].co"
vec_z = Vector((0.0, 0.0, 1.0))

frames = range(0,shape(Z)[0])

def get_vertex(t,num,Z,xx,yy):
    count=0
    scale=10
    zscale=1
    shape_z=np.shape(Z)
    #print(shape_z)
    for i in range (0, shape_z[1]):
        for j in range(0,shape_z[2]):
            if count==num:
                x = scale * xx[i]/abs(xx).max()
                y = scale * yy[j]/abs(yy).max()
                z = zscale * Z[t,i,j]
                vert = Vector((x,y,z))
            count=count+1
    return vert

count=0
for v in mesh.vertices:    
    fcurves = [action.fcurves.new(data_path % v.index, i) for i in range(3)]
    #print(v.co)
    co_rest = v.co
    for t in frames:
        #print(get_vertex(t,count,Z,x,y))
        co_kf = get_vertex(t,count,Z,x,y)
        insert_keyframe(fcurves, t*10, co_kf)  
    count=count+1