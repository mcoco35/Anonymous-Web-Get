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
import os
import random
sys.stdout = open(sys.stdout.fileno(), 'w', buffering=1)
###############################################

def read_chain_file(chainfile):
    with open(chainfile, 'r') as file:
        lines = file.readlines()
    num_ss = int(lines[0].strip())
    ss_list = [line.strip() for line in lines[1:num_ss+1]]
    return ss_list

def save_file(filename, conn):
    with open(filename, 'wb') as file:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            file.write(data)

def main(url, chainfile):
    if not chainfile:
        if os.path.exists("chaingang.txt"):
            chainfile = "chaingang.txt"
        else:
            print("Error: Chainfile not found.")
            sys.exit(1)

    ss_list = read_chain_file(chainfile)
    selected_ss = random.choice(ss_list)
    ss_list.remove(selected_ss)
    host, port = selected_ss.split()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, int(port)))
        s.sendall(f"{url}\n{len(ss_list)}\n" + "\n".join(ss_list).encode())

        filename = url.split('/')[-1] if '/' in url else 'index.html'
        save_file(filename, s)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: awget.py [URL] [-c chainfile]")
        sys.exit(1)

    url = sys.argv[1]
    chainfile = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == '-c' else None
    main(url, chainfile)