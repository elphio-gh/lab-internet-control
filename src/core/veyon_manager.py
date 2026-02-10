import csv
import subprocess
import os
import random
import platform
import json
from src.utils.logger import log
from src.utils.config import config

class VeyonManager:
    """
    Gestisce l'integrazione con Veyon, in particolare il recupero della lista dei PC.
    """

    def __init__(self):
        self.veyon_cli = config.get("veyon_cli_path")

    def get_hosts(self):
        """
        Restituisce una lista di hostname dei PC del laboratorio.
        Tenta di recuperarli da Veyon CLI.
        Se fallisce o è su Linux, usa un Mock.
        """
        hosts = []
        
        # 1. Tenta recupero reale (Windows)
        if platform.system() == "Windows":
            hosts = self._get_hosts_from_cli()
        
        # 2. Se vuoto (o Linux/Errore), usa Mock
        if not hosts:
            if platform.system() != "Windows":
                 log.info("Sistema non-Windows rilevato. Uso Mock Veyon Hosts.")
            else:
                 log.warning("Impossibile recuperare host da Veyon. Uso Mock.")
            hosts = self._get_mock_hosts()
            
        return hosts

    def _get_hosts_from_cli(self):
        """
        Esegue 'veyon-cli networkobjects export' e parsa l'output.
        """
        if not os.path.exists(self.veyon_cli):
            log.error(f"Veyon CLI non trovato: {self.veyon_cli}")
            return []

        # Usiamo un file temporaneo per l'esportazione CSV
        import tempfile
        tmp_csv = os.path.join(tempfile.gettempdir(), "veyon_hosts.csv")
        
        # Comando: veyon-cli networkobjects export <file> format:CSV
        # Nota: La sintassi esatta di veyon-cli purtroppo varia tra versioni.
        # Assumiamo 'networkobjects export <file>' funzioni per il CSV default.
        cmd = [self.veyon_cli, "networkobjects", "export", tmp_csv]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and os.path.exists(tmp_csv):
                hosts = []
                with open(tmp_csv, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    # Formato atteso Veyon CSV: Name,Host,MAC,Room...
                    # Ma potrebbe variare. Cerchiamo colonne che sembrano Hostname.
                    for row in reader:
                        if len(row) >= 2:
                            # Euristicamente prendiamo il secondo campo se non vuoto, o il primo
                            # Spesso: Nome, Hostname/IP
                            candidate = row[1].strip() if row[1].strip() else row[0].strip()
                            if candidate and candidate.lower() != "host": # Skip header
                                hosts.append(candidate)
                
                os.remove(tmp_csv)
                log.info(f"Recuperati {len(hosts)} host da Veyon CLI.")
                return hosts
            else:
                log.error(f"Errore export Veyon: {result.stderr}")
                return []
        except Exception as e:
            log.error(f"Eccezione Veyon CLI: {e}")
            return []

    def _get_mock_hosts(self):
        """
        Genera una lista casuale di PC per simulare un laboratorio.
        Tra 5 e 40 PC come richiesto.
        """
        count = random.randint(5, 40)
        log.info(f"Generati {count} host MOCK per la simulazione.")
        return [f"PC-{i:02d}" for i in range(1, count + 1)]

# Istanza globale
veyon = VeyonManager()
