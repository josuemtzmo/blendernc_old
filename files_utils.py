import logging

import os

logger = logging.getLogger(__name__)

def get_file_path():
    addon_directory = os.path.dirname(os.path.realpath(__file__))
    data_file = os.path.join(addon_directory, "data")

    if not os.path.isfile(data_file):
        logger.critical("Tools data not found. Please check your Blender addons directory.")
        return None

    return data_dir