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
import uuid
import pickle
sys.stdout = open(sys.stdout.fileno(), 'w', buffering=1)
###############################################

def handle_client(connection, address, chain_list, url):
    if not chain_list:
        filename = f"{str(uuid.uuid4())}_{url.split('/')[-1]}"
        subprocess.run(['wget', '-O', filename, '-N', url])
        with open(filename, 'rb') as file:
            while True:
                bytes_read = file.read(1024)
                if not bytes_read:
                    break
                connection.sendall(bytes_read)
        os.remove(filename)
    else:
        next_ss = random.choice(chain_list)
        chain_list.remove(next_ss)
        next_host, next_port = next_ss.split()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ss_socket:
            ss_socket.connect((next_host, int(next_port)))
            serialized_data = pickle.dumps([url] + chain_list)
            ss_socket.sendall(serialized_data)

            print(f'ss {next_host}, {next_port}:')
            print(f'Request: {url}...')
            print(f'chainlist is')
            for ss_entry in chain_list:
                print(ss_entry)
            print(f'next SS is {next_ss}')
            print('waiting for file...')
            
            while True:
                data = ss_socket.recv(1024)
                if not data:
                    break
                connection.sendall(data)

            print('Relaying file...')
    
    print('Goodbye!')
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
