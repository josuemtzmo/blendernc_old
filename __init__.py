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

# Import blendernc core
from . core import BlenderncEngine

# Import bpy clases
from . netcdf_load import ( TEST_OT_cursor_center, LOAD_NC_OT_netCDF_load, 
            SELECTED_RESOLUTION_OT_netCDF_load_resolution, 
            CONVERT_NC_OT_netCDF_texture )
from . blendernc_ui import ( BLENDERNC_UI_PT_3dview, BLENDERNC_LOAD_OT_Off, 
            BLENDERNC_LOAD_OT_On)

# Classes to register and unregister
classes = (TEST_OT_cursor_center, LOAD_NC_OT_netCDF_load, 
            SELECTED_RESOLUTION_OT_netCDF_load_resolution, 
            CONVERT_NC_OT_netCDF_texture,  BLENDERNC_UI_PT_3dview, 
            BLENDERNC_LOAD_OT_Off, BLENDERNC_LOAD_OT_On)

# Register and unregister functions
register, unregister = bpy.utils.register_classes_factory(classes)

# Initialize blendernc core
blendernc_core = BlenderncEngine()

# Update netCDF variables function of selected netCDF path and check if netCDF 
# file exists
def update_proxy_file(self, context):
    """
    Update function:
        -   Checks if netCDF file exists 
        -   Extracts variable names using netCDF4 conventions.
    """
    try:
        file_path=bpy.context.scene.blendernc_file
        blendernc_core.check_files_netcdf(file_path)
    except (NameError, ValueError):
        bpy.ops.blendernc.file_error()

# Update resolution function of netCDF dataset
def update_proxy_resolution(self, context):
    """
    Update function:
        -   Dynamically update the resolution of dataset.
    """
    bpy.ops.blendernc.netcdf_resolution()

# Scene globals
bpy.types.Scene.blendernc_resolution = bpy.props.FloatProperty(name = 'Resolution', 
                                                min = 1, max = 100, 
                                                default = 20,
                                                update=update_proxy_resolution)



bpy.types.Scene.blendernc_netcdf_vars = bpy.props.EnumProperty(items=(''),
                                                                name="")

bpy.types.Scene.blendernc_file = bpy.props.StringProperty(
    name="",
    description="Folder with assets blend files",
    default="",
    maxlen=1024,
    update=update_proxy_file,
    subtype='FILE_PATH')
