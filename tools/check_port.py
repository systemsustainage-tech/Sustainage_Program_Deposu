
import socket
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

HOST = '72.62.150.207'
PORT = 22

def main():
    try:
        logging.info(f"Checking {HOST}:{PORT}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((HOST, PORT))
        if result == 0:
            logging.info("Port 21 is OPEN")
            # Try to receive banner
            try:
                banner = sock.recv(1024)
                logging.info(f"Banner: {banner}")
            except:
                pass
        else:
            logging.info(f"Port 21 is CLOSED/FILTERED (Code: {result})")
        sock.close()
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()
