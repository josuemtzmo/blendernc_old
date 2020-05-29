import bpy
import os
import xarray

from . import files_utils

class BlenderncEngine():
    def __init__(self):
        self.current_file_path = files_utils.get_addon_path()

    # TO DO : move to file_utils
    def check_files_netcdf(self,file_path):
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
        if "*" in self.file_path:
            self.dataset = xarray.open_mfdataset(self.file_path,decode_times=False)
        else:
            self.dataset = xarray.open_dataset(self.file_path,decode_times=False)

    def netcdf_var(self):
        dimensions=[i for i in self.dataset.coords.dims.keys()]
        variable = list(self.dataset.variables.keys() - dimensions)

        var_names = [(variable[ii], variable[ii], self.dataset[variable[ii]].long_name, "DISK_DRIVE", ii) for ii in range(len(variable))]
        return var_names

    def netcdf_values(self,selected_variable,res):
        self.selected_variable=selected_variable
        active_resolution = res/100

        variable = self.dataset[selected_variable]
        
        dict_var_shape = {ii:slice(0,variable[ii].size,
                int(variable[ii].size//(variable[ii].size*active_resolution))) 
                for ii in variable.coords if 'time' not in ii}
        print(selected_variable,dict_var_shape)
        variable_res = variable#.isel(dict_var_shape)
        return variable_res
    

        #print(self.file_path)
        #self.assets_models = file_ops.generate_items_list(self.assets_path, "blend")