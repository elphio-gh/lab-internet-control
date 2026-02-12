import csv
import subprocess
import os
import random
import platform
import json
from src.utils.logger import log
from src.utils.config import config
from src.utils.process import run_silent_command


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
        
        # 2. Se vuoto (o Linux/Errore), restituisce lista vuota
        if not hosts:
            if platform.system() != "Windows":
                 log.info("Sistema non-Windows rilevato. Controllo simulazione...")
                 # Mock per Linux: Legge file JSON locale se esiste
                 sim_file = "simulated_hosts.json"
                 if os.path.exists(sim_file):
                     try:
                         with open(sim_file, 'r') as f:
                             hosts = json.load(f)
                         hosts.sort()
                         log.info(f"Caricati {len(hosts)} host simulati da {sim_file}")
                     except Exception as e:
                         log.error(f"Errore lettura {sim_file}: {e}")
            else:
                 log.warning("Impossibile recuperare host da Veyon.")
            
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
        
        # 🎓 DIDATTICA: Forziamo un formato esplicito per evitare problemi di parsing.
        # Sintassi corretta: veyon-cli ... export <FILE> format <FORMAT_STRING>
        cmd = [
            self.veyon_cli, "networkobjects", "export", tmp_csv,
            "format", "%type%;%name%;%host%;%mac%;%location%"
        ]
        
        try:
            # [FIX] Usa run_silent_command per evitare popup
            result = run_silent_command(cmd, timeout=5)
            
            # [FIX] Veyon CLI Bug workaround: Su Windows può crashare (0xC0000005) all'uscita 
            # pur avendo completato il lavoro. Controlliamo l'esistenza del file invece del returncode.
            if os.path.exists(tmp_csv) and os.path.getsize(tmp_csv) > 0:
                hosts = []
                # 🎓 DIDATTICA: Leggiamo il CSV con delimitatore ';' e newline='' per compatibilità universale
                with open(tmp_csv, 'r', encoding='utf-8', newline='') as f:
                    reader = csv.reader(f, delimiter=';')
                    for row in reader:
                        # Format: type;name;host;mac;location
                        if len(row) >= 2:
                            # Skip header se presente (controlliamo i primi due campi)
                            if row[0].lower() == "type" and row[1].lower() == "name":
                                continue
                                
                            # 🎓 DIDATTICA: Preferiamo il "Nome" visuale di Veyon, fallback su Host/IP
                            name = row[1].strip()
                            host = row[2].strip() if len(row) > 2 else ""
                            
                            # Workaround per nomi default "Nuovo computer" -> meglio usare Hostname per univocità
                            # Se il nome è generico, preferiamo l'host
                            if name.lower() == "nuovo computer" and host:
                                candidate = host
                            else:
                                candidate = name if name else host

                            if candidate:
                                hosts.append(candidate)
                
                try:
                    os.remove(tmp_csv)
                except OSError:
                    pass 
                    
                log.info(f"Recuperati {len(hosts)} host da Veyon CLI (RC={result.returncode}).")
                return hosts
            else:
                if result.returncode != 0:
                    log.error(f"Errore export Veyon: {result.stderr} (Code: {result.returncode})")
                return []
        except Exception as e:
            log.error(f"Eccezione Veyon CLI: {e}")
            return []


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
             log.warning("Export CSV non disponibile su Linux (Richiede Veyon CLI).")
             return False, "Operazione disponibile solo su Windows con Veyon."

        cmd = [
            self.veyon_cli, 
            "networkobjects", 
            "export", 
            file_path, 
            "format", "%type%;%name%;%host%;%mac%;%location%"
        ]
        
        try:
            # [FIX] Usa run_silent_command
            result = run_silent_command(cmd, timeout=10)
            
            # [FIX] Workaround crash Veyon: check file output
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                log.info(f"Export Veyon completato su {file_path} (RC={result.returncode})")
                return True, "Esportazione completata con successo."
            else:
                msg = result.stderr if result.stderr else f"Exit Code {result.returncode}"
                log.error(f"Errore export Veyon: {msg}")
                return False, f"Errore Veyon: {msg}"
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
             log.warning("Import CSV non disponibile su Linux (Richiede Veyon CLI).")
             return False, "Operazione disponibile solo su Windows con Veyon."

        try:
            # 1. Clear se richiesto
            if clear_existing:
                log.info("Richiesta cancellazione Network Objects Veyon pre-import.")
                cmd_clear = [self.veyon_cli, "networkobjects", "clear"]
                # [FIX] run_silent_command
                res_clear = run_silent_command(cmd_clear, timeout=10)
                # Anche qui potremmo dover ignorare il returncode se Veyon crasha sempre...
                # Per ora lasciamo il check ma con log
                if res_clear.returncode != 0:
                     log.warning(f"Clear Veyon RC={res_clear.returncode}. Continuo comunque.")
            
            # 2. Import
            # cmd: veyon-cli networkobjects import <file> format <FORMAT>
            cmd_import = [
                self.veyon_cli, 
                "networkobjects", 
                "import", 
                file_path, 
                "format", "%type%;%name%;%host%;%mac%;%location%"
            ]
            
            # [FIX] run_silent_command
            res_import = run_silent_command(cmd_import, timeout=15)
            
            # Workaround per Import: qui non possiamo controllare un file di output.
            # Dobbiamo sperare che se stdout dice [OK] sia andato tutto bene, o ignorare RC negativo.
            # Il log dell'utente mostrava STDOUT: '[OK]\n'
            
            if "[OK]" in res_import.stdout or res_import.returncode == 0:
                log.info(f"Import Veyon completato da {file_path} (RC={res_import.returncode})")
                return True, "Importazione completata con successo."
            else:
                msg = res_import.stderr if res_import.stderr else f"Exit Code {res_import.returncode}"
                log.error(f"Errore import Veyon: {msg}")
                return False, f"Errore Veyon: {msg}"

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
