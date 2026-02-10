import socket
import threading
from src.utils.logger import log
from src.utils.config import config

class UDPServer:
    """
    Server UDP per ricevere la telemetria dai PC studenti.
    Formato messaggio: HOSTNAME|STATO|UTENTE (opz.)
    """

    def __init__(self, message_callback):
        self.ip = "0.0.0.0"
        self.port = config.get("udp_port")
        self.sock = None
        self.running = False
        self.callback = message_callback
        self.thread = None

    def start(self):
        if self.running:
            return

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((self.ip, self.port))
            self.running = True
            
            self.thread = threading.Thread(target=self._listen_loop)
            self.thread.daemon = True
            self.thread.start()
            log.info(f"Server UDP Telemetria avviato su {self.ip}:{self.port}")
        except Exception as e:
            log.error(f"Errore avvio server UDP: {e}")

    def _listen_loop(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                message = data.decode('utf-8').strip()
                
                log.info(f"Ricevuto UDP da {addr}: {message}")
                
                # Parsiamo il messaggio: HOSTNAME|STATUS|USER
                parts = message.split("|")
                hostname = parts[0]
                status = "UNKNOWN"
                user = None
                
                if len(parts) >= 2:
                    status = parts[1]
                if len(parts) >= 3:
                    user = parts[2]
                
                if self.callback:
                    self.callback(hostname, status, user)

            except OSError:
                break
            except Exception as e:
                log.error(f"Errore ricezione UDP: {e}")

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()
        log.info("Server UDP fermato.")
