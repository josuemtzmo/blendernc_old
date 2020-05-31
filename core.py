import bpy
import os
import xarray
import numpy as np

from . import files_utils

class BlenderncEngine():
    """"
    """
    def __init__(self):
        self.current_file_path = files_utils.get_addon_path()

    # TO DO : move to file_utils
    def check_files_netcdf(self,file_path):
        """
        """
        if os.path.isfile(file_path):
            self.file_path = file_path
            self.check_netcdf()
        else:
            raise NameError("File doesn't exist:",file_path)
            
    def check_netcdf(self):
        """
        Check if file is a netcdf and contain at least one variable.
        """
        extension = self.file_path.split('.')[-1]
        if extension == ".nc":
            self.load_netcd()
        else:
            try:
                self.load_netcdf()
            except:
                raise ValueError("File isn't a netCDF:",self.file_path)

    def load_netcdf(self):
        """
        """
        if "*" in self.file_path:
            self.dataset = xarray.open_mfdataset(self.file_path,decode_times=False)
        else:
            self.dataset = xarray.open_dataset(self.file_path,decode_times=False)

    def netcdf_var(self):
        """
        """
        dimensions = [i for i in self.dataset.coords.dims.keys()]
        variable = list(self.dataset.variables.keys() - dimensions)

        var_names = [(variable[ii], variable[ii], self.dataset[variable[ii]].long_name, "DISK_DRIVE", ii) for ii in range(len(variable))]
        return var_names

    def netcdf_values(self,selected_variable,active_resolution):
        """
        """
        self.selected_variable = selected_variable

        variable = self.dataset[selected_variable]

        dict_var_shape = {ii:slice(0,variable[ii].size,self.resolution_steps(variable[ii].size,active_resolution))
                for ii in variable.coords if 'time' not in ii}
        print(active_resolution,selected_variable,dict_var_shape)
        # To Do: fix resolution implementation, perhaps a non linear coarsening
        variable_res = variable.isel(dict_var_shape)
        return variable_res
    
    def resolution_steps(self,size,res):
        res_interst = res/5 + 80
        log_scale = np.log10(size)/np.log10((size*res_interst/100)) - 1
        step = size * log_scale
        if step ==0:
            step = 1
        print(log_scale,step,np.log10((size*res_interst/100)),np.log10(size))
        return int(step)