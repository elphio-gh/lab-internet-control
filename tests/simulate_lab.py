
import threading
import socket
import time
import urllib.request
import argparse
import random
import sys

# Colori per output terminale
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

class SimulatedPC(threading.Thread):
    def __init__(self, hostname, user, udp_port=5005, http_port=8080):
        super().__init__()
        self.hostname = hostname
        self.user = user
        self.udp_port = udp_port
        self.http_port = http_port
        self.status = "ON"
        self.internet_status = "UNKNOWN"
        self.running = True
        self.daemon = True # Muore con il main thread

    def run(self):
        # Socket UDP per invio telemetria
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except Exception as e:
            print(f"{RED}[ERR] {self.hostname}: Impossibile creare socket UDP: {e}{RESET}")
            return

        while self.running:
            # 1. Invia UDP Telemetria
            # Formato: HOSTNAME|STATUS|USER
            message = f"{self.hostname}|{self.status}|{self.user}"
            try:
                sock.sendto(message.encode('utf-8'), ('127.0.0.1', self.udp_port))
                # print(f"[DEBUG] {self.hostname} -> UDP Sent: {message}")
            except Exception as e:
                print(f"{RED}[ERR] {self.hostname}: Errore invio UDP: {e}{RESET}")

            # 2. Check HTTP PAC (Simula browser)
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{self.http_port}/proxy.pac", timeout=2) as response:
                    pac_content = response.read().decode('utf-8')
                    
                    # Logica semplice: se contiene "PROXY", siamo bloccati. Se "DIRECT", siamo liberi.
                    # Nota: il PAC reale potrebbe avere logiche complesse, ma qui ci interessa
                    # se stiamo venendo reindirizzati al proxy locale di blocco (es. 127.0.0.1:6666)
                    
                    new_internet_status = "BLOCKED" if "PROXY" in pac_content else "FREE"
                    
                    if new_internet_status != self.internet_status:
                        self.internet_status = new_internet_status
                        # [FIX] Aggiorna lo stato inviato via UDP per riflettere il blocco nella Dashboard
                        # OFF = Internet Bloccato (Rosso)
                        # ON = Internet Libero (Verde)
                        self.status = "OFF" if self.internet_status == "BLOCKED" else "ON"
                        
                        color = RED if self.internet_status == "BLOCKED" else GREEN
                        print(f"{color}[CHANGE] {self.hostname}: Internet is now {self.internet_status} (UDP Status: {self.status}){RESET}")

            except Exception as e:
                # Se il server HTTP è giù, consideriamo "OFFLINE"
                if self.internet_status != "OFFLINE":
                    self.internet_status = "OFFLINE"
                    print(f"{RED}[ERR] {self.hostname}: Server PAC irraggiungibile ({e}){RESET}")

            # Attesa random tra i cicli per non sincronizzare troppo
            time.sleep(2 + random.random())

    def stop(self):
        self.running = False


def main():
    parser = argparse.ArgumentParser(description="Simula N PC studenti per Lab Internet Control")
    parser.add_argument("--count", type=int, default=5, help="Numero di PC da simulare")
    parser.add_argument("--udp-port", type=int, default=5005, help="Porta UDP del server (Default: 5005)")
    parser.add_argument("--http-port", type=int, default=8080, help="Porta HTTP del server PAC (Default: 8080)")
    args = parser.parse_args()

    print(f"Avvio simulazione di {args.count} PC...")
    
    # [NEW] Generiamo il file JSON per il VeyonManager (Mock su Linux)
    # Serve affinché la dashboard sappia quali PC mostrare
    import json
    sim_hosts = [f"PC-{i:02d}" for i in range(1, args.count + 1)]
    try:
        with open("simulated_hosts.json", "w") as f:
            json.dump(sim_hosts, f)
        print(f"{GREEN}[INFO] Creato file 'simulated_hosts.json' per la dashboard.{RESET}")
    except Exception as e:
        print(f"{RED}[ERR] Impossibile creare JSON simulazione: {e}{RESET}")

    pcs = []
    
    for i in range(1, args.count + 1):
        hostname = f"PC-{i:02d}" # PC-01, PC-02...
        user = f"Studente-{i}"
        
        pc = SimulatedPC(hostname, user, args.udp_port, args.http_port)
        pcs.append(pc)
        pc.start()
        print(f"Avviato {hostname} ({user})")

    print(f"\n{GREEN}Simulazione attiva! Premi Ctrl+C per terminare.{RESET}")
    print("I PC invieranno telemetria ogni ~2.5 secondi.")
    print("Monitoreranno lo stato di blocco internet in tempo reale.\n")

    # [NEW] Avvio automatico dell'applicazione principale
    import subprocess
    import os
    
    # Determina il path assoluto di src/main.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    main_py = os.path.join(project_root, "src", "main.py")
    
    print(f"{GREEN}[INFO] Avvio applicazione principale: {main_py}{RESET}")
    app_process = None
    try:
        # Usa sys.executable per usare lo stesso interprete (venv)
        app_process = subprocess.Popen([sys.executable, main_py])
    except Exception as e:
        print(f"{RED}[ERR] Errore avvio app principale: {e}{RESET}")

    try:
        while True:
            time.sleep(1)
            # Controlla se la GUI è stata chiusa dall'utente
            if app_process and app_process.poll() is not None:
                print(f"{RED}[INFO] Applicazione principale chiusa. Termino simulazione.{RESET}")
                break
    except KeyboardInterrupt:
        print("\nArresto simulazione in corso...")
    finally:
        for pc in pcs:
            pc.stop()
        
        if app_process and app_process.poll() is None:
            print(f"{GREEN}[INFO] Chiusura applicazione principale...{RESET}")
            app_process.terminate()
            try:
                app_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                 app_process.kill()
        
        print("Finito.")

if __name__ == "__main__":
    main()
