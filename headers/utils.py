# headers/utils.py
import os
import sys

def get_path(relative_path):
    """Return full path to resource, supports PyInstaller and dev mode."""
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)
