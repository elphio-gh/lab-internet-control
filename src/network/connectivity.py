import socket

def check_internet_connection(host="8.8.8.8", port=53, timeout=3):
    """
    Verifica la connettività internet tentando di connettersi a un host affidabile (Google DNS).
    L'operazione è bloccante per 'timeout' secondi, quindi dovrebbe essere eseguita in un thread separato.
    Utilizza socket diretto per ridurre l'overhead rispetto a richieste HTTP.
    
    Args:
        host (str): L'host da contattare (default: 8.8.8.8).
        port (int): La porta da contattare (default: 53 DNS).
        timeout (int): Timeout in secondi.
        
    Returns:
        bool: True se la connessione ha successo, False altrimenti.
    """
    try:
        # Tenta una semplice connessione TCP/UDP socket
        # Host: 8.8.8.8 (Google Public DNS) è altamente affidabile
        # Port: 53 (DNS) è generalmente aperto
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except OSError:
        return False
    except Exception:
        return False
