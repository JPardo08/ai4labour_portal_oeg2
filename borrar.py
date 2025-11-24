import os
import shutil
from pathlib import Path

def empty_folders(folder_paths):
    """
    Elimina todo el contenido de cada carpeta en folder_paths
    (archivos y subcarpetas), pero mantiene la carpeta raíz.
    """
    for folder in folder_paths:
        f = Path(folder)
        if not f.exists():
            print(f"[!] Carpeta no encontrada: {f}")
            continue
        if not f.is_dir():
            print(f"[!] No es una carpeta: {f}")
            continue

        for item in f.iterdir():
            try:
                if item.is_file() or item.is_symlink():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            except Exception as e:
                print(f"[!] Error eliminando {item}: {e}")
        print(f"[✓] Vaciada: {f}")

def remove_folders(folder_paths):
    
    for folder in folder_paths:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f"[✓] Carpeta eliminada: {folder}")
            except Exception as e:
                print(f"[!] Error al eliminar {folder}: {e}")
        else:
            print(f"[i] Carpeta no encontrada: {folder}")



# Ejemplo de uso:
def main():
    base = os.getcwd()
    
    folders = [
        #'artifacts',
        #'general',
        #'models',
        'results',
        'plots',
        'results_coursera',
        'plots_coursera'
    ]
    
    folders_to_empty = [os.path.join(base, i) for i in folders]

    remove_folders(folders_to_empty)


if __name__=='__main__':
    main()