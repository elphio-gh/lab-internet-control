import sys
import os

# 🎓 DIDATTICA: Aggiungiamo la root del progetto al path python per importare i moduli
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.app import App
from src.network.udp_server import UDPServer
from src.network.http_server import PACHTTPServer
from src.core.pac_manager import PACManager
from src.utils.logger import log

def main():
    log.info("Avvio Lab Internet Control...")

    # 1. Inizializziamo il PAC Manager
    pac_manager = PACManager()
    
    # 2. Colleghiamo il dispatcher al PAC Manager per sync stato
    dispatcher.set_pac_manager(pac_manager)

    # 3. Avviamo il server HTTP per il PAC
    http_server = PACHTTPServer(pac_manager)
    http_server.start()
    
    # 3. Inizializziamo la UI
    app = App(pac_manager)
    
    # 4. Avviamo il server UDP per la telemetria
    # Passiamo il metodo update_pc_status della app come callback
    # Nota: su Tkinter gli aggiornamenti UI devono avvenire nel thread principale.
    # CustomTkinter gestisce bene, ma per sicurezza useremo app.after se necessario.
    def udp_callback(hostname, status, user=None):
        # 🎓 DIDATTICA: .after(0, ...) mette l'azione in coda nel thread UI principale.
        app.after(0, lambda: app.update_pc_status(hostname, status, user))

    udp_server = UDPServer(udp_callback)
    udp_server.start()

    # 5. Loop principale UI
    try:
        app.mainloop()
    except KeyboardInterrupt:
        log.info("Interruzione da tastiera.")
    finally:
        # Pulizia alla chiusura
        udp_server.stop()
        http_server.stop()
        log.info("Applicazione terminata.")

if __name__ == "__main__":
    main()
