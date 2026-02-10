from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from src.utils.logger import log
from src.utils.config import config
from src.core.pac_manager import PACManager

class PACRequestHandler(BaseHTTPRequestHandler):
    """
    Gestore richieste HTTP per servire il file PAC.
    """
    
    # 🎓 DIDATTICA: Riferimento al PACManager per generare il contenuto al volo.
    pac_manager = None 

    def do_GET(self):
        """Risponde alle richieste GET (es. http://localhost:8080/proxy.pac)"""
        if self.path == '/proxy.pac':
            self.send_response(200)
            self.send_header('Content-type', 'application/x-ns-proxy-autoconfig')
            self.end_headers()
            
            if self.pac_manager:
                content = self.pac_manager.generate_pac_script()
                self.wfile.write(content.encode('utf-8'))
                log.info(f"PAC servito a {self.client_address[0]}")
            else:
                self.wfile.write(b"No PAC Manager configured")
                log.error("PAC Manager non configurato nel server HTTP")
        else:
            self.send_error(404, "File Not Found")

class PACHTTPServer:
    """
    Server HTTP che gira in un thread separato.
    """
    def __init__(self, pac_manager):
        self.port = config.get("http_port")
        self.server = None
        self.thread = None
        # Impostiamo il gestore statico
        PACRequestHandler.pac_manager = pac_manager

    def start(self):
        """Avvia il server in un thread separato per non bloccare la UI."""
        if self.server:
            return

        try:
            self.server = HTTPServer(('0.0.0.0', self.port), PACRequestHandler)
            self.thread = threading.Thread(target=self.server.serve_forever)
            self.thread.daemon = True # Il thread muore quando chiudiamo l'app
            self.thread.start()
            log.info(f"Server PAC HTTP avviato sulla porta {self.port}")
        except Exception as e:
            log.error(f"Errore avvio server HTTP: {e}")

    def stop(self):
        """Ferma il server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None
            log.info("Server PAC HTTP fermato.")
