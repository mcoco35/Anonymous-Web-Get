import os
import socket
import fcntl
import random 
import time

DEBUG                               = True
AWGET                               = 'awget.py'
SS                                  = 'ss.py'
RESTART                             = "<RESTART>"
END_TEST                            = "<ENDTEST>"
CHECK_OUTPUT                        = "<CHECK_OUTPUT>"
SUCCESS                             = "<SUCCESS>"
SUCCESS_LAST_CHAIN                  = "<SUCCESS_LAST_CHAIN>"
FAIL                                = "<FAIL>"
ERROR                               = "<ERROR>"
KILL                                = "<KILL>"
CAN_SET_UP_STEPPING_STONES_TEST     = "<CAN_SET_UP_STEPPING_STONES_TEST>"
ALL_STONES_HIT_DURING_AWGET         = "<ALL_STONES_HIT_DURING_AWGET>"
CORRECT_FILE_FROM_AWGET             = "<CORRECT_FILE_FROM_AWGET>"
DEFAULT_CHAIN_FILE                  = "chaingang.txt"
RANDOM_NUMBER_OF_CHAINS             = 2
MIN_NUMBER_CHAINS                   = 2

CHAIN_SERVERS = {
    'austin'  : 54367,
    'denver'  : 45674,
}


SAFE_FILES = [
    'tests',
    'utils',
    'test_server',
    'auto_grader',
    'student_autograder.README',
    SS,
    AWGET,
    DEFAULT_CHAIN_FILE
]

def make_non_blocking(fd):
        flags =fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

def generate_random_port():
    return random.randint(1024, 65535)

def get_random_chains(num_keys_to_get):
    if num_keys_to_get <= 0 or num_keys_to_get > len(CHAIN_SERVERS):
        raise ValueError("Invalid number of keys requested")

    keys = list(CHAIN_SERVERS.keys())
    random.shuffle(keys)

    random_keys = keys[:num_keys_to_get]

    return random_keys

def generate_chain_file(num_chains = RANDOM_NUMBER_OF_CHAINS, chain_file = DEFAULT_CHAIN_FILE):
    if num_chains == RANDOM_NUMBER_OF_CHAINS:
        num_chains = random.randint(MIN_NUMBER_CHAINS, len(CHAIN_SERVERS))
    chains = get_random_chains(num_chains)
    with open(chain_file, 'w') as new_chain_file:
        new_chain_file.write(f'{num_chains}\n')
        for i, chain in enumerate(chains):
            ip = socket.getaddrinfo(chain, None)[0][4][0]
            chain_string = f'{ip} {str(generate_random_port())}'
            chain_string =  chain_string if i >= num_chains-1 else chain_string + '\n'
            new_chain_file.write(chain_string)

def seen_stones(output):
    ss = []
    file = open(f'{DEFAULT_CHAIN_FILE}', "r")
    numStepingStones = int(file.readline())
    for line in file:
        ip, port = line.split(" ")
        ss.append((ip,port.strip()))

    stones_seen = [False]*len(ss)
    for out in output:
        for  i, stone in enumerate(ss):
            ip, port = stone
            if  port in out and ip in out:
                stones_seen[i]= True
    return all(stones_seen)


def get_most_recently_modified_file(directory_path):
    most_recent_file = None
    most_recent_timestamp = 0
    
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            timestamp = os.path.getmtime(file_path)
            if timestamp > most_recent_timestamp:
                most_recent_timestamp = timestamp
                most_recent_file = file_path
    
    return most_recent_file

def receive(client_socket):
    received_data = b""
    while True:
        chunk = client_socket.recv(128)  
        received_data += chunk
        if len(chunk) < 128:
            break

    if received_data:
        decoded_data = received_data.decode()
        return decoded_data

    return None  

def get_chains():
    file = open(DEFAULT_CHAIN_FILE, "r")
    int(file.readline())
    chain_list =[]
    for line in file:
        ip, port = line.split(" ")
        host_name = socket.gethostbyaddr(ip)[0].split('.')[0]
        chain_list.append((ip, host_name, port))
    file.close()
    return chain_list

def kill_test_severs(server_list):
    for server in server_list:
        server[0].send(KILL.encode())

def send_to_all_test_servers(server_list, item):
    for server in server_list:
        server[0].send(item.encode())

def found_all_strings(all_lines,string_list):
    return all(any(curr_string.lower() in line.lower() for line in all_lines) for curr_string in string_list)

def get_strings_after_timeout(process, string_list, timeout,any_of_strings=False):
    in_timeout = True
    start_time = time.time()
    all_lines = [""]
    while in_timeout:
        current_time = time.time()
        elapsed_time = current_time - start_time
        in_timeout = elapsed_time < timeout
        line = process.stdout.readline()
        error = process.stderr.readline()
        if len(all_lines) == 0 and line:
            all_lines = line
        elif line:
            all_lines.append(line)
        if DEBUG and len(line) != 0:
            print(f"[DEBUG] Line: {line}")
        if DEBUG and len(error) != 0:
            print(f"[DEBUG] Error:{error}")
        if any_of_strings and any(wanted_string in newline for newline in all_lines for wanted_string in string_list):
            return True, all_lines
        if found_all_strings(all_lines,string_list):
            return True, all_lines
     
    return False, all_lines

def get_port_of_stone(host_name, directory):
    file = open(f'{directory}/{DEFAULT_CHAIN_FILE}', "r")
    int(file.readline())
    for line in file:
        ip, port = line.split(" ")
        host = socket.gethostbyaddr(ip)[0].split('.')[0]
        if host_name == host:
            file.close()
            return port.strip()
    
        
def read_from_test_servers(test_servers):
    output = []

    for test_server, _, _ in test_servers:
        try:
            data = receive(test_server)
            if data:
                output.append(data)
        except socket.error:
            # Handle socket errors here if necessary
            pass

    if DEBUG:
        print(f"[DEBUG]: Output from test_servers: {output}")
    return output
