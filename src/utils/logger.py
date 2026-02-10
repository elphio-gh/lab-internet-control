import logging
import os
import sys
from datetime import datetime

class Logger:
    """
    Gestisce il logging dell'applicazione.
    Salva i log su file e li mostra anche in console per il debug.
    """
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._setup()
        return cls._instance

    def _setup(self):
        # 🎓 DIDATTICA: Creiamo una cartella 'logs' se non esiste, per tenere tutto ordinato.
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 🎓 DIDATTICA: Il nome del file include la data, così ogni giorno ha il suo log.
        log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y-%m-%d')}.log")

        # 🎓 DIDATTICA: Configuriamo il formato del log: Data - Livello - Messaggio.
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),  # Scrive su file
                logging.StreamHandler(sys.stdout) # Scrive in console (utile per noi dev)
            ]
        )
        self.logger = logging.getLogger("LabInternetControl")

    def info(self, message):
        """Registra un messaggio informativo."""
        self.logger.info(message)

    def error(self, message):
        """Registra un errore."""
        self.logger.error(message)

    def warning(self, message):
        """Registra un avviso."""
        self.logger.warning(message)

# Istanza globale pronta all'uso
log = Logger()
