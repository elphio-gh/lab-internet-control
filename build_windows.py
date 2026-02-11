import os
import shutil
import subprocess
import sys

# 🎓 DIDATTICA: Questo script automatizza la pulizia e la creazione della build.
# Va eseguito dentro la VM Windows dopo aver installato le dipendenze.

def build():
    print("--- Avvio Processo di Build Windows ---")
    
    # 1. Pulizia cartelle vecchie
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            print(f"Pulizia cartella {folder}...")
            shutil.rmtree(folder)

    # 2. Comando PyInstaller
    print("Esecuzione PyInstaller...")
    try:
        subprocess.run(["pyinstaller", "--noconfirm", "LabInternetControl.spec"], check=True)
        print("\n[OK] Build completata con successo nella cartella 'dist/LabInternetControl'")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERRORE] PyInstaller è fallito: {e}")
        return

    print("\nPROSSIMO PASSO:")
    print("1. Apri Inno Setup")
    print("2. Carica 'installer_config.iss'")
    print("3. Compila per generare il file .exe finale per i laboratori.")

if __name__ == "__main__":
    if os.name != 'nt':
        print("ATTENZIONE: Questo script è progettato per essere eseguito su WINDOWS.")
        confirm = input("Vuoi continuare comunque su Linux? (s/n): ")
        if confirm.lower() != 's':
            sys.exit(0)
    
    build()
