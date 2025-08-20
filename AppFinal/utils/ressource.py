import sys, os

def resource_path(relative_path):
    """Retourne le chemin correct selon qu'on est en .exe ou en mode script"""
    if hasattr(sys, "_MEIPASS"):
        # Cas PyInstaller (exécutable)
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)
