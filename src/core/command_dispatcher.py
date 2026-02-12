import subprocess
import os
import platform
from src.utils.logger import log
from src.utils.config import config
from src.utils.process import run_silent_command


class CommandDispatcher:
    """
    Gestisce l'invio dei comandi ai PC studenti tramite Veyon.
    Astrattizza l'uso di veyon-cli o altri metodi futuri.
    """

    def __init__(self):
        self.veyon_cli = config.get("veyon_cli_path")
        self.pac_manager = None

    def set_pac_manager(self, pac_manager):
        """Inietta l'istanza di PACManager per aggiornare lo stato."""
        self.pac_manager = pac_manager

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
            # [FIX] run_silent_command elimina il popup nero
            result = run_silent_command(full_cmd, timeout=10)
            
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
        
        # [NEW] Aggiorna stato PAC Manager
        if self.pac_manager:
            self.pac_manager.set_mode("RESTRICTED")

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
        
        # [NEW] Assicuriamoci che AutoConfigURL (PAC) sia vuoto per evitare conflitti
        cmd_clear_pac = 'reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v AutoConfigURL /f'
        full_cmd = f"({cmd_clear_pac} || echo No PAC) && {full_cmd}"
        
        for host in hosts:
            self._execute_remote_command(host, full_cmd)

    def unblock_internet(self, hosts):
        """Sblocca internet."""
        
        # [NEW] Aggiorna stato PAC Manager
        if self.pac_manager:
            self.pac_manager.set_mode("UNLOCKED")

        # Disabilita Proxy Manuale
        cmd_proxy = 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f'
        # Rimuovi PAC se presente
        cmd_pac = 'reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v AutoConfigURL /f'
        
        # Esegui entrambi (gestendo errore se PAC non esiste)
        cmd = f'{cmd_proxy} && ({cmd_pac} || echo No PAC to delete)'
        
        for host in hosts:
            self._execute_remote_command(host, cmd)

    def apply_whitelist(self, hosts, pac_url):
        """Applica la whitelist tramite PAC."""
        
        # [NEW] Aggiorna stato PAC Manager (Whitelist è comunque Restricted mode nel PAC)
        if self.pac_manager:
            self.pac_manager.set_mode("RESTRICTED")

        # 1. Imposta URL autoconfig
        cmd_pac = f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v AutoConfigURL /t REG_SZ /d "{pac_url}" /f'
        
        # 2. [NEW] Disabilita Proxy Manuale per evitare conflitti (lasciamo fare tutto al PAC)
        cmd_proxy_off = 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f'
        
        cmd = f'{cmd_pac} && {cmd_proxy_off}'
        
        for host in hosts:
            self._execute_remote_command(host, cmd)

    def scan_status(self, hosts, udp_port=5005):
        """
        Invia un comando PowerShell ai client per fargli inviare lo stato via UDP.
        Agent-less: Sfrutta Veyon per eseguire lo script al volo.
        """
        # Script PowerShell compattato
        # 1. Legge stato Proxy e PAC
        # 2. Ottiene Utente corrente
        # 3. Invia UDP Broadcast con formato HOST|STATUS|USER
        
        ps_script = f"""
$u=[System.Security.Principal.WindowsIdentity]::GetCurrent().Name;
$s='ON';
$p='HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings';
if((Get-ItemProperty -Path $p -Name ProxyEnable -ErrorAction SilentlyContinue).ProxyEnable -eq 1){{$s='OFF'}};
if((Get-ItemProperty -Path $p -Name AutoConfigURL -ErrorAction SilentlyContinue).AutoConfigURL){{$s='WL'}};
$c=New-Object System.Net.Sockets.UdpClient;
$b=[Text.Encoding]::UTF8.GetBytes(\"$env:COMPUTERNAME|$s|$u\");
$c.Connect('255.255.255.255',{udp_port});
$c.Send($b,$b.Length);
"""
        # Rimuoviamo newlines per passarlo come argomento singolo
        ps_oneliner = ps_script.replace('\\n', ' ').replace('  ', ' ')
        
        # Comando CMD che invoca PowerShell
        full_cmd = f'powershell -WindowStyle Hidden -Command "{ps_oneliner}"'
        
        # Esecuzione
        if platform.system() != "Windows":
             log.info(f"[NO-OP SCAN] System is not Windows. Skipping remote command for {len(hosts)} hosts.")
             return

        for host in hosts:
            self._execute_remote_command(host, full_cmd)

# Istanza globale
dispatcher = CommandDispatcher()
