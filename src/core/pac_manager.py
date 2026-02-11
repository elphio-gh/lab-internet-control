import os
import tempfile
from src.utils.logger import log
from src.utils.config import config

class PACManager:
    """
    Gestisce la creazione dinamica del file proxy.pac.
    Questo file dice al browser quali siti visitare direttamente (whitelist)
    e quali bloccare mandandoli a un proxy inesistente.
    """

    def __init__(self, whitelist=None):
        self.whitelist = whitelist if whitelist else []
        self.pac_file_path = None
        
        # [FIX] Inizializza lo stato in base all'ultima configurazione salvata (o default "ON")
        # Se l'app si chiude "Sbloccata", al riavvio deve essere "Sbloccata".
        last_state = config.get("last_state", "ON")
        self.mode = "UNLOCKED" if last_state == "ON" else "RESTRICTED"
        log.info(f"PAC Manager inizializzato in modalità: {self.mode} (da config: {last_state})")

    def set_mode(self, mode):
        """Imposta la modalità di generazione del PAC."""
        if mode in ["RESTRICTED", "UNLOCKED"]:
            self.mode = mode
            log.info(f"PAC Manager mode set to: {self.mode}")

    def update_whitelist(self, new_whitelist):
        """Aggiorna la lista dei siti consentiti."""
        self.whitelist = new_whitelist
        log.info(f"Whitelist aggiornata: {len(self.whitelist)} domini.")

    def generate_pac_script(self):
        """
        Genera il codice JavaScript del file PAC.
        """
        # 🎓 DIDATTICA: Iniziamo lo script PAC.
        # "FindProxyForURL" è la funzione standard che i browser chiamano per ogni richiesta.
        script = "function FindProxyForURL(url, host) {\n"
        
        # 🎓 DIDATTICA: Se siamo in modalità SBLOCCATA, tutto è diretto.
        if self.mode == "UNLOCKED":
             script += '    return "DIRECT";\n'
             script += "}\n"
             return script

        # 🎓 DIDATTICA: Aggiungiamo le eccezioni per la whitelist.
        # shExpMatch confronta l'host con un pattern (es. "*.google.com").
        for domain in self.whitelist:
            script += f'    if (shExpMatch(host, "*{domain}")) return "DIRECT";\n'

        # 🎓 DIDATTICA: Se non è in whitelist, MANDALO AL PROXY BLOCCATO (127.0.0.1:6666).
        # Se è in whitelist, "DIRECT" significa "vai dritto su internet senza proxy".
        script += '    return "PROXY 127.0.0.1:6666";\n'
        script += "}\n"
        
        return script

    def save_pac_file(self):
        """
        Salva lo script PAC su un file temporaneo e ritorna il percorso.
        Utile se vogliamo passarlo al browser come file:// (anche se useremo HTTP).
        """
        script_content = self.generate_pac_script()
        
        try:
            # Crea un file temporaneo 'proxy.pac'
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pac') as tmp:
                tmp.write(script_content)
                self.pac_file_path = tmp.name
                log.info(f"File PAC generato in: {self.pac_file_path}")
                return self.pac_file_path
        except Exception as e:
            log.error(f"Errore creazione file PAC: {e}")
            return None
