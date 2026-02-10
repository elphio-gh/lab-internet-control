import sys
import os
from abc import ABC, abstractmethod
from src.utils.logger import log

class BaseRegistryManager(ABC):
    """
    Classe base astratta per la gestione del registro di sistema.
    Definisce i metodi che devono essere implementati sia dalla versione Windows (reale)
    che dalla versione Linux (mock/simulata).
    """

    @abstractmethod
    def enable_proxy(self, proxy_address="127.0.0.1:6666"):
        """Attiva il proxy globale."""
        pass

    @abstractmethod
    def disable_proxy(self):
        """Disattiva il proxy e ripristina la connessione diretta."""
        pass

    @abstractmethod
    def set_pac_url(self, pac_url):
        """Imposta l'URL per il file PAC (whitelist)."""
        pass

    @abstractmethod
    def set_run_once_restore(self):
        """Imposta la chiave RunOnce per ripristinare Internet al riavvio."""
        pass
    
    @abstractmethod
    def remove_run_once_restore(self):
        """Rimuove la chiave RunOnce (usato quando si sblocca manualmente)."""
        pass


class WindowsRegistryManager(BaseRegistryManager):
    """
    Implementazione reale per Windows usando la libreria 'winreg'.
    """
    def __init__(self):
        try:
            import winreg
            self.winreg = winreg
            log.info("Windows Registry Manager inizializzato.")
        except ImportError:
            log.error("Impossibile importare 'winreg'. Sei su Windows?")
            raise

    def _set_internet_settings(self, name, value, type):
        """Helper per scrivere in HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings"""
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
        try:
            key = self.winreg.OpenKey(self.winreg.HKEY_CURRENT_USER, key_path, 0, self.winreg.KEY_WRITE)
            self.winreg.SetValueEx(key, name, 0, type, value)
            self.winreg.CloseKey(key)
            log.info(f"Registro: Impostato {name} = {value}")
        except Exception as e:
            log.error(f"Errore scrittura registro {name}: {e}")

    def _delete_internet_value(self, name):
        """Helper per cancellare un valore"""
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
        try:
            key = self.winreg.OpenKey(self.winreg.HKEY_CURRENT_USER, key_path, 0, self.winreg.KEY_WRITE)
            self.winreg.DeleteValue(key, name)
            self.winreg.CloseKey(key)
            log.info(f"Registro: Cancellato {name}")
        except FileNotFoundError:
            pass # Già assente
        except Exception as e:
            log.error(f"Errore cancellazione registro {name}: {e}")
            
    def _notify_system(self):
        """Notifica al sistema che le impostazioni sono cambiate (senza riavvio)."""
        # 🎓 DIDATTICA: Questo comando dice a Windows "Ehi, ho cambiato le impostazioni proxy, aggiornati subito!"
        # Usa ctypes per chiamare una funzione di sistema.
        try:
            import ctypes
            # INTERNET_OPTION_SETTINGS_CHANGED = 39
            # INTERNET_OPTION_REFRESH = 37
            ctypes.windll.wininet.InternetSetOptionW(0, 39, 0, 0)
            ctypes.windll.wininet.InternetSetOptionW(0, 37, 0, 0)
            log.info("Notifica di sistema InternetSetOption inviata.")
        except Exception as e:
            log.error(f"Errore notifica sistema: {e}")

    def enable_proxy(self, proxy_address="127.0.0.1:6666"):
        self._set_internet_settings("ProxyEnable", 1, self.winreg.REG_DWORD)
        self._set_internet_settings("ProxyServer", proxy_address, self.winreg.REG_SZ)
        self._set_internet_settings("AutoDetect", 0, self.winreg.REG_DWORD) # Disabilita rilevamento autom.
        self._delete_internet_value("AutoConfigURL") # Rimuove script PAC se presente
        self._notify_system()

    def disable_proxy(self):
        self._set_internet_settings("ProxyEnable", 0, self.winreg.REG_DWORD)
        self._delete_internet_value("ProxyServer")
        self._set_internet_settings("AutoDetect", 1, self.winreg.REG_DWORD) # Riabilita rilevamento autom. (default windows)
        self._delete_internet_value("AutoConfigURL")
        self._notify_system()

    def set_pac_url(self, pac_url):
        self._set_internet_settings("ProxyEnable", 0, self.winreg.REG_DWORD) # Proxy server manuale OFF quando si usa PAC
        self._delete_internet_value("ProxyServer")
        self._set_internet_settings("AutoConfigURL", pac_url, self.winreg.REG_SZ)
        self._notify_system()

    def set_run_once_restore(self):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\RunOnce"
        cmd = 'cmd /c reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f'
        try:
            key = self.winreg.OpenKey(self.winreg.HKEY_CURRENT_USER, key_path, 0, self.winreg.KEY_WRITE)
            self.winreg.SetValueEx(key, "SbloccoEmergenza", 0, self.winreg.REG_SZ, cmd)
            self.winreg.CloseKey(key)
            log.info("Impostato sblocco di emergenza in RunOnce.")
        except Exception as e:
            log.error(f"Errore RunOnce: {e}")

    def remove_run_once_restore(self):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\RunOnce"
        try:
            key = self.winreg.OpenKey(self.winreg.HKEY_CURRENT_USER, key_path, 0, self.winreg.KEY_WRITE)
            self.winreg.DeleteValue(key, "SbloccoEmergenza")
            self.winreg.CloseKey(key)
            log.info("Rimosso sblocco di emergenza da RunOnce.")
        except FileNotFoundError:
            pass
        except Exception as e:
            log.error(f"Errore rimozione RunOnce: {e}")


class LinuxMockRegistryManager(BaseRegistryManager):
    """
    Implementazione Mock per Linux.
    Scrive solo nei log cosa 'farebbe' su Windows.
    Utile per sviluppare la UI su Linux senza rompere nulla.
    """
    def enable_proxy(self, proxy_address="127.0.0.1:6666"):
        log.warning(f"[MOCK WINDOWS] Abilitazione Proxy: {proxy_address}")
        log.warning("[MOCK WINDOWS] Notifica sistema inviata.")

    def disable_proxy(self):
        log.warning("[MOCK WINDOWS] Disabilitazione Proxy (Internet Libero).")
        log.warning("[MOCK WINDOWS] Notifica sistema inviata.")

    def set_pac_url(self, pac_url):
        log.warning(f"[MOCK WINDOWS] Impostazione PAC URL: {pac_url}")
        log.warning("[MOCK WINDOWS] Notifica sistema inviata.")

    def set_run_once_restore(self):
        log.warning("[MOCK WINDOWS] Aggiunta chiave RunOnce per sblocco al riavvio.")

    def remove_run_once_restore(self):
        log.warning("[MOCK WINDOWS] Rimossa chiave RunOnce.")


# 🎓 DIDATTICA: Factory method per restituire la classe giusta in base al sistema operativo.
def get_registry_manager():
    if sys.platform == "win32":
        return WindowsRegistryManager()
    else:
        log.info("Siamo su Linux/Mac. Uso il RegistryManager simulato.")
        return LinuxMockRegistryManager()
