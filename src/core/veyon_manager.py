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


    def export_csv(self, file_path):
        """
        Esporta la configurazione dei Network Objects di Veyon in un file CSV.
        Usa il formato: %type%;%name%;%host%;%mac%;%location%
        """
        if not os.path.exists(self.veyon_cli) and platform.system() == "Windows":
             log.error(f"Veyon CLI non trovato per export: {self.veyon_cli}")
             return False, "Veyon CLI non trovato."

        # Comando: veyon-cli networkobjects export <file> format:...
        # Su Linux/Mock potremmo voler simulare se non c'è veyon.
        if platform.system() != "Windows":
             log.info(f"[MOCK] Esportazione CSV simulata verso {file_path}")
             try:
                 with open(file_path, 'w') as f:
                     f.write("type;name;host;mac;location\n")
                     f.write("computer;PC-01;PC-01;00:11:22:33:44:55;Lab1\n")
                 return True, "Export simulato completato."
             except Exception as e:
                 return False, str(e)

        cmd = [
            self.veyon_cli, 
            "networkobjects", 
            "export", 
            file_path, 
            "format:%type%;%name%;%host%;%mac%;%location%"
        ]
        
        try:
            # CREATE_NO_WINDOW per evitare popup su Windows se non si usa wcli (ma qui usiamo cli standard)
            # Se usiamo veyon-wcli sarebbe meglio, ma config ha veyon_cli_path generico.
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                log.info(f"Export Veyon completato su {file_path}")
                return True, "Esportazione completata con successo."
            else:
                log.error(f"Errore export Veyon: {result.stderr}")
                return False, f"Errore Veyon: {result.stderr}"
        except Exception as e:
            log.error(f"Eccezione Export Veyon: {e}")
            return False, str(e)

    def import_csv(self, file_path, clear_existing=False):
        """
        Importa una configurazione CSV in Veyon.
        Se clear_existing è True, prima cancella tutto.
        """
        if not os.path.exists(self.veyon_cli) and platform.system() == "Windows":
             return False, "Veyon CLI non trovato."

        if platform.system() != "Windows":
             log.info(f"[MOCK] Importazione CSV simulata da {file_path} (Clear={clear_existing})")
             return True, "Importazione simulata completata."

        try:
            # 1. Clear se richiesto
            if clear_existing:
                log.info("Richiesta cancellazione Network Objects Veyon pre-import.")
                cmd_clear = [self.veyon_cli, "networkobjects", "clear"]
                res_clear = subprocess.run(cmd_clear, capture_output=True, text=True, timeout=10)
                if res_clear.returncode != 0:
                     return False, f"Errore cancellazione dati esistenti: {res_clear.stderr}"
            
            # 2. Import
            # cmd: veyon-cli networkobjects import <file> format:...
            cmd_import = [
                self.veyon_cli, 
                "networkobjects", 
                "import", 
                file_path, 
                "format:%type%;%name%;%host%;%mac%;%location%"
            ]
            
            res_import = subprocess.run(cmd_import, capture_output=True, text=True, timeout=15)
            
            if res_import.returncode == 0:
                log.info(f"Import Veyon completato da {file_path}")
                return True, "Importazione completata con successo."
            else:
                log.error(f"Errore import Veyon: {res_import.stderr}")
                return False, f"Errore Veyon: {res_import.stderr}"

        except Exception as e:
            log.error(f"Eccezione Import Veyon: {e}")
            return False, str(e)


    def get_template_csv(self, file_path):
        """
        Genera un file CSV di esempio con l'intestazione e una riga di esempio.
        Questo aiuta l'utente a compilare correttamente la lista dei PC.
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # 🎓 DIDATTICA: Header richiesto da Veyon per l'importazione corretta.
                f.write("type;name;host;mac;location\n")
                # Riga di esempio per guidare l'utente
                f.write("computer;PC01-STUDENTE;192.168.1.1;00:11:22:33:44:55;Laboratorio1\n")
                f.write("computer;PC02-STUDENTE;pc02.local;00:11:22:33:44:66;Laboratorio1\n")
            return True, "File di esempio creato con successo."
        except Exception as e:
            log.error(f"Errore creazione template CSV: {e}")
            return False, str(e)

# Istanza globale
veyon = VeyonManager()
