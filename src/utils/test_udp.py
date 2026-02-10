import socket

def send_test_packet():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', 5005)
    # [UPDATED] Protocollo: HOST|STATUS|USER
    message = b'PC-TEST-01|ON|mario.rossi'
    
    try:
        print(f"Sending message: {message}")
        sent = sock.sendto(message, server_address)
        print(f"Sent {sent} bytes")
    finally:
        sock.close()

if __name__ == "__main__":
    send_test_packet()
