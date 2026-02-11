import requests
import webbrowser
from packaging import version
from src.utils.logger import log
from src.utils.version import APP_VERSION, APP_REPO

class UpdateManager:
    """
    Gestisce il controllo degli aggiornamenti tramite GitHub Releases.
    """

    def __init__(self):
        self.current_version = APP_VERSION
        # GitHub API URL per l'ultima release
        # Trasforma "https://github.com/elphio-gh/lab-internet-control" 
        # in "https://api.github.com/repos/elphio-gh/lab-internet-control/releases/latest"
        repo_path = APP_REPO.replace("https://github.com/", "")
        self.api_url = f"https://api.github.com/repos/{repo_path}/releases/latest"

    def check_for_updates(self):
        """
        Controlla se esiste una versione più recente su GitHub.
        Restituisce una tupla (has_update, latest_version_tag, download_url).
        """
        try:
            log.info(f"Controllo aggiornamenti su: {self.api_url}")
            response = requests.get(self.api_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                latest_tag = data.get("tag_name", "").strip()
                html_url = data.get("html_url", "")
                
                # Pulizia robusta versione (gestisce v0.3.1, v.0.3.1, .0.3.1)
                clean_latest = latest_tag.lstrip("v").lstrip(".")
                clean_current = self.current_version.lstrip("v").lstrip(".")
                
                log.debug(f"Confronto versioni: Cloud='{clean_latest}' vs Local='{clean_current}'")
                
                if version.parse(clean_latest) > version.parse(clean_current):
                    log.info(f"Nuovo aggiornamento trovato: {latest_tag}")
                    
                    # [NEW] Cerca asset .exe per download diretto
                    download_url = html_url
                    assets = data.get("assets", [])
                    for asset in assets:
                        name = asset.get("name", "").lower()
                        if name.endswith(".exe"):
                            download_url = asset.get("browser_download_url")
                            break
                            
                    return True, latest_tag, download_url
                else:
                    log.info("Nessun aggiornamento disponibile.")
                    return False, latest_tag, html_url
            else:
                log.warning(f"Errore API GitHub: {response.status_code}")
                return False, None, None

        except Exception as e:
            log.error(f"Eccezione controllo aggiornamenti: {e}")
            return False, None, None

    def open_download_page(self, url):
        """Apre la pagina di download nel browser predefinito."""
        if url:
            webbrowser.open(url)

    def download_installer(self, url, progress_callback=None):
        """
        Scarica l'installer dalla URL fornita.
        progress_callback(float): funzione chiamata con progresso 0.0-1.0
        Ritorna il path del file scaricato o None in caso di errore.
        """
        import os
        import tempfile
        try:
            log.info(f"Avvio download aggiornamento da: {url}")
            response = requests.get(url, stream=True, timeout=10)
            total_size = int(response.headers.get('content-length', 0))
            
            # Cartella Temp
            temp_dir = tempfile.gettempdir()
            # Nome file (o default se non deducibile)
            file_name = url.split("/")[-1]
            if not file_name.endswith(".exe"):
                file_name = "LabInternetControl_Update.exe"
                
            file_path = os.path.join(temp_dir, file_name)
            
            downloaded = 0
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            progress_callback(downloaded / total_size)
            
            log.info(f"Download completato: {file_path}")
            return file_path
            
        except Exception as e:
            log.error(f"Errore download aggiornamento: {e}")
            return None

    def run_installer(self, file_path):
        """
        Lancia l'installer e chiude l'applicazione corrente.
        """
        import subprocess
        import sys
        import os
        import platform
        
        try:
            log.info(f"Avvio installer: {file_path}")
            
            if platform.system() == "Windows":
                os.startfile(file_path)
            else:
                # Fallback Linux (magari chmod +x)
                subprocess.Popen(["xdg-open", file_path])
            
            # Chiude l'applicazione
            sys.exit(0)
            
        except Exception as e:
            log.error(f"Errore avvio installer: {e}")

