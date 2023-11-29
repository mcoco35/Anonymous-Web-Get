###############################################
# Group Name  : XXXXXX

# Member1 Name: XXXXXX
# Member1 SIS ID: XXXXXX
# Member1 Login ID: XXXXXX

# Member2 Name: XXXXXX
# Member2 SIS ID: XXXXXX
# Member2 Login ID: XXXXXX
###############################################

###############################################
# MUST KEEP: sets printing butter to 1, so it will always flush. allows the autograder to work. 
import sys
import socket
import threading
import os
import random
import subprocess
import argparse
import pickle
sys.stdout = open(sys.stdout.fileno(), 'w', buffering=1)
###############################################

def handle_client(connection, address, chain_list, url):
    if not chain_list:
        # Download file
        subprocess.run(['wget', url])
        filename = url.split('/')[-1]
        with open(filename, 'rb') as file:
            while True:
                bytes_read = file.read(1024)
                if not bytes_read:
                    break
                connection.sendall(bytes_read)
        # Delete file
        os.remove(filename)
    else:
        # Select and remove the next stepping stone
        next_ss = random.choice(chain_list)
        chain_list.remove(next_ss)
        next_host, next_port = next_ss.split()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ss_socket:
            ss_socket.connect((next_host, int(next_port)))
            # Serialize data with pickle
            serialized_data = pickle.dumps([url] + chain_list)
            ss_socket.sendall(serialized_data)
            while True:
                data = ss_socket.recv(1024)
                if not data:
                    break
                connection.sendall(data)

    connection.close()


def main(port):
    host = socket.gethostname()
    print(f"Hostname: {host}\nPort: {port}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()

        try:
            while True:
                conn, addr = s.accept()
                data = conn.recv(1024)
                if data:
                    data = pickle.loads(data)
                    url = data[0]
                    chain_list = data[1:]
                #url, num_ss, *chain_list = data.split('\n')
                threading.Thread(target=handle_client, args=(conn, addr, chain_list, url)).start()
        except KeyboardInterrupt:
            print("\nServer is shutting down.")
        finally:
            s.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stepping Stone for Anonymous Web Get")
    parser.add_argument('-p', '--port', type=int, default=20000, help='Port number to listen on')
    args = parser.parse_args()
    
    main(args.port)