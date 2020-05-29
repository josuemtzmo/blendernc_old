import logging
import os

logger = logging.getLogger(__name__)

def get_addon_path():
    addon_directory = os.path.dirname(os.path.realpath(__file__))
    data_file = os.path.join(addon_directory, "data")

    if not os.path.isfile(data_file):
        logger.critical("Please check your Blender addons directory.")
        return None

    return data_dir

def tmp_folder(blender_file_path):
    if os.path.exists(os.path.join(blender_file_path,'.tmp_blendernc/')):
        pass
    else:
        os.mkdir(os.path.join(blender_file_path,'.tmp_blendernc/'))
