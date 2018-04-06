from numpy import *
from netCDF4 import Dataset
import cmocean as cm
from pylab import *
import bpy
import math

# mesh arrays
verts = []
faces = []
 
depth=Dataset('/Users/josue/Documents/academia/phd/github/data.input/MOM6/topog.nc')
#depth=Dataset('/Users/josue/Documents/academia/phd/github/MITgcm/verification/dome/run/myncfile.nc')
dd=depth.variables['depth'][:]

 
# mesh variables
numX = np.shape(dd)[0]
numY = np.shape(dd)[0]
 
# wave variables
scale = 0.01
zscale = 0.001
 
#fill verts array
for i in range (0, numX):
    for j in range(0,numY):
 
        x = scale * i
        y = scale * j
        z = zscale * -dd[i,j]
 
        vert = (x,y,z) 
        verts.append(vert),
 
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
mesh = bpy.data.meshes.new("wave")
object = bpy.data.objects.new("wave",mesh)
 
#set mesh location
object.location = bpy.context.scene.cursor_location
bpy.context.scene.objects.link(object)
 
#create mesh from python data
mesh.from_pydata(verts,[],faces)
mesh.update(calc_edges=True)
