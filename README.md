# blendernc (Blender Addon 4 scientific visualization)

This add-on provides support of netCDF files into blender, additional, due to the porpouse of its development, the color map used is CMOCEAN (Read more about it at [cmocean GitHub](https://github.com/matplotlib/cmocean)):

![Alt Text](https://github.com/Josue-Martinez-Moreno/blendernc/blob/master/cmocean_materials.png "cmocean colorbar in different textures")

## Installation:

**Testend on Blender v2.79 with PYTHON 3.6**

Compile blender from scratch, The instructions are mostly the same as the official installation instructions except for a few modifications specified below: 

```bash
mkdir ~/.blender-build
cd ~/.blender-build
git clone http://git.blender.org/blender.git
cd blender
make update

mkdir ../build_python_3.6
cd ../build_python_3.6

cmake -DPYTHON_VERSION=3.6 ../blender

make

make install

cd /bin/blender.app/Contents/Resources/2.79/scripts/modules
```

Then link all the packages from your main python folder:
```bash
export PYTHON_PATH="python_path"

ln -s $PATH_PYTHON/lib/python3.6/site-packages/* .
```

This particular step is really important, because then you can use python modules (netCDF4, xarray, and others) and local installations from your main python distribution.

For more information look at:
https://wiki.blender.org/index.php/Dev:Doc/Building_Blender/Mac

The Add-on is not finished, so to test it you need to run it from the Text Editor Menu (Alt + P).

