# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "blendernc",
    "author" : "josuemtzmo",
    "description" : "Blender Add-On to visualize scientific data",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "View3D",
    "warning" : "This is currently under development, please contribute at: https://github.com/josuemtzmo/blendernc",
    "category" : "Generic"
}

import bpy

from . core import BlenderncEngine
from . netcdf_load import netCDF_Var, netCDF_load
from . blendernc_ui import Blendernc_Panel, ButtonLoadOff, ButtonLoadOn

# Classes to register and unregister
classes = (netCDF_Var, netCDF_load, Blendernc_Panel, 
            ButtonLoadOff, ButtonLoadOn)

register, unregister = bpy.utils.register_classes_factory(classes)

blendernc_core = BlenderncEngine()

def update_proxy_library(self, context):
    try:
        file_path=bpy.context.scene.blendernc_file
        blendernc_core.check_files_netcdf(file_path)
    except (NameError, ValueError):
        bpy.ops.blendernc.file_error()

bpy.types.Scene.blendernc_netcdf_vars = bpy.props.EnumProperty(items=(''),
                                                                name="")

bpy.types.Scene.blendernc_file = bpy.props.StringProperty(
    name="",
    description="Folder with assets blend files",
    default="",
    maxlen=1024,
    update=update_proxy_library,
    subtype='FILE_PATH')

