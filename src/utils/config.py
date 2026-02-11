import json
import os
from src.utils.logger import log

class Config:
    """
    Gestisce la configurazione dell'applicazione.
    Carica le impostazioni da un file JSON o usa i valori di default.
    """
    
    DEFAULT_CONFIG = {
        "lab_name": "Laboratorio 1",
        "udp_port": 5005,
        "http_port": 8080,
        "default_mode": "restart", # "restart" o "manual"
        "whitelist": ["google.com", "wikipedia.org", "classroom.google.com"],
        "veyon_cli_path": "C:\\Program Files\\Veyon\\veyon-cli.exe"
    }

    def __init__(self, config_file="config.json"):
        # 🎓 DIDATTICA: Identifichiamo dove salvare la configurazione per essere sicuri di avere i permessi.
        if os.name == 'nt' and not os.path.exists(config_file):
            # Se siamo su Windows e non c'è un file config locale (tipico di un'installazione)
            # usiamo la cartella AppData.
            appdata_dir = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
            config_dir = os.path.join(appdata_dir, "LabInternetControl")
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            self.config_file = os.path.join(config_dir, "config.json")
        else:
            # In sviluppo o se il file è presente nella cartella exe (portable mode)
            self.config_file = config_file
            
        self.data = self._load_config()

    def _load_config(self):
        """
        Carica la configurazione dal file JSON.
        Se il file non esiste, lo crea con i valori di default.
        """
        if not os.path.exists(self.config_file):
            log.warning(f"File di configurazione '{self.config_file}' non trovato. Creo quello di default.")
            self._save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG
        
        try:
            with open(self.config_file, 'r') as f:
                # 🎓 DIDATTICA: Leggiamo il file JSON e lo convertiamo in un dizionario Python.
                return json.load(f)
        except Exception as e:
            log.error(f"Errore nel caricamento della configurazione: {e}. Uso i default.")
            return self.DEFAULT_CONFIG

    def _save_config(self, data):
        """Salva la configurazione su file JSON."""
        try:
            with open(self.config_file, 'w') as f:
                # 🎓 DIDATTICA: Scriviamo il dizionario su file JSON con indentazione per renderlo leggibile.
                json.dump(data, f, indent=4)
        except Exception as e:
            log.error(f"Errore nel salvataggio della configurazione: {e}")

    def get(self, key, default=None):
        """
        Recupera un valore dalla configurazione.
        Ordine: 1. Config utente, 2. Default hardcoded, 3. Default argomento
        """
        if key in self.data:
            return self.data[key]
        if key in self.DEFAULT_CONFIG:
            return self.DEFAULT_CONFIG[key]
        return default

    def set(self, key, value):
        """Imposta un valore e salva la configurazione."""
        self.data[key] = value
        self._save_config(self.data)

# Istanza globale pronta all'uso
config = Config()
