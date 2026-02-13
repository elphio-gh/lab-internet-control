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
        # 🎓 DIDATTICA: Su Windows, se l'app è in Program Files, non possiamo scrivere log lì.
        # Usiamo %LOCALAPPDATA% per i log persistenti dell'utente.
        if os.name == 'nt':
            appdata_dir = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
            log_dir = os.path.join(appdata_dir, "LabInternetControl", "logs")
        else:
            # Su Linux/Sviluppo manteniamo la cartella locale per ora
            log_dir = "logs"

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 🎓 DIDATTICA: Il nome del file include la data, così ogni giorno ha il suo log.
        self.log_file_path = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y-%m-%d')}.log")

        # 🎓 DIDATTICA: Configuriamo il formato del log: Data - Livello - Messaggio.
        handlers = [logging.FileHandler(self.log_file_path, encoding='utf-8')]
        
        # 🎓 DIDATTICA: Aggiungiamo lo StreamHandler solo se abbiamo una console (sys.stdout)
        # Con pythonw.exe sys.stdout potrebbe essere None.
        if sys.stdout:
            handlers.append(logging.StreamHandler(sys.stdout))

        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=handlers
        )
        
        # 🎓 DIDATTICA: Silenziamo i log di debug di PIL (Pillow) che sono troppo verborroici (STREAM b'IHDR'...)
        logging.getLogger("PIL").setLevel(logging.INFO)
        
        self.logger = logging.getLogger("LabInternetControl")
        
        # Scriviamo l'header di sessione
        self.write_header()

    def get_log_file_path(self):
        """Restituisce il percorso completo del file di log corrente."""
        return self.log_file_path

    def info(self, message):
        """Registra un messaggio informativo."""
        self.logger.info(message)

    def error(self, message):
        """Registra un errore."""
        self.logger.error(message)

    def warning(self, message):
        """Registra un avviso."""
        self.logger.warning(message)

    def debug(self, message):
        """Registra un messaggio di debug."""
        self.logger.debug(message)

    def write_header(self):
        """Scrive un header grafico per l'inizio sessione."""
        sep = "=" * 60
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logger.info(f"\n{sep}\nSESSION START: {now}\n{sep}")

    def write_footer(self):
        """Scrive un footer grafico per la fine sessione."""
        sep = "-" * 60
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logger.info(f"\n{sep}\nSESSION END:   {now}\n{sep}\n")

# Istanza globale pronta all'uso
log = Logger()
