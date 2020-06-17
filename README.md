This repository is deprecated in favor of https://github.com/blendernc/blendernc/
============================================================================================================================

# blendernc (Blender Addon 4 scientific visualization)

| Read the Docs |
|:-------------:|
|[![Documentation Status](https://readthedocs.org/projects/blendernc/badge/?version=latest)](https://blendernc.readthedocs.io/en/latest/?badge=latest)|

This add-on allows to import netCDF files into Blender as Textures and Objects (Future development). 

This add-on currently allow to import:
- 2D fields (x, y):
![Alt Text](https://github.com/josuemtzmo/blendernc/blob/master/docs/images/gebco_topo.mp4 "GEBCO Topography")

- 3D fields (x, y, time): 
![Alt Text](https://github.com/josuemtzmo/blendernc/blob/master/docs/images/global_1deg_temp_brightness_vel_mag.png "Global 1 degree temperature, brightness: velocity magnitude")

- 4D fields (x, y, z = 0, time): 
![Alt Text](https://github.com/josuemtzmo/blendernc/blob/master/docs/images/global_1deg_temp_brightness_vel_mag.mp4 "Global 1 degree temperature, brightness: velocity magnitude")

Future development:
- Load 1D arrays or compute global averages to build plots.
- Apply displacement, texture and colormap to objects selected by user.
- Shader node of colormap CMOCEAN (Read more about it at [cmocean GitHub](https://github.com/matplotlib/cmocean)).
- Isosurface displacement.
- Implement slicing over dimensions.
- Load textures using Voxel Data for 4D and 3D without time implementations.

## Installation:
** Blendernc works in Blender > 2.8 **

- Include external python libraries into blender.

![Alt Text](https://github.com/josuemtzmo/blendernc/blob/master/docs/images/modules_path.png "Select external libraries")

Note that this folder must contain 3 sub-directories : `addons`, `modules`, and `startup`.
You can install additionally libraries in the modules folder.


- Link python libraries to compiled Blender. 
Note: Libraries and Blender python should have the same distribution, if unsure, 
compile blender following the official [Blender installation website](https://wiki.blender.org/index.php/Dev:Doc/Building_Blender/) instructions and modify: 

```bash
cmake -DPYTHON_VERSION=3.6 ../blender
```
On **macOS**, find the folder `modules` within the blender.app:
```bash
cd /path2Applications/blender.app/Contents/Resources/2.8x/scripts/modules
```

Then link all the packages from your python environment folder:
```bash
ln -s $PATH_PYTHON/lib/python3.6/site-packages/* .
```

This step allows blendernc to use python modules (netCDF4, xarray, and others) and 
local installations from your python environment. We encourage the use of 
environments, however you can also use the main python located in 
`/usr/local/lib/python3.6/site-packages/`

**This Add-on is under development.**

