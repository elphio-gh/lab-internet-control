import subprocess
import os
import sys
import platform

# Configurazione simulata
VEYON_CLI_PATH = r"C:\Program Files\Veyon\veyon-cli.exe"
TEMP_CSV = os.path.join(os.environ.get('TEMP', os.path.expanduser('~')), "debug_hosts.csv")

def run_debug():
    global VEYON_CLI_PATH
    print(f"--- DEBUG VEYON CLI WINDOWS ---")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Veyon CLI Path: {VEYON_CLI_PATH}")
    
    if not os.path.exists(VEYON_CLI_PATH):
        print("❌ ERRORE: Veyon CLI non trovato nel percorso standard!")
        # Prova a cercare in PATH
        import shutil
        if shutil.which("veyon-cli"):
            print("✅ TROVATO 'veyon-cli' nel PATH di sistema!")
            VEYON_CLI_PATH = "veyon-cli"
        else:
            print("❌ 'veyon-cli' non trovato nemmeno nel PATH.")
            return

    print(f"Temp CSV Path: {TEMP_CSV}")

    # Costruzione comando come nell'app
    # Sintassi che stiamo testando: veyon-cli networkobjects export <FILE> format <FMT>
    cmd = [
        VEYON_CLI_PATH, 
        "networkobjects", 
        "export", 
        TEMP_CSV,
        "format", 
        "%type%;%name%;%host%;%mac%;%location%"
    ]
    
    print(f"\n--- TENTATIVO 1: Esecuzione Standard (subprocess.run) ---")
    print(f"Comando: {cmd}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        print("\nRISULTATO:")
        print(f"Return Code: {result.returncode}")
        print(f"STDOUT: '{result.stdout}'")
        print(f"STDERR: '{result.stderr}'")
        
        if os.path.exists(TEMP_CSV):
            print(f"✅ File CSV creato! Dimensione: {os.path.getsize(TEMP_CSV)} bytes.")
            with open(TEMP_CSV, 'r') as f:
                print("Contenuto:")
                print(f.read())
            os.remove(TEMP_CSV)
        else:
            print("❌ File CSV NON creato.")
            
    except Exception as e:
        print(f"❌ Eccezione durante esecuzione: {e}")

    # Tentativo 2: Senza keyword 'format' separata (vecchio stile, giusto per sicurezza)
    print(f"\n--- TENTATIVO 2: Sintassi Alternativa (format:...) ---")
    cmd_alt = [
        VEYON_CLI_PATH, 
        "networkobjects", 
        "export", 
        TEMP_CSV,
        "format:%type%;%name%;%host%;%mac%;%location%"
    ]
    print(f"Comando: {cmd_alt}")
    try:
        result = subprocess.run(cmd_alt, capture_output=True, text=True, timeout=10)
        print(f"Return Code: {result.returncode}")
        print(f"STDOUT: '{result.stdout}'")
        print(f"STDERR: '{result.stderr}'")
    except Exception as e:
        print(f"Errore: {e}")

if __name__ == "__main__":
    run_debug()
    input("\nPremi INVIO per chiudere...")
