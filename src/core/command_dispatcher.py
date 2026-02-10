import subprocess
import os
import platform
from src.utils.logger import log
from src.utils.config import config

class CommandDispatcher:
    """
    Gestisce l'invio dei comandi ai PC studenti tramite Veyon.
    Astrattizza l'uso di veyon-cli o altri metodi futuri.
    """

    def __init__(self):
        self.veyon_cli = config.get("veyon_cli_path")

    def _execute_remote_command(self, host, command):
        """
        Esegue un comando su un PC remoto usando Veyon CLI.
        """
        # 🎓 DIDATTICA: Costruiamo il comando Veyon.
        # veyon-cli remoteaccess execute <host> <command>
        # Nota: Questo richiede che l'utente che esegue lo script abbia i permessi in Veyon.
        
        if platform.system() != "Windows":
             log.warning(f"[MOCK VEYON] Su {host} esegui: {command}")
             return True

        if not os.path.exists(self.veyon_cli):
            log.error(f"Veyon CLI non trovato in: {self.veyon_cli}")
            return False

        full_cmd = [self.veyon_cli, "remoteaccess", "execute", host, command]
        
        try:
            # subprocess.run esegue il comando e aspetta che finisca.
            result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                log.info(f"Comando inviato con successo a {host}")
                return True
            else:
                log.error(f"Errore comando su {host}: {result.stderr}")
                return False

        except Exception as e:
            log.error(f"Eccezione esecuzione comando su {host}: {e}")
            return False

    def block_internet(self, hosts, mode="restart"):
        """
        Blocca internet su una lista di host.
        :param mode: "restart" (default) imposta RunOnce per sblocco, "manual" no.
        """
        
        # 1. Comando REG per attivare Proxy Fake
        cmd_block = 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyServer /t REG_SZ /d "127.0.0.1:6666" /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1 /f'
        
        # 2. Gestione RunOnce (Fail-safe al riavvio)
        if mode == "restart":
            # Comando che sblocca internet al prossimo avvio
            cmd_runonce = 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce" /v SbloccoEmergenza /t REG_SZ /d "cmd /c reg add \\"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\" /v ProxyEnable /t REG_DWORD /d 0 /f" /f'
            full_cmd = f"{cmd_block} && {cmd_runonce}"
            log.info("Blocking Mode: RESTART (RunOnce set)")
        else:
            # Mode "manual": Rimuoviamo eventuale SbloccoEmergenza precedente per evitare sblocchi accidentali
            cmd_del_runonce = 'reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce" /v SbloccoEmergenza /f'
            # || echo (per non fallire se non esiste)
            full_cmd = f"{cmd_block} && ({cmd_del_runonce} || echo RunOnce not present)"
            log.info("Blocking Mode: MANUAL (RunOnce clear)")
        
        for host in hosts:
            self._execute_remote_command(host, full_cmd)

    def unblock_internet(self, hosts):
        """Sblocca internet."""
        cmd = 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f'
        for host in hosts:
            self._execute_remote_command(host, cmd)

    def apply_whitelist(self, hosts, pac_url):
        """Applica la whitelist tramite PAC."""
        # Imposta URL autoconfig
        cmd = f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v AutoConfigURL /t REG_SZ /d "{pac_url}" /f'
        for host in hosts:
            self._execute_remote_command(host, cmd)

# Istanza globale
dispatcher = CommandDispatcher()
