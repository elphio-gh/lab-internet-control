import os
import tempfile
import platform
import concurrent.futures
from src.utils.logger import log
from src.utils.config import config
from src.utils.process import run_silent_command

class LabController:
    """
    Controller centralizzato per la gestione del laboratorio.
    Unifica le funzionalità di:
    - PAC Manager (whitelist/blacklist)
    - Command Dispatcher (invio comandi Veyon)
    - Registry Manager (logica eliminata, ora integrata qui)
    """

    def __init__(self):
        # --- Stato PAC ---
        self.whitelist = []
        self.pac_file_path = None
        
        # [FIX] Inizializza lo stato in base all'ultima configurazione salvata
        last_state = config.get("last_state", "ON")
        self.mode = "UNLOCKED" if last_state == "ON" else "RESTRICTED"
        log.info(f"LabController inizializzato. Mode: {self.mode} (Last State: {last_state})")

        # --- Config Veyon ---
        self.veyon_cli = config.get("veyon_cli_path")

    # ==========================
    # SEZIONE PAC / WHITELIST
    # ==========================

    def set_mode(self, mode):
        """Imposta la modalità operativa (RESTRICTED o UNLOCKED)."""
        if mode in ["RESTRICTED", "UNLOCKED"]:
            self.mode = mode
            log.info(f"LabController mode set to: {self.mode}")

    def update_whitelist(self, new_whitelist):
        """Aggiorna la lista dei siti consentiti."""
        self.whitelist = new_whitelist
        log.info(f"Whitelist aggiornata: {len(self.whitelist)} domini.")

    def generate_pac_script(self):
        """Genera il codice JavaScript del file PAC."""
        script = "function FindProxyForURL(url, host) {\n"
        
        if self.mode == "UNLOCKED":
             script += '    return "DIRECT";\n'
             script += "}\n"
             return script

        # Whitelist exceptions
        for domain in self.whitelist:
            script += f'    if (shExpMatch(host, "*{domain}")) return "DIRECT";\n'

        # Default block (fake proxy)
        script += '    return "PROXY 127.0.0.1:6666";\n'
        script += "}\n"
        
        return script

    def save_pac_file(self):
        """Salva lo script su file temporaneo (opzionale)."""
        script_content = self.generate_pac_script()
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pac') as tmp:
                tmp.write(script_content)
                self.pac_file_path = tmp.name
                log.info(f"File PAC generato in: {self.pac_file_path}")
                return self.pac_file_path
        except Exception as e:
            log.error(f"Errore creazione file PAC: {e}")
            return None

    # ==========================
    # SEZIONE DISPATCHER / VEYON
    # ==========================

    def _execute_remote_command(self, host, command):
        """Esegue un comando su un PC remoto usando Veyon CLI."""
        if platform.system() != "Windows":
             log.warning(f"[MOCK VEYON] Su {host} esegui: {command}")
             return True

        if not os.path.exists(self.veyon_cli):
            log.error(f"Veyon CLI non trovato in: {self.veyon_cli}")
            return False

        full_cmd = [self.veyon_cli, "remoteaccess", "execute", host, command]
        
        try:
            # run_silent_command elimina il popup nero
            result = run_silent_command(full_cmd, timeout=10)
            
            # Veyon CLI Crash Workaround codes
            CMD_SUCCESS_CODES = [0, 3221225477, -1073741819] 
            
            if result.returncode in CMD_SUCCESS_CODES:
                log.info(f"Comando inviato con successo a {host} (RC={result.returncode})")
                return True
            else:
                log.error(f"Errore comando su {host}: {result.stderr} (RC={result.returncode})")
                return False

        except Exception as e:
            log.error(f"Eccezione esecuzione comando su {host}: {e}")
            return False

    def block_internet(self, hosts, mode="restart"):
        """Blocca internet su una lista di host."""
        
        # Aggiorna stato interno
        self.set_mode("RESTRICTED")

        # 1. Comando REG per attivare Proxy Fake
        cmd_block = 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyServer /t REG_SZ /d "127.0.0.1:6666" /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1 /f'
        
        # 2. Gestione RunOnce (Fail-safe al riavvio)
        if mode == "restart":
            cmd_runonce = 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce" /v SbloccoEmergenza /t REG_SZ /d "cmd /c reg add \\"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\" /v ProxyEnable /t REG_DWORD /d 0 /f" /f'
            full_cmd = f"{cmd_block} && {cmd_runonce}"
            log.info("Blocking Mode: RESTART (RunOnce set)")
        else:
            cmd_del_runonce = 'reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce" /v SbloccoEmergenza /f'
            full_cmd = f"{cmd_block} && ({cmd_del_runonce} || echo RunOnce not present)"
            log.info("Blocking Mode: MANUAL (RunOnce clear)")
        
        # 3. Assicuriamoci che AutoConfigURL (PAC) sia vuoto
        cmd_clear_pac = 'reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v AutoConfigURL /f'
        full_cmd = f"({cmd_clear_pac} || echo No PAC) && {full_cmd}"
        
        for host in hosts:
            self._execute_remote_command(host, full_cmd)

    def unblock_internet(self, hosts):
        """Sblocca internet."""
        
        # Aggiorna stato interno
        self.set_mode("UNLOCKED")

        # Disabilita Proxy Manuale
        cmd_proxy = 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f'
        # Rimuovi PAC se presente
        cmd_pac = 'reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v AutoConfigURL /f'
        
        cmd = f'{cmd_proxy} && ({cmd_pac} || echo No PAC to delete)'
        
        for host in hosts:
            self._execute_remote_command(host, cmd)

    def apply_whitelist(self, hosts, pac_url):
        """Applica la whitelist tramite PAC."""
        
        # Aggiorna stato interno (Whitelist è comunque Restricted mode nel PAC)
        self.set_mode("RESTRICTED")

        # 1. Imposta URL autoconfig
        cmd_pac = f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v AutoConfigURL /t REG_SZ /d "{pac_url}" /f'
        
        # 2. Disabilita Proxy Manuale per evitare conflitti
        cmd_proxy_off = 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f'
        
        cmd = f'{cmd_pac} && {cmd_proxy_off}'
        
        for host in hosts:
            self._execute_remote_command(host, cmd)

    def scan_status(self, hosts, udp_port=5005):
        """Scansione stato PC via PowerShell + UDP Broadcast."""
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
        ps_oneliner = ps_script.replace('\n', ' ').replace('  ', ' ')
        full_cmd = f'powershell -WindowStyle Hidden -Command "{ps_oneliner}"'
        
        if platform.system() != "Windows":
             log.info(f"[NO-OP SCAN] Skipping remote command for {len(hosts)} hosts.")
             return

        # Parallel execution
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(self._execute_remote_command, host, full_cmd): host for host in hosts}
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    log.error(f"Errore scan parallelo: {e}")
        
        log.info(f"Scansione completata per {len(hosts)} host.")

# Istanza globale
lab_controller = LabController()
