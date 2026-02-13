import subprocess
import platform
import logging
from src.utils.logger import log

def run_silent_command(cmd, timeout=10, check=False):
    """
    Esegue un comando subprocess nascondendo la finestra su Windows.
    Su Linux esegue normalmente.
    
    Args:
        cmd (list): Lista degli argomenti del comando.
        timeout (int): Timeout in secondi.
        check (bool): Se True, solleva CalledProcessError se il returncode != 0.
        
    Returns:
        subprocess.CompletedProcess: Il risultato dell'esecuzione.
    """
    startupinfo = None
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    # SW_HIDE = 0
    startupinfo.wShowWindow = 0

    try:
        # Usa anche creationflags se necessario per alcune versioni di PyInstaller/Windows
        creationflags = 0
        # Usa anche creationflags se necessario per alcune versioni di PyInstaller/Windows
        creationflags = subprocess.CREATE_NO_WINDOW

        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            startupinfo=startupinfo,
            creationflags=creationflags,
            check=check
        )
    except subprocess.TimeoutExpired:
        log.error(f"Timeout comando: {cmd}")
        raise
    except Exception as e:
        log.error(f"Errore esecuzione comando {cmd}: {e}")
        raise
