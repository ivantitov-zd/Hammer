import tempfile
import os

TEMP_IMAGE_PATH = os.path.join(tempfile.gettempdir(), str(os.getpid()) + 'hammer_mat_lib_thumb.png').replace('\\', '/')
