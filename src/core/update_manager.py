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
                
                # Rimuovi eventuale 'v' iniziale per confronto pulito
                clean_latest = latest_tag.lstrip("v")
                clean_current = self.current_version.lstrip("v")
                
                if version.parse(clean_latest) > version.parse(clean_current):
                    log.info(f"Nuovo aggiornamento trovato: {latest_tag}")
                    return True, latest_tag, html_url
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
