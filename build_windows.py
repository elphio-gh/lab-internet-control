import os
import shutil
import subprocess
import sys
import re

# 🎓 DIDATTICA: Aggiungiamo la root al path per poter importare il modulo version.
# Questo permette allo script di build di "sapere" quale versione stiamo compilando.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.utils.version import APP_VERSION

# 🎓 DIDATTICA: Questo script automatizza la pulizia, l'aggiornamento versione e la build.
# Va eseguito dentro la VM Windows dopo aver installato le dipendenze.

def update_installer_config():
    """
    Legge la versione da python e aggiorna il file di configurazione di Inno Setup (.iss).
    Così non devi modificarlo a mano ogni volta!
    """
    iss_file = "installer_config.iss"
    if not os.path.exists(iss_file):
        print(f"[ATTENZIONE] File {iss_file} non trovato. Salto aggiornamento versione.")
        return

    print(f"Aggiornamento versione in {iss_file} a v{APP_VERSION}...")
    
    try:
        with open(iss_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Regex per sostituire AppVersion=...
        content = re.sub(r"AppVersion=.*", f"AppVersion={APP_VERSION}", content)
        # Regex per sostituire OutputBaseFilename=...
        content = re.sub(r"OutputBaseFilename=.*", f"OutputBaseFilename=LabInternetControl_Setup_v{APP_VERSION}", content)
        
        with open(iss_file, "w", encoding="utf-8") as f:
            f.write(content)
            
        print("[OK] Configurazione Installer aggiornata.")
    except Exception as e:
        print(f"[ERRORE] Impossibile aggiornare .iss: {e}")

def build():
    print(f"--- Avvio Processo di Build Windows (v{APP_VERSION}) ---")
    
    # 0. Aggiorna versione in Inno Setup
    update_installer_config()

    # 1. Pulizia cartelle vecchie
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            print(f"Pulizia cartella {folder}...")
            shutil.rmtree(folder)

    # 2. Comando PyInstaller
    print("Esecuzione PyInstaller...")
    try:
        # 🎓 DIDATTICA: check=True solleva un'eccezione se il comando fallisce (exit code != 0)
        # Questo è fondamentale per la CI/CD: se la build fallisce, vogliamo che l'intero workflow si fermi!
        subprocess.run(["pyinstaller", "--noconfirm", "LabInternetControl.spec"], check=True)
        print("\n[OK] Build completata con successo nella cartella 'dist/LabInternetControl'")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERRORE CRITICO] PyInstaller è fallito con codice {e.returncode}: {e}")
        # Usciamo con un codice di errore in modo che GitHub Actions (o script chiamante) sappia che è fallito.
        sys.exit(1)

    print("\nPROSSIMO PASSO:")
    print("1. Apri Inno Setup")
    print(f"2. Compila 'installer_config.iss' (già aggiornato alla v{APP_VERSION})")
    print("3. Il file Setup.exe sarà pronto!")

if __name__ == "__main__":
    if os.name != 'nt':
        print("ATTENZIONE: Questo script è progettato per essere eseguito su WINDOWS.")
        # Se siamo in GitHub Actions, continuiamo senza chiedere
        if os.environ.get('GITHUB_ACTIONS'):
            print("Rilevato GitHub Actions: procedo con la build...")
        else:
            confirm = input("Vuoi continuare comunque su Linux (solo per test)? (s/n): ")
            if confirm.lower() != 's':
                sys.exit(0)
    
    build()
