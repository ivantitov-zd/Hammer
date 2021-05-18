import os

import hou

try:
    DB_FILE_PATH = os.environ['HAMMER_MATERIAL_LIB_DB_PATH']
except KeyError:
    DB_FILE_PATH = os.path.join(hou.homeHoudiniDirectory(), 'hammer_material_lib.db')
