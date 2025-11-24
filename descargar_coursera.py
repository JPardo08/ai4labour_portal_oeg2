import os
import zipfile

# Carpeta donde están los CSVs en el servidor
#CSV_DIR = "/home/jovyan/Joel_Pardo/AI4LABOUR/Mejoras/results"
CSV_DIR = "/home/jovyan/Joel_Pardo/AI4LABOUR/Mejoras/results_coursera"   # <-- cámbialo
PLOTS_DIR = "/home/jovyan/Joel_Pardo/AI4LABOUR/Mejoras/plots_coursera"   # <-- cámbialo
ZIP_NAME = "results_coursera3.zip"

def zip_csvs(folders, zip_name):
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for folder in folders:
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.endswith(".csv") or file.endswith("png") or file.endswith("svg") or file.endswith("txt"):
                        full_path = os.path.join(root, file)
                        arcname = os.path.relpath(full_path, folder)
                        zipf.write(full_path, arcname)
                        print(f"Añadido: {arcname}")
    print(f"\n[OK] CSVs comprimidos en {zip_name}")

if __name__ == "__main__":
    FOLDERS = [CSV_DIR, PLOTS_DIR]
    zip_csvs(FOLDERS, ZIP_NAME)
    print(f"Descarga el archivo {ZIP_NAME} con tu navegador o con scp.")
