import bpy
from . core import BlenderncEngine
from . files_utils import tmp_folder
import numpy as np
import os


blendernc_core = BlenderncEngine()

class TEST_OT_cursor_center(bpy.types.Operator):
    """
    Operator 
    """
    bl_idname = "blendernc.cursor_center"
    bl_label = "Simple Operator"
    bl_description = "Center 3d cursor"

    def execute(self, context):
        bpy.ops.view3d.snap_cursor_to_center()
        bpy.ops.blendernc.button_file_off()
        return {'FINISHED'}

class LOAD_NC_OT_netCDF_load(bpy.types.Operator):
    bl_idname = "blendernc.netcdf_load"
    bl_label = "Load netcdf variables"
    bl_description = "Check if netcdf exists and then returns variable names"

    def execute(self, context):
        try:
            file_path=context.scene.blendernc_file
            blendernc_core.check_files_netcdf(file_path)
            var_names = blendernc_core.netcdf_var()
            bpy.types.Scene.blendernc_netcdf_vars = bpy.props.EnumProperty(items=var_names,
                                                                name="")
        except NameError:
            self.report({"ERROR"}, "File doesn't exist")
        except ValueError:
            self.report({"ERROR"}, "File isn't a netCDF")

        #[ items.insert(var_n, (var_names[var_n]) ) for var_n in range(len(var_names))]
        return {'FINISHED'}

class SELECTED_RESOLUTION_OT_netCDF_load_resolution(bpy.types.Operator):
    bl_idname = "blendernc.netcdf_resolution"
    bl_label = "Create texture from netCDF"
    bl_description = "Create texture from netCDF"

    def modal(self, context, event):
        if event.type in {'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

    def execute(self, context):
        selected_variable=context.scene.blendernc_netcdf_vars
        selected_resolution = context.scene.blendernc_resolution
        if selected_variable != "":
            bpy.types.Scene.blendernc_data = blendernc_core.netcdf_values(selected_variable,selected_resolution)
            if bpy.data.textures.items() != []:
                if selected_variable in bpy.data.textures[len(bpy.data.textures)-1].name and (np.array(context.scene.blendernc_data.shape) < 1920).any():
                    #bpy.ops.blendernc.netcdf2texture()
                    pass
                else:
                    bpy.ops.blendernc.large_dataset()
        else:       
            bpy.ops.blendernc.button_file_on()
            self.report({"ERROR"}, "First you have to load a file")
        return {'FINISHED'}

class CONVERT_NC_OT_netCDF_texture(bpy.types.Operator):
    bl_idname = "blendernc.netcdf2texture"
    bl_label = "Create texture from netCDF"
    bl_description = "Create texture from netCDF"
    bl_use_preview = True

    def modal(self, context, event):
        if event.type in {'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

    def execute(self, context):
        if not bpy.data.is_saved:
            self.report({"ERROR"}, "Save the file")
            # TO DO: Move to:
            # ATM, the error is only display in the console not the UI.
            # bpy.ops.blendernc.file_is_saved()
            return {'FINISHED'}
        
        try: 
            context.scene.blendernc_data
        except AttributeError:
            bpy.types.Scene.blendernc_data = blendernc_core.netcdf_values( context.scene.blendernc_netcdf_vars, context.scene.blendernc_resolution )

        if context.scene.blendernc_data.name != context.scene.blendernc_netcdf_vars:
            bpy.ops.blendernc.netcdf_resolution()
            bpy.types.Scene.blendernc_data = blendernc_core.netcdf_values(context.scene.blendernc_netcdf_vars,context.scene.blendernc_resolution)
        
        context.view_layer.objects.active = None

        if any(context.scene.blendernc_data.name in key for key in bpy.data.textures.keys()):
            texture_name = context.scene.blendernc_data.name
        else:
            bpy.ops.texture.new()
            texture_name = bpy.data.textures[len(bpy.data.textures)-1].name
            bpy.data.textures[texture_name].name = context.scene.blendernc_data.name

        # Identify spatial coordinates.
        coords_names = {coords_name : 'x' if np.logical_or('x' in coords_name, 'lon' in coords_name) 
                                else 'y' if np.logical_or('y' in coords_name, 'lat' in coords_name)
                                else 'time' if np.logical_or('time' in coords_name, 'date' in coords_name) 
                                else 'others' for coords_name in context.scene.blendernc_data.coords}
        # Flip identified spatial coordinates to x:xcoord, y:ycoord
        bpy.types.Scene.blender_var_names = {value: key for key, value in coords_names.items()}

        # texture resolution
        x_res = len(context.scene.blendernc_data[ bpy.types.Scene.blender_var_names['x']])
        y_res = len(context.scene.blendernc_data[ bpy.types.Scene.blender_var_names['y']])
        
        if 'time' in coords_names.keys():
            time = len(context.scene.blendernc_data[ bpy.types.Scene.blender_var_names['time']])
        else:
            time = 1
        
        depth = 0 ## TO DO add level selection

        files = []

        blender_file_path = bpy.path.abspath('//')
       
        # Create temporal file
        tmp_folder(blender_file_path)
        tmp_folder_path = os.path.join(blender_file_path,'.tmp_blendernc/')
        
        # Data to texture
        ## TO DO: ADD support for 1D arrays to construct fancy plots
        if len( bpy.types.Scene.blender_var_names.keys()) == 2:
            data = context.scene.blendernc_data
        elif len( bpy.types.Scene.blender_var_names.keys()) == 3:
            data = context.scene.blendernc_data
        elif len( bpy.types.Scene.blender_var_names.keys()) == 4: 
            data = context.scene.blendernc_data.isel({ bpy.types.Scene.blender_var_names['others']:depth})
        else:
            self.report({"ERROR"}, "Blendernc currently supports 2D, 3D and 4D arrays")
            return {'FINISHED'}

        progress_manager = bpy.data.window_managers[0]
        progress_manager.progress_begin(0,100)

        image_format = context.scene.blendernc_data.name+".{0:05}.png"

        for ii in range(1,time+1):
            self.data2texture(ii,x_res,y_res, bpy.types.Scene.blender_var_names)
            progress_manager.progress_update(ii/time*100)

        progress_manager.progress_end()

        if len( bpy.types.Scene.blender_var_names.keys()) == 2:
            bpy.data.images[image_format.format(1)].source = "FILE"
        elif len( bpy.types.Scene.blender_var_names.keys()) >= 3:
            bpy.data.images[image_format.format(1)].source = "SEQUENCE"
        
        # STORE if BAKED
        bpy.data.images[image_format.format(1)].filepath = bpy.path.relpath(save_path)
        bpy.data.images[image_format.format(1)].reload()

        ## LAGGED FRAMES bpy.data.images['temp.00000.png.001'].frame_duration
        return {'FINISHED'}

    def data2texture(self,keyframe,x_res,y_res,coords_names):
        """
        """
        max_value = bpy.context.scene.blendernc_data.max()
        min_value = bpy.context.scene.blendernc_data.min()
        
        image_format = bpy.context.scene.blendernc_data.name+".{0:05}.png"
        image_name = image_format.format(1)

        if image_name not in bpy.data.images.keys():
            bpy.data.images.new(image_name,width=x_res, height=y_res, alpha=True, 
                            float_buffer=True)
        elif bpy.data.images[image_name].size[0] != x_res:
            bpy.data.images[image_name].scale(x_res,y_res)
        
        outputImg = bpy.data.images[image_name] 
        if 'time' in coords_names.keys() :
            data_snapshot = bpy.context.scene.blendernc_data.isel({ bpy.types.Scene.blender_var_names['time']:keyframe-1})
        else:
            data_snapshot = bpy.context.scene.blendernc_data
        alpha_channel = data_snapshot.where(np.isfinite(data_snapshot),0).where(~np.isfinite(data_snapshot),1).values
        normalized_data = (data_snapshot - min_value) / (max_value-min_value)

        #BW in RGB format for image
        rgb = np.repeat(normalized_data.values[:, :, np.newaxis], 3, axis=2)

        #BW = normalized_data.values[:, :, np.newaxis]
        np_out_img = np.concatenate((rgb,alpha_channel[:,:,np.newaxis]),axis=2)
        
        # Write image pixels
        outputImg.pixels = np_out_img.ravel()
        
        save_path = os.path.join(tmp_folder_path,image_format.format(ii))
        bpy.data.images[image_name].save_render(save_path)